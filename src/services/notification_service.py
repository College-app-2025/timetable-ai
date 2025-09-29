import smtplib
import html
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import asyncio
import os
from src.utils.logger_config import get_logger

logger = get_logger("notification_service")

class EmailNotificationService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email = os.getenv("SMTP_EMAIL")
        self.password = os.getenv("SMTP_PASSWORD")
        
        # ✅ ADDED: Rate limiting settings
        self.batch_size = int(os.getenv("EMAIL_BATCH_SIZE", "50"))
        self.batch_delay = int(os.getenv("EMAIL_BATCH_DELAY", "60"))
        
        self._validate_configuration()
        
    def _validate_configuration(self):
        if not self.email or not self.password:
            logger.error("SMTP credentials not configured")
            raise ValueError("SMTP_EMAIL and SMTP_PASSWORD environment variables are required")
        logger.info("Email service initialized successfully")
    
    async def test_connection(self) -> bool:
        """Test SMTP connection asynchronously"""
        try:
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                return await loop.run_in_executor(executor, self._test_connection_sync)
        except Exception as e:
            logger.error(f"SMTP connection test failed: {str(e)}")
            return False
    
    def _test_connection_sync(self) -> bool:
        """Synchronous connection test"""
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email, self.password)
                logger.info("SMTP connection test successful")
                return True
        except Exception as e:
            logger.error(f"SMTP connection test failed: {str(e)}")
            return False
    
    async def send_urgent_notification(
        self, 
        recipients: List[str],
        subject: str,
        message: str,
        institute_name: str,
        notification_type: str = "urgent"
    ) -> dict:
        """Send urgent notification email asynchronously"""
        
        if not recipients:
            return {"success": 0, "failed": 0, "errors": ["No recipients"]}
            
        if not subject or not message:
            return {"success": 0, "failed": 0, "errors": ["Subject/message required"]}
        
        try:
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                result = await loop.run_in_executor(
                    executor,
                    self._send_notification_sync,
                    recipients, subject, message, institute_name, notification_type
                )
            return result
        except Exception as e:
            logger.error(f"Email service failed: {str(e)}")
            return {"success": 0, "failed": len(recipients), "errors": [str(e)]}
    
    def _send_notification_sync(
        self,
        recipients: List[str],
        subject: str,
        message: str,
        institute_name: str,
        notification_type: str
    ) -> dict:
        """Synchronous email sending with rate limiting"""
        try:
            # Create message content once
            from_header = f"{institute_name} Scheduling System <{self.email}>"
            subject_header = f"🚨 URGENT: {subject}" if notification_type == "urgent" else f"📢 {subject}"
            
            text_content = self._create_text_content(subject, message, institute_name)
            html_content = self._create_html_content(subject, message, institute_name, notification_type)
            
            base_msg = self._create_base_message(from_header, subject_header, text_content, html_content)
            
            success_count = 0
            failed_count = 0
            errors = []
            
            # Process in batches with rate limiting
            for i in range(0, len(recipients), self.batch_size):
                batch = recipients[i:i + self.batch_size]
                batch_results = self._send_batch(base_msg, batch)
                
                success_count += batch_results["success"]
                failed_count += batch_results["failed"]
                errors.extend(batch_results["errors"])
                
                # Rate limiting between batches (except last batch)
                if i + self.batch_size < len(recipients):
                    time.sleep(self.batch_delay)
            
            logger.info(f"Email batch complete: {success_count} sent, {failed_count} failed")
            return {"success": success_count, "failed": failed_count, "errors": errors}
            
        except Exception as e:
            logger.error(f"Email sending failed: {str(e)}")
            return {"success": 0, "failed": len(recipients), "errors": [str(e)]}
    
    def _send_batch(self, base_msg: MIMEMultipart, recipients: List[str]) -> dict:
        """Send a batch of emails using single SMTP connection"""
        success_count = 0
        failed_count = 0
        errors = []
        
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email, self.password)
                
                for recipient in recipients:
                    try:
                        recipient_msg = base_msg.copy()
                        recipient_msg['To'] = recipient
                        server.send_message(recipient_msg)
                        success_count += 1
                        logger.debug(f"Email sent to {recipient}")
                    except Exception as e:
                        failed_count += 1
                        error_msg = f"Failed to send to {recipient}: {str(e)}"
                        errors.append(error_msg)
                        logger.error(error_msg)
                        
        except Exception as e:
            # SMTP connection failed for entire batch
            failed_count += len(recipients)
            errors.append(f"Batch failed: {str(e)}")
            logger.error(f"Batch sending failed: {str(e)}")
        
        return {"success": success_count, "failed": failed_count, "errors": errors}
    
    def _create_base_message(self, from_header: str, subject: str, text_content: str, html_content: str) -> MIMEMultipart:
        """Create base message without recipient"""
        msg = MIMEMultipart('alternative')
        msg['From'] = from_header
        msg['Subject'] = subject
        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))
        return msg
    
    def _create_text_content(self, subject: str, message: str, institute_name: str) -> str:
        return f"""URGENT NOTIFICATION - {institute_name}

Subject: {subject}

Message: {message}

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This is an automated message from the {institute_name} Scheduling System."""
    
    def _create_html_content(self, subject: str, message: str, institute_name: str, notification_type: str) -> str:
        color = "#dc3545" if notification_type == "urgent" else "#007bff"
        urgency_icon = "🚨" if notification_type == "urgent" else "📢"
        
        # ✅ FIXED: Escape user input to prevent XSS
        safe_message = html.escape(message)
        safe_subject = html.escape(subject)
        safe_institute = html.escape(institute_name)
        
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>/* your CSS here */</style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>📅 {safe_institute}</h2>
        </div>
        <div class="content">
            <h3 class="urgent">{urgency_icon} {safe_subject}</h3>
            <div class="message">{safe_message}</div>
        </div>
    </div>
</body>
</html>"""

class SMSNotificationService:
    """SMS notification service for urgent notifications."""
    
    def __init__(self):
        # Using Twilio or similar service
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_FROM_NUMBER")
        
    async def send_sms(self, to_number: str, message: str) -> dict:
        """Send SMS notification."""
        try:
            # Mock SMS sending for now
            logger.info(f"SMS sent to {to_number}: {message[:50]}...")
            return {"success": True, "message_id": f"sms_{int(time.time())}"}
        except Exception as e:
            logger.error(f"SMS sending failed: {str(e)}")
            return {"success": False, "error": str(e)}

class DynamicReallocationNotificationService:
    """Enhanced notification service for dynamic reallocation system."""
    
    def __init__(self):
        self.email_service = EmailNotificationService()
        self.sms_service = SMSNotificationService()
        self.logger = logger
    
    async def send_substitute_request(self, professor_email: str, assignment: dict, unavailability: dict) -> dict:
        """Send substitute request to professor."""
        try:
            subject = "Substitute Teaching Request"
            message = f"""
Dear Professor,

You have been requested to substitute for a class:

Course: {assignment.get('course_id', 'N/A')}
Section: {assignment.get('section_id', 'N/A')}
Time Slot: {assignment.get('time_slot_id', 'N/A')}
Date: {unavailability.get('unavailability_date', 'N/A')}
Reason: {unavailability.get('reason', 'N/A')}

Please respond within 2 hours to accept or decline this request.

Best regards,
Timetable Management System
            """
            
            result = await self.email_service.send_urgent_notification(
                recipients=[professor_email],
                subject=subject,
                message=message,
                institute_name="Timetable System",
                notification_type="urgent"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error sending substitute request: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def send_student_voting_notification(self, student_emails: list, reallocation_id: str, substitute_professor: str) -> dict:
        """Send voting notification to students."""
        try:
            subject = "Vote for Substitute Professor"
            message = f"""
Dear Students,

Your class needs a substitute professor. Please vote on the following candidate:

Substitute Professor: {substitute_professor}
Reallocation ID: {reallocation_id}

Please vote YES or NO by clicking the link in this email or responding to this message.

Voting closes in 24 hours.

Best regards,
Timetable Management System
            """
            
            result = await self.email_service.send_urgent_notification(
                recipients=student_emails,
                subject=subject,
                message=message,
                institute_name="Timetable System",
                notification_type="urgent"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error sending voting notification: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def send_rescheduling_options(self, professor_id: str, available_slots: list) -> dict:
        """Send rescheduling options to professor."""
        try:
            # Get professor email from database
            from src.utils.prisma import db
            await db.connect()
            professor = await db.teacher.find_unique(where={"teacher_id": professor_id})
            await db.disconnect()
            
            if not professor:
                return {"success": False, "error": "Professor not found"}
            
            subject = "Class Rescheduling Options"
            message = f"""
Dear Professor,

Your class needs to be rescheduled. Here are the available options:

{chr(10).join([f"• {slot.get('date', 'N/A')} - {slot.get('time_slot', 'N/A')}" for slot in available_slots])}

Please select your preferred option by responding to this email.

Best regards,
Timetable Management System
            """
            
            result = await self.email_service.send_urgent_notification(
                recipients=[professor["email"]],
                subject=subject,
                message=message,
                institute_name="Timetable System",
                notification_type="urgent"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error sending rescheduling options: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def send_weekend_class_notification(self, student_emails: list, weekend_date: str) -> dict:
        """Send weekend class notification to students."""
        try:
            subject = "Weekend Class Option"
            message = f"""
Dear Students,

Your missed class can be rescheduled to a weekend session:

Proposed Date: {weekend_date}
Time: 10:00 AM - 12:00 PM

Please vote YES or NO for this weekend class option.

Voting closes in 48 hours.

Best regards,
Timetable Management System
            """
            
            result = await self.email_service.send_urgent_notification(
                recipients=student_emails,
                subject=subject,
                message=message,
                institute_name="Timetable System",
                notification_type="urgent"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error sending weekend class notification: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def send_reallocation_complete_notification(self, recipients: list, reallocation_result: dict) -> dict:
        """Send reallocation completion notification."""
        try:
            subject = "Class Reallocation Complete"
            message = f"""
Dear All,

The class reallocation has been completed successfully.

Action Taken: {reallocation_result.get('action_taken', 'N/A')}
Step Used: {reallocation_result.get('step', 'N/A')}
Status: {reallocation_result.get('status', 'N/A')}

Thank you for your cooperation.

Best regards,
Timetable Management System
            """
            
            result = await self.email_service.send_urgent_notification(
                recipients=recipients,
                subject=subject,
                message=message,
                institute_name="Timetable System",
                notification_type="urgent"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error sending completion notification: {str(e)}")
            return {"success": False, "error": str(e)}

# Service instances
email_service = EmailNotificationService()
sms_service = SMSNotificationService()
notification_service = DynamicReallocationNotificationService()
