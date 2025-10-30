"""
Database models for the healthcare chatbot
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float

db = SQLAlchemy()

class User(db.Model):
    """User model for tracking chatbot users"""
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    preferred_language = db.Column(db.String(10), default='en')
    location = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'phone_number': self.phone_number,
            'preferred_language': self.preferred_language,
            'location': self.location,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_active': self.last_active.isoformat() if self.last_active else None
        }

class Conversation(db.Model):
    """Model for storing conversation history"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message_text = db.Column(db.Text, nullable=False)
    response_text = db.Column(db.Text)
    intent_detected = db.Column(db.String(50))
    confidence_score = db.Column(db.Float)
    channel = db.Column(db.String(20))  # 'whatsapp' or 'sms'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'message_text': self.message_text,
            'response_text': self.response_text,
            'intent_detected': self.intent_detected,
            'confidence_score': self.confidence_score,
            'channel': self.channel,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class HealthInfo(db.Model):
    """Model for storing healthcare information"""
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(10), nullable=False)
    category = db.Column(db.String(50))  # 'symptoms', 'preventive', 'vaccination'
    keywords = db.Column(db.Text)  # JSON string of keywords
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'topic': self.topic,
            'content': self.content,
            'language': self.language,
            'category': self.category,
            'keywords': self.keywords,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class VaccinationSchedule(db.Model):
    """Model for vaccination schedules"""
    id = db.Column(db.Integer, primary_key=True)
    vaccine_name = db.Column(db.String(100), nullable=False)
    age_group = db.Column(db.String(50), nullable=False)
    schedule_info = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(10), nullable=False)
    is_mandatory = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'vaccine_name': self.vaccine_name,
            'age_group': self.age_group,
            'schedule_info': self.schedule_info,
            'language': self.language,
            'is_mandatory': self.is_mandatory,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class HealthAlert(db.Model):
    """Model for health alerts and outbreak information"""
    id = db.Column(db.Integer, primary_key=True)
    alert_type = db.Column(db.String(50), nullable=False)  # 'outbreak', 'advisory', 'emergency'
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(10), nullable=False)
    location = db.Column(db.String(100))
    severity = db.Column(db.String(20), default='medium')  # 'low', 'medium', 'high', 'critical'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'alert_type': self.alert_type,
            'title': self.title,
            'content': self.content,
            'language': self.language,
            'location': self.location,
            'severity': self.severity,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }