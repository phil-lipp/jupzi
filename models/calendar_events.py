from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date, Time
from sqlalchemy.orm import relationship

from utils.database import Base

class CalendarEvent(Base):
    __tablename__ = 'calendar_events'

    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False)
    event_date = Column(Date, nullable=False)
    event_time = Column(Time)
    event_summary = Column(String)
    event_location = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    job = relationship("Job", back_populates="calendar_events")

    def __repr__(self):
        return f"<CalendarEvent(id={self.id}, date='{self.event_date}')>" 