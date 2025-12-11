"""
Analytics model for tracking website usage
"""
from datetime import datetime, timedelta
from .database import db
from sqlalchemy import func

class PageView(db.Model):
    """Track page views"""
    __tablename__ = 'page_views'
    
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(255), nullable=False, default='/')
    ip_hash = db.Column(db.String(64), nullable=True)  # Hashed for privacy
    user_agent = db.Column(db.String(500), nullable=True)
    referrer = db.Column(db.String(500), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    @classmethod
    def log_view(cls, path='/', ip_hash=None, user_agent=None, referrer=None):
        """Log a page view"""
        view = cls(
            path=path,
            ip_hash=ip_hash,
            user_agent=user_agent,
            referrer=referrer
        )
        db.session.add(view)
        db.session.commit()
        return view
    
    @classmethod
    def get_stats(cls, days=30):
        """Get analytics stats for the last N days"""
        since = datetime.utcnow() - timedelta(days=days)
        
        # Total views
        total_views = cls.query.filter(cls.created_at >= since).count()
        
        # Unique visitors (by IP hash)
        unique_visitors = db.session.query(
            func.count(func.distinct(cls.ip_hash))
        ).filter(cls.created_at >= since).scalar() or 0
        
        # Views by day
        views_by_day = db.session.query(
            func.date(cls.created_at).label('date'),
            func.count(cls.id).label('views')
        ).filter(cls.created_at >= since).group_by(
            func.date(cls.created_at)
        ).order_by(func.date(cls.created_at)).all()
        
        # Top referrers
        top_referrers = db.session.query(
            cls.referrer,
            func.count(cls.id).label('count')
        ).filter(
            cls.created_at >= since,
            cls.referrer.isnot(None),
            cls.referrer != ''
        ).group_by(cls.referrer).order_by(
            func.count(cls.id).desc()
        ).limit(10).all()
        
        return {
            'total_views': total_views,
            'unique_visitors': unique_visitors,
            'views_by_day': [{'date': str(v.date), 'views': v.views} for v in views_by_day],
            'top_referrers': [{'referrer': r.referrer, 'count': r.count} for r in top_referrers]
        }


class UsageEvent(db.Model):
    """Track specific usage events"""
    __tablename__ = 'usage_events'
    
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), nullable=False)
    # Event types: 'resume_generated', 'job_analyzed', 'payment_started', 'payment_completed'
    user_email = db.Column(db.String(255), nullable=True)
    event_metadata = db.Column(db.Text, nullable=True)  # JSON string for extra data
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    @classmethod
    def log_event(cls, event_type, user_email=None, event_metadata=None):
        """Log a usage event"""
        import json
        event = cls(
            event_type=event_type,
            user_email=user_email,
            event_metadata=json.dumps(event_metadata) if event_metadata else None
        )
        db.session.add(event)
        db.session.commit()
        return event
    
    @classmethod
    def get_event_stats(cls, days=30):
        """Get event statistics"""
        since = datetime.utcnow() - timedelta(days=days)
        
        # Count by event type
        event_counts = db.session.query(
            cls.event_type,
            func.count(cls.id).label('count')
        ).filter(cls.created_at >= since).group_by(
            cls.event_type
        ).all()
        
        # Events by day
        events_by_day = db.session.query(
            func.date(cls.created_at).label('date'),
            cls.event_type,
            func.count(cls.id).label('count')
        ).filter(cls.created_at >= since).group_by(
            func.date(cls.created_at),
            cls.event_type
        ).order_by(func.date(cls.created_at)).all()
        
        return {
            'event_counts': {e.event_type: e.count for e in event_counts},
            'events_by_day': [
                {'date': str(e.date), 'event': e.event_type, 'count': e.count}
                for e in events_by_day
            ]
        }

