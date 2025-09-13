"""
AI Service for processing healthcare queries and generating responses
"""

import os
import openai
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json
from models import HealthInfo, Conversation
from services.translation_service import TranslationService

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)

class AIService:
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        self.translation_service = TranslationService()
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        self.intent_keywords = self._load_intent_keywords()
        
    def _load_intent_keywords(self):
        """Load intent classification keywords"""
        return {
            'symptoms': ['fever', 'cough', 'headache', 'pain', 'nausea', 'vomiting', 'diarrhea', 'rash', 'dizzy', 'tired', 'weak'],
            'preventive': ['prevention', 'avoid', 'protect', 'hygiene', 'diet', 'exercise', 'healthy', 'wellness'],
            'vaccination': ['vaccine', 'vaccination', 'immunization', 'shot', 'dose', 'schedule'],
            'emergency': ['emergency', 'urgent', 'serious', 'critical', 'hospital', 'ambulance', 'help'],
            'medication': ['medicine', 'drug', 'tablet', 'prescription', 'treatment', 'cure']
        }
    
    def detect_intent(self, text):
        """Detect the intent of the user's message"""
        text_lower = text.lower()
        intent_scores = {}
        
        for intent, keywords in self.intent_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                intent_scores[intent] = score
        
        if intent_scores:
            detected_intent = max(intent_scores, key=intent_scores.get)
            confidence = intent_scores[detected_intent] / len(text.split())
            return detected_intent, min(confidence, 1.0)
        
        return 'general', 0.5
    
    def find_relevant_health_info(self, query, language='en', category=None):
        """Find relevant health information from the database"""
        from models import HealthInfo
        
        # Get health information from database
        query_filter = HealthInfo.query.filter_by(language=language)
        if category:
            query_filter = query_filter.filter_by(category=category)
        
        health_infos = query_filter.all()
        
        if not health_infos:
            return None
        
        # Calculate similarity scores
        documents = [info.content for info in health_infos]
        documents.append(query)
        
        try:
            tfidf_matrix = self.vectorizer.fit_transform(documents)
            query_vector = tfidf_matrix[-1]
            doc_vectors = tfidf_matrix[:-1]
            
            similarities = cosine_similarity(query_vector, doc_vectors).flatten()
            best_match_idx = np.argmax(similarities)
            
            if similarities[best_match_idx] > 0.1:  # Threshold for relevance
                return health_infos[best_match_idx]
        except Exception as e:
            print(f"Error in similarity calculation: {e}")
        
        return None
    
    def generate_ai_response(self, query, intent, language='en'):
        """Generate AI response using OpenAI GPT"""
        if not self.openai_api_key:
            return self._generate_template_response(query, intent, language)
        
        try:
            system_prompt = f"""You are a healthcare AI assistant for rural populations. 
            Provide accurate, helpful information about health topics. 
            Keep responses simple and actionable. 
            Always recommend consulting healthcare professionals for serious issues.
            Respond in {language} language if it's not English."""
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return self._generate_template_response(query, intent, language)
    
    def _generate_template_response(self, query, intent, language='en'):
        """Generate template response when OpenAI is not available"""
        templates = {
            'en': {
                'symptoms': "I understand you're asking about symptoms. For any concerning symptoms, please consult a healthcare professional. Common symptoms like fever can be managed with rest and hydration.",
                'preventive': "For preventive health, maintain good hygiene, eat a balanced diet, exercise regularly, and get adequate sleep. Regular health checkups are also important.",
                'vaccination': "Vaccination schedules vary by age. Please consult your local health center for personalized vaccination information and schedules.",
                'emergency': "For medical emergencies, please contact your local emergency services or visit the nearest hospital immediately.",
                'general': "Thank you for your health query. For specific medical advice, please consult with a qualified healthcare professional."
            },
            'hi': {
                'symptoms': "मैं समझता हूं कि आप लक्षणों के बारे में पूछ रहे हैं। किसी भी चिंताजनक लक्षण के लिए कृपया स्वास्थ्य पेशेवर से सलाह लें।",
                'preventive': "निवारक स्वास्थ्य के लिए अच्छी स्वच्छता बनाए रखें, संतुलित आहार लें, नियमित व्यायाम करें और पर्याप्त नींद लें।",
                'vaccination': "टीकाकरण की अनुसूची उम्र के अनुसार अलग होती है। व्यक्तिगत टीकाकरण जानकारी के लिए अपने स्थानीय स्वास्थ्य केंद्र से संपर्क करें।",
                'emergency': "चिकित्सा आपातकाल के लिए कृपया अपनी स्थानीय आपातकालीन सेवाओं से संपर्क करें या तुरंत निकटतम अस्पताल जाएं।",
                'general': "आपके स्वास्थ्य प्रश्न के लिए धन्यवाद। विशिष्ट चिकित्सा सलाह के लिए कृपया योग्य स्वास्थ्य पेशेवर से सलाह लें।"
            }
        }
        
        lang_templates = templates.get(language, templates['en'])
        return lang_templates.get(intent, lang_templates['general'])
    
    def process_health_query(self, user_message, user_language='en', user_id=None):
        """Process a complete health query and return response"""
        from models import db, Conversation
        
        # Translate to English for processing if needed
        english_message = user_message
        if user_language != 'en':
            english_message = self.translation_service.translate(user_message, 'en', user_language)
        
        # Detect intent
        intent, confidence = self.detect_intent(english_message)
        
        # Find relevant information
        relevant_info = self.find_relevant_health_info(english_message, user_language, intent)
        
        # Generate response
        if relevant_info:
            response = relevant_info.content
        else:
            response = self.generate_ai_response(english_message, intent, user_language)
        
        # Log conversation
        if user_id:
            conversation = Conversation(
                user_id=user_id,
                message_text=user_message,
                response_text=response,
                intent_detected=intent,
                confidence_score=confidence
            )
            db.session.add(conversation)
            db.session.commit()
        
        return {
            'response': response,
            'intent': intent,
            'confidence': confidence,
            'language': user_language
        }