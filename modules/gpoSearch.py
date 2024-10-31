from ldap3 import Server, Connection, ALL, ALL_ATTRIBUTES
import re
import pandas as pd
from dotenv import load_dotenv
import os
import sys

load_dotenv()

def gpoSearch():
    user = os.getenv("ad_dn")
    password = os.getenv("ad_pw")
    search = os.getenv("ad_computer")

    # Set up server and connection
    server = Server('ldap://powellnetworks.net', get_info=ALL)
    conn = Connection(server, user, password, auto_bind=True)


    conn.search(
        search_base=search,
        search_filter='(objectClass=organizationalUnit)',
        attributes=['gPLink']
    )


    gplink = conn.entries[0].gPLink.value if conn.entries else None

   
    if gplink:
        gpo_dns = re.findall(r'\[LDAP://([^;]+);', gplink)


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
        # print(df.apply(lambda row: str(row["gPCFileSysPath"]), axis=1))
        for ind in df.index:
            print(df['gPCFileSysPath'][ind])
    else:
        print("No GPOs linked to this OU.")


sys.modules[__name__] = gpoSearch