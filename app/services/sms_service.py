"""
SMS integration service using Twilio
"""

from twilio.rest import Client
from typing import Optional
from loguru import logger
from app.core.config import settings


class SMSService:
    """Service for SMS messaging via Twilio"""
    
    def __init__(self):
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.phone_number = settings.TWILIO_PHONE_NUMBER
        
        self.client = None
        if self.account_sid and self.auth_token:
            try:
                self.client = Client(self.account_sid, self.auth_token)
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {e}")
    
    async def send_sms(self, to: str, message: str) -> bool:
        """Send SMS message"""
        try:
            if not self.client or not self.phone_number:
                logger.warning("SMS service not configured")
                return False
            
            # Ensure the 'to' number is in E.164 format
            if not to.startswith('+'):
                to = '+91' + to  # Default to India country code
            
            message_obj = self.client.messages.create(
                body=message,
                from_=self.phone_number,
                to=to
            )
            
            logger.info(f"SMS sent successfully to {to}, SID: {message_obj.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            return False
    
    async def send_health_alert_sms(self, to: str, alert_type: str, message: str) -> bool:
        """Send health alert via SMS"""
        try:
            # Format SMS message (SMS has character limits)
            alert_prefix = {
                "outbreak": "HEALTH ALERT",
                "vaccination": "VACCINE REMINDER",
                "general": "HEALTH INFO",
                "emergency": "EMERGENCY"
            }
            
            prefix = alert_prefix.get(alert_type, "HEALTH INFO")
            
            # Keep SMS under 160 characters for single message
            sms_message = f"{prefix}: {message}"
            if len(sms_message) > 160:
                sms_message = sms_message[:157] + "..."
            
            sms_message += "\n\nFor emergency: Call 108"
            
            return await self.send_sms(to, sms_message)
            
        except Exception as e:
            logger.error(f"Error sending health alert SMS: {e}")
            return False
    
    async def send_vaccination_reminder_sms(self, to: str, vaccine_name: str, due_date: str) -> bool:
        """Send vaccination reminder via SMS"""
        try:
            message = f"VACCINE REMINDER: {vaccine_name} due on {due_date}. "
            message += "Consult your healthcare provider. "
            message += "Reply STOP to unsubscribe."
            
            return await self.send_sms(to, message)
            
        except Exception as e:
            logger.error(f"Error sending vaccination reminder SMS: {e}")
            return False
    
    async def send_symptom_assessment_sms(self, to: str, assessment_result: str, urgency: str) -> bool:
        """Send symptom assessment result via SMS"""
        try:
            urgency_prefix = {
                "critical": "URGENT",
                "high": "IMPORTANT",
                "moderate": "ADVICE",
                "low": "INFO"
            }
            
            prefix = urgency_prefix.get(urgency.lower(), "INFO")
            message = f"{prefix}: {assessment_result}"
            
            if urgency.lower() in ["critical", "high"]:
                message += " Seek medical attention. Emergency: 108"
            
            # Truncate if too long
            if len(message) > 160:
                message = message[:157] + "..."
            
            return await self.send_sms(to, message)
            
        except Exception as e:
            logger.error(f"Error sending assessment SMS: {e}")
            return False
    
    async def send_otp_sms(self, to: str, otp: str) -> bool:
        """Send OTP for verification"""
        try:
            message = f"Your AI Health Assistant verification code is: {otp}. Valid for 10 minutes. Do not share this code."
            return await self.send_sms(to, message)
            
        except Exception as e:
            logger.error(f"Error sending OTP SMS: {e}")
            return False
    
    async def handle_incoming_sms(self, from_number: str, message_body: str) -> Optional[str]:
        """Process incoming SMS message"""
        try:
            logger.info(f"Received SMS from {from_number}: {message_body}")
            
            # Handle common SMS commands
            message_lower = message_body.lower().strip()
            
            if message_lower in ["stop", "unsubscribe"]:
                # Handle unsubscribe request
                return "unsubscribe"
            elif message_lower in ["help", "info"]:
                # Send help information
                return "help"
            else:
                # Regular health query
                return message_body
            
        except Exception as e:
            logger.error(f"Error processing incoming SMS: {e}")
            return None
    
    def is_configured(self) -> bool:
        """Check if SMS service is properly configured"""
        return bool(self.client and self.phone_number)