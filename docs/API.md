# API Documentation

## Healthcare Chatbot REST API

Base URL: `http://localhost:8000` (development) / `https://your-domain.com` (production)

### Authentication
Currently, the API doesn't require authentication for basic endpoints. In production, implement appropriate authentication mechanisms.

### Content Type
All API requests and responses use `application/json` content type.

## Endpoints

### 1. System Status

#### GET `/api/v1/status`
Get system health status and service availability.

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "nlp": true,
    "health_db": true
  },
  "version": "1.0.0"
}
```

### 2. Chat Endpoints

#### POST `/api/v1/chat/message`
Send a message to the healthcare chatbot.

**Request Body:**
```json
{
  "message": "I have fever and cough",
  "user_id": "user123",
  "language": "en",
  "session_id": "session_abc"
}
```

**Response:**
```json
{
  "response": "Based on the symptoms you mentioned, here are some recommendations...",
  "detected_intent": "symptom_query",
  "confidence": 0.85,
  "language": "en",
  "suggestions": [
    "Tell me more about your symptoms",
    "When did these symptoms start?"
  ],
  "session_id": "session_abc"
}
```

#### POST `/api/v1/chat/assess-symptoms`
Assess symptoms and get health recommendations.

**Request Body:**
```json
{
  "symptoms": ["fever", "cough", "fatigue"],
  "age": 30,
  "gender": "male",
  "location": "Mumbai",
  "duration": "2 days"
}
```

**Response:**
```json
{
  "possible_conditions": [
    {
      "id": 2,
      "name": "COVID-19",
      "description": "Infectious disease caused by the SARS-CoV-2 virus",
      "symptoms": ["fever", "cough", "fatigue"],
      "prevention": "Vaccination, mask wearing, social distancing",
      "treatment": "Supportive care, consult healthcare provider",
      "severity_level": "moderate"
    }
  ],
  "urgency_level": "moderate",
  "recommendations": [
    "Monitor your symptoms closely",
    "Consider consulting a healthcare provider"
  ],
  "next_steps": [
    "Schedule appointment with healthcare provider",
    "Continue monitoring symptoms"
  ],
  "disclaimer": "This assessment is for informational purposes only..."
}
```

### 3. Health Information

#### GET `/api/v1/health/diseases`
Get information about diseases.

**Query Parameters:**
- `search` (optional): Search term for diseases

**Response:**
```json
[
  {
    "id": 1,
    "name": "Common Cold",
    "description": "A viral infection of the upper respiratory tract",
    "symptoms": ["runny nose", "cough", "sneezing"],
    "prevention": "Wash hands frequently, avoid close contact",
    "treatment": "Rest, fluids, over-the-counter medications",
    "severity_level": "low"
  }
]
```

#### GET `/api/v1/health/diseases/{disease_id}`
Get detailed information about a specific disease.

**Response:**
```json
{
  "id": 1,
  "name": "Common Cold",
  "description": "A viral infection of the upper respiratory tract",
  "symptoms": ["runny nose", "cough", "sneezing", "sore throat"],
  "prevention": "Wash hands frequently, avoid close contact with sick people",
  "treatment": "Rest, fluids, over-the-counter medications for symptom relief",
  "severity_level": "low"
}
```

#### GET `/api/v1/health/symptoms`
Get information about symptoms.

**Query Parameters:**
- `search` (optional): Search term for symptoms

**Response:**
```json
[
  {
    "id": 1,
    "name": "Fever",
    "description": "Elevated body temperature, often indicating infection",
    "severity_indicators": ["temperature above 100.4°F", "chills", "sweating"],
    "related_diseases": [1, 2, 3]
  }
]
```

#### GET `/api/v1/health/vaccination-schedule`
Get vaccination schedule information.

**Query Parameters:**
- `age_group` (optional): Filter by age group

**Response:**
```json
[
  {
    "id": 1,
    "vaccine_name": "COVID-19 Vaccine",
    "age_group": "18+ years",
    "schedule_description": "Two doses, 4-12 weeks apart",
    "doses_required": 2,
    "interval_days": 28
  }
]
```

#### GET `/api/v1/health/emergency-info`
Get emergency contact information and first aid tips.

**Response:**
```json
{
  "success": true,
  "message": "Emergency information retrieved successfully",
  "data": {
    "emergency_numbers": {
      "ambulance": "108",
      "fire": "101",
      "police": "100"
    },
    "emergency_symptoms": [
      "Severe chest pain",
      "Difficulty breathing"
    ],
    "first_aid_tips": [
      "Stay calm and assess the situation",
      "Call for emergency help if needed"
    ]
  }
}
```

### 4. Alerts and Outbreaks

#### GET `/api/v1/alerts/outbreaks`
Get current disease outbreak alerts.

**Query Parameters:**
- `location` (optional): Filter by location
- `severity` (optional): Filter by severity (low, moderate, high, critical)

**Response:**
```json
[
  {
    "id": 1,
    "disease_name": "Dengue Fever",
    "location": "Mumbai, Maharashtra",
    "severity": "high",
    "description": "Increased cases of dengue fever reported...",
    "prevention_measures": "Remove stagnant water, use mosquito nets...",
    "outbreak_date": "2023-12-01T00:00:00",
    "reported_date": "2023-12-03T10:30:00"
  }
]
```

#### POST `/api/v1/alerts/subscribe`
Subscribe to health alerts.

**Request Body:**
```json
{
  "user_id": "user123",
  "alert_type": "outbreak",
  "location_filter": "Mumbai"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully subscribed to outbreak alerts",
  "data": {
    "user_id": "user123",
    "alert_type": "outbreak",
    "location_filter": "Mumbai",
    "subscription_date": "2023-12-10T15:30:00"
  }
}
```

### 5. Webhooks (for WhatsApp/SMS Integration)

#### POST `/webhooks/whatsapp-webhook`
Handle incoming WhatsApp messages.

**Headers:**
- Content-Type: application/json

**Request Body:** WhatsApp webhook payload

#### GET `/webhooks/whatsapp-webhook`
Verify WhatsApp webhook.

**Query Parameters:**
- `hub.mode`: subscribe
- `hub.verify_token`: your verification token
- `hub.challenge`: challenge string

#### POST `/webhooks/sms-webhook`
Handle incoming SMS messages from Twilio.

**Headers:**
- Content-Type: application/x-www-form-urlencoded

**Form Data:**
- `From`: sender phone number
- `Body`: message content

## Error Responses

All endpoints return appropriate HTTP status codes:

- `200`: Success
- `400`: Bad Request
- `404`: Not Found
- `500`: Internal Server Error
- `503`: Service Unavailable

Error response format:
```json
{
  "detail": "Error description"
}
```

## Rate Limiting

In production, implement appropriate rate limiting:
- 100 requests per minute per IP for general endpoints
- 10 requests per minute for assessment endpoints
- 1000 requests per hour for webhooks

## Interactive Documentation

Visit `/docs` (Swagger UI) or `/redoc` (ReDoc) for interactive API documentation when the server is running.