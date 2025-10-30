"""
Database seeding script for initial healthcare data
"""

from models import HealthInfo, VaccinationSchedule, HealthAlert, db
from datetime import datetime, timedelta
import json

def seed_health_information():
    """Seed the database with initial health information"""
    
    print("Seeding health information...")
    
    # English health information
    health_data_en = [
        {
            'topic': 'Fever Management',
            'content': 'For fever: Rest, drink plenty of fluids, take paracetamol as directed. Seek medical help if temperature exceeds 102°F (39°C) or persists beyond 3 days.',
            'category': 'symptoms',
            'keywords': 'fever,temperature,hot,chills'
        },
        {
            'topic': 'Common Cold Prevention',
            'content': 'Prevent colds by washing hands frequently, avoiding close contact with sick people, not touching face with unwashed hands, and maintaining good hygiene.',
            'category': 'preventive',
            'keywords': 'cold,prevention,hygiene,handwashing'
        },
        {
            'topic': 'Cough Relief',
            'content': 'For persistent cough: Stay hydrated, use honey (for adults), avoid irritants. Consult doctor if cough persists beyond 2 weeks or includes blood.',
            'category': 'symptoms',
            'keywords': 'cough,throat,chest,breathing'
        },
        {
            'topic': 'Diarrhea Treatment',
            'content': 'For diarrhea: Drink ORS solution, avoid dairy and spicy foods, eat bland foods like rice and bananas. Seek medical help if severe dehydration occurs.',
            'category': 'symptoms',
            'keywords': 'diarrhea,stomach,dehydration,ors'
        },
        {
            'topic': 'Handwashing Technique',
            'content': 'Proper handwashing: Use soap and water for 20 seconds, scrub between fingers, under nails, and wrists. Use hand sanitizer when water unavailable.',
            'category': 'preventive',
            'keywords': 'handwashing,hygiene,sanitizer,prevention'
        }
    ]
    
    # Hindi health information
    health_data_hi = [
        {
            'topic': 'बुखार का इलाज',
            'content': 'बुखार के लिए: आराम करें, खूब तरल पदार्थ पिएं, निर्देशानुसार पैरासिटामोल लें। यदि तापमान 102°F (39°C) से अधिक हो या 3 दिनों से अधिक बना रहे तो चिकित्सा सहायता लें।',
            'category': 'symptoms',
            'keywords': 'बुखार,तापमान,गर्मी,कंपकंपी'
        },
        {
            'topic': 'सामान्य सर्दी की रोकथाम',
            'content': 'सर्दी से बचने के लिए: बार-बार हाथ धोएं, बीमार लोगों से दूरी बनाए रखें, बिना धुले हाथों से चेहरा न छुएं, और अच्छी स्वच्छता बनाए रखें।',
            'category': 'preventive',
            'keywords': 'सर्दी,बचाव,स्वच्छता,हाथ_धोना'
        },
        {
            'topic': 'खांसी का राहत',
            'content': 'लगातार खांसी के लिए: पर्याप्त पानी पिएं, शहद का प्रयोग करें (वयस्कों के लिए), परेशान करने वाली चीजों से बचें। यदि खांसी 2 सप्ताह से अधिक रहे या खून आए तो डॉक्टर से सलाह लें।',
            'category': 'symptoms',
            'keywords': 'खांसी,गला,छाती,सांस'
        },
        {
            'topic': 'दस्त का इलाज',
            'content': 'दस्त के लिए: ORS घोल पिएं, डेयरी और मसालेदार खाना से बचें, चावल और केले जैसा सादा खाना खाएं। गंभीर निर्जलीकरण होने पर चिकित्सा सहायता लें।',
            'category': 'symptoms',
            'keywords': 'दस्त,पेट,निर्जलीकरण,ors'
        },
        {
            'topic': 'हाथ धोने की तकनीक',
            'content': 'सही तरीके से हाथ धोना: साबुन और पानी से 20 सेकंड तक धोएं, उंगलियों के बीच, नाखूनों के नीचे और कलाई को रगड़ें। पानी उपलब्ध न हो तो हैंड सैनिटाइजर का प्रयोग करें।',
            'category': 'preventive',
            'keywords': 'हाथ_धोना,स्वच्छता,सैनिटाइजर,बचाव'
        }
    ]
    
    # Add English health information
    for data in health_data_en:
        health_info = HealthInfo(
            topic=data['topic'],
            content=data['content'],
            language='en',
            category=data['category'],
            keywords=data['keywords'],
            created_at=datetime.utcnow()
        )
        db.session.add(health_info)
    
    # Add Hindi health information
    for data in health_data_hi:
        health_info = HealthInfo(
            topic=data['topic'],
            content=data['content'],
            language='hi',
            category=data['category'],
            keywords=data['keywords'],
            created_at=datetime.utcnow()
        )
        db.session.add(health_info)
    
    db.session.commit()
    print(f"Added {len(health_data_en + health_data_hi)} health information entries")

def seed_vaccination_schedules():
    """Seed vaccination schedule data"""
    
    print("Seeding vaccination schedules...")
    
    # English vaccination schedules
    vaccination_data_en = [
        {
            'vaccine_name': 'BCG',
            'age_group': 'Newborn (0-1 year)',
            'schedule_info': 'Given at birth or within first year. Protects against tuberculosis.',
            'is_mandatory': True
        },
        {
            'vaccine_name': 'DPT (Diphtheria, Pertussis, Tetanus)',
            'age_group': 'Infants (6 weeks, 10 weeks, 14 weeks)',
            'schedule_info': 'Three doses: at 6 weeks, 10 weeks, and 14 weeks of age.',
            'is_mandatory': True
        },
        {
            'vaccine_name': 'Polio',
            'age_group': 'Infants (6 weeks, 10 weeks, 14 weeks)',
            'schedule_info': 'Multiple doses starting at 6 weeks. Oral and injectable versions available.',
            'is_mandatory': True
        },
        {
            'vaccine_name': 'Measles',
            'age_group': 'Children (9-12 months)',
            'schedule_info': 'First dose at 9-12 months, second dose at 15-18 months.',
            'is_mandatory': True
        },
        {
            'vaccine_name': 'Hepatitis B',
            'age_group': 'Newborn to Adult',
            'schedule_info': 'Three doses: at birth, 1-2 months, and 6-18 months.',
            'is_mandatory': True
        }
    ]
    
    # Hindi vaccination schedules
    vaccination_data_hi = [
        {
            'vaccine_name': 'बीसीजी',
            'age_group': 'नवजात (0-1 वर्ष)',
            'schedule_info': 'जन्म के समय या पहले वर्ष में दिया जाता है। तपेदिक से सुरक्षा प्रदान करता है।',
            'is_mandatory': True
        },
        {
            'vaccine_name': 'डीपीटी (डिप्थीरिया, पर्टुसिस, टिटनस)',
            'age_group': 'शिशु (6 सप्ताह, 10 सप्ताह, 14 सप्ताह)',
            'schedule_info': 'तीन खुराकें: 6 सप्ताह, 10 सप्ताह और 14 सप्ताह की उम्र में।',
            'is_mandatory': True
        },
        {
            'vaccine_name': 'पोलियो',
            'age_group': 'शिशु (6 सप्ताह, 10 सप्ताह, 14 सप्ताह)',
            'schedule_info': '6 सप्ताह से शुरू होकर कई खुराकें। मौखिक और इंजेक्शन दोनों प्रकार उपलब्ध।',
            'is_mandatory': True
        },
        {
            'vaccine_name': 'खसरा',
            'age_group': 'बच्चे (9-12 महीने)',
            'schedule_info': 'पहली खुराक 9-12 महीने में, दूसरी खुराक 15-18 महीने में।',
            'is_mandatory': True
        },
        {
            'vaccine_name': 'हेपेटाइटिस बी',
            'age_group': 'नवजात से वयस्क तक',
            'schedule_info': 'तीन खुराकें: जन्म के समय, 1-2 महीने में और 6-18 महीने में।',
            'is_mandatory': True
        }
    ]
    
    # Add English vaccination schedules
    for data in vaccination_data_en:
        vaccination = VaccinationSchedule(
            vaccine_name=data['vaccine_name'],
            age_group=data['age_group'],
            schedule_info=data['schedule_info'],
            language='en',
            is_mandatory=data['is_mandatory'],
            created_at=datetime.utcnow()
        )
        db.session.add(vaccination)
    
    # Add Hindi vaccination schedules
    for data in vaccination_data_hi:
        vaccination = VaccinationSchedule(
            vaccine_name=data['vaccine_name'],
            age_group=data['age_group'],
            schedule_info=data['schedule_info'],
            language='hi',
            is_mandatory=data['is_mandatory'],
            created_at=datetime.utcnow()
        )
        db.session.add(vaccination)
    
    db.session.commit()
    print(f"Added {len(vaccination_data_en + vaccination_data_hi)} vaccination schedules")

def seed_health_alerts():
    """Seed sample health alerts"""
    
    print("Seeding health alerts...")
    
    # Sample health alerts
    alerts_data = [
        {
            'alert_type': 'advisory',
            'title': 'Seasonal Flu Prevention',
            'content': 'Flu season is approaching. Get vaccinated and practice good hygiene to prevent seasonal influenza.',
            'language': 'en',
            'severity': 'low',
            'expires_at': datetime.utcnow() + timedelta(days=90)
        },
        {
            'alert_type': 'advisory',
            'title': 'मौसमी फ्लू की रोकथाम',
            'content': 'फ्लू का मौसम आ रहा है। मौसमी इन्फ्लूएंजा से बचने के लिए टीकाकरण कराएं और अच्छी स्वच्छता का अभ्यास करें।',
            'language': 'hi',
            'severity': 'low',
            'expires_at': datetime.utcnow() + timedelta(days=90)
        },
        {
            'alert_type': 'outbreak',
            'title': 'Water Quality Alert',
            'content': 'Boil water before drinking due to contamination reports in some areas. Use only treated or bottled water.',
            'language': 'en',
            'severity': 'medium',
            'expires_at': datetime.utcnow() + timedelta(days=30)
        },
        {
            'alert_type': 'outbreak',
            'title': 'पानी की गुणवत्ता अलर्ट',
            'content': 'कुछ क्षेत्रों में संदूषण की रिपोर्ट के कारण पीने से पहले पानी उबालें। केवल उपचारित या बोतलबंद पानी का प्रयोग करें।',
            'language': 'hi',
            'severity': 'medium',
            'expires_at': datetime.utcnow() + timedelta(days=30)
        },
        {
            'alert_type': 'emergency',
            'title': 'Heat Wave Advisory',
            'content': 'Extreme heat conditions expected. Stay indoors during peak hours (10 AM - 4 PM), drink plenty of water, and watch for heat exhaustion symptoms.',
            'language': 'en',
            'severity': 'high',
            'expires_at': datetime.utcnow() + timedelta(days=14)
        }
    ]
    
    for data in alerts_data:
        alert = HealthAlert(
            alert_type=data['alert_type'],
            title=data['title'],
            content=data['content'],
            language=data['language'],
            severity=data['severity'],
            is_active=True,
            expires_at=data['expires_at'],
            created_at=datetime.utcnow()
        )
        db.session.add(alert)
    
    db.session.commit()
    print(f"Added {len(alerts_data)} health alerts")

def run_seeding():
    """Run all seeding functions"""
    print("Starting database seeding...")
    
    from app import app
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Check if data already exists
        existing_health_info = HealthInfo.query.count()
        existing_vaccinations = VaccinationSchedule.query.count()
        existing_alerts = HealthAlert.query.count()
        
        if existing_health_info == 0:
            seed_health_information()
        else:
            print(f"Health information already exists ({existing_health_info} entries)")
        
        if existing_vaccinations == 0:
            seed_vaccination_schedules()
        else:
            print(f"Vaccination schedules already exist ({existing_vaccinations} entries)")
        
        if existing_alerts == 0:
            seed_health_alerts()
        else:
            print(f"Health alerts already exist ({existing_alerts} entries)")
        
        print("Database seeding completed!")

if __name__ == '__main__':
    run_seeding()