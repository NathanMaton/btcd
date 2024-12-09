from app import app, scheduled_email_job
from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler()

# Schedule daily email job at 9:00 AM Pacific Time
scheduler.add_job(scheduled_email_job, 'cron', hour=9, minute=0, timezone='US/Pacific')

if __name__ == '__main__':
    scheduler.start()
