from logging import PlaceHolder
import numpy as np
from sklearn.utils import check_matplotlib_support
import streamlit as st
from streamlit_option_menu import option_menu
import sklearn
import datetime
import time
import pytz
import pickle
import re # for regex
import random
import pandas as pd
import os

from validators import card_number


import database_access

from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score
from sklearn import ensemble

# Importing built-in library for SQLite functionality
import sqlite3 as sql



epochTime = datetime.datetime(1970,1,1)

if 'cardName' not in st.session_state:
    st.session_state['cardName'] = ''
if 'cardNo' not in st.session_state:
    st.session_state['cardNo'] = ''
if 'cardDate' not in st.session_state:
    st.session_state['cardDate'] = ''
if 'cardCVV' not in st.session_state:
    st.session_state['cardCVV'] = ''

#def prediction(model, VehType, startTime, endTime, totalCharge, Duration, effectiveCharge):
def prediction(model, featureArray):
    toNParray = np.asarray(featureArray)
    ReshapedArray = toNParray.reshape(1,-1)

    finalPred = model.predict(ReshapedArray)

    if(finalPred[0] == 0):
        return 'Short term parking' 
    else:
        return 'Seasonal parking'

def modelSelect():

    script_path = os.path.abspath(__file__) #e.g. /path/to/dir/smartparkingapp.py
    script_dir = os.path.split(script_path)[0] #e.g. /path/to/dir/ - removes the current file name

    #getting user input for which model to use
    option = st.selectbox(
     'What AI model would you like to use?',
     ('XGBoost - Default', 'Logistic Regression', 'K-nearest neighbours', 'SVC', 'SGD', 'Random Forest', 'Naive Bayes', 'MLP', 'Decision Tree'))
     
    if(option == "XGBoost - Default"):
        rel_path = "pkl folder/XGBoost_pkl_Final.pkl" #relative path of model files
        abs_file_path = os.path.join(script_dir, rel_path) #joins the 2 strings together to get the absolute path
        model = pickle.load(open(abs_file_path, 'rb'))
        return model
        

    elif(option == "K-nearest neighbours"):
        rel_path = "pkl folder/KNeighborsClassifier.pkl"
        abs_file_path = os.path.join(script_dir, rel_path)
        model = pickle.load(open(abs_file_path, 'rb'))
        return model

    elif(option == "SVC"):
        rel_path = "pkl folder/SVC.pkl"
        abs_file_path = os.path.join(script_dir, rel_path)
        model = pickle.load(open(abs_file_path, 'rb'))
        return model

    elif(option == "SGD"):
        rel_path = "pkl folder/SGDClassifier.pkl"
        abs_file_path = os.path.join(script_dir, rel_path)
        model = pickle.load(open(abs_file_path, 'rb'))
        return model

    elif(option == "Random Forest"):
        rel_path = "pkl folder/RandomForestClassifier.pkl"
        abs_file_path = os.path.join(script_dir, rel_path)
        model = pickle.load(open(abs_file_path, 'rb'))
        return model

    elif(option == "Logistic Regression"):
        rel_path = "pkl folder/logreg.pkl"
        abs_file_path = os.path.join(script_dir, rel_path)
        model = pickle.load(open(abs_file_path, 'rb')) 
        return model

    elif(option == "Naive Bayes"):
        rel_path = "pkl folder/NaiveBayes_pkl_Final.pkl"
        abs_file_path = os.path.join(script_dir, rel_path)
        model = pickle.load(open(abs_file_path, 'rb'))
        return model

    elif(option == "Decision Tree"):
        rel_path = "pkl folder/DecisionTree_pkl_latest.pkl"
        abs_file_path = os.path.join(script_dir, rel_path)
        model = pickle.load(open(abs_file_path, 'rb'))
        return model
    
    elif(option == "MLP"):
        rel_path = "pkl folder/MLP_pkl_latestest"
        abs_file_path = os.path.join(script_dir, rel_path)
        model = pickle.load(open(abs_file_path, 'rb'))
        return model
    
def durationSelect():
    #Calculate duration
    duration = st.number_input("Enter parking duration in minutes: ",value=30,step=30)

    if(duration < 0):
        error = '<p style="font-family:sans-serif; color:Red; font-size: 12px;">Invalid duration</p>'

        return st.markdown(error, unsafe_allow_html=True)

    else:
        return duration

def regex(plateNo):
    pattern = "([SFG][^AIO\d][^AIO\d][0-9]{1,4}[^FINOQVW\W\d])$|([SFG][^AIO\d][0-9]{1,4}[^FINOQVW\W\d])$|(J[^AIO\d][0-9]{1,4})$|(J[^AIO\d][^AIO\d][0-9]{1,4})$"
    if(re.search(pattern, plateNo)):
        return 'Valid'
    else:   
        return 'Invalid'

def epochCalc(dateTime):
    #Line to get amount of days and hours since epoch time using end datetime 
    endEpoch = dateTime - epochTime
    #Converting time to days so i can get total amount of seconds since epoch time
    strEpoch = str(endEpoch)
    endDaysEpoch = strEpoch.split(' days')
    intDaysEpoch = int(endDaysEpoch[0])
    #Converting the number of days in seconds
    daySeconds = intDaysEpoch * 3600 * 24
    #Finding the total seconds, adding up the seconds in days and the time seconds the user had to input
    inSeconds = daySeconds + endEpoch.seconds
    return inSeconds

def time_in_range(start, end, current):
    #Returns whether current is in the range [start, end]
    return start <= current <= end 

def chargeCalc(plateNo, duration, intCharge):
    # strtimeNow = datetime.datetime.strftime(timeNow,"%Y/%m/%d, %H:%M")
    # DTtimeNow = datetime.datetime.strptime(strtimeNow,"%Y/%m/%d, %H:%M")


    if(str(plateNo).startswith('J') or str(plateNo).startswith('S')):
        intCharge += 0.6 * int((duration/30))

    elif(str(plateNo).startswith("F")):
        intCharge += 0.65

        if(int(((duration/60)/12)) > 0):
            intCharge += (0.65 * int(((duration/60)/12)))
        
    elif(str(plateNo).startswith("G")):
        intCharge += 1.2 * int((duration/30))

    return intCharge

def customMsg(msg, wait=3, type_='warning'):
    placeholder = st.empty()
    styledMsg = f'\
        <div class="element-container" style="width: 693px;">\
            <div class="alert alert-{type_} stAlert" style="width: 693px;">\
                <div class="markdown-text-container">\
                    <p>{msg}</p></div></div></div>\
    '
    placeholder.markdown(styledMsg, unsafe_allow_html=True)
    time.sleep(wait)
    placeholder.empty()


def return_payment_info():
    st.session_state['cardName'] = st.session_state['cardName']
    st.session_state['cardNo'] = st.session_state['cardNo']
    st.session_state['cardDate'] = st.session_state['cardDate']
    st.session_state['cardCVV'] = st.session_state['cardCVV']


def main():
    database_access.check_db()

    #sidebar code
    with st.sidebar:
        nav = option_menu(
            menu_title = "Navigation",
            options = ["Home", "Sessions", "Payment"]
        )

    if(nav == "Home"):
        VehType = 0
        sesStart = 0
        sessEnd = 0
        intCharge = 0
        duration = 0
        effCharge = 0
        lotNumber = 0
        intCharge = 0
        #Title of our app
        st.title('HDB Smart Parking App')

        #Display session start time
        utctimeNow = datetime.datetime.utcnow()
        timeNow = datetime.datetime.now()
        new_title = '<p style="font-family:sans-serif; color:Green; font-size: 12px;">' + 'Session start time: ' + str(datetime.datetime.now().strftime("%Y/%m/%d, %H:%M")) + '</p>'
        st.markdown(new_title, unsafe_allow_html=True)

        #getting user input for which model to use
        model = modelSelect()

         #Getting user input license plate
        plateNo = st.text_input("Enter license plate").upper()
        if(plateNo != "" and regex(plateNo) == 'Invalid'):
            error = '<p style="font-family:sans-serif; color:Red; font-size: 12px;">Invalid License plate</p>'
            st.markdown(error, unsafe_allow_html=True)
        
        if(plateNo.startswith('J') or plateNo.startswith('S')):
            VehType = 0
          
        elif(plateNo.startswith("F")):
            VehType = 1

        elif(plateNo.startswith("G")):
            VehType = 2


        duration = durationSelect()

        #Calculate session start and end in minutes since Epoch
        sesStart = round((epochCalc(utctimeNow)),2)
        sessEnd = duration + sesStart
        
        sesStartDate = datetime.datetime.fromtimestamp((sesStart))

        try: 
            SessEndDate = datetime.datetime.fromtimestamp((sessEnd))
            st.text(str(int(duration/60)) + " hours " + str((duration%60)) + " minutes" )
        except:
            error = '<p style="font-family:sans-serif; color:Red; font-size: 12px;">Invalid duration</p>'
            st.markdown(error, unsafe_allow_html=True)


        intCharge = 0
        intCharge = chargeCalc(plateNo, duration, intCharge)       

        effCharge = intCharge       

        #initializing the prediciton variable
        pred = ''

        featureList = [VehType, sesStart, sessEnd, intCharge, duration, effCharge]
        

        if(plateNo != '' and  regex(plateNo) != 'Invalid' and duration > 0):
            # Connecting to database
            # prev_session = get_previous_sessions(plateNo) # Uncomment once get_previous_sessions() function is complete

            if(st.button('Predict',disabled=False)):
                if(database_access.noCurrentSess(plateNo)):           
                    pred = prediction(model, featureList)
                    st.success(pred)
                    #st.text("For troubleshooting purpose:" + "\nVehType: " + str(VehType) + "\nSession start: " + str(sesStart) + "\nSession End: " + str(sessEnd) + "\nTotal charge: " + str(intCharge) + "\nDuration: " + str(duration) + "\nEffective charge: " + str(effCharge))
                    
                    #Depending on model prediction, will assign a lot number to user
                    if(pred == 'Short term parking'):
                        lotNumber =  random.randint(161,480)
                    elif(pred == 'Seasonal parking'):
                        lotNumber =  random.randint(1,161)
                    elif(VehType == 1):
                        lotNumber =  random.randint(481,500)

                    sessionDeet = [plateNo, sesStartDate.strftime("%Y/%m/%d, %H:%M"), SessEndDate.strftime("%Y/%m/%d, %H:%M"), effCharge ,lotNumber, False]
                    database_access.add_session(sessionDeet)
                    
                    #Displaying lot number and session information for user
                    st.text("License plate: " + plateNo + "\nSession end time: " + str(SessEndDate.strftime("%Y/%m/%d, %H:%M")) + "\nLot number: " + str(lotNumber) + "\nTotal cost: $" + str(round(effCharge,2)))
                
                else:
                    st.text("There is already a current active session with this license plate")

                
        else:
            st.button('Predict',disabled=True)
        
        return_payment_info()

    elif(nav == "Sessions"):
        
        if "input" not in st.session_state:
            st.session_state.input = False

        if "extend" not in st.session_state:
            st.session_state.extend = False

        CheckPlate = st.text_input('Please enter license plate to search parking history for:').upper()

        currentSession =  st.empty()
        prevSession = st.empty()
        extendUI = st.empty()


        if(CheckPlate != ''):
            prevSess = database_access.get_previous_sessions(CheckPlate)
            prevSessDF = pd.DataFrame(prevSess, columns = ['License plate', 'Session Start', 'Session End', 'Cost', 'Lot number'])
            prevSessDF.Cost = "$" + prevSessDF['Cost'].round(decimals = 2).map(str)  
            


            if(database_access.noCurrentSess(CheckPlate) == False):       
                with currentSession.container():
                    st.header('Current session')
                    getCurrent = database_access.get_current_session(CheckPlate)
                    currentSess = pd.DataFrame(getCurrent, columns = ['License plate', 'Session Start', 'Session End', 'Cost', 'Lot number'])
                    currentSess.Cost = "$" + str(round(currentSess.Cost[0],2))
                    st.dataframe(currentSess)

                    EndSessionButton, extendSession = st.columns([1,1])

                    EndSessionButton = EndSessionButton.button('End session' )

                    extendSession = extendSession.button('Extend session')

                    if(EndSessionButton):
                        placeholdermsg = st.empty()
                        database_access.endSession(CheckPlate)
                        currentSession.empty()
                        placeholdermsg.success('Current active session has been ended')

                    if(extendSession):
                        st.session_state.input = True

                    if(st.session_state.input):                   
                        currentDT = currentSess['Session End'][0]
                        strToDate = datetime.datetime.strptime(currentDT, "%Y/%m/%d, %H:%M")

                        duration = durationSelect()          
                        try:
                            updatedDT = (strToDate + datetime.timedelta(minutes=duration)).strftime("%Y/%m/%d, %H:%M")
                            st.text(str(int(duration/60)) + " hours " + str((duration%60)) + " minutes" )  
                        except:
                            error = '<p style="font-family:sans-serif; color:Red; font-size: 12px;">Invalid duration</p>'
                            st.markdown(error, unsafe_allow_html=True)
                        
                        intCharge = database_access.getTotalCost(CheckPlate)

                        intCharge = round(chargeCalc(CheckPlate, duration, float(intCharge)),2)

                        print(intCharge)

                        confirm = st.button('Confirm')

                        if(confirm):
                            st.success(database_access.extendTimeCost(updatedDT,intCharge,CheckPlate))
                            st.session_state.input = False
                            st.session_state.extend = True
                            st.experimental_rerun()

                    if(st.session_state.extend):
                        st.success("Session has been extended")
                    st.session_state.extend = False

            if(database_access.noCurrentSess(CheckPlate) == False and len(prevSessDF.index) > 0):
                with prevSession.container():
                    st.header('Past Sessions')
                    st.dataframe(prevSessDF)
                    clearHist = st.button('Clear history')

                if(clearHist):
                        database_access.deleteSessions(CheckPlate)
                        st.success("History has been cleared")
                        prevSession.empty()

            if(database_access.noCurrentSess(CheckPlate) and len(prevSessDF.index) == 0):
                st.text('No parking history found')


        return_payment_info()


    elif(nav == "Payment"):
        with st.form(key='payment_form'):
            cardName = st.text_input('Cardholder name', value=st.session_state['cardName'], key='cardName')
            cardNo = st.text_input("Card number", value=st.session_state['cardNo'], key='cardNo')

            cardDate, cardCVV = st.columns(2)
            cardDate = cardDate.text_input("Expiry date", value=st.session_state['cardDate'], key='cardDate')
            cardCVV = cardCVV.text_input("Security code/CVV", value=st.session_state['cardCVV'], key='cardCVV')

            submit_button = st.form_submit_button(label='Submit')

#calling the main function
main()





