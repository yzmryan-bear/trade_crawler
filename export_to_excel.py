#!/usr/bin/env python3
"""Export all trading actions to Excel file."""

from src.storage.database import Database
import pandas as pd
from datetime import datetime

def export_to_excel(output_file="trading_actions_results.xlsx"):
    """Export all trading actions to Excel."""
    
    db = Database()
    
    # Get all actions
    actions = db.get_recent_actions(limit=10000, min_confidence=0.0)
    stats = db.get_action_statistics()
    
    print(f"📊 Exporting {len(actions)} trading actions to Excel...")
    
    # Prepare data for Excel
    excel_data = []
    for action in actions:
        excel_data.append({
            'Action Type': action['action_type'].upper(),
            'Symbol': action.get('symbol', ''),
            'Price': action.get('price', ''),
            'Quantity': action.get('quantity', ''),
            'Confidence': round(action.get('confidence', 0), 3),
            'Signal Time': action.get('action_signal_time', ''),
            'Extracted At': action.get('extracted_at', ''),
            'Sender': action.get('sender', ''),
            'Message Send Time': action.get('send_time', ''),
            'Original Message': action.get('message', ''),
            'Raw Message': action.get('raw_message', ''),
            'Message ID': action.get('message_id', ''),
            'Action ID': action.get('id', '')
        })
    
    # Create DataFrame
    df = pd.DataFrame(excel_data)
    
    # Create Excel writer with multiple sheets
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Main sheet with all actions
        df.to_excel(writer, sheet_name='All Actions', index=False)
        
        # Summary statistics sheet
        summary_data = {
            'Metric': [
                'Total Actions',
                'Average Confidence',
                'Buy Actions',
                'Sell Actions',
                'Hold Actions',
                'Unknown Actions',
                'Actions with Price',
                'Actions with Quantity',
                'Top Symbols'
            ],
            'Value': [
                stats['total_actions'],
                f"{stats['average_confidence']:.1%}",
                stats['by_type'].get('buy', 0),
                stats['by_type'].get('sell', 0),
                stats['by_type'].get('hold', 0),
                stats['by_type'].get('unknown', 0),
                len(df[df['Price'].notna() & (df['Price'] != '')]),
                len(df[df['Quantity'].notna() & (df['Quantity'] != '')]),
                ', '.join([f"{k}({v})" for k, v in list(stats['top_symbols'].items())[:10]])
            ]
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
        
        # Filtered sheets
        if len(df[df['Action Type'] == 'BUY']) > 0:
            df[df['Action Type'] == 'BUY'].to_excel(writer, sheet_name='Buy Actions', index=False)
        
        if len(df[df['Action Type'] == 'SELL']) > 0:
            df[df['Action Type'] == 'SELL'].to_excel(writer, sheet_name='Sell Actions', index=False)
        
        # High confidence actions (>= 0.8)
        high_conf = df[df['Confidence'] >= 0.8]
        if len(high_conf) > 0:
            high_conf.to_excel(writer, sheet_name='High Confidence (>=0.8)', index=False)
    
    print(f"✅ Successfully exported to {output_file}")
    print(f"   Total actions: {len(actions)}")
    print(f"   Sheets created:")
    print(f"     - All Actions: {len(df)} rows")
    print(f"     - Summary: Statistics")
    if len(df[df['Action Type'] == 'BUY']) > 0:
        print(f"     - Buy Actions: {len(df[df['Action Type'] == 'BUY'])} rows")
    if len(df[df['Action Type'] == 'SELL']) > 0:
        print(f"     - Sell Actions: {len(df[df['Action Type'] == 'SELL'])} rows")
    if len(high_conf) > 0:
        print(f"     - High Confidence (>=0.8): {len(high_conf)} rows")
    
    return output_file


if __name__ == "__main__":
    output_file = export_to_excel()
    print(f"\n📁 File saved: {output_file}")
    print("   You can open it in Excel or Google Sheets")

