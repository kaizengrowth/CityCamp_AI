import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, List, Optional
from datetime import datetime

from app.core.config import Settings
from app.services.base import BaseService
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class EmailService(BaseService):
    """Service for sending email notifications via SMTP"""

    def _setup(self):
        """Initialize email service and validate SMTP configuration"""
        # Validate required SMTP configuration
        required_config = ['smtp_host', 'smtp_port', 'smtp_username', 'smtp_password']
        if not self._validate_required_config(*required_config):
            self.logger.warning("Email service cannot be initialized - missing SMTP configuration. Emails will not be sent.")
            self.smtp_configured = False
            return
            
        self.smtp_configured = True
        
        # Log configuration details (without sensitive info)
        self.logger.info(f"SMTP Configuration: Host={self.settings.smtp_host}, Port={self.settings.smtp_port}, TLS={self.settings.smtp_tls}, SSL={self.settings.smtp_ssl}")
        self.logger.info(f"From Email: {self.settings.from_email}")
            
        self.smtp_host = self.settings.smtp_host
        self.smtp_port = self.settings.smtp_port
        self.smtp_username = self.settings.smtp_username
        self.smtp_password = self.settings.smtp_password
        self.smtp_tls = self.settings.smtp_tls
        self.smtp_ssl = self.settings.smtp_ssl
        self.from_email = self.settings.from_email or self.settings.smtp_username
        
        self.logger.info(f"Email service initialized with SMTP host: {self.smtp_host}:{self.smtp_port}")

    def _create_smtp_connection(self) -> smtplib.SMTP:
        """Create and configure SMTP connection"""
        if self.smtp_ssl:
            smtp = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
        else:
            smtp = smtplib.SMTP(self.smtp_host, self.smtp_port)
            
        if self.smtp_tls:
            smtp.starttls()
            
        if self.smtp_username and self.smtp_password:
            smtp.login(self.smtp_username, self.smtp_password)
            
        return smtp

    def send_email(
        self, 
        to_email: str, 
        subject: str, 
        html_content: str, 
        text_content: Optional[str] = None
    ) -> bool:
        """Send an email with both HTML and text content"""
        if not hasattr(self, 'smtp_configured') or not self.smtp_configured:
            self.logger.warning(f"Email service not configured - skipping email to {to_email}")
            return False
            
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email

            # Add text content
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)

            # Add HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)

            # Send email
            with self._create_smtp_connection() as smtp:
                smtp.send_message(msg)
                
            self._log_operation("Email sent successfully", f"to {to_email}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    def send_verification_email(self, to_email: str, verification_token: str, name: str) -> bool:
        """Send email verification email"""
        subject = "Verify Your Email - CityCamp AI"
        
        # Create verification URL (frontend will handle this)
        verification_url = f"/verify-email?token={verification_token}"
        
        html_content = f"""
        <html>
        <body>
            <h2>Welcome to CityCamp AI, {name}!</h2>
            <p>Please verify your email address by clicking the link below:</p>
            <p><a href="{verification_url}">Verify Email Address</a></p>
            <p>If you didn't sign up for CityCamp AI, you can ignore this email.</p>
            <p>Best regards,<br>The CityCamp AI Team</p>
        </body>
        </html>
        """
        
        text_content = f"""
        Welcome to CityCamp AI, {name}!
        
        Please verify your email address by visiting this link:
        {verification_url}
        
        If you didn't sign up for CityCamp AI, you can ignore this email.
        
        Best regards,
        The CityCamp AI Team
        """
        
        return self.send_email(to_email, subject, html_content, text_content)

    def send_welcome_email(self, to_email: str, name: str) -> bool:
        """Send welcome email after verification"""
        subject = "Welcome to CityCamp AI!"
        
        html_content = f"""
        <html>
        <body>
            <h2>Welcome to CityCamp AI, {name}!</h2>
            <p>Your email has been verified successfully. You're now subscribed to receive notifications about city meetings that match your interests.</p>
            <p>You'll receive notifications about:</p>
            <ul>
                <li>Upcoming city council meetings</li>
                <li>Meetings related to your selected topics</li>
                <li>Important city updates and announcements</li>
            </ul>
            <p>Thank you for staying informed about your city!</p>
            <p>Best regards,<br>The CityCamp AI Team</p>
        </body>
        </html>
        """
        
        text_content = f"""
        Welcome to CityCamp AI, {name}!
        
        Your email has been verified successfully. You're now subscribed to receive notifications about city meetings that match your interests.
        
        You'll receive notifications about:
        - Upcoming city council meetings
        - Meetings related to your selected topics
        - Important city updates and announcements
        
        Thank you for staying informed about your city!
        
        Best regards,
        The CityCamp AI Team
        """
        
        return self.send_email(to_email, subject, html_content, text_content)

    def send_meeting_notification(
        self, 
        to_email: str, 
        name: str, 
        meeting_data: Dict,
        topics: List[str]
    ) -> bool:
        """Send meeting notification email"""
        subject = f"Upcoming Meeting: {meeting_data.get('title', 'City Council Meeting')}"
        
        meeting_time = meeting_data.get('meeting_time', 'TBD')
        meeting_date = meeting_data.get('meeting_date', 'TBD')
        location = meeting_data.get('location', 'City Hall')
        
        html_content = f"""
        <html>
        <body>
            <h2>Upcoming Meeting Notification</h2>
            <p>Hello {name},</p>
            <p>There's an upcoming meeting that matches your interests:</p>
            <h3>{meeting_data.get('title', 'City Council Meeting')}</h3>
            <p><strong>Date:</strong> {meeting_date}</p>
            <p><strong>Time:</strong> {meeting_time}</p>
            <p><strong>Location:</strong> {location}</p>
            <p><strong>Topics:</strong> {', '.join(topics)}</p>
            <p>You can view more details and add this to your calendar on the CityCamp AI website.</p>
            <p>Best regards,<br>The CityCamp AI Team</p>
        </body>
        </html>
        """
        
        text_content = f"""
        Upcoming Meeting Notification
        
        Hello {name},
        
        There's an upcoming meeting that matches your interests:
        
        {meeting_data.get('title', 'City Council Meeting')}
        Date: {meeting_date}
        Time: {meeting_time}
        Location: {location}
        Topics: {', '.join(topics)}
        
        You can view more details and add this to your calendar on the CityCamp AI website.
        
        Best regards,
        The CityCamp AI Team
        """
        
        return self.send_email(to_email, subject, html_content, text_content) 