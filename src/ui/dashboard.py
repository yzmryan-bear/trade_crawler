"""Streamlit dashboard for monitoring messages and trading actions."""

import streamlit as st
import pandas as pd
from typing import Optional
from ..storage.database import Database
from ..models.trading_action import ActionType


def render_dashboard(db: Database):
    """Render the Streamlit dashboard.
    
    Args:
        db: Database instance
    """
    st.set_page_config(
        page_title="Trading Action Monitor",
        page_icon="📈",
        layout="wide"
    )
    
    st.title("📈 Trading Action Extraction Monitor")
    
    # Sidebar filters
    st.sidebar.header("Filters")
    min_confidence = st.sidebar.slider(
        "Minimum Confidence",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.05
    )
    
    action_type_filter = st.sidebar.selectbox(
        "Action Type",
        options=["All", "Buy", "Sell", "Hold", "Unknown"]
    )
    
    limit = st.sidebar.number_input(
        "Number of Results",
        min_value=10,
        max_value=1000,
        value=100,
        step=10
    )
    
    # Statistics
    stats = db.get_action_statistics()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Actions", stats["total_actions"])
    with col2:
        st.metric("Avg Confidence", f"{stats['average_confidence']:.2%}")
    with col3:
        buy_count = stats["by_type"].get("buy", 0)
        st.metric("Buy Actions", buy_count)
    with col4:
        sell_count = stats["by_type"].get("sell", 0)
        st.metric("Sell Actions", sell_count)
    
    # Recent Trading Actions
    st.header("Recent Trading Actions")
    
    actions = db.get_recent_actions(limit=limit, min_confidence=min_confidence)
    
    # Filter by action type
    if action_type_filter != "All":
        actions = [
            a for a in actions
            if a.get("action_type", "").lower() == action_type_filter.lower()
        ]
    
    if actions:
        # Prepare data for display
        df_data = []
        for action in actions:
            df_data.append({
                "Time": action.get("extracted_at", "")[:19] if action.get("extracted_at") else "",
                "Action": action.get("action_type", "").upper(),
                "Symbol": action.get("symbol", ""),
                "Price": f"${action.get('price', 0):.2f}" if action.get("price") else "N/A",
                "Quantity": action.get("quantity") or "N/A",
                "Confidence": f"{action.get('confidence', 0):.1%}",
                "Sender": action.get("sender", ""),
                "Message": action.get("message", "")[:100] + "..." if len(action.get("message", "")) > 100 else action.get("message", "")
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No trading actions found with the current filters.")
    
    # Recent Messages
    with st.expander("Recent Messages"):
        messages = db.get_recent_messages(limit=50)
        if messages:
            for msg in messages[:10]:  # Show first 10
                st.text(f"[{msg.get('send_time', '')}] {msg.get('sender', '')}: {msg.get('message', '')[:200]}")
        else:
            st.info("No messages in database.")
    
    # Top Symbols
    if stats.get("top_symbols"):
        st.header("Most Traded Symbols")
        symbols_df = pd.DataFrame([
            {"Symbol": symbol, "Count": count}
            for symbol, count in stats["top_symbols"].items()
        ])
        st.bar_chart(symbols_df.set_index("Symbol"))

