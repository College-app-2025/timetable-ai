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

email_service = EmailNotificationService()



# import asyncio
# from src.services.notification_service import email_service

# async def main():
#     recipients = ["student1@example.com", "student2@example.com"]
#     subject = "Class Cancelled"
#     message = "Tomorrow's 9 AM class is cancelled due to unforeseen circumstances."
#     institute_name = "NIT Agartala"

#     result = await email_service.send_urgent_notification(
#         recipients=recipients,
#         subject=subject,
#         message=message,
#         institute_name=institute_name,
#         notification_type="urgent"
#     )

#     print(result)

# asyncio.run(main())
