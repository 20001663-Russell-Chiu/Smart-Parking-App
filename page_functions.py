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

class CardNameError(Exception):
    """Exception raised when Card Name contains non-alphabetical characters."""
    def __init__(self, name):
        self.name = name
        message = f'Your Card Name contains non-alphabetical characters: {self.name}'
        super().__init__(message)
    
def validate_payment_info(cardName, cardNo, expiry_date, CVV):
    is_validated = True
    result_list = []
    
    regex_cardname = '([A-Za-z\\s])+'
    regex_cardNo = '[0-9]+'
    regex_expiry_date = ''
    regex_CVV = ''

    if cardName == '':
        is_validated = False
        result_list.append('Please enter a card name.')
    elif not re.search(regex_cardname, cardName):
        is_validated = False
        result_list.append('Your card name must only contain alphabetical characters.')
    
    if cardNo == '':
        is_validated = False
        result_list.append('Please enter a card cardNo.')
    elif not re.search(regex_cardNo, cardNo):
        is_validated = False
        result_list.append('Your card number is invalid.')

    if expiry_date == '':
        is_validated = False
        result_list.append('Please enter a card expiry_date.')
    elif not re.search(regex_expiry_date, expiry_date):
        is_validated = False
        result_list.append('placeholder')

    if CVV == '':
        is_validated = False
        result_list.append('Please enter a card CVV.')
    elif not re.search(regex_CVV, CVV):
        is_validated = False
        result_list.append('placeholder')

    return is_validated, result_list