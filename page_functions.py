from itertools import count
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
    
def regex(plateNo):
    pattern = "([SFG][^AIO\d][^AIO\d][0-9]{1,4}[^FINOQVW\W\d])$|([SFG][^AIO\d][0-9]{1,4}[^FINOQVW\W\d])$|(J[^AIO\d][0-9]{1,4})$|(J[^AIO\d][^AIO\d][0-9]{1,4})$"
    strPattern = '[A-Za-z]'

    split = list(plateNo)
    LetterList = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']

    checksum_list = ['A', 'Z', 'Y', 'X', 'U', 'T', 'S', 'R', 'P', 'M', 'L', 'K', 'J', 'H', 'G', 'E', 'D', 'C', 'B']
    csLetter = split[len(split)-1]
    
    countofNo = 0
    countofStr = 0

    if(re.search(pattern, plateNo)):
        for i in range(len(split)-1):
            if(re.search(strPattern, split[i])):   
                countofStr += 1
            else:
                countofNo +=1
        
        if(countofStr == 3):
            prefix1 = LetterList.index(split[1]) + 1
            prefix2 = LetterList.index(split[2]) + 1
            if(countofNo == 1):
                no1 = 0
                no2 = 0
                no3 = 0
                no4 = int(split[3])
            elif(countofNo == 2):
                no1 = 0
                no2 = 0
                no3 = int(split[3])
                no4 = int(split[4])
            elif(countofNo == 3):
                no1 = 0
                no2 = int(split[3])
                no3 = int(split[4])
                no4 = int(split[5])
            else:
                no1 = int(split[3])
                no2 = int(split[4])
                no3 = int(split[5])
                no4 = int(split[6])



        elif(countofStr == 2):
            prefix1 = LetterList.index(split[0]) + 1
            prefix2 = LetterList.index(split[1]) + 1

            if(countofNo == 1):
                no1 = 0
                no2 = 0
                no3 = 0
                no4 = int(split[2])

            elif(countofNo == 2):
                no1 = 0
                no2 = 0
                no3 = int(split[2])
                no4 = int(split[3])

            elif(countofNo == 3):
                no1 = 0
                no2 = int(split[2])
                no3 = int(split[3])
                no4 = int(split[4])
            else:    
                no1 = int(split[2])
                no2 = int(split[3])
                no3 = int(split[4])
                no4 = int(split[5])

        total = ((prefix1 * 9) + (prefix2 * 4) + (no1 * 5) + (no2 * 4) + (no3 * 3) + (no4 * 2))%19
        csChecker = checksum_list[total]

        if(csChecker == csLetter):
            return 'Valid'
        else:
            return 'Invalid'

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


def chargeCalc(plateNo, duration, intCharge):
    if(str(plateNo).startswith('J') or str(plateNo).startswith('S')):
        intCharge += 0.6 * int((duration/30))

    elif(str(plateNo).startswith("F")):
        intCharge += 0.65

        if(int(((duration/60)/12)) > 0):
            intCharge += (0.65 * int(((duration/60)/12)))
        
    elif(str(plateNo).startswith("G")):
        intCharge += 1.2 * int((duration/30))

    return intCharge


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