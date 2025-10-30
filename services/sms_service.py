"""
SMS Service using Twilio for rural healthcare communication
"""

import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
from typing import Dict, Optional

class SMSService:
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.phone_number = os.getenv('TWILIO_PHONE_NUMBER')
        
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
        else:
            self.client = None
            print("Warning: Twilio credentials not configured")
    
    def send_sms(self, to_phone: str, message: str) -> Dict:
        """Send SMS message"""
        if not self.client or not self.phone_number:
            return {'success': False, 'error': 'SMS service not configured'}
        
        try:
            # Ensure phone number format
            if not to_phone.startswith('+'):
                to_phone = '+' + to_phone
            
            # Truncate message if too long (SMS limit is 160 characters for single SMS)
            if len(message) > 1500:  # Allow for multiple SMS parts
                message = message[:1497] + "..."
            
            message_instance = self.client.messages.create(
                body=message,
                from_=self.phone_number,
                to=to_phone
            )
            
            return {
                'success': True,
                'message_sid': message_instance.sid,
                'status': message_instance.status,
                'price': message_instance.price,
                'direction': message_instance.direction
            }
            
        except TwilioException as e:
            return {
                'success': False,
                'error': f"Twilio error: {str(e)}",
                'error_code': getattr(e, 'code', None)
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"General error: {str(e)}"
            }
    
    def send_health_alert(self, to_phone: str, alert_message: str, severity: str = 'medium') -> Dict:
        """Send health alert SMS with priority handling"""
        # Add severity indicator
        severity_indicators = {
            'low': '📌',
            'medium': '⚠️',
            'high': '🚨',
            'critical': '🚨🚨'
        }
        
        indicator = severity_indicators.get(severity, '📌')
        formatted_message = f"{indicator} HEALTH ALERT: {alert_message}"
        
        return self.send_sms(to_phone, formatted_message)
    
    def send_vaccination_reminder(self, to_phone: str, vaccine_info: Dict, language: str = 'en') -> Dict:
        """Send vaccination reminder SMS"""
        templates = {
            'en': "💉 VACCINATION REMINDER: {vaccine_name} is due for {age_group}. Schedule: {schedule}. Contact your local health center.",
            'hi': "💉 टीकाकरण रिमाइंडर: {vaccine_name} {age_group} के लिए देय है। अनुसूची: {schedule}। अपने स्थानीय स्वास्थ्य केंद्र से संपर्क करें।"
        }
        
        template = templates.get(language, templates['en'])
        message = template.format(
            vaccine_name=vaccine_info.get('vaccine_name', 'Unknown'),
            age_group=vaccine_info.get('age_group', 'Unknown'),
            schedule=vaccine_info.get('schedule_info', 'Contact health center')
        )
        
        return self.send_sms(to_phone, message)
    
    def send_symptom_advice(self, to_phone: str, symptoms: str, advice: str, language: str = 'en') -> Dict:
        """Send symptom-based health advice"""
        templates = {
            'en': "🏥 HEALTH ADVICE: For symptoms like '{symptoms}': {advice} ⚠️ Consult a doctor if symptoms persist.",
            'hi': "🏥 स्वास्थ्य सलाह: '{symptoms}' जैसे लक्षणों के लिए: {advice} ⚠️ लक्षण बने रहने पर डॉक्टर से सलाह लें।"
        }
        
        template = templates.get(language, templates['en'])
        message = template.format(symptoms=symptoms[:50], advice=advice)
        
        return self.send_sms(to_phone, message)
    
    def send_emergency_info(self, to_phone: str, emergency_type: str, instructions: str, language: str = 'en') -> Dict:
        """Send emergency health information"""
        templates = {
            'en': "🚨 EMERGENCY: {emergency_type}. IMMEDIATE ACTION: {instructions} Call emergency services: 108",
            'hi': "🚨 आपातकाल: {emergency_type}। तत्काल कार्य: {instructions} आपातकालीन सेवा कॉल करें: 108"
        }
        
        template = templates.get(language, templates['en'])
        message = template.format(
            emergency_type=emergency_type,
            instructions=instructions
        )
        
        return self.send_sms(to_phone, message)
    
    def send_preventive_tip(self, to_phone: str, tip: str, category: str, language: str = 'en') -> Dict:
        """Send preventive health tips"""
        templates = {
            'en': "🌟 HEALTH TIP ({category}): {tip} Stay healthy!",
            'hi': "🌟 स्वास्थ्य सुझाव ({category}): {tip} स्वस्थ रहें!"
        }
        
        template = templates.get(language, templates['en'])
        message = template.format(category=category, tip=tip)
        
        return self.send_sms(to_phone, message)
    
    def parse_incoming_sms(self, request_data: Dict) -> Optional[Dict]:
        """Parse incoming SMS from Twilio webhook"""
        try:
            return {
                'from': request_data.get('From'),
                'to': request_data.get('To'),
                'body': request_data.get('Body', ''),
                'message_sid': request_data.get('MessageSid'),
                'account_sid': request_data.get('AccountSid'),
                'from_country': request_data.get('FromCountry'),
                'from_state': request_data.get('FromState'),
                'from_city': request_data.get('FromCity')
            }
        except Exception as e:
            print(f"Error parsing incoming SMS: {e}")
            return None
    
    def get_message_status(self, message_sid: str) -> Dict:
        """Get status of sent SMS"""
        if not self.client:
            return {'success': False, 'error': 'SMS service not configured'}
        
        try:
            message = self.client.messages(message_sid).fetch()
            return {
                'success': True,
                'status': message.status,
                'price': message.price,
                'error_code': message.error_code,
                'error_message': message.error_message,
                'direction': message.direction,
                'date_sent': message.date_sent.isoformat() if message.date_sent else None
            }
        except TwilioException as e:
            return {'success': False, 'error': str(e)}
    
    def send_bulk_sms(self, phone_numbers: list, message: str) -> Dict:
        """Send SMS to multiple recipients"""
        if not self.client:
            return {'success': False, 'error': 'SMS service not configured'}
        
        results = []
        success_count = 0
        
        for phone in phone_numbers:
            result = self.send_sms(phone, message)
            results.append({
                'phone': phone,
                'result': result
            })
            if result.get('success'):
                success_count += 1
        
        return {
            'success': success_count > 0,
            'total_sent': len(phone_numbers),
            'successful': success_count,
            'failed': len(phone_numbers) - success_count,
            'results': results
        }