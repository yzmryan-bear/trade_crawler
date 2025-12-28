"""Message data model for representing messages from various platforms."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Message:
    """Represents a message from a platform (Discord, Telegram, JSON file, etc.)."""
    
    sender: str
    send_time: str  # Timestamp as string (e.g., "10/5/2024 12:25 PM")
    message: str  # Message content
    channel: Optional[str] = None  # Channel/group name (optional)
    message_id: Optional[str] = None  # Platform-specific message ID (optional)
    platform: Optional[str] = None  # Source platform (e.g., "json", "discord", "telegram")
    
    def to_dict(self) -> dict:
        """Convert message to dictionary."""
        return {
            "sender": self.sender,
            "send_time": self.send_time,
            "message": self.message,
            "channel": self.channel,
            "message_id": self.message_id,
            "platform": self.platform
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Message":
        """Create Message from dictionary."""
        return cls(
            sender=data.get("sender", ""),
            send_time=data.get("send_time", ""),
            message=data.get("message", ""),
            channel=data.get("channel"),
            message_id=data.get("message_id"),
            platform=data.get("platform")
        )
    
    def parse_time(self) -> Optional[datetime]:
        """Attempt to parse send_time string into datetime object."""
        # Common formats: "10/5/2024 12:25 PM", "10/5/2024 12:25:00 PM"
        try:
            # Try common date formats
            formats = [
                "%m/%d/%Y %I:%M %p",
                "%m/%d/%Y %I:%M:%S %p",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d %H:%M",
            ]
            for fmt in formats:
                try:
                    return datetime.strptime(self.send_time, fmt)
                except ValueError:
                    continue
            return None
        except Exception:
            return None

