"""Abstract base class for platform adapters."""

from abc import ABC, abstractmethod
from typing import List, Callable, Optional
from ..models.message import Message


class BasePlatformAdapter(ABC):
    """Abstract base class for all platform adapters.
    
    This interface ensures consistency across different message sources
    (JSON file, Discord, Telegram, etc.).
    """
    
    @abstractmethod
    def connect(self) -> None:
        """Connect to the message source.
        
        Raises:
            ConnectionError: If connection fails
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the message source."""
        pass
    
    @abstractmethod
    def get_messages(self, limit: Optional[int] = None) -> List[Message]:
        """Retrieve messages from the platform.
        
        Args:
            limit: Maximum number of messages to retrieve. None for all available.
        
        Returns:
            List of Message objects
        """
        pass
    
    @abstractmethod
    def listen(self, callback: Callable[[Message], None]) -> None:
        """Listen for new messages and call callback for each.
        
        Args:
            callback: Function to call with each new message
        """
        pass
    
    def is_connected(self) -> bool:
        """Check if adapter is connected.
        
        Returns:
            True if connected, False otherwise
        """
        # Default implementation - subclasses can override
        return hasattr(self, '_connected') and self._connected

