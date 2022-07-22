import numpy as np
import streamlit as st
import sklearn
import datetime
import pytz
import pickle
import re # for regex
import random

from xgboost import XGBClassifier
import xgboost as xgb


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
        print(finalPred[0])
        return 'Short term parking' 
    else:
        return 'Seasonal parking'

def modelSelect():
    #getting user input for which model to use
    option = st.selectbox(
     'What AI model would you like to use?',
     ('XGBoost - Default', 'Logistic Regression', 'K-nearest neighbours', 'SVC', 'SGD', 'Random Forest', 'Naive Bayes', 'MLP', 'Decision Tree'))
     
    if(option == "XGBoost - Default"):
        model = xgb.XGBClassifier()
        model.load_model('model.txt')

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
        model = pickle.load(open('NaiveBayes_pkl_Latest2.pkl', 'rb'))
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

def convert_datetime_timezone(dt, tz1, tz2):
    tz1 = pytz.timezone(tz1)
    tz2 = pytz.timezone(tz2)

    dt = datetime.datetime.strptime(dt,"%Y-%m-%d %H:%M:%S")
    dt = tz1.localize(dt)
    dt = dt.astimezone(tz2)
    dt = dt.strftime("%Y-%m-%d %H:%M:%S")

    return dt

def main():
    #sidebar code
    nav = st.sidebar.radio("Navigation",["Home",""])

    if(nav == "Home"):
        VehType = 0
        sesStart = 0
        sessEnd = 0
        totalCharge = 0
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


        if(plateNo.startswith("S" or "J")):
            VehType = 0
        elif(plateNo.startswith("F")):
            VehType = 1
        elif(plateNo.startswith("G")):
            VehType = 2
       

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

        intCharge = 0
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
                    
                if(pred == 'Short term parking'):
                    lotNumber =  random.randint(161,480)
                elif(pred == 'Seasonal parking'):
                    lotNumber =  random.randint(1,161)
                elif(VehType == 1):
                    lotNumber =  random.randint(481,500)
                st.text("License plate: " + plateNo + "\nSession end time: " + str(SessEndDate.strftime("%Y/%m/%d, %H:%M")) + "\nLot number: " + str(lotNumber))
        else:
            st.button('Predict',disabled=True)
        





    elif(nav == "Payment"):
        learnMore = st.selectbox(
     'What AI model would you like to learn more about?',
     ('XGBoost', 'Logistic Regression', 'K-nearest neighbours', 'SVC', 'SGD', 'Random Forest', 'Naive Bayes', 'MLP', 'Decision Tree'))

        if(learnMore == "XGBoost"):
            st.text("lorem ipsum for XGBoost")
        
        elif(learnMore == "Logistic Regression"):
            st.text("lorem ipsum for Logistic Regression")

        elif(learnMore == "K-nearest neighbours"):
            st.text("lorem ipsum for K-nearest neighbours")

        elif(learnMore == "SVC"):
            st.text("lorem ipsum for SVC")

        elif(learnMore == "SGD"):
            st.text("lorem ipsum for SGD")

        elif(learnMore == "Random Forest"):
            st.text("lorem ipsum for Random Forest")

        elif(learnMore == "Naive Bayes"):
            st.text("lorem ipsum for Naive Bayes")

        elif(learnMore == "MLP"):
            st.text("lorem ipsum for MLP")
        
        elif(learnMore == "Decision Tree"):
            st.text("lorem ipsum for Decision Tree")

#calling the main function
main()




