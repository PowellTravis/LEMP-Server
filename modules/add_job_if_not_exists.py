from apscheduler.triggers.cron import CronTrigger
import sys

def add_job_if_not_exists(scheduler, job_func, cron_expression, job_id, args):
    cron_trigger = CronTrigger.from_crontab(cron_expression)
    
    scheduler.add_job(job_func, cron_trigger, id=job_id, args=args)
    print(f"Job with ID '{job_id}' added successfully with arguments {args}.")
        
sys.modules[__name__] = add_job_if_not_exists