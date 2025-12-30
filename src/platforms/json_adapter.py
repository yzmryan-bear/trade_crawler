"""JSON file adapter for reading messages from dc_tracker.json."""

import json
import os
from typing import List, Callable, Optional
from .base import BasePlatformAdapter
from ..models.message import Message


class JSONAdapter(BasePlatformAdapter):
    """Adapter for reading messages from a JSON file.
    
    Reads messages from dc_tracker.json file format:
    [
        {
            "sender": "sender_name",
            "send_time": "10/5/2024 12:25 PM",
            "message": "message content"
        },
        ...
    ]
    """
    
    def __init__(self, json_path: str):
        """Initialize JSON adapter.
        
        Args:
            json_path: Path to JSON file containing messages
        """
        self.json_path = json_path
        self._connected = False
        self._messages: List[Message] = []
        self._current_index = 0
    
    def connect(self) -> None:
        """Load messages from JSON file."""
        if not os.path.exists(self.json_path):
            raise FileNotFoundError(f"JSON file not found: {self.json_path}")
        
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert JSON data to Message objects
            self._messages = []
            for item in data:
                message = Message(
                    sender=item.get("sender", ""),
                    send_time=item.get("send_time", ""),
                    message=item.get("message", ""),
                    channel=None,  # JSON doesn't have channel info
                    message_id=None,  # JSON doesn't have message IDs
                    platform="json"
                )
                self._messages.append(message)
            
            self._connected = True
            self._current_index = 0
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON file: {e}")
        except Exception as e:
            raise ConnectionError(f"Failed to load JSON file: {e}")
    
    def disconnect(self) -> None:
        """Disconnect from JSON file."""
        self._connected = False
        self._messages = []
        self._current_index = 0
    
    def get_messages(self, limit: Optional[int] = None) -> List[Message]:
        """Retrieve messages from JSON file.
        
        Args:
            limit: Maximum number of messages to retrieve. None for all.
        
        Returns:
            List of Message objects
        """
        if not self._connected:
            self.connect()
        
        if limit is None:
            return self._messages.copy()
        else:
            return self._messages[:limit].copy()
    
    def listen(self, callback: Callable[[Message], None]) -> None:
        """Simulate listening by iterating through loaded messages.
        
        For JSON files, this iterates through all messages in order.
        For live platforms, this would listen for new messages.
        
        Args:
            callback: Function to call with each message
        """
        if not self._connected:
            self.connect()
        
        # Start from current index and process remaining messages
        for message in self._messages[self._current_index:]:
            callback(message)
            self._current_index += 1
    
    def reset(self) -> None:
        """Reset the adapter to start from beginning."""
        self._current_index = 0

