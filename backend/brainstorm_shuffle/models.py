from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from . import db

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action_id = db.Column(db.Integer, nullable=False)
    action_data = db.Column(db.String(2048), nullable=False)
    user_name = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

