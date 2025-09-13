"""
WhatsApp Business API integration service
"""

import requests
from typing import Dict, Any, Optional
from loguru import logger
from app.core.config import settings


class WhatsAppService:
    """Service for WhatsApp Business API integration"""
    
    def __init__(self):
        self.access_token = settings.WHATSAPP_TOKEN
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.business_account_id = settings.WHATSAPP_BUSINESS_ACCOUNT_ID
        self.base_url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}/messages"
        
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    async def send_text_message(self, to: str, message: str) -> bool:
        """Send a text message via WhatsApp"""
        try:
            if not self.access_token or not self.phone_number_id:
                logger.warning("WhatsApp credentials not configured")
                return False
            
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to,
                "type": "text",
                "text": {
                    "body": message
                }
            }
            
            response = requests.post(
                self.base_url,
                json=payload,
                headers=self.headers
            )
            
            if response.status_code == 200:
                logger.info(f"WhatsApp message sent successfully to {to}")
                return True
            else:
                logger.error(f"Failed to send WhatsApp message: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {e}")
            return False
    
    async def send_template_message(self, to: str, template_name: str, language: str = "en", components: Optional[list] = None) -> bool:
        """Send a template message via WhatsApp"""
        try:
            if not self.access_token or not self.phone_number_id:
                logger.warning("WhatsApp credentials not configured")
                return False
            
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {
                        "code": language
                    }
                }
            }
            
            if components:
                payload["template"]["components"] = components
            
            response = requests.post(
                self.base_url,
                json=payload,
                headers=self.headers
            )
            
            if response.status_code == 200:
                logger.info(f"WhatsApp template message sent successfully to {to}")
                return True
            else:
                logger.error(f"Failed to send WhatsApp template message: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending WhatsApp template message: {e}")
            return False
    
    async def send_health_alert(self, to: str, alert_type: str, message: str, language: str = "en") -> bool:
        """Send health alert via WhatsApp"""
        try:
            # Format health alert message
            alert_emoji = {
                "outbreak": "🚨",
                "vaccination": "💉",
                "general": "ℹ️",
                "emergency": "🆘"
            }
            
            emoji = alert_emoji.get(alert_type, "ℹ️")
            formatted_message = f"{emoji} *Health Alert*\n\n{message}\n\n_This is an official health notification. For emergencies, call 108._"
            
            return await self.send_text_message(to, formatted_message)
            
        except Exception as e:
            logger.error(f"Error sending health alert via WhatsApp: {e}")
            return False
    
    async def send_vaccination_reminder(self, to: str, vaccine_name: str, due_date: str, language: str = "en") -> bool:
        """Send vaccination reminder via WhatsApp"""
        try:
            message = f"💉 *Vaccination Reminder*\n\n"
            message += f"Vaccine: {vaccine_name}\n"
            message += f"Due Date: {due_date}\n\n"
            message += "Please consult your healthcare provider to schedule your vaccination.\n\n"
            message += "_This is an automated reminder from AI Health Assistant._"
            
            return await self.send_text_message(to, message)
            
        except Exception as e:
            logger.error(f"Error sending vaccination reminder via WhatsApp: {e}")
            return False
    
    async def handle_incoming_message(self, message_data: Dict[str, Any]) -> Optional[str]:
        """Process incoming WhatsApp message"""
        try:
            if "messages" not in message_data.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {}):
                return None
            
            message_info = message_data["entry"][0]["changes"][0]["value"]["messages"][0]
            
            user_phone = message_info["from"]
            message_text = message_info.get("text", {}).get("body", "")
            message_type = message_info.get("type", "text")
            
            if message_type == "text" and message_text:
                logger.info(f"Received WhatsApp message from {user_phone}: {message_text}")
                return message_text
            
            return None
            
        except Exception as e:
            logger.error(f"Error processing incoming WhatsApp message: {e}")
            return None
    
    def is_configured(self) -> bool:
        """Check if WhatsApp service is properly configured"""
        return bool(self.access_token and self.phone_number_id)