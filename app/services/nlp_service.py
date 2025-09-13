"""
NLP Service for multilingual healthcare chatbot
Handles language detection, translation, and intent recognition
"""

import asyncio
from typing import Dict, List, Optional, Tuple
import json
import re
from googletrans import Translator
from loguru import logger
from app.core.config import settings
from app.models.api_models import LanguageEnum


class NLPService:
    """Natural Language Processing service for healthcare chatbot"""
    
    def __init__(self):
        self.translator = Translator()
        self.is_initialized = False
        self.supported_languages = settings.supported_languages_list
        
        # Healthcare-specific intent patterns
        self.intent_patterns = {
            "symptom_query": [
                r"(?i).*(?:symptoms?|signs?|feeling|pain|hurt|ache|fever|cough|cold)",
                r"(?i).*(?:बुखार|खांसी|दर्द|बीमारी|लक्षण)",  # Hindi
                r"(?i).*(?:காய்ச்சல்|இருமல்|வலி|அறிகுறி)",  # Tamil
            ],
            "disease_info": [
                r"(?i).*(?:what is|tell me about|information about|disease|illness|condition)",
                r"(?i).*(?:क्या है|बारे में|बीमारी के बारे में)",  # Hindi
                r"(?i).*(?:என்ன|பற்றி|நோய்)",  # Tamil
            ],
            "vaccination": [
                r"(?i).*(?:vaccin|immun|shot|inject|schedule)",
                r"(?i).*(?:टीका|वैक्सीन|इंजेक्शन)",  # Hindi
                r"(?i).*(?:தடுப்பூசி|ஊசி)",  # Tamil
            ],
            "prevention": [
                r"(?i).*(?:prevent|avoid|protect|precaution|safety)",
                r"(?i).*(?:बचाव|सुरक्षा|बचना)",  # Hindi
                r"(?i).*(?:தடுப்பு|பாதுகாப்பு)",  # Tamil
            ],
            "emergency": [
                r"(?i).*(?:emergency|urgent|severe|critical|help|serious)",
                r"(?i).*(?:आपातकाल|गंभीर|मदद|तुरंत)",  # Hindi
                r"(?i).*(?:அவசரம்|கடுமையான|உதவி)",  # Tamil
            ]
        }
        
        # Healthcare keywords for better context understanding
        self.health_keywords = {
            "en": [
                "fever", "cough", "headache", "pain", "nausea", "vomiting", "diarrhea",
                "diabetes", "hypertension", "covid", "malaria", "dengue", "tuberculosis",
                "vaccination", "medicine", "doctor", "hospital", "treatment"
            ],
            "hi": [
                "बुखार", "खांसी", "सिरदर्द", "दर्द", "उल्टी", "दस्त",
                "मधुमेह", "उच्च रक्तचाप", "कोविड", "मलेरिया", "डेंगू", "तपेदिक",
                "टीकाकरण", "दवा", "डॉक्टर", "अस्पताल", "इलाज"
            ],
            "ta": [
                "காய்ச்சல்", "இருமல்", "தலைவலி", "வலி", "வாந்தி", "வயிற்றுப்போக்கு",
                "நீரிழிவு", "உயர் இரத்த அழுத்தம்", "கோவிட்", "மலேரியா", "டெங்கு",
                "தடுப்பூசி", "மருந்து", "மருத்துவர்", "மருத்துவமனை", "சிகிச்சை"
            ]
        }
    
    async def initialize(self):
        """Initialize NLP models and services"""
        try:
            logger.info("Initializing NLP service...")
            
            # Test translator connection
            await self._test_translator()
            
            self.is_initialized = True
            logger.info("NLP service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize NLP service: {e}")
            raise
    
    async def _test_translator(self):
        """Test translator functionality"""
        try:
            # Test translation
            test_result = self.translator.translate("Hello", dest='hi')
            logger.info(f"Translator test successful: {test_result.text}")
        except Exception as e:
            logger.warning(f"Translator test failed: {e}, continuing with limited functionality")
    
    def detect_language(self, text: str) -> Tuple[str, float]:
        """
        Detect language of input text
        Returns: (language_code, confidence)
        """
        try:
            detection = self.translator.detect(text)
            language = detection.lang
            confidence = detection.confidence
            
            # Map detected language to supported languages
            if language not in self.supported_languages:
                # Default to English if language not supported
                language = "en"
                confidence = 0.5
            
            return language, confidence
            
        except Exception as e:
            logger.warning(f"Language detection failed: {e}")
            return "en", 0.5  # Default to English
    
    async def translate_text(self, text: str, target_lang: str = "en") -> str:
        """Translate text to target language"""
        try:
            if target_lang == "en":
                return text
            
            result = self.translator.translate(text, dest=target_lang)
            return result.text
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return text  # Return original text if translation fails
    
    def detect_intent(self, text: str, language: str = "en") -> Tuple[str, float]:
        """
        Detect user intent from text
        Returns: (intent, confidence)
        """
        text_lower = text.lower()
        best_intent = "general"
        max_confidence = 0.0
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    confidence = self._calculate_pattern_confidence(text, pattern, language)
                    if confidence > max_confidence:
                        max_confidence = confidence
                        best_intent = intent
        
        # Boost confidence if health-related keywords are present
        if language in self.health_keywords:
            health_keyword_count = sum(
                1 for keyword in self.health_keywords[language]
                if keyword in text_lower
            )
            if health_keyword_count > 0:
                max_confidence = min(1.0, max_confidence + (health_keyword_count * 0.1))
        
        return best_intent, max_confidence
    
    def _calculate_pattern_confidence(self, text: str, pattern: str, language: str) -> float:
        """Calculate confidence score for pattern match"""
        # Base confidence for pattern match
        base_confidence = 0.7
        
        # Boost confidence for health-related terms
        if language in self.health_keywords:
            health_terms = [kw for kw in self.health_keywords[language] if kw in text.lower()]
            health_boost = len(health_terms) * 0.05
            base_confidence = min(1.0, base_confidence + health_boost)
        
        return base_confidence
    
    async def process_query(self, text: str, user_language: str = "en") -> Dict:
        """
        Process user query and return structured response
        """
        try:
            # Detect language if not provided
            if user_language == "auto":
                detected_lang, lang_confidence = self.detect_language(text)
                user_language = detected_lang
            else:
                lang_confidence = 1.0
            
            # Translate to English for processing if needed
            english_text = text
            if user_language != "en":
                english_text = await self.translate_text(text, "en")
            
            # Detect intent
            intent, intent_confidence = self.detect_intent(english_text, user_language)
            
            # Extract entities (symptoms, diseases, etc.)
            entities = self._extract_entities(english_text)
            
            return {
                "original_text": text,
                "processed_text": english_text,
                "detected_language": user_language,
                "language_confidence": lang_confidence,
                "intent": intent,
                "intent_confidence": intent_confidence,
                "entities": entities
            }
            
        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            return {
                "original_text": text,
                "processed_text": text,
                "detected_language": user_language,
                "language_confidence": 0.5,
                "intent": "general",
                "intent_confidence": 0.5,
                "entities": {}
            }
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract medical entities from text"""
        entities = {
            "symptoms": [],
            "diseases": [],
            "body_parts": [],
            "medications": []
        }
        
        text_lower = text.lower()
        
        # Common symptoms
        symptom_keywords = [
            "fever", "cough", "headache", "pain", "nausea", "vomiting", "diarrhea",
            "fatigue", "weakness", "dizziness", "shortness of breath", "chest pain"
        ]
        
        # Common diseases
        disease_keywords = [
            "covid", "coronavirus", "flu", "malaria", "dengue", "tuberculosis", "diabetes",
            "hypertension", "pneumonia", "bronchitis", "asthma"
        ]
        
        # Body parts
        body_part_keywords = [
            "head", "chest", "stomach", "abdomen", "throat", "nose", "ear", "eye",
            "back", "leg", "arm", "hand", "foot"
        ]
        
        # Extract entities based on keywords
        for symptom in symptom_keywords:
            if symptom in text_lower:
                entities["symptoms"].append(symptom)
        
        for disease in disease_keywords:
            if disease in text_lower:
                entities["diseases"].append(disease)
        
        for body_part in body_part_keywords:
            if body_part in text_lower:
                entities["body_parts"].append(body_part)
        
        return entities
    
    def is_ready(self) -> bool:
        """Check if NLP service is ready"""
        return self.is_initialized
    
    async def cleanup(self):
        """Cleanup NLP resources"""
        logger.info("Cleaning up NLP service...")
        self.is_initialized = False