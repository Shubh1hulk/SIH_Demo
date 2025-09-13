"""
Chat API routes for the healthcare chatbot
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Dict, Any
import uuid
from loguru import logger

from app.models.api_models import (
    ChatMessageRequest, ChatMessageResponse, APIResponse,
    HealthAssessmentRequest, HealthAssessmentResponse
)
from app.services.nlp_service import NLPService
from app.services.health_service import HealthService
from main import get_nlp_service, get_health_service

router = APIRouter()


@router.post("/message", response_model=ChatMessageResponse)
async def send_message(
    request: ChatMessageRequest,
    nlp_service: NLPService = Depends(get_nlp_service),
    health_service: HealthService = Depends(get_health_service)
):
    """Process a chat message and return bot response"""
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Process the message through NLP
        nlp_result = await nlp_service.process_query(
            request.message, 
            request.language.value if request.language else "en"
        )
        
        # Generate response based on intent
        bot_response = await _generate_response(nlp_result, health_service, request.language.value)
        
        # Translate response back to user language if needed
        if request.language and request.language.value != "en":
            bot_response["response"] = await nlp_service.translate_text(
                bot_response["response"], 
                request.language.value
            )
        
        return ChatMessageResponse(
            response=bot_response["response"],
            detected_intent=nlp_result["intent"],
            confidence=nlp_result["intent_confidence"],
            language=request.language or "en",
            suggestions=bot_response.get("suggestions", []),
            session_id=session_id
        )
        
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/assess-symptoms", response_model=HealthAssessmentResponse)
async def assess_symptoms(
    request: HealthAssessmentRequest,
    health_service: HealthService = Depends(get_health_service)
):
    """Assess user symptoms and provide health recommendations"""
    try:
        assessment = await health_service.assess_symptoms(request)
        return assessment
        
    except Exception as e:
        logger.error(f"Error assessing symptoms: {e}")
        raise HTTPException(status_code=500, detail="Failed to assess symptoms")


@router.get("/history/{user_id}")
async def get_chat_history(user_id: str) -> APIResponse:
    """Get chat history for a user"""
    try:
        # In a real implementation, this would fetch from database
        return APIResponse(
            success=True,
            message="Chat history retrieved successfully",
            data={
                "user_id": user_id,
                "conversations": []
            }
        )
        
    except Exception as e:
        logger.error(f"Error retrieving chat history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chat history")


async def _generate_response(nlp_result: Dict, health_service: HealthService, language: str) -> Dict[str, Any]:
    """Generate bot response based on NLP analysis"""
    intent = nlp_result["intent"]
    entities = nlp_result["entities"]
    confidence = nlp_result["intent_confidence"]
    
    response = {
        "response": "I'm here to help with your health questions. How can I assist you today?",
        "suggestions": []
    }
    
    try:
        if intent == "symptom_query":
            if entities.get("symptoms"):
                # Create assessment request from detected symptoms
                assessment_request = HealthAssessmentRequest(symptoms=entities["symptoms"])
                assessment = await health_service.assess_symptoms(assessment_request)
                
                response["response"] = f"Based on the symptoms you mentioned, here are some recommendations: {', '.join(assessment.recommendations[:2])}"
                response["suggestions"] = [
                    "Tell me more about your symptoms",
                    "When did these symptoms start?",
                    "Get vaccination information"
                ]
            else:
                response["response"] = "I understand you're asking about symptoms. Can you tell me more specifically what symptoms you're experiencing?"
                response["suggestions"] = [
                    "I have fever and cough",
                    "I have headache and nausea",
                    "I'm feeling dizzy and weak"
                ]
        
        elif intent == "disease_info":
            if entities.get("diseases"):
                disease_name = entities["diseases"][0]
                response["response"] = f"I can provide information about {disease_name}. This is a condition that requires proper medical attention."
                response["suggestions"] = [
                    f"How to prevent {disease_name}",
                    f"Treatment options for {disease_name}",
                    "Find nearby healthcare facilities"
                ]
            else:
                response["response"] = "I can help you learn about various health conditions. Which disease or condition would you like to know about?"
                response["suggestions"] = [
                    "Tell me about COVID-19",
                    "What is malaria?",
                    "Information about diabetes"
                ]
        
        elif intent == "vaccination":
            vaccines = await health_service.get_vaccination_schedule()
            if vaccines:
                vaccine_names = [v.vaccine_name for v in vaccines[:3]]
                response["response"] = f"Here are some important vaccinations: {', '.join(vaccine_names)}. Would you like specific information about any of these?"
                response["suggestions"] = [
                    "COVID-19 vaccination schedule",
                    "Childhood vaccination schedule",
                    "Where to get vaccinated"
                ]
            else:
                response["response"] = "Vaccination is crucial for preventing diseases. I can help you with vaccination schedules and information."
                response["suggestions"] = [
                    "Show vaccination schedule",
                    "Find vaccination centers",
                    "Vaccination for adults"
                ]
        
        elif intent == "prevention":
            response["response"] = "Prevention is the best medicine! Here are general preventive measures: maintain good hygiene, eat healthy food, exercise regularly, and get regular check-ups."
            response["suggestions"] = [
                "How to prevent infectious diseases",
                "Healthy lifestyle tips",
                "Vaccination information"
            ]
        
        elif intent == "emergency":
            response["response"] = "If this is a medical emergency, please call emergency services immediately at 108. For urgent but non-emergency situations, contact your healthcare provider or visit the nearest hospital."
            response["suggestions"] = [
                "Emergency contact numbers",
                "Nearest hospital locations",
                "First aid information"
            ]
        
        else:  # general intent
            response["response"] = "I'm your AI health assistant. I can help you with symptoms, disease information, vaccination schedules, and health advice. What would you like to know?"
            response["suggestions"] = [
                "I have symptoms to report",
                "Tell me about a disease",
                "Vaccination information",
                "Health prevention tips"
            ]
        
        # Add confidence-based modifications
        if confidence < 0.6:
            response["response"] += "\n\nIf I didn't understand your question correctly, please rephrase it or choose from the suggestions below."
    
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        response["response"] = "I apologize, but I encountered an error processing your request. Please try asking your question differently."
    
    return response