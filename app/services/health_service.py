"""
Health Service for managing healthcare information and queries
"""

from typing import List, Dict, Optional, Any
import json
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.core.database import get_db
from app.models.database_models import (
    HealthKnowledge, Disease, Symptom, VaccinationSchedule, 
    DiseaseOutbreak, User, Conversation
)
from app.models.api_models import (
    DiseaseInfo, SymptomInfo, VaccinationInfo, OutbreakAlert,
    HealthAssessmentRequest, HealthAssessmentResponse, SeverityEnum
)
from loguru import logger
import requests
from app.core.config import settings


class HealthService:
    """Service for managing healthcare information and assessments"""
    
    def __init__(self):
        self.is_initialized = False
        self.government_api_base = settings.GOVERNMENT_HEALTH_API_URL
        self.api_key = settings.GOVERNMENT_HEALTH_API_KEY
        
        # Initialize health knowledge base
        self.symptom_disease_mapping = {}
        self.emergency_symptoms = [
            "severe chest pain", "difficulty breathing", "severe bleeding",
            "loss of consciousness", "severe allergic reaction", "stroke symptoms",
            "heart attack symptoms", "severe burns", "poisoning"
        ]
    
    async def initialize(self):
        """Initialize health service with knowledge base"""
        try:
            logger.info("Initializing Health service...")
            
            # Load health knowledge from database
            await self._load_health_knowledge()
            
            self.is_initialized = True
            logger.info("Health service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Health service: {e}")
            raise
    
    async def _load_health_knowledge(self):
        """Load health knowledge base from database"""
        try:
            # Initialize with basic health data if database is empty
            await self._initialize_basic_health_data()
            
        except Exception as e:
            logger.warning(f"Failed to load health knowledge: {e}")
    
    async def _initialize_basic_health_data(self):
        """Initialize database with basic health information"""
        try:
            # Sample diseases data
            basic_diseases = [
                {
                    "name": "Common Cold",
                    "description": "A viral infection of the upper respiratory tract",
                    "symptoms": ["runny nose", "cough", "sneezing", "sore throat", "mild fever"],
                    "prevention": "Wash hands frequently, avoid close contact with sick people",
                    "treatment": "Rest, fluids, over-the-counter medications for symptom relief",
                    "severity_level": "low"
                },
                {
                    "name": "COVID-19",
                    "description": "Infectious disease caused by the SARS-CoV-2 virus",
                    "symptoms": ["fever", "cough", "fatigue", "loss of taste or smell", "difficulty breathing"],
                    "prevention": "Vaccination, mask wearing, social distancing, hand hygiene",
                    "treatment": "Supportive care, antiviral medications in severe cases",
                    "severity_level": "moderate"
                },
                {
                    "name": "Malaria",
                    "description": "Mosquito-borne infectious disease",
                    "symptoms": ["fever", "chills", "sweating", "headache", "nausea", "vomiting"],
                    "prevention": "Use mosquito nets, antimalarial medications, eliminate standing water",
                    "treatment": "Antimalarial medications as prescribed by healthcare provider",
                    "severity_level": "high"
                }
            ]
            
            # Sample vaccination schedules
            basic_vaccines = [
                {
                    "vaccine_name": "COVID-19 Vaccine",
                    "age_group": "18+ years",
                    "schedule_description": "Two doses, 4-12 weeks apart, with boosters as recommended",
                    "doses_required": 2,
                    "interval_days": 28
                },
                {
                    "vaccine_name": "Hepatitis B",
                    "age_group": "Infants",
                    "schedule_description": "Birth, 1-2 months, 6-18 months",
                    "doses_required": 3,
                    "interval_days": 30
                }
            ]
            
            # This would normally be populated from database initialization
            logger.info("Basic health data loaded")
            
        except Exception as e:
            logger.error(f"Failed to initialize basic health data: {e}")
    
    async def assess_symptoms(self, request: HealthAssessmentRequest) -> HealthAssessmentResponse:
        """Assess symptoms and provide health recommendations"""
        try:
            symptoms = [s.lower() for s in request.symptoms]
            
            # Check for emergency symptoms
            emergency_detected = any(
                emergency_symptom.lower() in ' '.join(symptoms)
                for emergency_symptom in self.emergency_symptoms
            )
            
            if emergency_detected:
                return HealthAssessmentResponse(
                    possible_conditions=[],
                    urgency_level=SeverityEnum.CRITICAL,
                    recommendations=[
                        "Seek immediate medical attention",
                        "Call emergency services if necessary",
                        "Do not delay medical care"
                    ],
                    next_steps=[
                        "Contact emergency services: 108",
                        "Go to nearest hospital emergency room",
                        "Have someone accompany you if possible"
                    ],
                    disclaimer="This is an emergency situation. Seek immediate medical care."
                )
            
            # Analyze symptoms for possible conditions
            possible_conditions = await self._analyze_symptoms(symptoms)
            
            # Determine urgency level
            urgency_level = self._determine_urgency(symptoms, possible_conditions)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(symptoms, urgency_level)
            
            # Generate next steps
            next_steps = self._generate_next_steps(urgency_level)
            
            return HealthAssessmentResponse(
                possible_conditions=possible_conditions,
                urgency_level=urgency_level,
                recommendations=recommendations,
                next_steps=next_steps,
                disclaimer="This assessment is for informational purposes only and does not replace professional medical advice."
            )
            
        except Exception as e:
            logger.error(f"Symptom assessment failed: {e}")
            raise
    
    async def _analyze_symptoms(self, symptoms: List[str]) -> List[DiseaseInfo]:
        """Analyze symptoms to identify possible conditions"""
        possible_conditions = []
        
        # Sample analysis - in production, this would use ML models
        symptom_set = set(symptoms)
        
        # COVID-19 symptoms
        covid_symptoms = {"fever", "cough", "fatigue", "loss of taste", "loss of smell", "difficulty breathing"}
        if len(symptom_set.intersection(covid_symptoms)) >= 2:
            possible_conditions.append(DiseaseInfo(
                id=2,
                name="COVID-19",
                description="Infectious disease caused by the SARS-CoV-2 virus",
                symptoms=["fever", "cough", "fatigue", "loss of taste or smell"],
                prevention="Vaccination, mask wearing, social distancing",
                treatment="Supportive care, consult healthcare provider",
                severity_level=SeverityEnum.MODERATE
            ))
        
        # Common cold symptoms
        cold_symptoms = {"runny nose", "cough", "sneezing", "sore throat", "mild fever"}
        if len(symptom_set.intersection(cold_symptoms)) >= 2:
            possible_conditions.append(DiseaseInfo(
                id=1,
                name="Common Cold",
                description="Viral infection of the upper respiratory tract",
                symptoms=["runny nose", "cough", "sneezing", "sore throat"],
                prevention="Hand hygiene, avoid close contact with sick people",
                treatment="Rest, fluids, symptom relief medications",
                severity_level=SeverityEnum.LOW
            ))
        
        # Malaria symptoms
        malaria_symptoms = {"fever", "chills", "sweating", "headache", "nausea", "vomiting"}
        if len(symptom_set.intersection(malaria_symptoms)) >= 3:
            possible_conditions.append(DiseaseInfo(
                id=3,
                name="Malaria",
                description="Mosquito-borne infectious disease",
                symptoms=["fever", "chills", "sweating", "headache", "nausea"],
                prevention="Use mosquito nets, eliminate standing water",
                treatment="Antimalarial medications - consult healthcare provider",
                severity_level=SeverityEnum.HIGH
            ))
        
        return possible_conditions
    
    def _determine_urgency(self, symptoms: List[str], conditions: List[DiseaseInfo]) -> SeverityEnum:
        """Determine urgency level based on symptoms and conditions"""
        
        # High-priority symptoms
        high_priority = {"difficulty breathing", "severe chest pain", "severe fever", "severe bleeding"}
        moderate_priority = {"fever", "persistent cough", "severe headache", "vomiting"}
        
        symptom_set = set(' '.join(symptoms).lower().split())
        
        if any(hp in ' '.join(symptoms).lower() for hp in high_priority):
            return SeverityEnum.HIGH
        elif any(mp in ' '.join(symptoms).lower() for mp in moderate_priority):
            return SeverityEnum.MODERATE
        else:
            return SeverityEnum.LOW
    
    def _generate_recommendations(self, symptoms: List[str], urgency: SeverityEnum) -> List[str]:
        """Generate health recommendations based on symptoms and urgency"""
        recommendations = [
            "Monitor your symptoms closely",
            "Stay hydrated and get adequate rest",
            "Maintain good hygiene practices"
        ]
        
        if urgency == SeverityEnum.HIGH:
            recommendations = [
                "Seek medical attention promptly",
                "Monitor symptoms closely",
                "Have someone stay with you if possible",
                "Keep emergency contacts readily available"
            ]
        elif urgency == SeverityEnum.MODERATE:
            recommendations.extend([
                "Consider consulting a healthcare provider",
                "Isolate if symptoms suggest infectious illness",
                "Take over-the-counter medications for symptom relief if appropriate"
            ])
        else:
            recommendations.extend([
                "Continue home care measures",
                "Seek medical care if symptoms worsen or persist"
            ])
        
        return recommendations
    
    def _generate_next_steps(self, urgency: SeverityEnum) -> List[str]:
        """Generate next steps based on urgency level"""
        if urgency == SeverityEnum.CRITICAL:
            return [
                "Call emergency services: 108",
                "Go to nearest hospital emergency room immediately",
                "Do not drive yourself - have someone else drive or call ambulance"
            ]
        elif urgency == SeverityEnum.HIGH:
            return [
                "Contact your healthcare provider within 24 hours",
                "Go to urgent care or hospital if provider unavailable",
                "Keep monitoring symptoms"
            ]
        elif urgency == SeverityEnum.MODERATE:
            return [
                "Schedule appointment with healthcare provider",
                "Continue monitoring symptoms",
                "Call provider if symptoms worsen"
            ]
        else:
            return [
                "Continue home care",
                "Monitor symptoms for 2-3 days",
                "Consult healthcare provider if no improvement"
            ]
    
    async def get_disease_info(self, disease_name: str) -> Optional[DiseaseInfo]:
        """Get information about a specific disease"""
        # This would query the database in a real implementation
        return None
    
    async def get_vaccination_schedule(self, age_group: str = None) -> List[VaccinationInfo]:
        """Get vaccination schedule information"""
        # Sample vaccination data
        vaccines = [
            VaccinationInfo(
                id=1,
                vaccine_name="COVID-19 Vaccine",
                age_group="18+ years",
                schedule_description="Two doses, 4-12 weeks apart",
                doses_required=2,
                interval_days=28
            ),
            VaccinationInfo(
                id=2,
                vaccine_name="Influenza Vaccine",
                age_group="6+ months",
                schedule_description="Annual vaccination",
                doses_required=1,
                interval_days=365
            )
        ]
        
        if age_group:
            return [v for v in vaccines if age_group.lower() in v.age_group.lower()]
        return vaccines
    
    async def get_active_outbreaks(self, location: str = None) -> List[OutbreakAlert]:
        """Get active disease outbreaks"""
        # This would integrate with government APIs in production
        sample_outbreaks = []
        
        # Try to fetch from government API
        try:
            if self.government_api_base and self.api_key:
                # This would make actual API calls to government health systems
                pass
        except Exception as e:
            logger.warning(f"Failed to fetch outbreak data from government API: {e}")
        
        return sample_outbreaks
    
    def is_ready(self) -> bool:
        """Check if health service is ready"""
        return self.is_initialized
    
    async def cleanup(self):
        """Cleanup health service resources"""
        logger.info("Cleaning up Health service...")
        self.is_initialized = False