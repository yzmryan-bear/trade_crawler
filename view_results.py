#!/usr/bin/env python3
"""Simple script to view extraction results."""

from src.storage.database import Database
import pandas as pd

db = Database()

# Get all actions
actions = db.get_recent_actions(limit=1000, min_confidence=0.0)
stats = db.get_action_statistics()

print("=" * 80)
print("📊 TRADING ACTIONS EXTRACTION RESULTS")
print("=" * 80)
print(f"\n📈 Statistics:")
print(f"   Total Actions: {stats['total_actions']}")
print(f"   Average Confidence: {stats['average_confidence']:.1%}")
print(f"   By Type: {stats['by_type']}")
if stats['top_symbols']:
    print(f"   Top Symbols: {dict(list(stats['top_symbols'].items())[:5])}")

print(f"\n📋 All Extracted Actions ({len(actions)} total):")
print("-" * 80)

# Create DataFrame for better display
df_data = []
for action in actions:
    df_data.append({
        'Action': action['action_type'].upper(),
        'Symbol': action.get('symbol', 'N/A'),
        'Price': f"${action.get('price', 'N/A')}" if action.get('price') else 'N/A',
        'Quantity': action.get('quantity', 'N/A'),
        'Confidence': f"{action.get('confidence', 0):.2f}",
        'Signal Time': action.get('action_signal_time', 'N/A'),
        'Sender': action.get('sender', 'N/A'),
        'Message': (action.get('message', '')[:50] + '...') if action.get('message') else 'N/A'
    })

df = pd.DataFrame(df_data)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', 50)

print(df.to_string(index=False))

print("\n" + "=" * 80)
print("💡 To view in interactive dashboard, run:")
print("   python3 -m streamlit run streamlit_app.py")
print("   Then open http://localhost:8501 in your browser")
print("=" * 80)

