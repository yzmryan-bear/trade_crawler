#!/usr/bin/env python3
"""Simple test script to verify the pipeline works."""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.platforms.json_adapter import JSONAdapter
from src.models.message import Message
from src.models.trading_action import TradingAction, ActionType
from src.services.validator import ActionValidator
from src.storage.database import Database


def test_pipeline():
    """Test the basic pipeline without LLM (to avoid API costs)."""
    print("🧪 Testing Trading Action Extraction Pipeline...\n")
    
    # Test 1: JSON Adapter
    print("1. Testing JSON Adapter...")
    adapter = JSONAdapter("dc_tracker.json")
    adapter.connect()
    messages = adapter.get_messages(limit=3)
    print(f"   ✅ Loaded {len(messages)} messages")
    for msg in messages:
        print(f"      - {msg.sender}: {msg.message[:50]}...")
    
    # Test 2: Message Model
    print("\n2. Testing Message Model...")
    test_message = Message(
        sender="test_user",
        send_time="10/5/2024 12:25 PM",
        message="Buy 100 shares of AAPL at $150",
        platform="test"
    )
    print(f"   ✅ Message created: {test_message.sender}")
    print(f"      Dict: {test_message.to_dict()}")
    
    # Test 3: Trading Action Model
    print("\n3. Testing Trading Action Model...")
    test_action = TradingAction(
        action_type=ActionType.BUY,
        symbol="AAPL",
        price=150.0,
        quantity=100,
        confidence=0.95
    )
    print(f"   ✅ Action created: {test_action.action_type.value} {test_action.symbol}")
    print(f"      Valid: {test_action.is_valid()}")
    print(f"      Executable: {test_action.is_executable()}")
    
    # Test 4: Validator
    print("\n4. Testing Validator...")
    validator = ActionValidator(min_confidence=0.7)
    print(f"   ✅ Validator created")
    print(f"      Validates high confidence: {validator.validate(test_action)}")
    
    low_conf_action = TradingAction(
        action_type=ActionType.BUY,
        symbol="TSLA",
        confidence=0.5
    )
    print(f"      Validates low confidence: {validator.validate(low_conf_action)}")
    
    # Test 5: Database
    print("\n5. Testing Database...")
    db = Database("./data/test_pipeline.db")
    msg_id = db.save_message(test_message)
    action_id = db.save_trading_action(test_action, msg_id)
    print(f"   ✅ Saved message (ID: {msg_id}) and action (ID: {action_id})")
    
    stats = db.get_action_statistics()
    print(f"      Statistics: {stats}")
    
    # Cleanup
    os.remove("./data/test_pipeline.db")
    
    print("\n✅ All tests passed!")
    print("\n💡 To test with LLM extraction, run: python3 main.py")
    print("💡 To view dashboard, run: streamlit run streamlit_app.py")


if __name__ == "__main__":
    test_pipeline()

