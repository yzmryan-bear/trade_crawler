"""Unit tests for trading action extraction."""

import unittest
from src.models.message import Message
from src.models.trading_action import TradingAction, ActionType
from src.services.validator import ActionValidator


class TestTradingAction(unittest.TestCase):
    """Test TradingAction model."""
    
    def test_valid_action(self):
        """Test valid trading action."""
        action = TradingAction(
            action_type=ActionType.BUY,
            symbol="AAPL",
            price=150.0,
            quantity=100,
            confidence=0.9
        )
        self.assertTrue(action.is_valid())
        self.assertTrue(action.is_executable())
    
    def test_invalid_action(self):
        """Test invalid trading action."""
        action = TradingAction(
            action_type=ActionType.UNKNOWN,
            symbol="",
            confidence=0.5
        )
        self.assertFalse(action.is_valid())
        self.assertFalse(action.is_executable())


class TestValidator(unittest.TestCase):
    """Test ActionValidator."""
    
    def setUp(self):
        """Set up test validator."""
        self.validator = ActionValidator(min_confidence=0.7)
    
    def test_validate_high_confidence(self):
        """Test validation with high confidence."""
        action = TradingAction(
            action_type=ActionType.BUY,
            symbol="TSLA",
            confidence=0.9
        )
        self.assertTrue(self.validator.validate(action))
    
    def test_validate_low_confidence(self):
        """Test validation with low confidence."""
        action = TradingAction(
            action_type=ActionType.BUY,
            symbol="TSLA",
            confidence=0.5
        )
        self.assertFalse(self.validator.validate(action))


if __name__ == "__main__":
    unittest.main()

