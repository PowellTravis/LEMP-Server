from tasks import ouSearch, groupPolicyAutoSchedule
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import time
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

mysqlDB = mysql.connector.connect(
    host = os.getenv("mysql_host"),
    user = os.getenv("mysql_user"),
    passwd = os.getenv("mysql_password"),
    database = os.getenv("mysql_db")
)

scheduler = BackgroundScheduler()

mysql_cursor = mysqlDB.cursor()
    
oudQuery = "Select valueField from ServerSettings WHERE settingName='ou_discovery_interval'"
mysql_cursor.execute(oudQuery)
oudResults = mysql_cursor.fetchone()[0]

scheduler.add_job(ouSearch, CronTrigger.from_crontab(oudResults), id='ou_discovery_interval')

gpasdQuery = "Select valueField from ServerSettings WHERE settingName='gp_auto_schedule_deploy'"
mysql_cursor.execute(gpasdQuery)
gpasdResults = mysql_cursor.fetchone()[0]
mysql_cursor.close()
mysqlDB.close()
scheduler.add_job(groupPolicyAutoSchedule, CronTrigger.from_crontab(oudResults), args={scheduler}, id='gp_auto_schedule_deploy')

scheduler.start()

try:
    while True:
        time.sleep(1)
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()