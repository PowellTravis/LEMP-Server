from ldap3 import Server, Connection, ALL, ALL_ATTRIBUTES
import re
import pandas as pd
from dotenv import load_dotenv
import os
import sys
from smb.SMBConnection import SMBConnection

load_dotenv()

def gpoSearch():
    user = os.getenv("ad_dn")
    password = os.getenv("ad_pw")
    search = os.getenv("ad_computer")
    ad_un = os.getenv("ad_un")
    returned_data = ""

    # Set up server and connection
    server = Server('ldap://powellnetworks.net', get_info=ALL)
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
                # print(df.apply(lambda row: str(row["gPCFileSysPath"]), axis=1))
                for ind in df.index:
                    path = rf"{df['gPCFileSysPath'][ind][0]}"
                    path = path.replace('\\', '/').split('/powellnetworks.net/P')[1]
                    print(path)
                    sconn = SMBConnection(ad_un, password, 'AD-Ansible', 'powellnetworks.net', domain='POWELLNETWORKS', use_ntlm_v2=True, is_direct_tcp=True)
                    assert sconn.connect('powellnetworks.net', 445)
                    try:
                        with open("GPO.cmt", "wb") as local_file:
                            sconn.retrieveFile('SysVol', '/powellnetworks.net/P' + path + "/GPO.cmt", local_file)
                        print("File downloaded successfully.")
                        
                        # Optionally, read the file content
                        file_data = open("GPO.cmt", 'r')
                        if 'updateDay' in file_data.read():
                            returned_data = file_data.read()
                            print(file_data.read())
                            break
                        file_data.close()
                        os.remove("GPO.cmt")
                    except Exception as e:
                        print("Error reading file")
                    sconn.close()
                break
    else:
        print("No GPOs linked to this OU.")
    print(returned_data)
    if(returned_data != ""):
        return returned_data
    else:
        return None

sys.modules[__name__] = gpoSearch