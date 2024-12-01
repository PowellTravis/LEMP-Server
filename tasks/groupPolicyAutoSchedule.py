import sys

def groupPolicyAutoSchedule(scheduler):
    from modules import add_job_if_not_exists
    import policyApply
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
    
    query = "Select * from GroupPolicy WHERE scheduleEnabled=1"
    mysql_cursor.execute(query)
    results = mysql_cursor.fetchall()
    for row in results:
        jobID = row[0]
        name = row[3]
        jobName = f'{jobID}-{name}'
        dn = row[4]
        linuxCommand = row[6]
        schedule = row[7]
        add_job_if_not_exists(scheduler, policyApply, schedule, jobName, {dn, linuxCommand})
    mysql_cursor.close()
    mysqlDB.close()
    
sys.modules[__name__] = groupPolicyAutoSchedule