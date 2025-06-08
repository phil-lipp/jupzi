from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from utils.database import Base

class Job(Base):
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # 'calendar_check', 'poll', etc.
    status = Column(String, nullable=False)  # 'pending', 'running', 'completed', 'failed'
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    next_run = Column(DateTime)  # For scheduled jobs
    cron_expression = Column(String)  # For scheduled jobs
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    metadata = relationship("JobMetadata", back_populates="job", cascade="all, delete-orphan")
    calendar_events = relationship("CalendarEvent", back_populates="job", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Job(id={self.id}, name='{self.name}', status='{self.status}')>"

class JobMetadata(Base):
    __tablename__ = 'job_metadata'

    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False)
    key = Column(String, nullable=False)
    value = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    job = relationship("Job", back_populates="metadata")

    def __repr__(self):
        return f"<JobMetadata(id={self.id}, key='{self.key}')>" 