"""
Multilingual AI Chatbot for Rural Healthcare
Main Flask application entry point
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///healthcare_chatbot.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Import and initialize db from models
from models import db
db.init_app(app)
CORS(app)

# Import routes after app initialization
from routes import whatsapp_routes, sms_routes, health_routes, analytics_routes

# Register blueprints
app.register_blueprint(whatsapp_routes.bp)
app.register_blueprint(sms_routes.bp)
app.register_blueprint(health_routes.bp)
app.register_blueprint(analytics_routes.bp)

@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    """Basic health check endpoint"""
    return jsonify({
        'status': 'active',
        'service': 'Multilingual AI Healthcare Chatbot',
        'version': '1.0.0'
    })

@app.route('/webhook', methods=['GET', 'POST'])
def webhook_verification():
    """Webhook verification for WhatsApp"""
    if request.method == 'GET':
        # Verify webhook token
        verify_token = request.args.get('hub.verify_token')
        if verify_token == os.getenv('WHATSAPP_VERIFY_TOKEN'):
            return request.args.get('hub.challenge')
        return 'Invalid verification token', 403
    
    # Handle incoming messages
    return jsonify({'status': 'received'})

if __name__ == '__main__':
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    )