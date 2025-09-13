"""
WhatsApp routes for handling incoming messages and webhooks
"""

from flask import Blueprint, request, jsonify
from services.whatsapp_service import WhatsAppService
from services.ai_service import AIService
from services.translation_service import TranslationService
from models import User, Conversation, db
from datetime import datetime

bp = Blueprint('whatsapp', __name__, url_prefix='/whatsapp')
whatsapp_service = WhatsAppService()
ai_service = AIService()
translation_service = TranslationService()

@bp.route('/webhook', methods=['GET', 'POST'])
def whatsapp_webhook():
    """Handle WhatsApp webhook for message verification and processing"""
    
    if request.method == 'GET':
        # Webhook verification
        verify_token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        if verify_token == whatsapp_service.verify_token:
            return challenge
        return 'Invalid verification token', 403
    
    # Handle incoming messages
    webhook_data = request.get_json()
    
    if not webhook_data:
        return jsonify({'status': 'error', 'message': 'No data received'}), 400
    
    # Parse the incoming message
    message_data = whatsapp_service.parse_webhook_message(webhook_data)
    
    if not message_data:
        return jsonify({'status': 'received'}), 200
    
    # Process the message
    try:
        response_result = process_whatsapp_message(message_data)
        return jsonify({'status': 'processed', 'result': response_result}), 200
    except Exception as e:
        print(f"Error processing WhatsApp message: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

def process_whatsapp_message(message_data):
    """Process incoming WhatsApp message and generate response"""
    
    phone_number = message_data.get('from')
    message_text = message_data.get('text', '')
    message_id = message_data.get('id')
    
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
        # Send welcome message with menu
        result = whatsapp_service.send_health_menu(phone_number, user.preferred_language)
        greeting = translation_service.get_common_phrase('greeting', user.preferred_language)
        
        if not result.get('success'):
            # Fallback to text message
            result = whatsapp_service.send_message(phone_number, greeting)
        
        return result
    
    elif message_lower in ['help', 'मदद']:
        help_text = translation_service.get_common_phrase('help', user.preferred_language)
        return whatsapp_service.send_message(phone_number, help_text)
    
    elif message_lower in ['menu', 'options', 'मेनू']:
        return whatsapp_service.send_health_menu(phone_number, user.preferred_language)
    
    # Process health query using AI service
    ai_response = ai_service.process_health_query(
        message_text, 
        user.preferred_language, 
        user.id
    )
    
    response_text = ai_response.get('response', '')
    
    # Add disclaimer for medical advice
    disclaimer = translation_service.get_common_phrase('disclaimer', user.preferred_language)
    if disclaimer:
        response_text += f"\n\n⚠️ {disclaimer}"
    
    # Mark original message as read
    whatsapp_service.mark_message_read(message_id)
    
    # Send response
    result = whatsapp_service.send_message(phone_number, response_text)
    
    # Log conversation with channel info
    if 'conversation' not in locals():  # If not already logged by AI service
        conversation = Conversation(
            user_id=user.id,
            message_text=message_text,
            response_text=response_text,
            intent_detected=ai_response.get('intent'),
            confidence_score=ai_response.get('confidence'),
            channel='whatsapp',
            timestamp=datetime.utcnow()
        )
        db.session.add(conversation)
        db.session.commit()
    
    return result

@bp.route('/send', methods=['POST'])
def send_whatsapp_message():
    """Manually send WhatsApp message (for admin/testing purposes)"""
    data = request.get_json()
    
    if not data or 'phone' not in data or 'message' not in data:
        return jsonify({'error': 'Phone number and message are required'}), 400
    
    phone = data['phone']
    message = data['message']
    message_type = data.get('type', 'text')
    
    result = whatsapp_service.send_message(phone, message, message_type)
    
    return jsonify(result)

@bp.route('/broadcast', methods=['POST'])
def broadcast_health_alert():
    """Broadcast health alert to multiple users"""
    data = request.get_json()
    
    if not data or 'message' not in data:
        return jsonify({'error': 'Message is required'}), 400
    
    message = data['message']
    location = data.get('location')
    language = data.get('language', 'en')
    
    # Get users to broadcast to
    query = User.query
    if location:
        query = query.filter_by(location=location)
    if language != 'all':
        query = query.filter_by(preferred_language=language)
    
    users = query.all()
    
    results = []
    success_count = 0
    
    for user in users:
        # Translate message to user's preferred language if needed
        user_message = message
        if user.preferred_language != language:
            user_message = translation_service.translate(message, user.preferred_language, language)
        
        result = whatsapp_service.send_message(user.phone_number, user_message)
        results.append({
            'phone': user.phone_number,
            'language': user.preferred_language,
            'success': result.get('success', False),
            'error': result.get('error')
        })
        
        if result.get('success'):
            success_count += 1
    
    return jsonify({
        'total_users': len(users),
        'successful_sends': success_count,
        'failed_sends': len(users) - success_count,
        'results': results
    })

@bp.route('/users', methods=['GET'])
def get_whatsapp_users():
    """Get list of WhatsApp users"""
    users = User.query.all()
    return jsonify({
        'total_users': len(users),
        'users': [user.to_dict() for user in users]
    })