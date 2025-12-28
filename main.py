#!/usr/bin/env python3
"""Main entry point for Trading Action Extraction Agent."""

import os
import sys
import yaml
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.platforms.json_adapter import JSONAdapter
from src.extractors.llm_extractor import LLMExtractor
from src.services.validator import ActionValidator
from src.services.message_processor import MessageProcessor
from src.storage.database import Database


def load_config():
    """Load configuration from config.yaml."""
    config_path = Path("config/config.yaml")
    if not config_path.exists():
        # Try example file
        config_path = Path("config/config.yaml.example")
        if not config_path.exists():
            return {}
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f) or {}


def main():
    """Main function."""
    print("🚀 Starting Trading Action Extraction Agent...")
    
    # Load configuration
    config = load_config()
    
    # Get settings with defaults
    json_path = config.get("json", {}).get("file_path", "dc_tracker.json")
    db_path = config.get("database", {}).get("path", "./data/trading_actions.db")
    min_confidence = config.get("extraction", {}).get("confidence_threshold", 0.7)
    llm_model = config.get("extraction", {}).get("llm_model", "gpt-4o-mini")
    llm_provider = config.get("extraction", {}).get("llm_provider", "openai")
    
    # Initialize components
    print("📂 Initializing components...")
    
    # Platform adapter
    adapter = JSONAdapter(json_path)
    
    # Database
    database = Database(db_path)
    
    # LLM Extractor
    try:
        extractor = LLMExtractor(
            model=llm_model,
            provider=llm_provider
        )
    except Exception as e:
        print(f"❌ Error initializing LLM extractor: {e}")
        print("💡 Make sure you have set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable")
        return
    
    # Validator
    validator = ActionValidator(min_confidence=min_confidence)
    
    # Message processor
    processor = MessageProcessor(
        platform_adapter=adapter,
        extractor=extractor,
        validator=validator,
        database=database
    )
    
    # Process messages
    print(f"📊 Processing messages from {json_path}...")
    try:
        actions = processor.process_all()
        print(f"✅ Processed messages and extracted {len(actions)} trading actions")
        
        # Show statistics
        stats = database.get_action_statistics()
        print(f"\n📈 Statistics:")
        print(f"   Total actions: {stats['total_actions']}")
        print(f"   Average confidence: {stats['average_confidence']:.1%}")
        print(f"   By type: {stats['by_type']}")
        
    except Exception as e:
        print(f"❌ Error processing messages: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n✅ Processing complete!")
    print("💡 Run 'streamlit run src/ui/dashboard.py' to view the dashboard")


if __name__ == "__main__":
    main()

