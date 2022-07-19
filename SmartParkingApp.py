import numpy as np
import streamlit as st
import sklearn
import datetime
import pytz
import pickle
import re # for regex
import random

from numpy import intc, loadtxt
from sympy import DiracDelta
from xgboost import XGBClassifier
import xgboost as xgb


from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score
from sklearn import ensemble

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
    pattern = "([SFG][^AIO][^IO\d]\d\d\d\d[^FINOQVW\W\d])$|([SFG][^AIO]\d\d\d\d[^FINOQVW\W\d])$"
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

#timePicker() function is a custom timepicker for 10 minute intervals instead of the usual 15 minute intervals which is in st.time_input function
def timePicker():
    start = "00:00"
    end = "23:50"
    times = []
    start = now = datetime.datetime.strptime(start, "%H:%M")
    end = datetime.datetime.strptime(end, "%H:%M")
    while now != end:
        times.append(str(now.strftime("%H:%M")))
        now += datetime.timedelta(minutes=10)
    times.append(end.strftime("%H:%M"))
    endTime = st.multiselect('Input session end time:',times)

    return endTime

def main():
    #sidebar code
    nav = st.sidebar.radio("Navigation",["Home","More info about models"])

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


        if(plateNo.startswith("S")):
            VehType = 0
        elif(plateNo.startswith("F")):
            VehType = 1
        elif(plateNo.startswith("G")):
            VehType = 2


        #Unused variable to randomly assign user a lot number for prediction purposes
        lotNumber = random.randint(1,500)

        #user input for end session date
        endDate = st.date_input("Select session end date: ")

        #Getting user input session end time
        endTime = st.time_input("Please enter session end time: ")

        #Line 170 to 183 if using the timePicker() function
        # if len(endTime) != 0: 
        #     index1 = endTime[0]
        #     #timeSplit to split the hours and minutes
        #     timeSplit = index1.split(':')
        #     dateTime = datetime.datetime(int(endDate.year), int(endDate.month), int(endDate.day), int(timeSplit[0]), int(timeSplit[1]))
        #     convertedStrUTC = convert_datetime_timezone(str(dateTime),'Singapore','UTC')
        #     endUTC = datetime.datetime.strptime(convertedStrUTC,"%Y-%m-%d %H:%M:%S")
        #     #If using web hosted app, use code for deployed webapp, if using app on local host, use code for local host
        #     duration = round((epochCalc(endUTC) - epochCalc(utctimeNow)) /60,2) #code for local host
        #     duration = round((epochCalc(dateTime) - epochCalc(utctimeNow)) /60,2) #code for deployed webapp


        #Creating a datetime object by combining endDate and endTime variables
        dateTime = datetime.datetime(int(endDate.year), int(endDate.month), int(endDate.day), int(endTime.hour), int(endTime.minute))
        
        #Converting local timezone to UTC time zone - only needed for local host 
        convertedStrUTC = convert_datetime_timezone(str(dateTime),'Singapore','UTC')
        endUTC = datetime.datetime.strptime(convertedStrUTC,"%Y-%m-%d %H:%M:%S")

        #Calculate duration
        duration = round((epochCalc(endUTC) - epochCalc(utctimeNow)) /60,2) #code for local host

        #Calculate session start and end in minutes since Epoch
        sessEnd = round((epochCalc(endUTC)/60),2)
        sesStart = round((epochCalc(utctimeNow)/60),2)

        #To get an estimated charge amount from the user
        estTotalCharge = st.text_input('Please enter estimated total charge: ')
        if(estTotalCharge != ''):
            intCharge = float(estTotalCharge)

        #totalCharge = 4 
        effCharge = intCharge

        #initializing the prediciton variable
        pred = ''

        featureList = [VehType, sesStart, sessEnd, intCharge, duration, effCharge]
        

        if(plateNo != '' and  regex(plateNo) != 'Invalid' and endTime != []):
            if st.button('Predict'):
                pred = prediction(model, featureList)
                st.success(pred)
                st.text("For troubleshooting purpose:" + "\nVehType: " + str(VehType) + "\nSession start: " + str(sesStart) + "\nSession End: " + str(sessEnd) + "\nTotal charge: " + str(intCharge) + "\nDuration: " + str(duration) + "\nEffective charge: " + str(effCharge))

    elif(nav == "More info about models"):
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




