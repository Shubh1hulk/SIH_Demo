"""
Webhook handlers for WhatsApp and SMS integration
"""

from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from loguru import logger
import json
from typing import Dict, Any

from app.services.whatsapp_service import WhatsAppService
from app.services.sms_service import SMSService
from app.services.nlp_service import NLPService
from app.services.health_service import HealthService
from app.models.api_models import ChatMessageRequest

router = APIRouter()
whatsapp_service = WhatsAppService()
sms_service = SMSService()


@router.post("/whatsapp-webhook")
async def whatsapp_webhook(
    request: Request,
    background_tasks: BackgroundTasks
):
    """Handle incoming WhatsApp messages"""
    try:
        data = await request.json()
        logger.info(f"Received WhatsApp webhook: {json.dumps(data, indent=2)}")
        
        # Process the message in background
        background_tasks.add_task(process_whatsapp_message, data)
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Error processing WhatsApp webhook: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")


@router.get("/whatsapp-webhook")
async def verify_whatsapp_webhook(
    request: Request
):
    """Verify WhatsApp webhook (required by WhatsApp API)"""
    try:
        params = request.query_params
        mode = params.get("hub.mode")
        token = params.get("hub.verify_token")
        challenge = params.get("hub.challenge")
        
        # Verify the webhook (use your actual verify token)
        if mode == "subscribe" and token == "your_verify_token":
            logger.info("WhatsApp webhook verified successfully")
            return int(challenge)
        else:
            raise HTTPException(status_code=403, detail="Verification failed")
            
    except Exception as e:
        logger.error(f"Error verifying WhatsApp webhook: {e}")
        raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/sms-webhook")
async def sms_webhook(
    request: Request,
    background_tasks: BackgroundTasks
):
    """Handle incoming SMS messages from Twilio"""
    try:
        form_data = await request.form()
        
        from_number = form_data.get("From", "")
        message_body = form_data.get("Body", "")
        
        logger.info(f"Received SMS from {from_number}: {message_body}")
        
        # Process the message in background
        background_tasks.add_task(process_sms_message, from_number, message_body)
        
        # Return TwiML response
        return """<?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Message>Thank you for your message. We're processing it and will respond shortly.</Message>
        </Response>"""
        
    except Exception as e:
        logger.error(f"Error processing SMS webhook: {e}")
        return """<?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Message>Sorry, there was an error processing your message. Please try again.</Message>
        </Response>"""


async def process_whatsapp_message(webhook_data: Dict[str, Any]):
    """Process incoming WhatsApp message"""
    try:
        # Extract message from webhook data
        message_text = whatsapp_service.handle_incoming_message(webhook_data)
        
        if not message_text:
            return
        
        # Get user phone number
        entry = webhook_data.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [{}])
        
        if messages:
            from_number = messages[0].get("from", "")
            
            # Process through NLP and generate response
            if NLPService and HealthService:
                nlp_service = NLPService()
                health_service = HealthService()
                
                # Create chat request
                chat_request = ChatMessageRequest(
                    message=message_text,
                    user_id=from_number,
                    language="auto"  # Auto-detect language
                )
                
                # Process through NLP
                nlp_result = await nlp_service.process_query(
                    chat_request.message,
                    "auto"
                )
                
                # Generate health response
                response = await _generate_health_response(nlp_result, health_service)
                
                # Send response via WhatsApp
                await whatsapp_service.send_text_message(from_number, response)
            
    except Exception as e:
        logger.error(f"Error processing WhatsApp message: {e}")


async def process_sms_message(from_number: str, message_body: str):
    """Process incoming SMS message"""
    try:
        # Handle SMS commands
        processed_message = await sms_service.handle_incoming_sms(from_number, message_body)
        
        if processed_message == "unsubscribe":
            # Handle unsubscribe
            response = "You have been unsubscribed from health alerts. Reply 'START' to resubscribe."
            await sms_service.send_sms(from_number, response)
            return
        elif processed_message == "help":
            # Send help information
            response = "AI Health Assistant: Send symptoms for assessment. Emergency: Call 108. Reply STOP to unsubscribe."
            await sms_service.send_sms(from_number, response)
            return
        
        # Process health query
        if NLPService and HealthService:
            nlp_service = NLPService()
            health_service = HealthService()
            
            # Process through NLP
            nlp_result = await nlp_service.process_query(processed_message, "auto")
            
            # Generate health response
            response = await _generate_health_response(nlp_result, health_service)
            
            # Send response via SMS (truncated for SMS limits)
            if len(response) > 160:
                response = response[:157] + "..."
            
            await sms_service.send_sms(from_number, response)
        
    except Exception as e:
        logger.error(f"Error processing SMS message: {e}")


async def _generate_health_response(nlp_result: Dict, health_service) -> str:
    """Generate health response based on NLP analysis"""
    intent = nlp_result.get("intent", "general")
    entities = nlp_result.get("entities", {})
    confidence = nlp_result.get("intent_confidence", 0.5)
    
    if intent == "emergency":
        return "🚨 If this is an emergency, call 108 immediately. For urgent care, go to the nearest hospital."
    
    elif intent == "symptom_query" and entities.get("symptoms"):
        from app.models.api_models import HealthAssessmentRequest
        
        # Assess symptoms
        assessment_request = HealthAssessmentRequest(symptoms=entities["symptoms"])
        assessment = await health_service.assess_symptoms(assessment_request)
        
        # Generate response based on urgency
        if assessment.urgency_level.value == "critical":
            return f"⚠️ URGENT: {assessment.recommendations[0]} Call 108 for emergency."
        else:
            return f"Health Assessment: {assessment.recommendations[0]} For more info, consult a healthcare provider."
    
    elif intent == "vaccination":
        vaccines = await health_service.get_vaccination_schedule()
        if vaccines:
            return f"💉 Important vaccines: {', '.join([v.vaccine_name for v in vaccines[:2]])}. Consult your doctor for schedule."
        else:
            return "💉 Vaccination is important for health. Consult your healthcare provider for appropriate vaccines."
    
    elif intent == "disease_info":
        return "I can provide information about various health conditions. Please be specific about which disease or condition you'd like to know about."
    
    else:
        return "I'm your AI health assistant. I can help with symptoms, diseases, vaccines, and health advice. What do you need help with?"