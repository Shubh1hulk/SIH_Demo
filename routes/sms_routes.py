"""
SMS routes for handling incoming SMS messages and sending responses
"""

from flask import Blueprint, request, jsonify
from services.sms_service import SMSService
from services.ai_service import AIService
from services.translation_service import TranslationService
from models import User, Conversation, db
from datetime import datetime

bp = Blueprint('sms', __name__, url_prefix='/sms')
sms_service = SMSService()
ai_service = AIService()
translation_service = TranslationService()

@bp.route('/webhook', methods=['POST'])
def sms_webhook():
    """Handle incoming SMS messages from Twilio"""
    
    # Parse incoming SMS data
    sms_data = sms_service.parse_incoming_sms(request.form.to_dict())
    
    if not sms_data:
        return jsonify({'status': 'error', 'message': 'Invalid SMS data'}), 400
    
    # Process the SMS message
    try:
        response_result = process_sms_message(sms_data)
        return jsonify({'status': 'processed', 'result': response_result}), 200
    except Exception as e:
        print(f"Error processing SMS message: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

def process_sms_message(sms_data):
    """Process incoming SMS message and generate response"""
    
    phone_number = sms_data.get('from', '').replace('+', '')
    message_text = sms_data.get('body', '').strip()
    message_sid = sms_data.get('message_sid')
    
    if not phone_number or not message_text:
        return {'success': False, 'error': 'Missing phone number or message text'}
    
    # Get or create user
    user = User.query.filter_by(phone_number=phone_number).first()
    if not user:
        # Detect language from first message
        detected_language = translation_service.detect_language(message_text)
        
        user = User(
            phone_number=phone_number,
            preferred_language=detected_language,
            created_at=datetime.utcnow(),
            last_active=datetime.utcnow()
        )
        db.session.add(user)
        db.session.commit()
    else:
        # Update last active
        user.last_active = datetime.utcnow()
        db.session.commit()
    
    # Check for special commands
    message_lower = message_text.lower().strip()
    
    if message_lower in ['hi', 'hello', 'start', 'नमस्ते', 'हैलो']:
        # Send welcome message
        greeting = translation_service.get_common_phrase('greeting', user.preferred_language)
        help_text = translation_service.get_common_phrase('help', user.preferred_language)
        welcome_message = f"{greeting}\n\n{help_text}"
        
        result = sms_service.send_sms(phone_number, welcome_message)
        return result
    
    elif message_lower in ['help', 'मदद']:
        help_text = translation_service.get_common_phrase('help', user.preferred_language)
        menu_options = {
            'en': "\n\nOptions:\n1. Symptoms\n2. Prevention\n3. Vaccination\n4. Emergency",
            'hi': "\n\nविकल्प:\n1. लक्षण\n2. बचाव\n3. टीकाकरण\n4. आपातकाल"
        }
        full_help = help_text + menu_options.get(user.preferred_language, menu_options['en'])
        
        return sms_service.send_sms(phone_number, full_help)
    
    elif message_lower in ['stop', 'unsubscribe', 'बंद']:
        stop_message = {
            'en': 'You have been unsubscribed from health notifications. Reply START to resume.',
            'hi': 'आपको स्वास्थ्य सूचनाओं से अनसब्स्क्राइब कर दिया गया है। फिर से शुरू करने के लिए START भेजें।'
        }
        message = stop_message.get(user.preferred_language, stop_message['en'])
        return sms_service.send_sms(phone_number, message)
    
    # Process health query using AI service
    ai_response = ai_service.process_health_query(
        message_text, 
        user.preferred_language, 
        user.id
    )
    
    response_text = ai_response.get('response', '')
    intent = ai_response.get('intent', 'general')
    
    # Add disclaimer for medical advice
    disclaimer = translation_service.get_common_phrase('disclaimer', user.preferred_language)
    if disclaimer and len(response_text + disclaimer) < 1400:  # SMS length limit
        response_text += f"\n\n⚠️ {disclaimer}"
    
    # Send response based on intent
    if intent == 'emergency':
        result = sms_service.send_emergency_info(
            phone_number, 
            'Health Emergency', 
            response_text, 
            user.preferred_language
        )
    elif intent == 'symptoms':
        result = sms_service.send_symptom_advice(
            phone_number, 
            message_text[:50], 
            response_text, 
            user.preferred_language
        )
    elif intent == 'preventive':
        result = sms_service.send_preventive_tip(
            phone_number, 
            response_text, 
            'General', 
            user.preferred_language
        )
    else:
        result = sms_service.send_sms(phone_number, response_text)
    
    # Log conversation with channel info
    conversation = Conversation(
        user_id=user.id,
        message_text=message_text,
        response_text=response_text,
        intent_detected=intent,
        confidence_score=ai_response.get('confidence'),
        channel='sms',
        timestamp=datetime.utcnow()
    )
    db.session.add(conversation)
    db.session.commit()
    
    return result

@bp.route('/send', methods=['POST'])
def send_sms():
    """Manually send SMS message (for admin/testing purposes)"""
    data = request.get_json()
    
    if not data or 'phone' not in data or 'message' not in data:
        return jsonify({'error': 'Phone number and message are required'}), 400
    
    phone = data['phone']
    message = data['message']
    
    result = sms_service.send_sms(phone, message)
    
    return jsonify(result)

@bp.route('/broadcast', methods=['POST'])
def broadcast_sms_alert():
    """Broadcast SMS alert to multiple users"""
    data = request.get_json()
    
    if not data or 'message' not in data:
        return jsonify({'error': 'Message is required'}), 400
    
    message = data['message']
    location = data.get('location')
    language = data.get('language', 'en')
    alert_type = data.get('alert_type', 'general')
    severity = data.get('severity', 'medium')
    
    # Get users to broadcast to
    query = User.query
    if location:
        query = query.filter_by(location=location)
    if language != 'all':
        query = query.filter_by(preferred_language=language)
    
    users = query.all()
    phone_numbers = [user.phone_number for user in users]
    
    # Translate message if needed
    translated_messages = {}
    for user in users:
        if user.preferred_language not in translated_messages:
            if user.preferred_language != language:
                translated_msg = translation_service.translate(message, user.preferred_language, language)
            else:
                translated_msg = message
            translated_messages[user.preferred_language] = translated_msg
    
    # Send based on alert type
    results = []
    success_count = 0
    
    for user in users:
        user_message = translated_messages[user.preferred_language]
        
        if alert_type == 'health_alert':
            result = sms_service.send_health_alert(user.phone_number, user_message, severity)
        elif alert_type == 'vaccination':
            # Parse vaccination info from message (simplified)
            vaccine_info = {
                'vaccine_name': 'General Vaccination',
                'age_group': 'All Ages',
                'schedule_info': user_message
            }
            result = sms_service.send_vaccination_reminder(user.phone_number, vaccine_info, user.preferred_language)
        else:
            result = sms_service.send_sms(user.phone_number, user_message)
        
        results.append({
            'phone': user.phone_number,
            'language': user.preferred_language,
            'success': result.get('success', False),
            'error': result.get('error'),
            'message_sid': result.get('message_sid')
        })
        
        if result.get('success'):
            success_count += 1
    
    return jsonify({
        'total_users': len(users),
        'successful_sends': success_count,
        'failed_sends': len(users) - success_count,
        'results': results
    })

@bp.route('/status/<message_sid>', methods=['GET'])
def get_sms_status(message_sid):
    """Get status of sent SMS"""
    result = sms_service.get_message_status(message_sid)
    return jsonify(result)

@bp.route('/vaccination-reminder', methods=['POST'])
def send_vaccination_reminder():
    """Send vaccination reminder to specific users"""
    data = request.get_json()
    
    required_fields = ['phone_numbers', 'vaccine_name', 'age_group', 'schedule_info']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    phone_numbers = data['phone_numbers']
    vaccine_info = {
        'vaccine_name': data['vaccine_name'],
        'age_group': data['age_group'],
        'schedule_info': data['schedule_info']
    }
    
    results = []
    success_count = 0
    
    for phone in phone_numbers:
        # Get user's preferred language
        user = User.query.filter_by(phone_number=phone.replace('+', '')).first()
        language = user.preferred_language if user else 'en'
        
        result = sms_service.send_vaccination_reminder(phone, vaccine_info, language)
        results.append({
            'phone': phone,
            'success': result.get('success', False),
            'message_sid': result.get('message_sid'),
            'error': result.get('error')
        })
        
        if result.get('success'):
            success_count += 1
    
    return jsonify({
        'total_recipients': len(phone_numbers),
        'successful_sends': success_count,
        'failed_sends': len(phone_numbers) - success_count,
        'results': results
    })