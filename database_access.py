import os
import sqlite3 as sql

#All Functions for our database

# Establishing name of database
database_name = 'parking.db'

'''
Checks if database is created, then creates table. 
Should be called at the start of the main() function.
'''
def check_db(): # Progress: Complete
    if not os.path.isfile(database_name):
        # Creates a parking.db file if it does not exist, otherwise accesses it if exists
        con = sql.connect(database_name)
        
        # Create a cursor object to access table
        # Note: All SQL commands are done with the cursor object.
        cur = con.cursor()

        # Creating table if table does not exist
        cur.execute("""
        CREATE TABLE IF NOT EXISTS sessions(
        license_number VARCHAR(25),
        session_start DATETIME,
        session_end DATETIME,
        session_cost DECIMAL(3, 2),
        lot_number INT(500),
        paid BOOLEAN
        );
        """)
        con.commit()
        con.close()


''' 
Takes in a tuple of session details containing: 
License Number in string
Session Start in datetime
Session End in datetime
Cost in DECIMAL(10,2)
Lot Number in integer
Paid in boolean

Adds the tuple of session details into the database.
Commits after change is done then close the connection.
'''
def add_session(session): # Progress: Complete
    # Creates a parking.db file if it does not exist, otherwise accesses it if exists
    con = sql.connect(database_name)

    # Create a cursor object to access table
    # Note: All SQL commands are done with the cursor object.
    cur = con.cursor()

    sql_command = "INSERT INTO sessions VALUES(?, ?, ?, ?, ?, ?)"
    cur.execute(sql_command, session)

    con.commit()
    con.close()


# Takes in user's plate number and finds any records in the database containing that plate number
def get_previous_sessions(plate_number): # Progress: Complete
     # Creates a parking.db file if it does not exist, otherwise accesses it if exists
    con = sql.connect(database_name) 
    
    # Create a cursor object to access table
    # Note: All SQL commands are done with the cursor object.
    cur = con.cursor()
    
    # Getting previous sessions
    cur.execute("SELECT license_number, session_start, session_end, session_cost, lot_number FROM sessions WHERE license_number == ? AND paid == True", (plate_number,))
    
    prev_sessions = cur.fetchall()

    con.commit()
    con.close()
    
    return prev_sessions

    # Takes in user's plate number and finds any records in the database containing that plate number
def get_current_session(plate_number): # Progress: Complete
     # Creates a parking.db file if it does not exist, otherwise accesses it if exists
    con = sql.connect(database_name) 
    
    # Create a cursor object to access table
    # Note: All SQL commands are done with the cursor object.
    cur = con.cursor()
    
    # Getting current sessions if any
    cur.execute("SELECT license_number, session_start, session_end, session_cost, lot_number FROM sessions WHERE license_number == ? AND paid == False", (plate_number,))
    
    prev_sessions = cur.fetchall()

    con.commit()
    con.close()
    
    return prev_sessions


def deleteSessions(plate_number):
     # Creates a parking.db file if it does not exist, otherwise accesses it if exists
    con = sql.connect(database_name) 
    
    # Create a cursor object to access table
    # Note: All SQL commands are done with the cursor object.
    cur = con.cursor()
    
    # Getting previous sessions
    cur.execute("DELETE FROM sessions WHERE license_number == ? AND paid == True", (plate_number,))
    
    prev_sessions = cur.fetchall()

    con.commit()
    con.close()
    
    return 'History has been cleared'

def noCurrentSess(plate_number):
     # Creates a parking.db file if it does not exist, otherwise accesses it if exists
    con = sql.connect(database_name) 
    
    # Create a cursor object to access table
    # Note: All SQL commands are done with the cursor object.
    cur = con.cursor()
    
    #Checks if this license number has a current active session
    cur.execute("SELECT * FROM sessions WHERE license_number == ? AND paid == False", (plate_number,))
    
    currentSession = cur.fetchall()

    if(len(currentSession) == 0):
        NoCurrentSess = True
    else:
        NoCurrentSess = False

    con.commit()
    con.close()
    
    return NoCurrentSess

def endSession(plate_number):
     # Creates a parking.db file if it does not exist, otherwise accesses it if exists
    con = sql.connect(database_name) 
    
    # Create a cursor object to access table
    # Note: All SQL commands are done with the cursor object.
    cur = con.cursor()
    
    #Update session paid column to true
    cur.execute("UPDATE sessions SET paid = True WHERE license_number == ? AND paid == False", (plate_number,))


    con.commit()
    con.close()
    
    return 'Session ended'


def extendTimeCost(endTime, Cost, license_number):
     # Creates a parking.db file if it does not exist, otherwise accesses it if exists
    con = sql.connect(database_name) 
    
    # Create a cursor object to access table
    # Note: All SQL commands are done with the cursor object.
    cur = con.cursor()
    
    #Update session end time and session cost fields
    cur.execute("UPDATE sessions SET session_end = ?, session_cost = ? WHERE license_number == ? AND paid == False", (endTime, Cost, license_number,))

    con.commit()
    con.close()
    
    return 'Session extended successfully'


def getTotalCost(plate_number):
     # Creates a parking.db file if it does not exist, otherwise accesses it if exists
    con = sql.connect(database_name) 
    
    # Create a cursor object to access table
    # Note: All SQL commands are done with the cursor object.
    cur = con.cursor()
    
    #Selects the session cost for the current active session
    cur.execute("SELECT session_cost FROM sessions WHERE license_number == ? AND paid == False", (plate_number,))
    
    cost = cur.fetchall()
    
    for item in cost:                                                                           
        cost = item[0]  

    con.commit()
    con.close()
    
    return cost

