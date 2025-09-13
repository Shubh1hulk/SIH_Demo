#!/bin/bash

# Healthcare Chatbot Deployment Script for AWS EC2

set -e

echo "🚀 Starting Healthcare Chatbot deployment on AWS..."

# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.0.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone repository
git clone https://github.com/Shubh1hulk/SIH_Demo.git
cd SIH_Demo

# Set up environment variables
cp .env.example .env
echo "⚙️  Please configure .env file with your API keys and settings"

# Build and start services
docker-compose up --build -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 30

# Health check
if curl -f http://localhost:8000/api/v1/status; then
    echo "✅ Healthcare Chatbot deployed successfully!"
    echo "📱 API available at: http://your-ec2-ip:8000"
    echo "📚 Documentation at: http://your-ec2-ip:8000/docs"
else
    echo "❌ Deployment failed. Check logs with: docker-compose logs"
    exit 1
fi

echo "🎉 Deployment complete! Don't forget to:"
echo "1. Configure your domain and SSL certificates"
echo "2. Set up WhatsApp Business API credentials"
echo "3. Configure Twilio SMS credentials"
echo "4. Set up database backup strategies"