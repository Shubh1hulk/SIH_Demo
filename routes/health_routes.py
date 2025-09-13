"""
Health information and data management routes
"""

from flask import Blueprint, request, jsonify
from models import HealthInfo, VaccinationSchedule, HealthAlert, db
from services.translation_service import TranslationService
from datetime import datetime, timedelta
import json

bp = Blueprint('health', __name__, url_prefix='/health')
translation_service = TranslationService()

@bp.route('/info', methods=['GET', 'POST'])
def health_info():
    """Get or create health information"""
    
    if request.method == 'POST':
        # Create new health information
        data = request.get_json()
        
        if not data or not all(key in data for key in ['topic', 'content', 'language', 'category']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        health_info = HealthInfo(
            topic=data['topic'],
            content=data['content'],
            language=data['language'],
            category=data['category'],
            keywords=data.get('keywords', ''),
            created_at=datetime.utcnow()
        )
        
        db.session.add(health_info)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'id': health_info.id,
            'data': health_info.to_dict()
        }), 201
    
    # GET request - retrieve health information
    category = request.args.get('category')
    language = request.args.get('language', 'en')
    topic = request.args.get('topic')
    
    query = HealthInfo.query.filter_by(language=language)
    
    if category:
        query = query.filter_by(category=category)
    
    if topic:
        query = query.filter(HealthInfo.topic.ilike(f'%{topic}%'))
    
    health_infos = query.all()
    
    return jsonify({
        'total': len(health_infos),
        'language': language,
        'category': category,
        'data': [info.to_dict() for info in health_infos]
    })

@bp.route('/info/<int:info_id>', methods=['GET', 'PUT', 'DELETE'])
def health_info_detail(info_id):
    """Get, update, or delete specific health information"""
    
    health_info = HealthInfo.query.get_or_404(info_id)
    
    if request.method == 'GET':
        return jsonify(health_info.to_dict())
    
    elif request.method == 'PUT':
        # Update health information
        data = request.get_json()
        
        if 'topic' in data:
            health_info.topic = data['topic']
        if 'content' in data:
            health_info.content = data['content']
        if 'category' in data:
            health_info.category = data['category']
        if 'keywords' in data:
            health_info.keywords = data['keywords']
        
        health_info.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': health_info.to_dict()
        })
    
    elif request.method == 'DELETE':
        # Delete health information
        db.session.delete(health_info)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Health information deleted'})

@bp.route('/vaccination', methods=['GET', 'POST'])
def vaccination_schedule():
    """Get or create vaccination schedule information"""
    
    if request.method == 'POST':
        # Create new vaccination schedule
        data = request.get_json()
        
        required_fields = ['vaccine_name', 'age_group', 'schedule_info', 'language']
        if not data or not all(key in data for key in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        vaccination = VaccinationSchedule(
            vaccine_name=data['vaccine_name'],
            age_group=data['age_group'],
            schedule_info=data['schedule_info'],
            language=data['language'],
            is_mandatory=data.get('is_mandatory', True),
            created_at=datetime.utcnow()
        )
        
        db.session.add(vaccination)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'id': vaccination.id,
            'data': vaccination.to_dict()
        }), 201
    
    # GET request - retrieve vaccination schedules
    language = request.args.get('language', 'en')
    age_group = request.args.get('age_group')
    vaccine_name = request.args.get('vaccine_name')
    
    query = VaccinationSchedule.query.filter_by(language=language)
    
    if age_group:
        query = query.filter(VaccinationSchedule.age_group.ilike(f'%{age_group}%'))
    
    if vaccine_name:
        query = query.filter(VaccinationSchedule.vaccine_name.ilike(f'%{vaccine_name}%'))
    
    vaccinations = query.all()
    
    return jsonify({
        'total': len(vaccinations),
        'language': language,
        'age_group': age_group,
        'data': [vaccination.to_dict() for vaccination in vaccinations]
    })

@bp.route('/alerts', methods=['GET', 'POST'])
def health_alerts():
    """Get or create health alerts"""
    
    if request.method == 'POST':
        # Create new health alert
        data = request.get_json()
        
        required_fields = ['alert_type', 'title', 'content', 'language']
        if not data or not all(key in data for key in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Set expiration date if provided
        expires_at = None
        if 'expires_in_days' in data:
            expires_at = datetime.utcnow() + timedelta(days=data['expires_in_days'])
        elif 'expires_at' in data:
            expires_at = datetime.fromisoformat(data['expires_at'])
        
        alert = HealthAlert(
            alert_type=data['alert_type'],
            title=data['title'],
            content=data['content'],
            language=data['language'],
            location=data.get('location'),
            severity=data.get('severity', 'medium'),
            is_active=data.get('is_active', True),
            expires_at=expires_at,
            created_at=datetime.utcnow()
        )
        
        db.session.add(alert)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'id': alert.id,
            'data': alert.to_dict()
        }), 201
    
    # GET request - retrieve health alerts
    language = request.args.get('language', 'en')
    location = request.args.get('location')
    alert_type = request.args.get('alert_type')
    severity = request.args.get('severity')
    active_only = request.args.get('active_only', 'true').lower() == 'true'
    
    query = HealthAlert.query.filter_by(language=language)
    
    if location:
        query = query.filter_by(location=location)
    
    if alert_type:
        query = query.filter_by(alert_type=alert_type)
    
    if severity:
        query = query.filter_by(severity=severity)
    
    if active_only:
        query = query.filter_by(is_active=True)
        query = query.filter(
            (HealthAlert.expires_at.is_(None)) | 
            (HealthAlert.expires_at > datetime.utcnow())
        )
    
    alerts = query.order_by(HealthAlert.created_at.desc()).all()
    
    return jsonify({
        'total': len(alerts),
        'language': language,
        'location': location,
        'data': [alert.to_dict() for alert in alerts]
    })

@bp.route('/alerts/<int:alert_id>', methods=['GET', 'PUT', 'DELETE'])
def health_alert_detail(alert_id):
    """Get, update, or delete specific health alert"""
    
    alert = HealthAlert.query.get_or_404(alert_id)
    
    if request.method == 'GET':
        return jsonify(alert.to_dict())
    
    elif request.method == 'PUT':
        # Update health alert
        data = request.get_json()
        
        updatable_fields = ['title', 'content', 'location', 'severity', 'is_active']
        for field in updatable_fields:
            if field in data:
                setattr(alert, field, data[field])
        
        if 'expires_in_days' in data:
            alert.expires_at = datetime.utcnow() + timedelta(days=data['expires_in_days'])
        elif 'expires_at' in data:
            alert.expires_at = datetime.fromisoformat(data['expires_at'])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': alert.to_dict()
        })
    
    elif request.method == 'DELETE':
        # Delete health alert
        db.session.delete(alert)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Health alert deleted'})

@bp.route('/symptoms', methods=['POST'])
def analyze_symptoms():
    """Analyze symptoms and provide recommendations"""
    data = request.get_json()
    
    if not data or 'symptoms' not in data:
        return jsonify({'error': 'Symptoms are required'}), 400
    
    symptoms = data['symptoms']
    language = data.get('language', 'en')
    
    # Simple symptom analysis (can be enhanced with ML models)
    symptom_keywords = {
        'fever': ['fever', 'temperature', 'hot', 'chills'],
        'respiratory': ['cough', 'breathing', 'chest', 'throat', 'lungs'],
        'digestive': ['stomach', 'nausea', 'vomiting', 'diarrhea', 'appetite'],
        'neurological': ['headache', 'dizzy', 'confusion', 'memory'],
        'skin': ['rash', 'itching', 'swelling', 'bumps']
    }
    
    detected_categories = []
    symptoms_lower = symptoms.lower()
    
    for category, keywords in symptom_keywords.items():
        if any(keyword in symptoms_lower for keyword in keywords):
            detected_categories.append(category)
    
    # Get relevant health information
    recommendations = []
    for category in detected_categories:
        health_info = HealthInfo.query.filter_by(
            language=language,
            category='symptoms'
        ).filter(HealthInfo.keywords.contains(category)).first()
        
        if health_info:
            recommendations.append({
                'category': category,
                'recommendation': health_info.content
            })
    
    # General advice if no specific recommendations found
    if not recommendations:
        general_advice = {
            'en': 'For any concerning symptoms, please consult a healthcare professional. Stay hydrated, get rest, and monitor your symptoms.',
            'hi': 'किसी भी चिंताजनक लक्षण के लिए कृपया स्वास्थ्य पेशेवर से सलाह लें। हाइड्रेटेड रहें, आराम करें और अपने लक्षणों पर नजर रखें।'
        }
        
        recommendations.append({
            'category': 'general',
            'recommendation': general_advice.get(language, general_advice['en'])
        })
    
    return jsonify({
        'symptoms': symptoms,
        'detected_categories': detected_categories,
        'recommendations': recommendations,
        'language': language,
        'disclaimer': translation_service.get_common_phrase('disclaimer', language)
    })

@bp.route('/translate', methods=['POST'])
def translate_content():
    """Translate health content to different languages"""
    data = request.get_json()
    
    if not data or not all(key in data for key in ['content', 'target_language']):
        return jsonify({'error': 'Content and target_language are required'}), 400
    
    content = data['content']
    target_language = data['target_language']
    source_language = data.get('source_language', 'en')
    
    if not translation_service.is_language_supported(target_language):
        return jsonify({'error': f'Target language {target_language} is not supported'}), 400
    
    translated_content = translation_service.translate(content, target_language, source_language)
    
    return jsonify({
        'original_content': content,
        'translated_content': translated_content,
        'source_language': source_language,
        'target_language': target_language
    })

@bp.route('/languages', methods=['GET'])
def supported_languages():
    """Get list of supported languages"""
    return jsonify({
        'supported_languages': translation_service.get_supported_languages()
    })