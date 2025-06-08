import logging
from typing import Dict, Optional
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.triggers.cron import CronTrigger

from app.core.config import Config
from app.models.jobs import Job

logger = logging.getLogger(__name__)

class JobScheduler:
    """
    Manages scheduled jobs and tasks for the bot.
    Uses APScheduler for job management.
    """
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the job scheduler.
        
        Args:
            config: Optional configuration object
        """
        self.config = config
        self.scheduler = BackgroundScheduler(
            jobstores={
                'default': SQLAlchemyJobStore(url=config.database_url if config else 'sqlite:///jobs.db')
            },
            executors={
                'default': ThreadPoolExecutor(20)
            },
            job_defaults={
                'coalesce': False,
                'max_instances': 1
            }
        )
        self._is_running = False

    def start(self) -> None:
        """Start the scheduler."""
        if not self._is_running:
            self.scheduler.start()
            self._is_running = True
            logger.info("Job scheduler started")

    def stop(self) -> None:
        """Stop the scheduler."""
        if self._is_running:
            self.scheduler.shutdown()
            self._is_running = False
            logger.info("Job scheduler stopped")

    def add_job(self, job: Job) -> None:
        """
        Add a new job to the scheduler.
        
        Args:
            job: Job object containing job details
        """
        try:
            if job.cron_expression:
                trigger = CronTrigger.from_crontab(job.cron_expression)
            else:
                trigger = 'date'
                run_date = job.next_run

            self.scheduler.add_job(
                func=self._execute_job,
                trigger=trigger,
                args=[job],
                id=str(job.id),
                name=job.name,
                replace_existing=True
            )
            logger.info(f"Added job: {job.name} (ID: {job.id})")
        except Exception as e:
            logger.error(f"Failed to add job {job.name}: {str(e)}")
            raise

    def remove_job(self, job_id: int) -> None:
        """
        Remove a job from the scheduler.
        
        Args:
            job_id: ID of the job to remove
        """
        try:
            self.scheduler.remove_job(str(job_id))
            logger.info(f"Removed job with ID: {job_id}")
        except Exception as e:
            logger.error(f"Failed to remove job {job_id}: {str(e)}")
            raise

    def get_job(self, job_id: int) -> Optional[Dict]:
        """
        Get information about a scheduled job.
        
        Args:
            job_id: ID of the job to retrieve
            
        Returns:
            Dictionary containing job information or None if not found
        """
        try:
            job = self.scheduler.get_job(str(job_id))
            if job:
                return {
                    'id': job_id,
                    'name': job.name,
                    'next_run': job.next_run_time,
                    'trigger': str(job.trigger)
                }
            return None
        except Exception as e:
            logger.error(f"Failed to get job {job_id}: {str(e)}")
            return None

    def _execute_job(self, job: Job) -> None:
        """
        Execute a scheduled job.
        
        Args:
            job: Job object to execute
        """
        try:
            logger.info(f"Executing job: {job.name} (ID: {job.id})")
            # Job execution logic will be implemented here
            # This will be connected to the appropriate service based on job type
        except Exception as e:
            logger.error(f"Failed to execute job {job.name}: {str(e)}")
            raise

    def is_running(self) -> bool:
        """Check if the scheduler is currently running."""
        return self._is_running 