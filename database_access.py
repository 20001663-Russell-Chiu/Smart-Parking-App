# Establishing name of database
database_name = 'parking.db'

# Checks if database is created, then creates table. Should be called after
def check_db(): # Progress: Complete
    # Creates a parking.db file if it does not exist, otherwise accesses it if exists
    connection = sql.connect(database_name) 
    
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

# Takes in user's plate number and finds any records in the database containing that plate number
def get_previous_sessions(plate_number): # Progress: Complete
     # Creates a parking.db file if it does not exist, otherwise accesses it if exists
    connection = sql.connect(database_name) 
    
    # Create a cursor object to access table
    # Note: All SQL commands are done with the cursor object.
    cur = con.cursor()
    
    # Getting previous sessions
    cur.execute("SELECT * FROM sessions WHERE license_number == ?", (plate_number))
    
    prev_sessions = cur.fetchall()

    con.commit()
    con.close()
    
    return prev_sessions