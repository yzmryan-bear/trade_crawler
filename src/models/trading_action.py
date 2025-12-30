"""Trading action data model for extracted trading actions."""

from dataclasses import dataclass
from typing import Optional
from enum import Enum


class ActionType(str, Enum):
    """Trading action types."""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    UNKNOWN = "unknown"


@dataclass
class TradingAction:
    """Represents an extracted trading action from a message."""
    
    action_type: ActionType
    symbol: str  # Stock symbol (e.g., "AAPL", "TSLA")
    price: Optional[float] = None  # Price per share (optional)
    quantity: Optional[int] = None  # Number of shares (optional)
    confidence: float = 0.0  # Confidence score 0.0-1.0
    message_id: Optional[str] = None  # Reference to original message
    raw_message: Optional[str] = None  # Original message text
    extracted_at: Optional[str] = None  # Timestamp when action was extracted
    action_signal_time: Optional[str] = None  # Message sending time (from original message)
    
    def to_dict(self) -> dict:
        """Convert trading action to dictionary."""
        return {
            "action_type": self.action_type.value,
            "symbol": self.symbol.upper(),  # Normalize to uppercase
            "price": self.price,
            "quantity": self.quantity,
            "confidence": self.confidence,
            "message_id": self.message_id,
            "raw_message": self.raw_message,
            "extracted_at": self.extracted_at,
            "action_signal_time": self.action_signal_time
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "TradingAction":
        """Create TradingAction from dictionary."""
        action_type_str = data.get("action_type", "unknown")
        try:
            action_type = ActionType(action_type_str.lower())
        except ValueError:
            action_type = ActionType.UNKNOWN
        
        return cls(
            action_type=action_type,
            symbol=data.get("symbol", "").upper(),
            price=data.get("price"),
            quantity=data.get("quantity"),
            confidence=data.get("confidence", 0.0),
            message_id=data.get("message_id"),
            raw_message=data.get("raw_message"),
            extracted_at=data.get("extracted_at"),
            action_signal_time=data.get("action_signal_time")
        )
    
    def is_valid(self) -> bool:
        """Check if the trading action has minimum required fields."""
        return (
            self.action_type != ActionType.UNKNOWN
            and bool(self.symbol)
            and len(self.symbol) >= 1
            and 0.0 <= self.confidence <= 1.0
        )
    
    def is_executable(self, min_confidence: float = 0.7) -> bool:
        """Check if action is executable (has required fields and meets confidence threshold)."""
        return (
            self.is_valid()
            and self.confidence >= min_confidence
            and self.action_type in [ActionType.BUY, ActionType.SELL]
        )

