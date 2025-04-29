from app import db
from datetime import datetime

class Resume(db.Model):
    """Model for storing resume information"""
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    candidate_name = db.Column(db.String(255), nullable=False)
    job_role = db.Column(db.String(255), nullable=True)
    skills = db.Column(db.Text, nullable=True)  # Stored as JSON string
    similarity_score = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Resume {self.filename}>'
