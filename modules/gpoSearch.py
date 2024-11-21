from ldap3 import Server, Connection, ALL, ALL_ATTRIBUTES, Tls, AUTO_BIND_NO_TLS
import re
import ssl
import pandas as pd
from dotenv import load_dotenv
import os
import sys
import logging
logging.basicConfig(level=logging.DEBUG)

load_dotenv()

def gpoSearch():
    user = os.getenv("ad_dn")
    password = os.getenv("ad_pw")
    search = os.getenv("ad_computer")
    ad_un = os.getenv("ad_un")
    returned_data = ""

    # Set up server and connection
    tls = Tls(validate=0,version=ssl.PROTOCOL_TLSv1_2)
    server = Server(os.getenv('ad_server'), get_info=ALL, use_ssl=True, tls=tls)
    conn = Connection(server, user, password, auto_bind=True)

    conn.search(
        search_base=search,
        search_filter='(objectClass=organizationalUnit)',
        attributes=['gPLink']
    )

    # gplink = conn.entries[0].gPLink.value if conn.entries else None
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
                    print(rf"{df['displayName'][ind][0]}")
                    print(rf"{df['distinguishedName'][ind][0]}")
                    # path = rf"{df['name'][ind][0]}"
                #     path = path.replace('\\', '/').split('/powellnetworks.net/P')[1]
                #     print(path)
                # break
    else:
        print("No GPOs linked to this OU.")
    print(returned_data)
    return returned_data

sys.modules[__name__] = gpoSearch