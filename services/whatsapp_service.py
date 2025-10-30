"""
WhatsApp Business API integration service
"""

import os
import requests
import json
from typing import Dict, Optional

class WhatsAppService:
    def __init__(self):
        self.api_url = os.getenv('WHATSAPP_API_URL', 'https://graph.facebook.com/v17.0')
        self.access_token = os.getenv('WHATSAPP_ACCESS_TOKEN')
        self.phone_number_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
        self.verify_token = os.getenv('WHATSAPP_VERIFY_TOKEN')
        
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def send_message(self, to_phone: str, message: str, message_type: str = 'text') -> Dict:
        """Send a message via WhatsApp Business API"""
        if not self.access_token or not self.phone_number_id:
            return {'success': False, 'error': 'WhatsApp credentials not configured'}
        
        url = f"{self.api_url}/{self.phone_number_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to_phone,
            "type": message_type
        }
        
        if message_type == 'text':
            payload["text"] = {"body": message}
        elif message_type == 'template':
            # For template messages (future enhancement)
            payload["template"] = {
                "name": "health_info",
                "language": {"code": "en"},
                "components": [
                    {
                        "type": "body",
                        "parameters": [{"type": "text", "text": message}]
                    }
                ]
            }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response_data = response.json()
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message_id': response_data.get('messages', [{}])[0].get('id'),
                    'response': response_data
                }
            else:
                return {
                    'success': False,
                    'error': response_data.get('error', {}).get('message', 'Unknown error'),
                    'response': response_data
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def send_interactive_message(self, to_phone: str, body_text: str, buttons: list) -> Dict:
        """Send an interactive message with buttons"""
        if not self.access_token or not self.phone_number_id:
            return {'success': False, 'error': 'WhatsApp credentials not configured'}
        
        url = f"{self.api_url}/{self.phone_number_id}/messages"
        
        # Format buttons for WhatsApp API
        formatted_buttons = []
        for i, button in enumerate(buttons[:3]):  # WhatsApp allows max 3 buttons
            formatted_buttons.append({
                "type": "reply",
                "reply": {
                    "id": f"btn_{i}",
                    "title": button[:20]  # Max 20 characters for button title
                }
            })
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to_phone,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": body_text},
                "action": {"buttons": formatted_buttons}
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response_data = response.json()
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message_id': response_data.get('messages', [{}])[0].get('id'),
                    'response': response_data
                }
            else:
                return {
                    'success': False,
                    'error': response_data.get('error', {}).get('message', 'Unknown error'),
                    'response': response_data
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def send_health_menu(self, to_phone: str, language: str = 'en') -> Dict:
        """Send health information menu"""
        menu_text = {
            'en': "🏥 Health Information Menu\n\nWhat would you like to know about?",
            'hi': "🏥 स्वास्थ्य जानकारी मेनू\n\nआप किस बारे में जानना चाहते हैं?"
        }
        
        buttons = {
            'en': ["💊 Symptoms", "🛡️ Prevention", "💉 Vaccination"],
            'hi': ["💊 लक्षण", "🛡️ बचाव", "💉 टीकाकरण"]
        }
        
        text = menu_text.get(language, menu_text['en'])
        button_list = buttons.get(language, buttons['en'])
        
        return self.send_interactive_message(to_phone, text, button_list)
    
    def parse_webhook_message(self, webhook_data: Dict) -> Optional[Dict]:
        """Parse incoming WhatsApp webhook message"""
        try:
            entry = webhook_data.get('entry', [])
            if not entry:
                return None
            
            changes = entry[0].get('changes', [])
            if not changes:
                return None
            
            value = changes[0].get('value', {})
            messages = value.get('messages', [])
            
            if not messages:
                return None
            
            message = messages[0]
            
            # Extract message details
            return {
                'from': message.get('from'),
                'id': message.get('id'),
                'timestamp': message.get('timestamp'),
                'type': message.get('type'),
                'text': message.get('text', {}).get('body', ''),
                'interactive': message.get('interactive', {}),
                'contacts': value.get('contacts', [])
            }
            
        except Exception as e:
            print(f"Error parsing webhook message: {e}")
            return None
    
    def mark_message_read(self, message_id: str) -> Dict:
        """Mark a message as read"""
        if not self.access_token or not self.phone_number_id:
            return {'success': False, 'error': 'WhatsApp credentials not configured'}
        
        url = f"{self.api_url}/{self.phone_number_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            return {'success': response.status_code == 200, 'response': response.json()}
        except Exception as e:
            return {'success': False, 'error': str(e)}