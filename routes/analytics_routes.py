"""
Analytics and monitoring routes for tracking chatbot performance
"""

from flask import Blueprint, request, jsonify
from models import User, Conversation, HealthAlert, db
from datetime import datetime, timedelta
from sqlalchemy import func, desc
import json

bp = Blueprint('analytics', __name__, url_prefix='/analytics')

@bp.route('/dashboard', methods=['GET'])
def analytics_dashboard():
    """Get comprehensive analytics dashboard data"""
    
    # Get time range from query parameters
    days = int(request.args.get('days', 30))
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Basic statistics
    total_users = User.query.count()
    active_users = User.query.filter(
        User.last_active >= start_date
    ).count()
    
    total_conversations = Conversation.query.filter(
        Conversation.timestamp >= start_date
    ).count()
    
    # Language distribution
    language_stats = db.session.query(
        User.preferred_language,
        func.count(User.id).label('count')
    ).group_by(User.preferred_language).all()
    
    # Channel distribution
    channel_stats = db.session.query(
        Conversation.channel,
        func.count(Conversation.id).label('count')
    ).filter(
        Conversation.timestamp >= start_date
    ).group_by(Conversation.channel).all()
    
    # Intent distribution
    intent_stats = db.session.query(
        Conversation.intent_detected,
        func.count(Conversation.id).label('count')
    ).filter(
        Conversation.timestamp >= start_date
    ).group_by(Conversation.intent_detected).all()
    
    # Daily conversation trends
    daily_stats = db.session.query(
        func.date(Conversation.timestamp).label('date'),
        func.count(Conversation.id).label('count')
    ).filter(
        Conversation.timestamp >= start_date
    ).group_by(func.date(Conversation.timestamp)).all()
    
    # Average confidence scores
    avg_confidence = db.session.query(
        func.avg(Conversation.confidence_score)
    ).filter(
        Conversation.timestamp >= start_date,
        Conversation.confidence_score.isnot(None)
    ).scalar()
    
    # High confidence queries (accuracy metric)
    high_confidence_count = Conversation.query.filter(
        Conversation.timestamp >= start_date,
        Conversation.confidence_score >= 0.8
    ).count()
    
    accuracy_rate = (high_confidence_count / total_conversations * 100) if total_conversations > 0 else 0
    
    return jsonify({
        'period': {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'days': days
        },
        'overview': {
            'total_users': total_users,
            'active_users': active_users,
            'total_conversations': total_conversations,
            'average_confidence': float(avg_confidence) if avg_confidence else 0,
            'accuracy_rate': round(accuracy_rate, 2)
        },
        'language_distribution': [
            {'language': lang, 'count': count} 
            for lang, count in language_stats
        ],
        'channel_distribution': [
            {'channel': channel or 'unknown', 'count': count} 
            for channel, count in channel_stats
        ],
        'intent_distribution': [
            {'intent': intent or 'unknown', 'count': count} 
            for intent, count in intent_stats
        ],
        'daily_trends': [
            {'date': date.isoformat(), 'conversations': count}
            for date, count in daily_stats
        ]
    })

@bp.route('/user-engagement', methods=['GET'])
def user_engagement():
    """Get user engagement analytics"""
    
    days = int(request.args.get('days', 30))
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # User activity distribution
    user_activity = db.session.query(
        User.id,
        User.phone_number,
        User.preferred_language,
        User.location,
        func.count(Conversation.id).label('message_count'),
        func.max(Conversation.timestamp).label('last_interaction')
    ).join(
        Conversation, User.id == Conversation.user_id
    ).filter(
        Conversation.timestamp >= start_date
    ).group_by(User.id).order_by(desc('message_count')).limit(50).all()
    
    # New users vs returning users
    new_users = User.query.filter(
        User.created_at >= start_date
    ).count()
    
    returning_users = db.session.query(User.id).join(
        Conversation, User.id == Conversation.user_id
    ).filter(
        User.created_at < start_date,
        Conversation.timestamp >= start_date
    ).distinct().count()
    
    # User retention (simplified - users who interacted in multiple days)
    retention_data = db.session.query(
        User.id,
        func.count(func.distinct(func.date(Conversation.timestamp))).label('active_days')
    ).join(
        Conversation, User.id == Conversation.user_id
    ).filter(
        Conversation.timestamp >= start_date
    ).group_by(User.id).all()
    
    retention_categories = {
        'single_day': 0,
        'multi_day': 0,
        'highly_engaged': 0  # 5+ days
    }
    
    for user_id, active_days in retention_data:
        if active_days == 1:
            retention_categories['single_day'] += 1
        elif active_days < 5:
            retention_categories['multi_day'] += 1
        else:
            retention_categories['highly_engaged'] += 1
    
    return jsonify({
        'period': {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'days': days
        },
        'user_acquisition': {
            'new_users': new_users,
            'returning_users': returning_users,
            'total_active': new_users + returning_users
        },
        'user_retention': retention_categories,
        'top_active_users': [
            {
                'user_id': user_id,
                'phone_number': phone[-4:].rjust(len(phone), '*'),  # Mask phone number
                'language': language,
                'location': location,
                'message_count': message_count,
                'last_interaction': last_interaction.isoformat() if last_interaction else None
            }
            for user_id, phone, language, location, message_count, last_interaction in user_activity
        ]
    })

@bp.route('/health-topics', methods=['GET'])
def health_topics_analytics():
    """Analyze most common health topics and queries"""
    
    days = int(request.args.get('days', 30))
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Intent popularity over time
    intent_trends = db.session.query(
        Conversation.intent_detected,
        func.date(Conversation.timestamp).label('date'),
        func.count(Conversation.id).label('count')
    ).filter(
        Conversation.timestamp >= start_date
    ).group_by(
        Conversation.intent_detected, 
        func.date(Conversation.timestamp)
    ).all()
    
    # Most common intents
    popular_intents = db.session.query(
        Conversation.intent_detected,
        func.count(Conversation.id).label('count'),
        func.avg(Conversation.confidence_score).label('avg_confidence')
    ).filter(
        Conversation.timestamp >= start_date
    ).group_by(
        Conversation.intent_detected
    ).order_by(desc('count')).all()
    
    # Low confidence queries (need improvement)
    low_confidence_queries = Conversation.query.filter(
        Conversation.timestamp >= start_date,
        Conversation.confidence_score < 0.5
    ).order_by(desc(Conversation.timestamp)).limit(20).all()
    
    # Query complexity (word count distribution)
    query_complexity = db.session.query(
        func.length(Conversation.message_text).label('length'),
        func.count(Conversation.id).label('count')
    ).filter(
        Conversation.timestamp >= start_date
    ).group_by('length').order_by('length').all()
    
    return jsonify({
        'period': {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'days': days
        },
        'popular_intents': [
            {
                'intent': intent or 'unknown',
                'count': count,
                'avg_confidence': float(avg_confidence) if avg_confidence else 0
            }
            for intent, count, avg_confidence in popular_intents
        ],
        'intent_trends': [
            {
                'intent': intent or 'unknown',
                'date': date.isoformat(),
                'count': count
            }
            for intent, date, count in intent_trends
        ],
        'improvement_needed': [
            {
                'message': query.message_text[:100],
                'intent': query.intent_detected,
                'confidence': float(query.confidence_score) if query.confidence_score else 0,
                'timestamp': query.timestamp.isoformat(),
                'channel': query.channel
            }
            for query in low_confidence_queries
        ],
        'query_complexity_distribution': [
            {'length_range': f"{length//10*10}-{length//10*10+9}", 'count': count}
            for length, count in query_complexity[:10]  # Group by 10s
        ]
    })

@bp.route('/health-awareness', methods=['GET'])
def health_awareness_metrics():
    """Calculate health awareness improvement metrics"""
    
    # Get baseline period (e.g., first 30 days) vs current period
    current_days = int(request.args.get('current_days', 30))
    baseline_days = int(request.args.get('baseline_days', 30))
    
    current_end = datetime.utcnow()
    current_start = current_end - timedelta(days=current_days)
    
    baseline_end = current_start
    baseline_start = baseline_end - timedelta(days=baseline_days)
    
    # Current period metrics
    current_users = User.query.filter(
        User.last_active >= current_start
    ).count()
    
    current_health_queries = Conversation.query.filter(
        Conversation.timestamp >= current_start,
        Conversation.intent_detected.in_(['symptoms', 'preventive', 'vaccination'])
    ).count()
    
    # Baseline period metrics
    baseline_users = User.query.filter(
        User.last_active >= baseline_start,
        User.last_active < baseline_end
    ).count()
    
    baseline_health_queries = Conversation.query.filter(
        Conversation.timestamp >= baseline_start,
        Conversation.timestamp < baseline_end,
        Conversation.intent_detected.in_(['symptoms', 'preventive', 'vaccination'])
    ).count()
    
    # Calculate improvement percentages
    user_growth = ((current_users - baseline_users) / baseline_users * 100) if baseline_users > 0 else 0
    query_growth = ((current_health_queries - baseline_health_queries) / baseline_health_queries * 100) if baseline_health_queries > 0 else 0
    
    # Health topic engagement
    health_topic_engagement = db.session.query(
        Conversation.intent_detected,
        func.count(Conversation.id).label('count')
    ).filter(
        Conversation.timestamp >= current_start,
        Conversation.intent_detected.in_(['symptoms', 'preventive', 'vaccination', 'emergency'])
    ).group_by(Conversation.intent_detected).all()
    
    # Active alerts impact
    active_alerts = HealthAlert.query.filter(
        HealthAlert.is_active == True,
        HealthAlert.created_at >= current_start
    ).count()
    
    return jsonify({
        'periods': {
            'baseline': {
                'start': baseline_start.isoformat(),
                'end': baseline_end.isoformat(),
                'days': baseline_days
            },
            'current': {
                'start': current_start.isoformat(),
                'end': current_end.isoformat(),
                'days': current_days
            }
        },
        'health_awareness_metrics': {
            'user_engagement_growth': round(user_growth, 2),
            'health_query_growth': round(query_growth, 2),
            'current_active_users': current_users,
            'current_health_queries': current_health_queries,
            'baseline_users': baseline_users,
            'baseline_health_queries': baseline_health_queries
        },
        'health_topic_engagement': [
            {'topic': topic, 'queries': count}
            for topic, count in health_topic_engagement
        ],
        'active_health_alerts': active_alerts,
        'awareness_improvement_target': {
            'target_percentage': 20,
            'current_achievement': min(round(user_growth, 2), 100),
            'status': 'on_track' if user_growth >= 15 else 'needs_improvement'
        }
    })

@bp.route('/accuracy', methods=['GET'])
def accuracy_metrics():
    """Get chatbot accuracy metrics"""
    
    days = int(request.args.get('days', 30))
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Overall accuracy metrics
    total_queries = Conversation.query.filter(
        Conversation.timestamp >= start_date,
        Conversation.confidence_score.isnot(None)
    ).count()
    
    high_confidence_queries = Conversation.query.filter(
        Conversation.timestamp >= start_date,
        Conversation.confidence_score >= 0.8
    ).count()
    
    medium_confidence_queries = Conversation.query.filter(
        Conversation.timestamp >= start_date,
        Conversation.confidence_score >= 0.5,
        Conversation.confidence_score < 0.8
    ).count()
    
    low_confidence_queries = Conversation.query.filter(
        Conversation.timestamp >= start_date,
        Conversation.confidence_score < 0.5
    ).count()
    
    overall_accuracy = (high_confidence_queries / total_queries * 100) if total_queries > 0 else 0
    
    # Accuracy by intent
    intent_accuracy = db.session.query(
        Conversation.intent_detected,
        func.avg(Conversation.confidence_score).label('avg_confidence'),
        func.count(Conversation.id).label('count')
    ).filter(
        Conversation.timestamp >= start_date,
        Conversation.confidence_score.isnot(None)
    ).group_by(Conversation.intent_detected).all()
    
    # Accuracy by language
    language_accuracy = db.session.query(
        User.preferred_language,
        func.avg(Conversation.confidence_score).label('avg_confidence'),
        func.count(Conversation.id).label('count')
    ).join(
        Conversation, User.id == Conversation.user_id
    ).filter(
        Conversation.timestamp >= start_date,
        Conversation.confidence_score.isnot(None)
    ).group_by(User.preferred_language).all()
    
    return jsonify({
        'period': {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'days': days
        },
        'overall_accuracy': {
            'accuracy_rate': round(overall_accuracy, 2),
            'total_queries': total_queries,
            'high_confidence': high_confidence_queries,
            'medium_confidence': medium_confidence_queries,
            'low_confidence': low_confidence_queries,
            'target_accuracy': 80,
            'target_achievement': 'achieved' if overall_accuracy >= 80 else 'in_progress'
        },
        'accuracy_by_intent': [
            {
                'intent': intent or 'unknown',
                'avg_confidence': round(float(avg_confidence), 3),
                'query_count': count,
                'accuracy_percentage': round(float(avg_confidence) * 100, 2)
            }
            for intent, avg_confidence, count in intent_accuracy
        ],
        'accuracy_by_language': [
            {
                'language': language,
                'avg_confidence': round(float(avg_confidence), 3),
                'query_count': count,
                'accuracy_percentage': round(float(avg_confidence) * 100, 2)
            }
            for language, avg_confidence, count in language_accuracy
        ]
    })

@bp.route('/export', methods=['GET'])
def export_analytics():
    """Export analytics data for external analysis"""
    
    days = int(request.args.get('days', 30))
    format_type = request.args.get('format', 'json')  # json or csv
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get conversation data for export
    conversations = db.session.query(
        Conversation.id,
        Conversation.message_text,
        Conversation.response_text,
        Conversation.intent_detected,
        Conversation.confidence_score,
        Conversation.channel,
        Conversation.timestamp,
        User.preferred_language,
        User.location
    ).join(
        User, Conversation.user_id == User.id
    ).filter(
        Conversation.timestamp >= start_date
    ).all()
    
    export_data = []
    for conv in conversations:
        export_data.append({
            'conversation_id': conv.id,
            'message_length': len(conv.message_text),
            'intent': conv.intent_detected,
            'confidence_score': float(conv.confidence_score) if conv.confidence_score else None,
            'channel': conv.channel,
            'language': conv.preferred_language,
            'location': conv.location,
            'timestamp': conv.timestamp.isoformat(),
            'date': conv.timestamp.date().isoformat(),
            'hour': conv.timestamp.hour
        })
    
    return jsonify({
        'export_metadata': {
            'export_date': datetime.utcnow().isoformat(),
            'period_start': start_date.isoformat(),
            'period_end': end_date.isoformat(),
            'total_records': len(export_data),
            'format': format_type
        },
        'data': export_data
    })