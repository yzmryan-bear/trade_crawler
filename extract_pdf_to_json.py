#!/usr/bin/env python3
"""
Extract messages from PDF and convert to JSON format.
Extracts: sender name, sending time, and message content.
Translates messages from Chinese to English.
"""

import json
import re
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False
    try:
        import PyPDF2
        HAS_PYPDF2 = True
    except ImportError:
        HAS_PYPDF2 = False

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    print("Warning: OpenAI library not available. Install with: pip install openai")

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not required, can use system env vars


def extract_text_with_pdfplumber(pdf_path: str) -> str:
    """Extract all text from PDF using pdfplumber."""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def extract_text_with_pypdf2(pdf_path: str) -> str:
    """Extract all text from PDF using PyPDF2."""
    text = ""
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
    return text


def parse_messages(text: str) -> List[Dict]:
    """
    Parse messages from Discord export format.
    Pattern: "sender MM/DD/YYYY HH:MM AM/PM" followed by message content.
    """
    messages = []
    lines = text.split('\n')
    
    # Pattern to match: "sender date time"
    # Examples: "yuanzidan 10/5/2024 12:25 PM", "Microfund(Jeffrey) ID 10/5/2024 12:23 PM"
    message_pattern = re.compile(
        r'^([^\d]+?)\s+(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}:\d{2}\s*(?:AM|PM))',
        re.IGNORECASE
    )
    
    current_message = None
    current_content = []
    skip_patterns = [
        r'^file:///',  # File paths
        r'^\d+/\d+/\d+,\s+\d+:\d+\s+PM',  # Page headers like "8/22/25, 10:13 PM"
        r'^Exported \d+ message',  # Footer
        r'^Timezone:',  # Footer
        r'^Image attachment',  # Image markers
        r'^\d+\s+\d+$',  # Reaction counts like "29 10"
        r'^Microfund Capital Growth',  # Headers
        r'^嘉宾分享',  # Headers
    ]
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # Skip header/footer lines
        should_skip = False
        for pattern in skip_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                should_skip = True
                break
        if should_skip:
            continue
        
        # Check if this line starts a new message
        match = message_pattern.match(line)
        if match:
            # Save previous message if exists
            if current_message and current_content:
                current_message['message'] = '\n'.join(current_content).strip()
                if current_message['message']:  # Only add if has content
                    messages.append(current_message)
            
            # Start new message
            sender = match.group(1).strip()
            date_str = match.group(2)
            time_str = match.group(3)
            
            # Extract message content from the same line (after timestamp)
            remaining = line[match.end():].strip()
            
            current_message = {
                'sender': sender,
                'send_time': f"{date_str} {time_str}",
                'message': ''
            }
            current_content = []
            
            if remaining:
                current_content.append(remaining)
        else:
            # Continue current message
            if current_message:
                # Skip lines that are just numbers (reactions)
                if not re.match(r'^\d+$', line):
                    current_content.append(line)
    
    # Add last message
    if current_message and current_content:
        current_message['message'] = '\n'.join(current_content).strip()
        if current_message['message']:
            messages.append(current_message)
    
    return messages


def translate_with_openai(text: str, client: OpenAI) -> str:
    """Translate text from Chinese to English using OpenAI."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Using mini for cost efficiency
            messages=[
                {
                    "role": "system",
                    "content": "You are a translator. Translate the following Chinese text to English. Only return the translation, no explanations."
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


def translate_messages(messages: List[Dict], api_key: Optional[str] = None) -> List[Dict]:
    """Translate messages from Chinese to English using OpenAI."""
    if not HAS_OPENAI:
        print("OpenAI library not available. Messages will not be translated.")
        return messages
    
    if not api_key:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("Warning: OPENAI_API_KEY not set. Messages will not be translated.")
            print("Set it in environment or .env file, or pass as argument.")
            return messages
    
    client = OpenAI(api_key=api_key)
    translated = []
    
    print(f"Translating {len(messages)} messages...")
    for i, msg in enumerate(messages):
        if (i + 1) % 10 == 0:
            print(f"  Progress: {i + 1}/{len(messages)}")
        
        original_text = msg.get('message', '')
        if not original_text:
            translated.append(msg)
            continue
        
        # Check if text contains Chinese characters
        has_chinese = bool(re.search(r'[\u4e00-\u9fff]', original_text))
        
        if has_chinese:
            try:
                translated_text = translate_with_openai(original_text, client)
                msg['message'] = translated_text
                msg['original_message'] = original_text  # Keep original
            except Exception as e:
                print(f"Translation error for message {i+1}: {e}")
                msg['message'] = original_text
        else:
            # Already in English or no Chinese characters
            msg['message'] = original_text
        
        translated.append(msg)
    
    return translated


def main():
    import sys
    
    pdf_path = "2024:10-2025:08_yuanzidan_dc_track.pdf"
    output_path = "dc_tracker.json"
    
    # Check if PDF exists
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found: {pdf_path}")
        return
    
    print(f"Extracting text from PDF: {pdf_path}")
    
    # Extract text from PDF
    if HAS_PDFPLUMBER:
        print("Using pdfplumber...")
        try:
            text = extract_text_with_pdfplumber(pdf_path)
        except Exception as e:
            print(f"Error with pdfplumber: {e}")
            if HAS_PYPDF2:
                print("Trying PyPDF2 instead...")
                text = extract_text_with_pypdf2(pdf_path)
            else:
                raise
    elif HAS_PYPDF2:
        print("Using PyPDF2...")
        text = extract_text_with_pypdf2(pdf_path)
    else:
        print("Error: No PDF library available. Please install one:")
        print("  pip install pdfplumber")
        print("  OR")
        print("  pip install PyPDF2")
        return
    
    print(f"Extracted {len(text)} characters")
    
    # Save raw text for inspection
    sample_path = "pdf_extracted_text_sample.txt"
    with open(sample_path, "w", encoding="utf-8") as f:
        f.write(text[:10000])  # First 10000 chars for inspection
    print(f"Saved sample text to {sample_path} for inspection")
    
    # Parse messages
    print("Parsing messages...")
    messages = parse_messages(text)
    print(f"Parsed {len(messages)} messages")
    
    if not messages:
        print("Warning: No messages parsed. Check the PDF format.")
        print(f"Please inspect {sample_path} to understand the format.")
        return
    
    # Translate messages
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print("Translating messages to English using OpenAI...")
        messages = translate_messages(messages, api_key=api_key)
    else:
        print("Warning: OPENAI_API_KEY not set. Skipping translation.")
        print("Set OPENAI_API_KEY environment variable to enable translation.")
        print("Messages will be saved with original Chinese text.")
    
    # Save to JSON
    print(f"Saving to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Successfully extracted {len(messages)} messages to {output_path}")
    if messages:
        print(f"\nSample message:")
        print(json.dumps(messages[0], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
