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

    # Step 1: Retrieve the gPLink attribute for the specified OU
    conn.search(
        search_base=search,
        search_filter='(objectClass=organizationalUnit)',
        attributes=['gPLink']
    )

    # Extract the gPLink attribute (if it exists)
    gplink = conn.entries[0].gPLink.value if conn.entries else None

    # Step 2: Parse the gPLink value to get the GPO DNs
    if gplink:
        # Regex to extract each GPO DN from gPLink format
        gpo_dns = re.findall(r'\[LDAP://([^;]+);', gplink)

        # Step 3: Retrieve details for each GPO found in gPLink
        gpo_data = []
        for gpo_dn in gpo_dns:
            conn.search(
                search_base=gpo_dn,
                search_filter='(objectClass=groupPolicyContainer)',
                attributes=ALL_ATTRIBUTES
            )
            if conn.entries:
                gpo_data.append(conn.entries[0].entry_attributes_as_dict)

        # Convert GPO data to DataFrame for easier handling
        df = pd.DataFrame(gpo_data)
        print(df)
    else:
        print("No GPOs linked to this OU.")

sys.modules[__name__] = gpoSearch