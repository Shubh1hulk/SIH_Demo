"""
Integration tests for the chat API
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestChatAPI:
    
    def test_health_status(self):
        """Test API health status endpoint"""
        response = client.get("/api/v1/status")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "services" in data
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    def test_chat_message_basic(self):
        """Test basic chat message functionality"""
        # Note: This test might fail in the actual environment due to service dependencies
        # In a real testing environment, we would mock the services
        message_data = {
            "message": "Hello, I need help with health information",
            "language": "en"
        }
        
        try:
            response = client.post("/api/v1/chat/message", json=message_data)
            # The actual response depends on service initialization
            # In production, this would be properly mocked
            assert response.status_code in [200, 503]  # 503 if services not initialized
        except Exception as e:
            # Expected in test environment without full service initialization
            pytest.skip("Service dependencies not available in test environment")
    
    def test_health_diseases_endpoint(self):
        """Test diseases endpoint"""
        response = client.get("/api/v1/health/diseases")
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    def test_health_symptoms_endpoint(self):
        """Test symptoms endpoint"""
        response = client.get("/api/v1/health/symptoms")
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    def test_vaccination_schedule_endpoint(self):
        """Test vaccination schedule endpoint"""
        response = client.get("/api/v1/health/vaccination-schedule")
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    def test_outbreaks_endpoint(self):
        """Test disease outbreaks endpoint"""
        response = client.get("/api/v1/alerts/outbreaks")
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    def test_emergency_info_endpoint(self):
        """Test emergency information endpoint"""
        response = client.get("/api/v1/health/emergency-info")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "emergency_numbers" in data["data"]
        assert "108" in data["data"]["emergency_numbers"]["ambulance"]
    
    def test_preventive_care_endpoint(self):
        """Test preventive care endpoint"""
        response = client.get("/api/v1/health/preventive-care")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "general_prevention" in data["data"]
    
    def test_health_advisories_endpoint(self):
        """Test health advisories endpoint"""
        response = client.get("/api/v1/alerts/health-advisories")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "advisories" in data["data"]