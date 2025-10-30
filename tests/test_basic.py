"""
Basic tests for the healthcare chatbot
"""

import pytest
import json
from app import app, db
from models import User, HealthInfo, Conversation
from services.translation_service import TranslationService
from services.ai_service import AIService

@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client

@pytest.fixture
def sample_health_info(client):
    """Create sample health information"""
    with app.app_context():
        health_info = HealthInfo(
            topic='Test Fever Management',
            content='For fever: Rest and drink fluids.',
            language='en',
            category='symptoms',
            keywords='fever,temperature'
        )
        db.session.add(health_info)
        db.session.commit()
        return health_info

def test_health_check(client):
    """Test basic health check endpoint"""
    response = client.get('/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'active'
    assert 'chatbot' in data['service'].lower()

def test_create_health_info(client):
    """Test creating health information"""
    health_data = {
        'topic': 'Cough Treatment',
        'content': 'For cough: Stay hydrated and rest.',
        'language': 'en',
        'category': 'symptoms',
        'keywords': 'cough,throat'
    }
    
    response = client.post('/health/info', 
                          data=json.dumps(health_data),
                          content_type='application/json')
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['success'] == True
    assert data['data']['topic'] == 'Cough Treatment'

def test_get_health_info(client, sample_health_info):
    """Test retrieving health information"""
    response = client.get('/health/info?language=en&category=symptoms')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['total'] >= 1
    assert data['language'] == 'en'
    assert data['data'][0]['topic'] == 'Test Fever Management'

def test_translation_service():
    """Test translation service functionality"""
    translation_service = TranslationService()
    
    # Test language detection
    detected = translation_service.detect_language('Hello, how are you?')
    assert detected == 'en'
    
    # Test supported languages
    languages = translation_service.get_supported_languages()
    assert 'en' in languages
    assert 'hi' in languages

def test_ai_service():
    """Test AI service intent detection"""
    ai_service = AIService()
    
    # Test intent detection
    intent, confidence = ai_service.detect_intent('I have a fever and headache')
    assert intent == 'symptoms'
    assert confidence > 0
    
    # Test preventive intent
    intent, confidence = ai_service.detect_intent('How can I prevent getting sick?')
    assert intent == 'preventive'

def test_whatsapp_send_endpoint(client):
    """Test WhatsApp send message endpoint"""
    message_data = {
        'phone': '+1234567890',
        'message': 'Test health message'
    }
    
    response = client.post('/whatsapp/send',
                          data=json.dumps(message_data),
                          content_type='application/json')
    
    # Should fail without proper credentials but endpoint should exist
    assert response.status_code in [200, 400, 500]

def test_sms_send_endpoint(client):
    """Test SMS send message endpoint"""
    message_data = {
        'phone': '+1234567890',
        'message': 'Test health SMS'
    }
    
    response = client.post('/sms/send',
                          data=json.dumps(message_data),
                          content_type='application/json')
    
    # Should fail without proper credentials but endpoint should exist
    assert response.status_code in [200, 400, 500]

def test_analytics_dashboard(client):
    """Test analytics dashboard endpoint"""
    response = client.get('/analytics/dashboard')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'overview' in data
    assert 'total_users' in data['overview']

def test_supported_languages_endpoint(client):
    """Test supported languages endpoint"""
    response = client.get('/health/languages')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'supported_languages' in data
    assert 'en' in data['supported_languages']

def test_symptom_analysis(client):
    """Test symptom analysis endpoint"""
    symptom_data = {
        'symptoms': 'I have fever, cough and headache',
        'language': 'en'
    }
    
    response = client.post('/health/symptoms',
                          data=json.dumps(symptom_data),
                          content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'detected_categories' in data
    assert 'recommendations' in data

if __name__ == '__main__':
    pytest.main([__file__])