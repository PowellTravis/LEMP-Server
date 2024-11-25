from tasks import ouSearch
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import time

scheduler = BackgroundScheduler()