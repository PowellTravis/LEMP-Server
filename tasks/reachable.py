import sys

def reachable():
    import mysql.connector
    from dotenv import load_dotenv
    import os
    load_dotenv()
    
    # Initiate MYSQL connection
    mysqlDB = mysql.connector.connect(
        host = os.getenv("mysql_host"),
        user = os.getenv("mysql_user"),
        passwd = os.getenv("mysql_password"),
        database = os.getenv("mysql_db")
    )
    
    mysql_cursor = mysqlDB.cursor()
    
    query = "Select dnsName from Server"
    mysql_cursor.execute(query)
    systems = mysql_cursor.fetchall()
    
    for system in systems:
        param = '-c'
        response = os.system(f"ping {param} 1 {system[0]}")
        if response == 0:
            print(f'Checked {system[0]}, and it is reachable...')
            updateQuery = f"UPDATE Server SET reachable = 1 WHERE dnsName='{system[0]}'"
            mysql_cursor.execute(updateQuery)
        else:
            print(f'Checked {system}, and it is not reachable...')
            updateQuery = f"UPDATE Server SET reachable = 0 WHERE dnsName='{system[0]}'"
            mysql_cursor.execute(updateQuery)
        print(system[0])
    mysqlDB.commit()
    mysql_cursor.close()
    mysqlDB.close()
sys.modules[__name__] = reachable