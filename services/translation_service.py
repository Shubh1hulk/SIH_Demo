"""
Translation Service for multilingual support
"""

from googletrans import Translator
import json
import os

class TranslationService:
    def __init__(self):
        self.translator = Translator()
        self.supported_languages = {
            'en': 'English',
            'hi': 'Hindi',
            'bn': 'Bengali',
            'te': 'Telugu',
            'ta': 'Tamil',
            'gu': 'Gujarati',
            'mr': 'Marathi',
            'kn': 'Kannada',
            'ml': 'Malayalam',
            'or': 'Odia',
            'pa': 'Punjabi',
            'ur': 'Urdu'
        }
        self.common_phrases = self._load_common_phrases()
    
    def _load_common_phrases(self):
        """Load common healthcare phrases for better translation accuracy"""
        return {
            'en': {
                'greeting': 'Hello! I can help you with health information.',
                'help': 'You can ask me about symptoms, prevention, vaccinations, or health emergencies.',
                'goodbye': 'Take care of your health! Consult a doctor for serious concerns.',
                'disclaimer': 'This is general health information. Please consult a healthcare professional for medical advice.'
            },
            'hi': {
                'greeting': 'नमस्ते! मैं आपको स्वास्थ्य जानकारी में मदद कर सकता हूं।',
                'help': 'आप मुझसे लक्षण, बचाव, टीकाकरण या स्वास्थ्य आपातकाल के बारे में पूछ सकते हैं।',
                'goodbye': 'अपने स्वास्थ्य का ख्याल रखें! गंभीर समस्याओं के लिए डॉक्टर से सलाह लें।',
                'disclaimer': 'यह सामान्य स्वास्थ्य जानकारी है। चिकित्सा सलाह के लिए कृपया स्वास्थ्य पेशेवर से सलाह लें।'
            }
        }
    
    def detect_language(self, text):
        """Detect the language of the input text"""
        try:
            detection = self.translator.detect(text)
            detected_lang = detection.lang
            
            # Map to supported languages
            if detected_lang in self.supported_languages:
                return detected_lang
            else:
                # Default to English if not supported
                return 'en'
        except Exception as e:
            print(f"Language detection error: {e}")
            return 'en'
    
    def translate(self, text, target_language, source_language=None):
        """Translate text to target language"""
        try:
            # Auto-detect source language if not provided
            if source_language is None:
                source_language = self.detect_language(text)
            
            # Return original text if target language is same as source
            if source_language == target_language:
                return text
            
            # Check if target language is supported
            if target_language not in self.supported_languages:
                print(f"Unsupported target language: {target_language}")
                return text
            
            # Perform translation
            translation = self.translator.translate(
                text, 
                src=source_language, 
                dest=target_language
            )
            
            return translation.text
            
        except Exception as e:
            print(f"Translation error: {e}")
            return text
    
    def get_common_phrase(self, phrase_key, language='en'):
        """Get a common phrase in the specified language"""
        lang_phrases = self.common_phrases.get(language, self.common_phrases['en'])
        return lang_phrases.get(phrase_key, '')
    
    def get_supported_languages(self):
        """Get list of supported languages"""
        return self.supported_languages
    
    def is_language_supported(self, language_code):
        """Check if a language is supported"""
        return language_code in self.supported_languages
    
    def translate_health_content(self, content_dict, target_language):
        """Translate healthcare content preserving structure"""
        try:
            if not isinstance(content_dict, dict):
                return self.translate(str(content_dict), target_language)
            
            translated_dict = {}
            for key, value in content_dict.items():
                if isinstance(value, str):
                    translated_dict[key] = self.translate(value, target_language)
                elif isinstance(value, dict):
                    translated_dict[key] = self.translate_health_content(value, target_language)
                elif isinstance(value, list):
                    translated_dict[key] = [
                        self.translate(item, target_language) if isinstance(item, str) 
                        else item for item in value
                    ]
                else:
                    translated_dict[key] = value
            
            return translated_dict
            
        except Exception as e:
            print(f"Content translation error: {e}")
            return content_dict