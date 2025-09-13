# AI-Powered Multilingual Healthcare Chatbot

This is a comprehensive multilingual AI chatbot designed to bridge the healthcare information gap in rural and semi-urban communities. The chatbot provides accessible, reliable, and timely education on preventive healthcare, disease symptoms, and vaccination schedules.

## Features

### Core Functionality
- **Multilingual Support**: Supports 10+ Indian regional languages including Hindi, Tamil, Telugu, Bengali, Gujarati, Marathi, Malayalam, Kannada, and Punjabi
- **Healthcare Knowledge Base**: Comprehensive database of symptoms, diseases, preventive care, and vaccination schedules
- **Government API Integration**: Real-time integration with official government health databases
- **Disease Outbreak Alerts**: Real-time notifications about local disease outbreaks
- **WhatsApp & SMS Access**: Accessible via WhatsApp and SMS for maximum reach in areas with limited internet

### Technical Features
- **NLP Engine**: Advanced Natural Language Processing using Rasa framework
- **High Accuracy**: Targets 80% accuracy in interpreting and answering health queries
- **Cloud Scalability**: Deployed on AWS/Google Cloud for high availability
- **Secure APIs**: Secure integration with national health data systems
- **Real-time Processing**: Fast response times for critical health information

## Architecture

```
├── app/
│   ├── api/routes/          # API endpoints
│   ├── core/                # Core configuration and database
│   ├── models/              # Data models
│   ├── services/            # Business logic services
│   ├── utils/               # Utility functions
│   └── data/                # Health knowledge base and language data
├── tests/                   # Test suites
├── deployment/              # Deployment configurations
└── docs/                    # Documentation
```

## Quick Start

### Prerequisites
- Python 3.9+
- Redis server
- SQLite (for development) or PostgreSQL (for production)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Shubh1hulk/SIH_Demo.git
cd SIH_Demo
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Initialize the database:
```bash
python -m app.core.database
```

5. Run the application:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Chat Endpoints
- `POST /api/v1/chat/message` - Send a message to the chatbot
- `GET /api/v1/chat/history/{user_id}` - Get chat history

### Health Information
- `GET /api/v1/health/symptoms` - Get symptom information
- `GET /api/v1/health/diseases` - Get disease information
- `GET /api/v1/health/vaccination-schedule` - Get vaccination schedules

### Alerts
- `GET /api/v1/alerts/outbreaks` - Get current disease outbreak alerts
- `POST /api/v1/alerts/subscribe` - Subscribe to health alerts

## WhatsApp Integration

The chatbot integrates with WhatsApp Business API to provide healthcare information directly through WhatsApp messages. Users can:

1. Send symptoms or health questions in their local language
2. Receive accurate health information and recommendations
3. Get vaccination reminders and schedules
4. Receive real-time disease outbreak alerts

## SMS Integration

For areas with limited internet connectivity, the chatbot supports SMS through Twilio:

1. Send SMS to the registered number
2. Receive health information via SMS
3. Subscribe to health alerts and reminders

## Supported Languages

- English (en)
- Hindi (hi) 
- Tamil (ta)
- Telugu (te)
- Bengali (bn)
- Gujarati (gu)
- Marathi (mr)
- Malayalam (ml)
- Kannada (kn)
- Punjabi (pa)

## Deployment

### Docker Deployment
```bash
docker build -t healthcare-chatbot .
docker run -p 8000:8000 healthcare-chatbot
```

### AWS Deployment
See `deployment/aws/` for CloudFormation templates and deployment scripts.

### Google Cloud Deployment
See `deployment/gcp/` for Google Cloud deployment configurations.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please create an issue in the GitHub repository or contact the development team.

## Acknowledgments

- Built for Smart India Hackathon (SIH)
- Designed to serve rural and semi-urban healthcare needs
- Supports government healthcare initiatives and digital health infrastructure