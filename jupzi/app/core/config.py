import os
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseSettings, Field, validator, root_validator

class Config(BaseSettings):
    """
    Configuration settings for the bot.
    Uses pydantic for validation and environment variable loading.
    """
    # Environment
    environment: str = Field(default='development', env='ENVIRONMENT')
    
    # Bot settings
    bot_token: str = Field(..., env='BOT_TOKEN')
    admin_chat_id: int = Field(..., env='ADMIN_CHAT_ID')
    
    # Database settings
    database_url: str = Field(..., env='DATABASE_URL')
    database_pool_size: int = Field(default=5, env='DATABASE_POOL_SIZE')
    database_max_overflow: int = Field(default=10, env='DATABASE_MAX_OVERFLOW')
    database_pool_timeout: int = Field(default=30, env='DATABASE_POOL_TIMEOUT')
    
    # State management
    state_file_path: str = Field(
        default='data/bot_state.json',
        env='STATE_FILE_PATH'
    )
    
    # Logging
    log_level: str = Field(default='INFO', env='LOG_LEVEL')
    log_file: Optional[str] = Field(default=None, env='LOG_FILE')
    log_rotation: str = Field(default='1 day', env='LOG_ROTATION')
    log_retention: str = Field(default='7 days', env='LOG_RETENTION')
    
    # Calendar settings
    calendar_check_interval: int = Field(
        default=300,  # 5 minutes
        env='CALENDAR_CHECK_INTERVAL'
    )
    
    # Poll settings
    poll_timeout: int = Field(
        default=3600,  # 1 hour
        env='POLL_TIMEOUT'
    )
    
    # Security
    allowed_chat_ids: list[int] = Field(default_factory=list, env='ALLOWED_CHAT_IDS')
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        
    @validator('environment')
    def validate_environment(cls, v):
        allowed = {'development', 'staging', 'production'}
        if v not in allowed:
            raise ValueError(f'Environment must be one of {allowed}')
        return v
    
    @validator('log_level')
    def validate_log_level(cls, v):
        allowed = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
        if v.upper() not in allowed:
            raise ValueError(f'Log level must be one of {allowed}')
        return v.upper()
    
    @root_validator
    def validate_config(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration values."""
        if values['environment'] == 'production':
            if not values['log_file']:
                raise ValueError('Log file must be specified in production environment')
            if not values['allowed_chat_ids']:
                raise ValueError('Allowed chat IDs must be specified in production environment')
        return values
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure state file directory exists
        Path(self.state_file_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Ensure log directory exists if log file is specified
        if self.log_file:
            Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def from_env(cls) -> 'Config':
        """
        Create a Config instance from environment variables.
        
        Returns:
            Config: A new Config instance
        """
        return cls() 