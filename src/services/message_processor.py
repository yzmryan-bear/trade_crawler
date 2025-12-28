"""Message processor service that orchestrates the extraction pipeline."""

from typing import List, Optional, Callable
from ..platforms.base import BasePlatformAdapter
from ..extractors.llm_extractor import LLMExtractor
from ..services.validator import ActionValidator
from ..storage.database import Database
from ..models.message import Message
from ..models.trading_action import TradingAction


class MessageProcessor:
    """Main service that orchestrates message processing, extraction, and storage."""
    
    def __init__(
        self,
        platform_adapter: BasePlatformAdapter,
        extractor: LLMExtractor,
        validator: ActionValidator,
        database: Database
    ):
        """Initialize message processor.
        
        Args:
            platform_adapter: Platform adapter for message source
            extractor: LLM extractor for trading actions
            validator: Action validator
            database: Database for storage
        """
        self.platform_adapter = platform_adapter
        self.extractor = extractor
        self.validator = validator
        self.database = database
        self._on_action_extracted: Optional[Callable[[TradingAction], None]] = None
    
    def set_action_callback(self, callback: Callable[[TradingAction], None]) -> None:
        """Set callback for when actions are extracted.
        
        Args:
            callback: Function to call with each extracted action
        """
        self._on_action_extracted = callback
    
    def process_message(self, message: Message) -> List[TradingAction]:
        """Process a single message: extract and validate actions.
        
        Args:
            message: Message to process
        
        Returns:
            List of validated trading actions
        """
        # Extract actions from message
        raw_actions = self.extractor.extract(message)
        
        # Validate actions
        valid_actions = self.validator.filter(raw_actions)
        
        # Save message to database
        message_db_id = self.database.save_message(message)
        
        # Save actions to database and trigger callbacks
        for action in valid_actions:
            self.database.save_trading_action(action, message_db_id)
            
            if self._on_action_extracted:
                self._on_action_extracted(action)
        
        return valid_actions
    
    def process_messages(self, messages: List[Message]) -> List[TradingAction]:
        """Process multiple messages.
        
        Args:
            messages: List of messages to process
        
        Returns:
            List of all validated trading actions
        """
        all_actions = []
        
        for message in messages:
            actions = self.process_message(message)
            all_actions.extend(actions)
        
        return all_actions
    
    def process_all(self, limit: Optional[int] = None) -> List[TradingAction]:
        """Process all messages from the platform adapter.
        
        Args:
            limit: Maximum number of messages to process (None for all)
        
        Returns:
            List of all validated trading actions
        """
        # Connect to platform
        if not self.platform_adapter.is_connected():
            self.platform_adapter.connect()
        
        # Get messages
        messages = self.platform_adapter.get_messages(limit=limit)
        
        # Process all messages
        return self.process_messages(messages)
    
    def start_listening(self) -> None:
        """Start listening for new messages and process them automatically."""
        if not self.platform_adapter.is_connected():
            self.platform_adapter.connect()
        
        def process_callback(message: Message):
            """Callback for new messages."""
            self.process_message(message)
        
        self.platform_adapter.listen(process_callback)

