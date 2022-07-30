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

# User-defined functions for additional functionality
import database_access
from page_functions import *

def payment_page():
    CheckPlate = st.session_state.endsession_plate

    with st.form(key='payment_form', clear_on_submit=False):
        cardName = st.text_input('Cardholder name', placeholder='Enter your name')
        cardNo = st.text_input("Card number", placeholder='Enter a VISA/Mastercard card number')

        cardDate, cardCVV = st.columns(2)
        cardDate = cardDate.text_input("Expiry date", placeholder="MM/YY")
        cardCVV = cardCVV.text_input("Security code/CVV", placeholder='Enter your CVV')

        inputs = (cardName, cardNo, cardDate, cardCVV)

        submit_button = st.form_submit_button(label='Submit')
        
        if submit_button:
            # Put code for validating inputs
            inputs_validated, result_list = validate_payment_info(*inputs)
            
            if inputs_validated:
                # When inputs are validated, proceed to:
                # - Display Success Message
                # - Display Total Cost
                # - End current session in database (Changing session field "paid" to True)
                total_cost = st.session_state.total_cost
                database_access.endSession(CheckPlate)

                # Displaying Messages
                st.write(f'Total Cost: {total_cost}')
                st.success('Your payment is successful! You may return to menu.')
            else:
                # Displays Error Messages for any of the input fields if the user input is invalid
                for result_msg in result_list:
                    st.error(result_msg)
        
    go_to_main = st.button('Return to Menu')
    
    if go_to_main:
        st.session_state.runpage = main
        st.experimental_rerun()
        
def main_page_Home():
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


    duration = st.number_input("Enter parking duration in minutes: ",value=30,step=30)

    if(duration < 0 or duration > 100000):
        error = '<p style="font-family:sans-serif; color:Red; font-size: 12px;">Invalid duration</p>'
        st.markdown(error, unsafe_allow_html=True)
    else:
        st.text(str(int(duration/60)) + " hours " + str((duration%60)) + " minutes" )
        #Calculate session start and end in minutes since Epoch
        sesStart = round((epochCalc(utctimeNow)),2)
        sessEnd = (duration*60) + sesStart
        
        sesStartDate = datetime.datetime.fromtimestamp((sesStart))
        SessEndDate = datetime.datetime.fromtimestamp((sessEnd))

    

    intCharge = 0
    intCharge = chargeCalc(plateNo, duration, intCharge)       

    effCharge = intCharge       

    #initializing the prediciton variable
    pred = ''

    featureList = [VehType, sesStart, sessEnd, intCharge, duration, effCharge]
    

    if(plateNo != '' and  regex(plateNo) != 'Invalid' and duration > 0 and duration < 100000):
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

def main_page_Sessions():
    if "input" not in st.session_state:
        st.session_state.input = False

    if "extend" not in st.session_state:
        st.session_state.extend = False

    CheckPlate = st.text_input('Please enter license plate to search parking history for:').upper()

    currentSession =  st.empty()
    prevSession = st.empty()


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

                EndSessionButton = EndSessionButton.button('End session')

                extendSession = extendSession.button('Extend session')

                if(EndSessionButton):
                    st.session_state.endsession_plate = CheckPlate
                    st.session_state.total_cost = currentSess.Cost[0]
                    st.session_state.runpage = payment_page
                    st.experimental_rerun()

                if(extendSession):
                    st.session_state.input = True

                if(st.session_state.input):                   
                    currentDT = currentSess['Session End'][0]
                    strToDate = datetime.datetime.strptime(currentDT, "%Y/%m/%d, %H:%M")

                    duration = st.number_input("Enter parking duration in minutes: ",value=30,step=30)   

                    if(duration < 0 or duration > 100000):
                        error = '<p style="font-family:sans-serif; color:Red; font-size: 12px;">Invalid duration</p>'
                        st.markdown(error, unsafe_allow_html=True)
                    else:
                        updatedDT = (strToDate + datetime.timedelta(minutes=duration)).strftime("%Y/%m/%d, %H:%M")
                        st.text(str(int(duration/60)) + " hours " + str((duration%60)) + " minutes" )   
                    
                    intCharge = database_access.getTotalCost(CheckPlate)

                    try:
                        intCharge = round(chargeCalc(CheckPlate, duration, float(intCharge)),2)
                    except:
                        print('')
    
                    if(duration >= 0 and duration < 100000):
                        confirm = st.button('Confirm')
                    else:
                        confirm = st.button('Confirm',disabled=True)

                    if(confirm):
                        st.success(database_access.extendTimeCost(updatedDT,intCharge,CheckPlate))
                        st.session_state.input = False
                        st.session_state.extend = True
                        st.experimental_rerun()

                if(st.session_state.extend):
                    st.success("Session has been extended")
                st.session_state.extend = False

        if(len(prevSessDF.index) > 0):
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

def main():        
    database_access.check_db()

    #sidebar code
    with st.sidebar:
        nav = option_menu(
            menu_title = "Navigation",
            options = ["Home", "Sessions"]
        )

    if(nav == "Home"):
        main_page_Home()

    elif(nav == "Sessions"):
        main_page_Sessions()
        
#calling the main function
if 'runpage' not in st.session_state:
    st.session_state['runpage'] = main
    st.session_state.runpage()
else:
    st.session_state.runpage()





