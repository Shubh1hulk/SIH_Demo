"""
Health alerts and outbreak notification API routes
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from typing import List, Optional
from datetime import datetime, timedelta
from loguru import logger

from app.models.api_models import (
    OutbreakAlert, AlertSubscriptionRequest, APIResponse, SeverityEnum
)
from app.services.health_service import HealthService
from main import get_health_service

router = APIRouter()


@router.get("/outbreaks", response_model=List[OutbreakAlert])
async def get_disease_outbreaks(
    location: Optional[str] = Query(None, description="Filter by location"),
    severity: Optional[SeverityEnum] = Query(None, description="Filter by severity"),
    health_service: HealthService = Depends(get_health_service)
):
    """Get current disease outbreak alerts"""
    try:
        # Sample outbreak data - in production this would come from government APIs
        current_time = datetime.now()
        sample_outbreaks = [
            OutbreakAlert(
                id=1,
                disease_name="Dengue Fever",
                location="Mumbai, Maharashtra",
                severity=SeverityEnum.HIGH,
                description="Increased cases of dengue fever reported in Mumbai metropolitan area. Residents advised to take precautions against mosquito breeding.",
                prevention_measures="Remove stagnant water, use mosquito nets, wear long sleeves, use repellents",
                outbreak_date=current_time - timedelta(days=7),
                reported_date=current_time - timedelta(days=5)
            ),
            OutbreakAlert(
                id=2,
                disease_name="Seasonal Influenza",
                location="Delhi NCR",
                severity=SeverityEnum.MODERATE,
                description="Seasonal flu outbreak in Delhi and surrounding areas. Increased hospital admissions reported.",
                prevention_measures="Get flu vaccination, maintain hygiene, wear masks in crowded places",
                outbreak_date=current_time - timedelta(days=14),
                reported_date=current_time - timedelta(days=10)
            ),
            OutbreakAlert(
                id=3,
                disease_name="Chikungunya",
                location="Bangalore, Karnataka",
                severity=SeverityEnum.MODERATE,
                description="Chikungunya cases reported in several areas of Bangalore. Vector control measures being implemented.",
                prevention_measures="Eliminate breeding sites, use protective clothing, seek medical attention for symptoms",
                outbreak_date=current_time - timedelta(days=5),
                reported_date=current_time - timedelta(days=3)
            )
        ]
        
        # Apply filters
        filtered_outbreaks = sample_outbreaks
        
        if location:
            filtered_outbreaks = [
                outbreak for outbreak in filtered_outbreaks
                if location.lower() in outbreak.location.lower()
            ]
        
        if severity:
            filtered_outbreaks = [
                outbreak for outbreak in filtered_outbreaks
                if outbreak.severity == severity
            ]
        
        # Get real outbreak data from health service
        real_outbreaks = await health_service.get_active_outbreaks(location)
        filtered_outbreaks.extend(real_outbreaks)
        
        return filtered_outbreaks
        
    except Exception as e:
        logger.error(f"Error retrieving disease outbreaks: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve outbreak information")


@router.get("/outbreaks/{outbreak_id}", response_model=OutbreakAlert)
async def get_outbreak_details(
    outbreak_id: int,
    health_service: HealthService = Depends(get_health_service)
):
    """Get detailed information about a specific outbreak"""
    try:
        # Sample data - in production this would query the database
        current_time = datetime.now()
        sample_outbreaks = {
            1: OutbreakAlert(
                id=1,
                disease_name="Dengue Fever",
                location="Mumbai, Maharashtra",
                severity=SeverityEnum.HIGH,
                description="Increased cases of dengue fever reported in Mumbai metropolitan area. Total confirmed cases: 1,250. Residents advised to take immediate precautions against mosquito breeding. Health department has increased surveillance and vector control activities.",
                prevention_measures="Remove stagnant water from containers, coolers, and plant pots. Use mosquito nets while sleeping. Wear long-sleeved clothing. Use mosquito repellents. Seek immediate medical attention for fever, headache, or body aches.",
                outbreak_date=current_time - timedelta(days=7),
                reported_date=current_time - timedelta(days=5)
            )
        }
        
        if outbreak_id not in sample_outbreaks:
            raise HTTPException(status_code=404, detail="Outbreak not found")
        
        return sample_outbreaks[outbreak_id]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving outbreak {outbreak_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve outbreak details")


@router.post("/subscribe")
async def subscribe_to_alerts(
    request: AlertSubscriptionRequest,
    background_tasks: BackgroundTasks
) -> APIResponse:
    """Subscribe to health alerts"""
    try:
        # In production, this would save to database and set up notification triggers
        background_tasks.add_task(_process_alert_subscription, request)
        
        return APIResponse(
            success=True,
            message=f"Successfully subscribed to {request.alert_type} alerts",
            data={
                "user_id": request.user_id,
                "alert_type": request.alert_type,
                "location_filter": request.location_filter,
                "subscription_date": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Error subscribing to alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to subscribe to alerts")


@router.get("/subscriptions/{user_id}")
async def get_user_subscriptions(user_id: str) -> APIResponse:
    """Get user's alert subscriptions"""
    try:
        # Sample subscription data - in production this would query the database
        subscriptions = [
            {
                "id": 1,
                "alert_type": "outbreak",
                "location_filter": "Mumbai",
                "created_at": (datetime.now() - timedelta(days=30)).isoformat(),
                "is_active": True
            },
            {
                "id": 2,
                "alert_type": "vaccination",
                "location_filter": None,
                "created_at": (datetime.now() - timedelta(days=15)).isoformat(),
                "is_active": True
            }
        ]
        
        return APIResponse(
            success=True,
            message="User subscriptions retrieved successfully",
            data={
                "user_id": user_id,
                "subscriptions": subscriptions
            }
        )
        
    except Exception as e:
        logger.error(f"Error retrieving user subscriptions: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve subscriptions")


@router.delete("/subscriptions/{subscription_id}")
async def unsubscribe_alert(subscription_id: int) -> APIResponse:
    """Unsubscribe from a specific alert"""
    try:
        # In production, this would update the database
        return APIResponse(
            success=True,
            message=f"Successfully unsubscribed from alert {subscription_id}",
            data={"subscription_id": subscription_id}
        )
        
    except Exception as e:
        logger.error(f"Error unsubscribing from alert {subscription_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to unsubscribe from alert")


@router.get("/health-advisories")
async def get_health_advisories() -> APIResponse:
    """Get current health advisories and recommendations"""
    try:
        advisories = [
            {
                "id": 1,
                "title": "Monsoon Health Advisory",
                "description": "Stay healthy during monsoon season",
                "recommendations": [
                    "Drink boiled or purified water",
                    "Avoid street food and raw vegetables",
                    "Keep surroundings clean and dry",
                    "Use mosquito protection measures",
                    "Seek medical help for fever or stomach issues"
                ],
                "severity": "moderate",
                "valid_until": (datetime.now() + timedelta(days=90)).isoformat()
            },
            {
                "id": 2,
                "title": "Heat Wave Precautions",
                "description": "Protect yourself during extreme heat",
                "recommendations": [
                    "Stay indoors during peak hours (11 AM - 4 PM)",
                    "Drink plenty of fluids",
                    "Wear light-colored, loose-fitting clothes",
                    "Use ORS for dehydration",
                    "Watch for heat exhaustion symptoms"
                ],
                "severity": "high",
                "valid_until": (datetime.now() + timedelta(days=60)).isoformat()
            }
        ]
        
        return APIResponse(
            success=True,
            message="Health advisories retrieved successfully",
            data={"advisories": advisories}
        )
        
    except Exception as e:
        logger.error(f"Error retrieving health advisories: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve health advisories")


@router.post("/send-alert")
async def send_emergency_alert(
    background_tasks: BackgroundTasks,
    alert_message: str,
    target_location: Optional[str] = None,
    severity: SeverityEnum = SeverityEnum.HIGH
) -> APIResponse:
    """Send emergency health alert (admin function)"""
    try:
        # This would be restricted to authorized health officials
        alert_data = {
            "message": alert_message,
            "location": target_location,
            "severity": severity.value,
            "timestamp": datetime.now().isoformat()
        }
        
        # Queue alert for distribution
        background_tasks.add_task(_distribute_emergency_alert, alert_data)
        
        return APIResponse(
            success=True,
            message="Emergency alert queued for distribution",
            data=alert_data
        )
        
    except Exception as e:
        logger.error(f"Error sending emergency alert: {e}")
        raise HTTPException(status_code=500, detail="Failed to send emergency alert")


async def _process_alert_subscription(request: AlertSubscriptionRequest):
    """Background task to process alert subscription"""
    try:
        # In production, this would:
        # 1. Save subscription to database
        # 2. Set up notification triggers
        # 3. Send confirmation message to user
        logger.info(f"Processing alert subscription for user {request.user_id}")
        
    except Exception as e:
        logger.error(f"Error processing subscription: {e}")


async def _distribute_emergency_alert(alert_data: dict):
    """Background task to distribute emergency alerts"""
    try:
        # In production, this would:
        # 1. Get subscribed users for the location
        # 2. Send WhatsApp/SMS notifications
        # 3. Update alert status in database
        logger.info(f"Distributing emergency alert: {alert_data['message']}")
        
    except Exception as e:
        logger.error(f"Error distributing alert: {e}")