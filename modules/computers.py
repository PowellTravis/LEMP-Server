import sys

def computers(search):
    from ldap3 import Server, Connection, ALL, ALL_ATTRIBUTES, Tls, AUTO_BIND_NO_TLS
    import mysql.connector
    import ssl
    import pandas as pd
    from dotenv import load_dotenv
    import os
    import socket

    load_dotenv()

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
    
    # Initialize AD Connection
    tls = Tls(validate=0,version=ssl.PROTOCOL_TLSv1_2)
    server = Server(os.getenv('ad_server'), get_info=ALL, use_ssl=True, tls=tls)
    conn = Connection(server, user, password, auto_bind=True)
    
    # Finds all computers in AD OU. Removes the Windows systems by filtering for linux systems.
    conn.search(search, '(&(objectClass=computer)(operatingSystem=pc-linux-gnu))', attributes=ALL_ATTRIBUTES)

    # Extract attributes for each entry
    data = []
    for entry in conn.entries:
        # Convert each entry's attributes to a dictionary
        data.append(entry.entry_attributes_as_dict)

    # Load data into a DataFrame
    df = pd.DataFrame(data)
    for ind in df.index:
        name = rf"{df['name'][ind][0]}"
        dnsName = rf"{df['dNSHostName'][ind][0]}"
        ipData = socket.gethostbyname(dnsName)
        ip = repr(ipData)
        #     return ip
        # except Exception:
        #     # fail gracefully!
        #     return False
        sqlStatement = "INSERT INTO Server (name, ipAddress, dnsName, dn) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE dnsName = IF(dnsName IS NULL, VALUES(dnsName), dnsName), ipAddress = IF(ipAddress IS NULL, VALUES(ipAddress), ipAddress), dn = IF(dn IS NULL, VALUES(dn), dn);"
        sqlValues = (name, ip, dnsName, search)
        mysql_cursor.execute(sqlStatement, sqlValues)
    mysqlDB.commit()
    # print(df.to_string())
    mysql_cursor.close()
    mysqlDB.close()

sys.modules[__name__] = computers