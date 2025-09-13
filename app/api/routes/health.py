"""
Health information API routes
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from loguru import logger

from app.models.api_models import (
    DiseaseInfo, SymptomInfo, VaccinationInfo, APIResponse
)
from app.services.health_service import HealthService
from main import get_health_service

router = APIRouter()


@router.get("/diseases", response_model=List[DiseaseInfo])
async def get_diseases(
    search: Optional[str] = Query(None, description="Search term for diseases"),
    health_service: HealthService = Depends(get_health_service)
):
    """Get information about diseases"""
    try:
        # Sample disease data
        diseases = [
            DiseaseInfo(
                id=1,
                name="Common Cold",
                description="A viral infection of the upper respiratory tract",
                symptoms=["runny nose", "cough", "sneezing", "sore throat", "mild fever"],
                prevention="Wash hands frequently, avoid close contact with sick people",
                treatment="Rest, fluids, over-the-counter medications for symptom relief",
                severity_level="low"
            ),
            DiseaseInfo(
                id=2,
                name="COVID-19",
                description="Infectious disease caused by the SARS-CoV-2 virus",
                symptoms=["fever", "cough", "fatigue", "loss of taste or smell", "difficulty breathing"],
                prevention="Vaccination, mask wearing, social distancing, hand hygiene",
                treatment="Supportive care, antiviral medications in severe cases",
                severity_level="moderate"
            ),
            DiseaseInfo(
                id=3,
                name="Malaria",
                description="Mosquito-borne infectious disease",
                symptoms=["fever", "chills", "sweating", "headache", "nausea", "vomiting"],
                prevention="Use mosquito nets, antimalarial medications, eliminate standing water",
                treatment="Antimalarial medications as prescribed by healthcare provider",
                severity_level="high"
            )
        ]
        
        # Filter by search term if provided
        if search:
            search_lower = search.lower()
            diseases = [
                d for d in diseases 
                if search_lower in d.name.lower() or search_lower in d.description.lower()
            ]
        
        return diseases
        
    except Exception as e:
        logger.error(f"Error retrieving diseases: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve disease information")


@router.get("/diseases/{disease_id}", response_model=DiseaseInfo)
async def get_disease(
    disease_id: int,
    health_service: HealthService = Depends(get_health_service)
):
    """Get information about a specific disease"""
    try:
        # Sample data - in production this would query the database
        diseases = {
            1: DiseaseInfo(
                id=1,
                name="Common Cold",
                description="A viral infection of the upper respiratory tract",
                symptoms=["runny nose", "cough", "sneezing", "sore throat", "mild fever"],
                prevention="Wash hands frequently, avoid close contact with sick people",
                treatment="Rest, fluids, over-the-counter medications for symptom relief",
                severity_level="low"
            ),
            2: DiseaseInfo(
                id=2,
                name="COVID-19",
                description="Infectious disease caused by the SARS-CoV-2 virus",
                symptoms=["fever", "cough", "fatigue", "loss of taste or smell", "difficulty breathing"],
                prevention="Vaccination, mask wearing, social distancing, hand hygiene",
                treatment="Supportive care, antiviral medications in severe cases",
                severity_level="moderate"
            )
        }
        
        if disease_id not in diseases:
            raise HTTPException(status_code=404, detail="Disease not found")
        
        return diseases[disease_id]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving disease {disease_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve disease information")


@router.get("/symptoms", response_model=List[SymptomInfo])
async def get_symptoms(
    search: Optional[str] = Query(None, description="Search term for symptoms"),
    health_service: HealthService = Depends(get_health_service)
):
    """Get information about symptoms"""
    try:
        # Sample symptoms data
        symptoms = [
            SymptomInfo(
                id=1,
                name="Fever",
                description="Elevated body temperature, often indicating infection or illness",
                severity_indicators=["temperature above 100.4°F (38°C)", "chills", "sweating"],
                related_diseases=[1, 2, 3]  # Common cold, COVID-19, Malaria
            ),
            SymptomInfo(
                id=2,
                name="Cough",
                description="Reflex action to clear airways of irritants",
                severity_indicators=["persistent cough", "coughing up blood", "difficulty breathing"],
                related_diseases=[1, 2]  # Common cold, COVID-19
            ),
            SymptomInfo(
                id=3,
                name="Headache",
                description="Pain in the head or upper neck",
                severity_indicators=["severe pain", "vision changes", "neck stiffness"],
                related_diseases=[3]  # Malaria
            )
        ]
        
        # Filter by search term if provided
        if search:
            search_lower = search.lower()
            symptoms = [
                s for s in symptoms 
                if search_lower in s.name.lower() or search_lower in s.description.lower()
            ]
        
        return symptoms
        
    except Exception as e:
        logger.error(f"Error retrieving symptoms: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve symptom information")


@router.get("/vaccination-schedule", response_model=List[VaccinationInfo])
async def get_vaccination_schedule(
    age_group: Optional[str] = Query(None, description="Filter by age group"),
    health_service: HealthService = Depends(get_health_service)
):
    """Get vaccination schedule information"""
    try:
        vaccines = await health_service.get_vaccination_schedule(age_group)
        return vaccines
        
    except Exception as e:
        logger.error(f"Error retrieving vaccination schedule: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve vaccination schedule")


@router.get("/emergency-info")
async def get_emergency_info() -> APIResponse:
    """Get emergency health information and contact numbers"""
    try:
        emergency_data = {
            "emergency_numbers": {
                "ambulance": "108",
                "fire": "101",
                "police": "100",
                "disaster_management": "108",
                "women_helpline": "1091",
                "child_helpline": "1098"
            },
            "emergency_symptoms": [
                "Severe chest pain",
                "Difficulty breathing or shortness of breath",
                "Severe bleeding",
                "Loss of consciousness",
                "Severe allergic reaction",
                "Signs of stroke (face drooping, arm weakness, speech difficulty)",
                "Signs of heart attack",
                "Severe burns",
                "Poisoning"
            ],
            "first_aid_tips": [
                "Stay calm and assess the situation",
                "Call for emergency help if needed",
                "Check for responsiveness and breathing",
                "Apply pressure to stop bleeding",
                "Do not move someone with potential spinal injury",
                "Keep the person warm and comfortable"
            ]
        }
        
        return APIResponse(
            success=True,
            message="Emergency information retrieved successfully",
            data=emergency_data
        )
        
    except Exception as e:
        logger.error(f"Error retrieving emergency info: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve emergency information")


@router.get("/preventive-care")
async def get_preventive_care() -> APIResponse:
    """Get preventive healthcare information"""
    try:
        preventive_data = {
            "general_prevention": [
                "Maintain good personal hygiene",
                "Eat a balanced and nutritious diet",
                "Exercise regularly",
                "Get adequate sleep (7-9 hours for adults)",
                "Manage stress effectively",
                "Avoid smoking and limit alcohol consumption",
                "Stay up to date with vaccinations",
                "Get regular health check-ups"
            ],
            "infectious_disease_prevention": [
                "Wash hands frequently with soap and water",
                "Use hand sanitizer when soap is not available",
                "Avoid touching face with unwashed hands",
                "Maintain social distance during outbreaks",
                "Wear masks when recommended",
                "Cover coughs and sneezes",
                "Stay home when sick",
                "Disinfect frequently touched surfaces"
            ],
            "chronic_disease_prevention": [
                "Maintain healthy weight",
                "Control blood pressure and cholesterol",
                "Monitor blood sugar levels",
                "Limit processed and high-sodium foods",
                "Include fruits and vegetables in diet",
                "Stay physically active",
                "Don't smoke",
                "Limit alcohol intake"
            ]
        }
        
        return APIResponse(
            success=True,
            message="Preventive care information retrieved successfully",
            data=preventive_data
        )
        
    except Exception as e:
        logger.error(f"Error retrieving preventive care info: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve preventive care information")