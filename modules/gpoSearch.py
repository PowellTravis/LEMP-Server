import sys

def gpoSearch(search):
    from ldap3 import Server, Connection, ALL, ALL_ATTRIBUTES, Tls, AUTO_BIND_NO_TLS
    import mysql.connector
    import re
    import ssl
    import pandas as pd
    from dotenv import load_dotenv
    import os
    import logging
    logging.basicConfig(level=logging.DEBUG)

    load_dotenv()
    
    user = os.getenv("ad_dn")
    password = os.getenv("ad_pw")
    returned_data = ""

    # Initiate MYSQL connection
    mysqlDB = mysql.connector.connect(
        host = os.getenv("mysql_host"),
        user = os.getenv("mysql_user"),
        passwd = os.getenv("mysql_password"),
        database = os.getenv("mysql_db")
    )

    mysql_cursor = mysqlDB.cursor()

    # Set up AD server connection
    tls = Tls(validate=0,version=ssl.PROTOCOL_TLSv1_2)
    server = Server(os.getenv('ad_server'), get_info=ALL, use_ssl=True, tls=tls)
    conn = Connection(server, user, password, auto_bind=True)

    conn.search(
        search_base=search,
        search_filter=f'(objectClass=organizationalUnit)',
        attributes=['gPLink']
    )

    gpLinks = []
    for x in conn.entries:
        if x.gPLink.value != ' ':
            gpLinks.append(x.gPLink.value)
        else:
            print("Skipped Empty")

    if gpLinks:
        for gp in gpLinks:
            if gp != None:
                gpo_dns = re.findall(r'\[LDAP://([^;]+);', gp)
                gpo_data = []
                for gpo_dn in gpo_dns:
                    conn.search(
                        search_base=gpo_dn,
                        search_filter='(objectClass=groupPolicyContainer)',
                        attributes=ALL_ATTRIBUTES
                    )
                    if conn.entries:
                        gpo_data.append(conn.entries[0].entry_attributes_as_dict)

                df = pd.DataFrame(gpo_data)
                # print(df.to_string())
                for ind in df.index:
                    name = rf"{df['displayName'][ind][0]}"
                    # print(name)
                    smbFilePath = rf"{df['gPCFileSysPath'][ind][0]}"
                    sqlStatement = "INSERT INTO GroupPolicy (name, dn, smbPath, linuxEquivalent) SELECT %s, %s, %s, %s WHERE NOT EXISTS ( SELECT 1 FROM GroupPolicy WHERE dn = %s AND smbPath = %s);"
                    sqlValues = (name, search, smbFilePath, '', search, smbFilePath)
                    mysql_cursor.execute(sqlStatement, sqlValues)
        mysqlDB.commit()
    else:
        print("No GPOs linked to this OU.")
    mysql_cursor.close()
    mysqlDB.close()


sys.modules[__name__] = gpoSearch