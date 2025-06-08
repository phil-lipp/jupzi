from datetime import datetime, UTC
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Index, CheckConstraint
from sqlalchemy.orm import relationship

from utils.database import Base

class Job(Base):
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # 'calendar_check', 'poll', etc.
    status = Column(String(20), nullable=False)  # 'pending', 'running', 'completed', 'failed'
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    next_run = Column(DateTime)  # For scheduled jobs
    cron_expression = Column(String(100))  # For scheduled jobs
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime)

    # Relationships
    metadata = relationship("JobMetadata", back_populates="job", cascade="all, delete-orphan")
    calendar_events = relationship("CalendarEvent", back_populates="job", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_job_status', 'status'),
        Index('idx_job_type', 'type'),
        Index('idx_job_next_run', 'next_run'),
        Index('idx_job_created_at', 'created_at'),
        CheckConstraint("status IN ('pending', 'running', 'completed', 'failed')", name='valid_job_status'),
        CheckConstraint("type IN ('calendar_check', 'poll')", name='valid_job_type'),
    )

    def __repr__(self):
        return f"<Job(id={self.id}, name='{self.name}', status='{self.status}')>"

    def soft_delete(self):
        """Soft delete the job by marking it as deleted."""
        self.is_deleted = True
        self.deleted_at = datetime.now(UTC)

class JobMetadata(Base):
    __tablename__ = 'job_metadata'

    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False)
    key = Column(String(100), nullable=False)
    value = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    job = relationship("Job", back_populates="metadata")

    # Indexes
    __table_args__ = (
        Index('idx_job_metadata_key', 'key'),
        Index('idx_job_metadata_job_id', 'job_id'),
    )

    def __repr__(self):
        return f"<JobMetadata(id={self.id}, key='{self.key}')>" 