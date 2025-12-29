#!/usr/bin/env python3
"""Translate messages in dc_tracker.json from Chinese to English."""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    print("Error: OpenAI library not available. Install with: pip install openai")
    sys.exit(1)

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def translate_with_openai(text: str, client: OpenAI) -> str:
    """Translate text from Chinese to English using OpenAI."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a translator. Translate the following Chinese text to English. Only return the translation, no explanations. Preserve any stock symbols, numbers, and technical terms."
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Translation error: {e}")
        return text


def has_chinese(text: str) -> bool:
    """Check if text contains Chinese characters."""
    return bool(re.search(r'[\u4e00-\u9fff]', text))


def translate_messages(messages: List[Dict], api_key: str) -> List[Dict]:
    """Translate messages from Chinese to English."""
    client = OpenAI(api_key=api_key)
    translated = []
    
    print(f"Translating {len(messages)} messages...")
    for i, msg in enumerate(messages):
        if (i + 1) % 10 == 0:
            print(f"  Progress: {i + 1}/{len(messages)}")
        
        original_text = msg.get("message", "")
        if not original_text:
            translated.append(msg)
            continue
        
        # Check if text contains Chinese
        if has_chinese(original_text):
            try:
                translated_text = translate_with_openai(original_text, client)
                # Update message with English translation, keep original
                msg["message"] = translated_text
                msg["original_message"] = original_text
            except Exception as e:
                print(f"Translation error for message {i+1}: {e}")
                msg["message"] = original_text
        else:
            # Already in English or no Chinese characters
            msg["message"] = original_text
        
        translated.append(msg)
    
    return translated


def main():
    json_path = "dc_tracker.json"
    output_path = "dc_tracker.json"
    
    # Check if JSON exists
    if not os.path.exists(json_path):
        print(f"Error: JSON file not found: {json_path}")
        print(f"Looking in: {os.path.abspath(json_path)}")
        return
    
    # Get API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not set.")
        print("\nTo translate messages, set your OpenAI API key:")
        print("  export OPENAI_API_KEY='your-key-here'")
        print("\nOr create a .env file in the project root with:")
        print("  OPENAI_API_KEY=your-key-here")
        print("\nThen run this script again.")
        return
    
    print(f"Loading messages from {json_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        messages = json.load(f)
    
    print(f"Loaded {len(messages)} messages")
    
    # Translate messages
    print("Translating messages to English...")
    translated_messages = translate_messages(messages, api_key)
    
    # Save translated messages
    print(f"Saving translated messages to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(translated_messages, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Successfully translated {len(translated_messages)} messages")
    print(f"Sample translated message:")
    if translated_messages:
        sample = translated_messages[1] if len(translated_messages) > 1 else translated_messages[0]
        print(json.dumps(sample, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

