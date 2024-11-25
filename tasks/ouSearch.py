from modules import gpoSearch
from modules import computers
from ldap3 import Server, Connection, ALL, ALL_ATTRIBUTES, Tls, AUTO_BIND_NO_TLS
import mysql.connector
import ssl
import pandas as pd
from dotenv import load_dotenv
import os
import sys

load_dotenv()

def ouSearch():
    user = os.getenv("ad_dn")
    password = os.getenv("ad_pw")

    # Initiate MYSQL connection
    mysqlDB = mysql.connector.connect(
        host = os.getenv("mysql_host"),
        user = os.getenv("mysql_user"),
        passwd = os.getenv("mysql_password"),
        database = os.getenv("mysql_db")
    )
    
    mysql_cursor = mysqlDB.cursor()
    
    query = "Select valueField from ServerSettings WHERE settingName='searchableOUs'"
    mysql_cursor.execute(query)
    results = mysql_cursor.fetchall()
    for row in results:
        for ou in row[0].split(';'):
            print(f'Currently Searching GPOs in {ou}')
            gpoSearch(ou)
            print(f'Currently Computers in {ou}')
            computers(ou)
    mysql_cursor.close()
    mysqlDB.close()
    
sys.modules[__name__] = ouSearch