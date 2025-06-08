from typing import List, Optional, Dict
from datetime import datetime, timedelta
import logging

from app.core.base_service import BaseService
from app.core.config import Config
from app.models.polls import Poll, PollOption, PollVote

logger = logging.getLogger(__name__)

class PollService(BaseService):
    """
    Service for managing polls and votes.
    """
    def __init__(self, config: Config):
        super().__init__(config)
        self._polls: Dict[int, Poll] = {}
        self._poll_timeout = self.get_config_value('poll_timeout', 3600)

    def initialize(self) -> None:
        """Initialize the poll service."""
        try:
            # Load existing polls from database
            self._load_polls()
            self._is_initialized = True
            self.log_info("Poll service initialized")
        except Exception as e:
            self.log_error("Failed to initialize poll service", e)
            raise

    def cleanup(self) -> None:
        """Clean up poll service resources."""
        self._polls.clear()
        self._is_initialized = False
        self.log_info("Poll service cleaned up")

    def _load_polls(self) -> None:
        """Load polls from the database."""
        # TODO: Implement database loading
        pass

    def create_poll(self, title: str, options: List[str], creator_id: int) -> Poll:
        """
        Create a new poll.
        
        Args:
            title: Poll title
            options: List of poll options
            creator_id: ID of the user creating the poll
            
        Returns:
            Created Poll object
        """
        try:
            poll = Poll(
                title=title,
                creator_id=creator_id,
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(seconds=self._poll_timeout)
            )
            
            # Add options
            for option_text in options:
                option = PollOption(text=option_text)
                poll.options.append(option)
            
            # TODO: Save to database
            self._polls[poll.id] = poll
            self.log_info(f"Created poll: {title}")
            
            return poll
        except Exception as e:
            self.log_error(f"Failed to create poll: {title}", e)
            raise

    def get_poll(self, poll_id: int) -> Optional[Poll]:
        """
        Get a poll by ID.
        
        Args:
            poll_id: ID of the poll to retrieve
            
        Returns:
            Poll object if found, None otherwise
        """
        try:
            return self._polls.get(poll_id)
        except Exception as e:
            self.log_error(f"Failed to get poll: {poll_id}", e)
            return None

    def add_vote(self, poll_id: int, option_id: int, user_id: int) -> bool:
        """
        Add a vote to a poll option.
        
        Args:
            poll_id: ID of the poll
            option_id: ID of the option to vote for
            user_id: ID of the user voting
            
        Returns:
            True if vote was added successfully, False otherwise
        """
        try:
            poll = self.get_poll(poll_id)
            if not poll:
                return False
                
            if poll.expires_at < datetime.utcnow():
                return False
                
            # Check if user already voted
            if any(vote.user_id == user_id for vote in poll.votes):
                return False
                
            # Add vote
            vote = PollVote(
                poll_id=poll_id,
                option_id=option_id,
                user_id=user_id,
                created_at=datetime.utcnow()
            )
            
            # TODO: Save to database
            poll.votes.append(vote)
            self.log_info(f"Added vote to poll {poll_id} by user {user_id}")
            
            return True
        except Exception as e:
            self.log_error(f"Failed to add vote to poll {poll_id}", e)
            return False

    def get_poll_results(self, poll_id: int) -> Optional[Dict[str, int]]:
        """
        Get the results of a poll.
        
        Args:
            poll_id: ID of the poll
            
        Returns:
            Dictionary mapping option text to vote count, or None if poll not found
        """
        try:
            poll = self.get_poll(poll_id)
            if not poll:
                return None
                
            results = {}
            for option in poll.options:
                vote_count = sum(1 for vote in poll.votes if vote.option_id == option.id)
                results[option.text] = vote_count
                
            return results
        except Exception as e:
            self.log_error(f"Failed to get poll results: {poll_id}", e)
            return None

    def cleanup_expired_polls(self) -> None:
        """Remove expired polls."""
        try:
            now = datetime.utcnow()
            expired_polls = [
                poll_id for poll_id, poll in self._polls.items()
                if poll.expires_at < now
            ]
            
            for poll_id in expired_polls:
                # TODO: Remove from database
                del self._polls[poll_id]
                
            if expired_polls:
                self.log_info(f"Cleaned up {len(expired_polls)} expired polls")
        except Exception as e:
            self.log_error("Failed to cleanup expired polls", e)
            raise 