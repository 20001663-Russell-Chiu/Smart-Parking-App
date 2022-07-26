import numpy as np
import streamlit as st
from streamlit_option_menu import option_menu
import sklearn
import datetime
import pytz
import pickle
import re # for regex
import random
import pandas as pd


import database_access

from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score
from sklearn import ensemble

# Importing built-in library for SQLite functionality
import sqlite3 as sql



epochTime = datetime.datetime(1970,1,1)

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
    #getting user input for which model to use
    option = st.selectbox(
     'What AI model would you like to use?',
     ('XGBoost - Default', 'Logistic Regression', 'K-nearest neighbours', 'SVC', 'SGD', 'Random Forest', 'Naive Bayes', 'MLP', 'Decision Tree'))
     
    if(option == "XGBoost - Default"):
        model = pickle.load(open('XGBoost_pkl_Latest6.pkl', 'rb'))
        return model
        

    elif(option == "K-nearest neighbours"):
        model = pickle.load(open('KNeighborsClassifier.pkl', 'rb'))
        return model

    elif(option == "SVC"):
        model = pickle.load(open('SVC.pkl', 'rb'))
        return model

    elif(option == "SGD"):
        model = pickle.load(open('SGDClassifier.pkl', 'rb'))
        return model

    elif(option == "Random Forest"):
        model = pickle.load(open('RandomForestClassifier.pkl', 'rb'))
        return model

    elif(option == "Logistic Regression"):
        model = pickle.load(open('logreg.pkl', 'rb')) 
        return model

    elif(option == "Naive Bayes"):
        model = pickle.load(open('NaiveBayes_pkl_Latest3.pkl', 'rb'))
        return model

    elif(option == "Decision Tree"):
        model = pickle.load(open('DecisionTree_pkl_latest.pkl', 'rb'))
        return model
    
    elif(option == "MLP"):
        model = pickle.load(open('MLP_pkl_latest', 'rb'))
        return model
    

def regex(plateNo):
    pattern = "([SFG][^AIO][^IO\d]\d\d\d\d[^FINOQVW\W\d])$|([SFG][^AIO]\d\d\d\d[^FINOQVW\W\d])$|(J[^AIO]\d\d\d\d)$|(J[^AIO][^AIO]\d\d\d\d)$"
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

def main():

    database_access.check_db()


    #sidebar code
    with st.sidebar:
        nav = option_menu(
            menu_title = "Navigation",
            options = ["Home", "History", "Payment"]
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
        plateNo = st.text_input('Please enter License plate number: ').upper()
        if(plateNo != "" and regex(plateNo) == 'Invalid'):
            error = '<p style="font-family:sans-serif; color:Red; font-size: 12px;">Invalid License plate</p>'
            st.markdown(error, unsafe_allow_html=True)




        #Calculate duration
        duration = st.number_input("Enter parking duration in minutes: ",value=30,step=30)
        validDuration = True
        if(duration < 0):
            validDuration = False
            error = '<p style="font-family:sans-serif; color:Red; font-size: 12px;">Invalid duration</p>'
            st.markdown(error, unsafe_allow_html=True)
        else:
            hours = duration/60
            st.text(str(int(hours)) + " hours " + str((duration%60)) + " minutes" )


        #Calculate session start and end in minutes since Epoch
        sesStart = round((epochCalc(utctimeNow)/60),2)
        sessEnd = duration + sesStart
        
        SessEndDate = datetime.datetime.fromtimestamp((sessEnd*60))
        sesStartDate = datetime.datetime.fromtimestamp((sesStart*60))

        if(plateNo.startswith('J') or plateNo.startswith('S')):
            VehType = 0
            intCharge = 0.6 * int((duration/30))

        elif(plateNo.startswith("F")):
            VehType = 1
            start = datetime.datetime(timeNow.year, timeNow.month, timeNow.day,7,0,0)
            end = datetime.datetime(timeNow.year, timeNow.month, timeNow.day,22,30,0)

            #Night time charge range
            startNight = datetime.datetime(timeNow.year, timeNow.month, timeNow.day,22,30,0)
            endNight = datetime.datetime(timeNow.year, timeNow.month, (timeNow.day + 1),7,0,0)

            #If session start time and session end date is within both day and night time periods, the fee will be $1.2
            if(time_in_range(start,end, timeNow) and time_in_range(startNight,endNight, SessEndDate)):
                intCharge += 1.2
            #If the session starts in the day but ends before night time, the fee will be $0.65 and vice versa
            elif(time_in_range(start,end, timeNow) or time_in_range(startNight,endNight, SessEndDate)):
                intCharge += 0.65

        elif(plateNo.startswith("G")):
            VehType = 2
            intCharge = 1.2 * int((duration/30))        

        effCharge = intCharge

        #initializing the prediciton variable
        pred = ''

        featureList = [VehType, sesStart, sessEnd, intCharge, duration, effCharge]
        

        if(plateNo != '' and  regex(plateNo) != 'Invalid' and validDuration == True):
            # Connecting to database
            # prev_session = get_previous_sessions(plateNo) # Uncomment once get_previous_sessions() function is complete
        
            if(st.button('Predict',disabled=False)):
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

                sessionDeet = [plateNo, sesStartDate.strftime("%Y/%m/%d, %H:%M"), SessEndDate.strftime("%Y/%m/%d, %H:%M"), lotNumber]
                database_access.add_session(sessionDeet)
                
                #Displaying lot number and session information for user
                st.text("License plate: " + plateNo + "\nSession end time: " + str(SessEndDate.strftime("%Y/%m/%d, %H:%M")) + "\nLot number: " + str(lotNumber) + "\nTotal cost: $" + str(round(effCharge,2)))
        else:
            st.button('Predict',disabled=True)
        


    elif(nav == "History"):
        CheckPlate = st.text_input('Please enter license plate to search parking history for:').upper()

        if(CheckPlate != ''):
            DBrows = database_access.get_previous_sessions(CheckPlate)
            df = pd.DataFrame(DBrows, columns = ['License plate', 'Session Start', 'Session End', 'Lot number'])
            if(len(df.index) == 0):
                st.text('No parking history found')
            else:
                st.table(df)
                if(st.button('Clear history')):
                    st.text(database_access.deleteSessions(CheckPlate))

    elif(nav == "Payment"):
        cardDeet = st.text_input("Please enter card ")
            

#calling the main function
main()





