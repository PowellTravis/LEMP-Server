import sys

def policyApply(dn, linuxCommand):
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
    
    query = f"Select dnsName from Server WHERE dn={dn}"
    mysql_cursor.execute(query)
    dnsResults = mysql_cursor.fetchall()
    
sys.modules[__name__] = policyApply