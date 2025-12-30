#!/usr/bin/env python3
"""Export all messages with LLM extraction results for manual labeling."""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.storage.database import Database


def load_all_messages_from_json(json_path: str) -> List[Dict]:
    """Load all messages from dc_tracker.json."""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_message_actions_map(db: Database) -> Dict[int, List[Dict]]:
    """Get a map of message_id -> list of trading actions."""
    # Get all trading actions with their message_id
    conn = db._get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT ta.*, m.sender, m.send_time, m.message
        FROM trading_actions ta
        LEFT JOIN messages m ON ta.message_id = m.id
        ORDER BY ta.extracted_at DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    # Group actions by message_id
    actions_map = {}
    for row in rows:
        msg_id = row['message_id']
        if msg_id:
            if msg_id not in actions_map:
                actions_map[msg_id] = []
            actions_map[msg_id].append(dict(row))
    
    return actions_map


def find_database_message_id(
    json_message: Dict,
    db_messages: List[Dict]
) -> Optional[int]:
    """Find database message ID by matching sender, send_time, and message content."""
    json_sender = json_message.get("sender", "")
    json_send_time = json_message.get("send_time", "")
    json_message_text = json_message.get("message", "")
    
    # Try exact match first
    for db_msg in db_messages:
        if (db_msg.get("sender") == json_sender and
            db_msg.get("send_time") == json_send_time and
            db_msg.get("message") == json_message_text):
            return db_msg.get("id")
    
    # Try match by sender and send_time (in case message content differs slightly)
    for db_msg in db_messages:
        if (db_msg.get("sender") == json_sender and
            db_msg.get("send_time") == json_send_time):
            return db_msg.get("id")
    
    return None


def export_all_messages_for_labeling(
    json_path: str = "dc_tracker.json",
    output_file: str = "all_messages_for_labeling.xlsx"
):
    """Export all messages with LLM results for manual labeling."""
    
    print("📊 Loading messages and extraction results...")
    
    # Load all messages from JSON
    json_messages = load_all_messages_from_json(json_path)
    print(f"   Loaded {len(json_messages)} messages from {json_path}")
    
    # Load database
    db = Database()
    
    # Get all messages from database
    db_messages = db.get_recent_messages(limit=10000)
    print(f"   Found {len(db_messages)} messages in database")
    
    # Get all trading actions grouped by message_id
    actions_map = get_message_actions_map(db)
    print(f"   Found {sum(len(v) for v in actions_map.values())} trading actions")
    
    # Prepare Excel data
    excel_rows = []
    
    for idx, json_msg in enumerate(json_messages, 1):
        # Find corresponding database message
        db_msg_id = find_database_message_id(json_msg, db_messages)
        
        # Get trading actions for this message (if any)
        actions = actions_map.get(db_msg_id, []) if db_msg_id else []
        
        # Use the first action if multiple exist (or combine them)
        primary_action = actions[0] if actions else None
        
        # Prepare row data
        row = {
            # Message Information
            "Message ID": idx,
            "Sender": json_msg.get("sender", ""),
            "Send Time": json_msg.get("send_time", ""),
            "Message Content": json_msg.get("message", ""),
            "Original Message": json_msg.get("original_message", ""),
            
            # LLM Extraction Results
            "LLM Detected Signal?": "Yes" if primary_action else "No",
            "LLM Action Type": primary_action.get("action_type", "").upper() if primary_action else "",
            "LLM Symbol": primary_action.get("symbol", "") if primary_action else "",
            "LLM Price": primary_action.get("price", "") if primary_action else "",
            "LLM Quantity": primary_action.get("quantity", "") if primary_action else "",
            "LLM Confidence": round(primary_action.get("confidence", 0), 3) if primary_action else "",
            "LLM Signal Time": primary_action.get("action_signal_time", "") if primary_action else "",
            "LLM Extracted At": primary_action.get("extracted_at", "") if primary_action else "",
            "Number of Actions": len(actions),  # In case multiple actions per message
            
            # Manual Labeling Columns (empty for user to fill)
            "Manual: Is Trade Signal?": "",
            "Manual: Action Type": "",
            "Manual: Symbol": "",
            "Manual: Price": "",
            "Manual: Quantity": "",
            "Manual: Notes": "",
            "LLM Correct?": ""
        }
        
        excel_rows.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(excel_rows)
    
    # Create Excel file
    print(f"\n📝 Creating Excel file: {output_file}...")
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='All Messages for Labeling', index=False)
        
        # Get the worksheet to format it
        worksheet = writer.sheets['All Messages for Labeling']
        
        # Freeze first row
        worksheet.freeze_panes = 'A2'
        
        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    # Print summary
    total_messages = len(excel_rows)
    messages_with_signals = sum(1 for row in excel_rows if row["LLM Detected Signal?"] == "Yes")
    
    print(f"✅ Successfully exported to {output_file}")
    print(f"\n📊 Summary:")
    print(f"   Total messages: {total_messages}")
    print(f"   Messages with LLM signals: {messages_with_signals}")
    print(f"   Messages without signals: {total_messages - messages_with_signals}")
    print(f"\n📋 Columns included:")
    print(f"   - Message information (5 columns)")
    print(f"   - LLM extraction results (9 columns)")
    print(f"   - Manual labeling columns (7 columns)")
    print(f"\n💡 You can now open {output_file} in Excel to start manual labeling!")


if __name__ == "__main__":
    export_all_messages_for_labeling()

