"""Validator for trading actions."""

from typing import List
from ..models.trading_action import TradingAction, ActionType


class ActionValidator:
    """Validates and filters trading actions."""
    
    def __init__(self, min_confidence: float = 0.7):
        """Initialize validator.
        
        Args:
            min_confidence: Minimum confidence threshold for valid actions
        """
        self.min_confidence = min_confidence
    
    def validate(self, action: TradingAction) -> bool:
        """Validate a single trading action.
        
        Args:
            action: TradingAction to validate
        
        Returns:
            True if action is valid, False otherwise
        """
        # Check basic validity
        if not action.is_valid():
            return False
        
        # Check confidence threshold
        if action.confidence < self.min_confidence:
            return False
        
        # Validate symbol format (basic check)
        if not self._is_valid_symbol(action.symbol):
            return False
        
        # Validate price if present
        if action.price is not None and action.price <= 0:
            return False
        
        # Validate quantity if present
        if action.quantity is not None and action.quantity <= 0:
            return False
        
        return True
    
    def filter(self, actions: List[TradingAction]) -> List[TradingAction]:
        """Filter list of actions, keeping only valid ones.
        
        Args:
            actions: List of TradingAction objects
        
        Returns:
            Filtered list of valid actions
        """
        return [action for action in actions if self.validate(action)]
    
    def _is_valid_symbol(self, symbol: str) -> bool:
        """Check if stock symbol format is valid.
        
        Args:
            symbol: Stock symbol to validate
        
        Returns:
            True if symbol format is valid
        """
        if not symbol or len(symbol) < 1:
            return False
        
        # Basic validation: 1-5 uppercase letters/numbers
        # Common formats: AAPL, TSLA, QQQ, SPY, etc.
        if len(symbol) > 10:  # Reasonable max length
            return False
        
        # Should be alphanumeric
        if not symbol.replace(".", "").isalnum():
            return False
        
        return True
    
    def get_executable_actions(self, actions: List[TradingAction]) -> List[TradingAction]:
        """Get actions that are executable (buy/sell with sufficient confidence).
        
        Args:
            actions: List of TradingAction objects
        
        Returns:
            List of executable actions
        """
        return [
            action for action in actions
            if action.is_executable(self.min_confidence) and self.validate(action)
        ]

