from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from utils.database import Base

class Poll(Base):
    __tablename__ = 'polls'

    id = Column(Integer, primary_key=True)
    telegram_poll_id = Column(String, nullable=False)
    chat_id = Column(Integer, nullable=False)
    message_id = Column(Integer, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(String, nullable=False)  # 'active', 'completed', 'interrupted'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    responses = relationship("PollResponse", back_populates="poll", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Poll(id={self.id}, status='{self.status}')>"

class PollResponse(Base):
    __tablename__ = 'poll_responses'

    id = Column(Integer, primary_key=True)
    poll_id = Column(Integer, ForeignKey('polls.id'), nullable=False)
    user_id = Column(Integer, nullable=False)
    username = Column(String)
    response = Column(Text, nullable=False)
    responded_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    poll = relationship("Poll", back_populates="responses")

    def __repr__(self):
        return f"<PollResponse(id={self.id}, user_id={self.user_id})>" 