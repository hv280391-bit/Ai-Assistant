"""
Reminder scheduling tool
"""

import time
from datetime import datetime, timedelta
from typing import Dict, Any
import re
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from rich.console import Console

from .base import BaseTool

console = Console()

class ScheduleReminderTool(BaseTool):
    """Tool for scheduling reminders"""
    
    def __init__(self, config, auth_manager, audit_logger):
        super().__init__(config, auth_manager, audit_logger)
        
        # Initialize scheduler
        jobstore = SQLAlchemyJobStore(url=f'sqlite:///{config.data["reminder_db_path"]}')
        self.scheduler = BackgroundScheduler(jobstores={'default': jobstore})
        self.scheduler.start()
    
    def get_required_permission(self) -> str:
        return "can_schedule_reminders"
    
    def execute(self, text: str, when: str = None, when_epoch: float = None) -> Dict[str, Any]:
        """Schedule a reminder"""
        try:
            # Parse time
            if when_epoch:
                reminder_time = datetime.fromtimestamp(when_epoch)
            elif when:
                reminder_time = self._parse_time_string(when)
                if not reminder_time:
                    return {"error": f"Could not parse time: {when}"}
            else:
                return {"error": "No time specified for reminder"}
            
            # Check if time is in the future
            if reminder_time <= datetime.now():
                return {"error": "Reminder time must be in the future"}
            
            # Schedule the reminder
            job = self.scheduler.add_job(
                self._show_reminder,
                'date',
                run_date=reminder_time,
                args=[text, self.auth_manager.current_user],
                id=f"reminder_{int(time.time())}_{self.auth_manager.current_user}"
            )
            
            self.log_execution(
                {"text": text, "when": when or str(when_epoch)},
                {"success": f"Scheduled reminder for {reminder_time}"}
            )
            
            return {
                "success": f"Reminder scheduled for {reminder_time.strftime('%Y-%m-%d %H:%M:%S')}",
                "data": {
                    "reminder_text": text,
                    "scheduled_time": reminder_time.isoformat(),
                    "job_id": job.id
                }
            }
            
        except Exception as e:
            error_result = {"error": str(e)}
            self.log_execution({"text": text, "when": when}, error_result)
            return error_result
    
    def _parse_time_string(self, time_str: str) -> datetime:
        """Parse natural language time string"""
        now = datetime.now()
        time_str = time_str.lower().strip()
        
        # Handle relative times
        if 'in' in time_str:
            # "in 5 minutes", "in 2 hours", etc.
            match = re.search(r'in\s+(\d+)\s+(minute|hour|day|week)s?', time_str)
            if match:
                amount = int(match.group(1))
                unit = match.group(2)
                
                if unit == 'minute':
                    return now + timedelta(minutes=amount)
                elif unit == 'hour':
                    return now + timedelta(hours=amount)
                elif unit == 'day':
                    return now + timedelta(days=amount)
                elif unit == 'week':
                    return now + timedelta(weeks=amount)
        
        # Handle specific times
        # "at 3pm", "at 15:30", etc.
        time_match = re.search(r'(?:at\s+)?(\d{1,2}):?(\d{0,2})\s*(am|pm)?', time_str)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2)) if time_match.group(2) else 0
            am_pm = time_match.group(3)
            
            if am_pm:
                if am_pm == 'pm' and hour != 12:
                    hour += 12
                elif am_pm == 'am' and hour == 12:
                    hour = 0
            
            target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # If time has passed today, schedule for tomorrow
            if target_time <= now:
                target_time += timedelta(days=1)
            
            return target_time
        
        return None
    
    def _show_reminder(self, text: str, user: str):
        """Display reminder notification"""
        console.print(f"\n[bold yellow]🔔 REMINDER for {user}:[/bold yellow]")
        console.print(f"[yellow]{text}[/yellow]\n")
        
        # Log reminder execution
        self.audit_logger.log_event("reminder_triggered", {
            "user": user,
            "text": text,
            "timestamp": time.time()
        })