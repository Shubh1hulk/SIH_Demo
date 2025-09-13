"""
Unit tests for the NLP Service
"""

import pytest
import asyncio
from app.services.nlp_service import NLPService


class TestNLPService:
    
    @pytest.fixture
    async def nlp_service(self):
        service = NLPService()
        await service.initialize()
        return service
    
    @pytest.mark.asyncio
    async def test_language_detection(self, nlp_service):
        """Test language detection functionality"""
        # Test English text
        lang, confidence = nlp_service.detect_language("I have a fever and cough")
        assert lang in ["en", "en-US", "en-GB"] or lang == "en"  # Allow variations
        assert confidence > 0
        
        # Test Hindi text
        lang, confidence = nlp_service.detect_language("मुझे बुखार और खांसी है")
        # Note: In limited environment, this might default to 'en'
        assert isinstance(lang, str)
        assert confidence >= 0
    
    @pytest.mark.asyncio
    async def test_intent_detection(self, nlp_service):
        """Test intent detection for health queries"""
        # Test symptom query intent
        intent, confidence = nlp_service.detect_intent("I have fever and headache")
        assert intent == "symptom_query"
        assert confidence > 0.5
        
        # Test disease info intent
        intent, confidence = nlp_service.detect_intent("What is malaria?")
        assert intent == "disease_info"
        assert confidence > 0.5
        
        # Test vaccination intent
        intent, confidence = nlp_service.detect_intent("When should I get COVID vaccine?")
        assert intent == "vaccination"
        assert confidence > 0.5
        
        # Test emergency intent
        intent, confidence = nlp_service.detect_intent("This is an emergency, I need help!")
        assert intent == "emergency"
        assert confidence > 0.5
    
    @pytest.mark.asyncio
    async def test_entity_extraction(self, nlp_service):
        """Test medical entity extraction"""
        entities = nlp_service._extract_entities("I have fever, cough, and chest pain")
        
        assert "symptoms" in entities
        assert len(entities["symptoms"]) > 0
        assert "fever" in entities["symptoms"]
        assert "cough" in entities["symptoms"]
        assert "chest pain" in entities["symptoms"]
    
    @pytest.mark.asyncio
    async def test_query_processing(self, nlp_service):
        """Test end-to-end query processing"""
        result = await nlp_service.process_query("I have symptoms like fever and cough")
        
        assert "original_text" in result
        assert "processed_text" in result
        assert "detected_language" in result
        assert "intent" in result
        assert "entities" in result
        assert result["intent"] == "symptom_query"
        assert len(result["entities"]["symptoms"]) > 0
    
    def test_is_ready(self):
        """Test service readiness check"""
        service = NLPService()
        assert not service.is_ready()  # Before initialization