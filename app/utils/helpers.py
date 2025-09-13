"""
Utility functions for the healthcare chatbot
"""

import re
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import hashlib
import random
import string


def clean_phone_number(phone: str) -> str:
    """Clean and format phone number to E.164 format"""
    # Remove all non-digit characters
    cleaned = re.sub(r'[^\d]', '', phone)
    
    # Add country code if not present
    if len(cleaned) == 10:  # Indian mobile number without country code
        cleaned = '91' + cleaned
    
    # Add + prefix
    if not cleaned.startswith('+'):
        cleaned = '+' + cleaned
    
    return cleaned


def validate_phone_number(phone: str) -> bool:
    """Validate phone number format"""
    # Basic validation for Indian phone numbers
    pattern = r'^\+91[6-9]\d{9}$'
    return bool(re.match(pattern, phone))


def generate_session_id(user_id: str = None) -> str:
    """Generate a unique session ID"""
    timestamp = str(int(datetime.now().timestamp()))
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    
    if user_id:
        # Create a hash of user_id + timestamp for uniqueness
        hash_input = f"{user_id}_{timestamp}_{random_str}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:16]
    else:
        return f"{timestamp}_{random_str}"


def sanitize_message(message: str) -> str:
    """Sanitize user input message"""
    # Remove excessive whitespace
    message = re.sub(r'\s+', ' ', message.strip())
    
    # Remove potentially harmful characters but keep basic punctuation
    message = re.sub(r'[<>\"\'`]', '', message)
    
    # Limit message length
    if len(message) > 1000:
        message = message[:1000] + "..."
    
    return message


def extract_age_from_text(text: str) -> Optional[int]:
    """Extract age from text"""
    # Look for patterns like "I am 25 years old", "25 years", "age 30", etc.
    patterns = [
        r'(?:I am|age|aged)\s*(\d{1,3})\s*(?:years?)?',
        r'(\d{1,3})\s*(?:years?)\s*(?:old)?',
        r'(?:age|aged)?\s*(\d{1,3})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            age = int(match.group(1))
            if 1 <= age <= 120:  # Reasonable age range
                return age
    
    return None


def format_health_response(response: str, language: str = "en") -> str:
    """Format health response based on language and context"""
    
    # Add appropriate greetings based on language
    greetings = {
        "en": "Hello! ",
        "hi": "नमस्ते! ",
        "ta": "வணக்கம்! ",
        "te": "నమస్కారం! ",
        "bn": "নমস্কার! ",
        "gu": "નમસ્તે! ",
        "mr": "नमस्कार! ",
        "ml": "നമസ്കാരം! ",
        "kn": "ನಮಸ್ಕಾರ! ",
        "pa": "ਸਤ ਸ੍ਰੀ ਅਕਾਲ! "
    }
    
    greeting = greetings.get(language, "")
    
    # Add disclaimer for health advice
    disclaimers = {
        "en": "\n\n⚠️ This is general health information. Please consult a healthcare professional for medical advice.",
        "hi": "\n\n⚠️ यह सामान्य स्वास्थ्य जानकारी है। चिकित्सा सलाह के लिए कृपया डॉक्टर से संपर्क करें।",
        # Add more languages as needed
    }
    
    disclaimer = disclaimers.get(language, disclaimers["en"])
    
    # Format the complete response
    if not response.startswith(greeting.strip()):
        response = greeting + response
    
    response += disclaimer
    
    return response


def calculate_urgency_score(symptoms: List[str]) -> float:
    """Calculate urgency score based on symptoms"""
    # Define severity weights for different symptoms
    symptom_weights = {
        # Critical symptoms (weight: 1.0)
        'chest pain': 1.0,
        'difficulty breathing': 1.0,
        'severe bleeding': 1.0,
        'loss of consciousness': 1.0,
        'severe allergic reaction': 1.0,
        
        # High priority symptoms (weight: 0.8)
        'severe fever': 0.8,
        'severe headache': 0.8,
        'severe abdominal pain': 0.8,
        'persistent vomiting': 0.8,
        
        # Moderate symptoms (weight: 0.6)
        'fever': 0.6,
        'persistent cough': 0.6,
        'nausea': 0.6,
        'dizziness': 0.6,
        
        # Mild symptoms (weight: 0.3)
        'headache': 0.3,
        'runny nose': 0.3,
        'sore throat': 0.3,
        'mild cough': 0.3,
    }
    
    total_weight = 0.0
    matched_symptoms = 0
    
    for symptom in symptoms:
        symptom_lower = symptom.lower().strip()
        
        # Check for exact matches
        if symptom_lower in symptom_weights:
            total_weight += symptom_weights[symptom_lower]
            matched_symptoms += 1
        else:
            # Check for partial matches
            for key_symptom, weight in symptom_weights.items():
                if key_symptom in symptom_lower or symptom_lower in key_symptom:
                    total_weight += weight
                    matched_symptoms += 1
                    break
    
    # Normalize the score
    if matched_symptoms == 0:
        return 0.3  # Default low urgency
    
    average_weight = total_weight / matched_symptoms
    
    # Account for multiple symptoms (increases urgency)
    multiplier = min(1.2, 1.0 + (matched_symptoms - 1) * 0.05)
    
    return min(1.0, average_weight * multiplier)


def format_vaccination_reminder(vaccine_name: str, due_date: str, language: str = "en") -> str:
    """Format vaccination reminder message"""
    templates = {
        "en": f"💉 Vaccination Reminder\n\nVaccine: {vaccine_name}\nDue Date: {due_date}\n\nPlease schedule your appointment with a healthcare provider.",
        "hi": f"💉 टीकाकरण अनुस्मारक\n\nटीका: {vaccine_name}\nनियत तारीख: {due_date}\n\nकृपया अपने डॉक्टर से अपॉइंटमेंट लें।"
    }
    
    return templates.get(language, templates["en"])


def parse_date_from_text(text: str) -> Optional[datetime]:
    """Parse date from natural language text"""
    # This is a simplified version - in production, use a proper date parsing library
    today = datetime.now()
    
    if "today" in text.lower():
        return today
    elif "tomorrow" in text.lower():
        return today + timedelta(days=1)
    elif "yesterday" in text.lower():
        return today - timedelta(days=1)
    
    # Look for date patterns like "2023-12-25", "25/12/2023", etc.
    date_patterns = [
        r'(\d{4})-(\d{1,2})-(\d{1,2})',
        r'(\d{1,2})/(\d{1,2})/(\d{4})',
        r'(\d{1,2})-(\d{1,2})-(\d{4})'
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            try:
                if pattern == date_patterns[0]:  # YYYY-MM-DD
                    year, month, day = map(int, match.groups())
                else:  # DD/MM/YYYY or DD-MM-YYYY
                    day, month, year = map(int, match.groups())
                
                return datetime(year, month, day)
            except ValueError:
                continue
    
    return None


def get_language_name(language_code: str) -> str:
    """Get full language name from code"""
    language_names = {
        "en": "English",
        "hi": "हिन्दी (Hindi)",
        "ta": "தமிழ் (Tamil)",
        "te": "తెలుగు (Telugu)",
        "bn": "বাংলা (Bengali)",
        "gu": "ગુજરાતી (Gujarati)",
        "mr": "मराठी (Marathi)",
        "ml": "മലയാളം (Malayalam)",
        "kn": "ಕನ್ನಡ (Kannada)",
        "pa": "ਪੰਜਾਬੀ (Punjabi)"
    }
    
    return language_names.get(language_code, "Unknown")


def is_emergency_keyword(text: str) -> bool:
    """Check if text contains emergency keywords"""
    emergency_keywords = [
        "emergency", "urgent", "help", "critical", "serious",
        "ambulance", "hospital", "doctor", "pain", "bleeding",
        "unconscious", "breathing", "heart attack", "stroke",
        # Hindi emergency keywords
        "आपातकाल", "तुरंत", "मदद", "गंभीर", "दर्द",
        # Add more languages as needed
    ]
    
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in emergency_keywords)