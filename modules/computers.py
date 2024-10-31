from ldap3 import Server, Connection, ALL
import pandas as pd
from dotenv import load_dotenv
import os
import sys

load_dotenv()

def computers():
    user = os.getenv("ad_dn")
    password = os.getenv("ad_pw")
    search = os.getenv("ad_computer")

    server = Server('ldap://powellnetworks.net', get_info=ALL)
    conn = Connection(server, user, password, auto_bind=True)
    conn.search(search, '(&(objectClass=computer)(operatingSystem=pc-linux-gnu))', attributes=['dNSHostName', 'name'])

    # Extract attributes for each entry
    data = []
    for entry in conn.entries:
        # Convert each entry's attributes to a dictionary
        data.append(entry.entry_attributes_as_dict)

    # Load data into a DataFrame
    df = pd.DataFrame(data)
    return df

sys.modules[__name__] = computers