import os
import sqlite3 as sql

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
        lot_number INT(500)
        );
        """)
        con.commit()
        con.close()
    else:
        print('Database already exists.')

''' 
Takes in a tuple of session details containing: 
License Number in string
Session Start in datetime
Session End in datetime
Lot Number in integer

Adds the tuple of session details into the database.
Commits after change is done then close the connection.

'''
def add_session(session): # Progress: Complete
    # Creates a parking.db file if it does not exist, otherwise accesses it if exists
    con = sql.connect(database_name)

    # Create a cursor object to access table
    # Note: All SQL commands are done with the cursor object.
    cur = con.cursor()

    sql_command = "INSERT INTO sessions VALUES(?, ?, ?, ?)"
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
    cur.execute("SELECT * FROM sessions WHERE license_number == ?", (plate_number))
    
    prev_sessions = cur.fetchall()

    con.commit()
    con.close()
    
    return prev_sessions