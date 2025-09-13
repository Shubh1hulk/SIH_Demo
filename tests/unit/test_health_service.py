"""
Unit tests for the Health Service
"""

import pytest
import asyncio
from app.services.health_service import HealthService
from app.models.api_models import HealthAssessmentRequest, SeverityEnum


class TestHealthService:
    
    @pytest.fixture
    async def health_service(self):
        service = HealthService()
        await service.initialize()
        return service
    
    @pytest.mark.asyncio
    async def test_symptom_assessment_normal(self, health_service):
        """Test normal symptom assessment"""
        request = HealthAssessmentRequest(
            symptoms=["mild fever", "runny nose"],
            age=30,
            gender="male"
        )
        
        response = await health_service.assess_symptoms(request)
        
        assert response.urgency_level in [SeverityEnum.LOW, SeverityEnum.MODERATE]
        assert len(response.recommendations) > 0
        assert len(response.next_steps) > 0
        assert response.disclaimer is not None
    
    @pytest.mark.asyncio
    async def test_symptom_assessment_emergency(self, health_service):
        """Test emergency symptom assessment"""
        request = HealthAssessmentRequest(
            symptoms=["severe chest pain", "difficulty breathing"],
            age=45,
            gender="female"
        )
        
        response = await health_service.assess_symptoms(request)
        
        assert response.urgency_level == SeverityEnum.CRITICAL
        assert any("immediate" in rec.lower() for rec in response.recommendations)
        assert any("108" in step for step in response.next_steps)
    
    @pytest.mark.asyncio
    async def test_vaccination_schedule(self, health_service):
        """Test vaccination schedule retrieval"""
        vaccines = await health_service.get_vaccination_schedule()
        
        assert isinstance(vaccines, list)
        assert len(vaccines) > 0
        
        # Test specific age group filtering
        adult_vaccines = await health_service.get_vaccination_schedule("18+")
        assert isinstance(adult_vaccines, list)
    
    @pytest.mark.asyncio
    async def test_outbreak_alerts(self, health_service):
        """Test disease outbreak alerts"""
        outbreaks = await health_service.get_active_outbreaks()
        assert isinstance(outbreaks, list)
        
        # Test location-specific outbreaks
        mumbai_outbreaks = await health_service.get_active_outbreaks("Mumbai")
        assert isinstance(mumbai_outbreaks, list)
    
    def test_urgency_determination(self):
        """Test urgency level determination"""
        service = HealthService()
        
        # Test high urgency symptoms
        high_urgency = service._determine_urgency(
            ["severe chest pain", "difficulty breathing"], 
            []
        )
        assert high_urgency == SeverityEnum.HIGH
        
        # Test moderate urgency symptoms
        moderate_urgency = service._determine_urgency(
            ["fever", "persistent cough"], 
            []
        )
        assert moderate_urgency == SeverityEnum.MODERATE
        
        # Test low urgency symptoms
        low_urgency = service._determine_urgency(
            ["mild headache"], 
            []
        )
        assert low_urgency == SeverityEnum.LOW
    
    def test_is_ready(self):
        """Test service readiness check"""
        service = HealthService()
        assert not service.is_ready()  # Before initialization