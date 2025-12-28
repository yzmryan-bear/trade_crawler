# Trading Action Extraction Agent

An agentic application that extracts trading actions (buy/sell, stock symbols, prices) from expert messages in Discord/Telegram channels, with initial testing support via JSON message file (dc_tracker.json).

## Project Structure

```
follow_trader/
├── src/
│   ├── platforms/      # Platform adapters (JSON, Discord, Telegram)
│   ├── extractors/     # Trading action extraction logic
│   ├── models/         # Data models (Message, TradingAction)
│   ├── storage/        # Database layer
│   ├── services/       # Business logic services
│   └── ui/             # User interface (Streamlit dashboard)
├── config/             # Configuration files
├── scripts/            # Utility scripts (PDF extraction, etc.)
├── data/               # Data files (database, etc.)
├── tests/              # Unit tests
├── dc_tracker.json     # Pre-extracted messages (619 messages)
├── requirements.txt    # Python dependencies
└── main.py            # Application entry point (to be created)
```

## Setup Instructions

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   - Copy `.env.example` to `.env` (or create manually)
   - Add your LLM API key (OpenAI or Anthropic)

3. **Configure the application:**
   - Copy `config/config.yaml.example` to `config/config.yaml`
   - Update JSON file path (dc_tracker.json) and other settings as needed

## Development Status

Currently in Phase 1: Message Extraction Agent
- Step 1: ✅ Project structure setup (completed)
- Step 1.5: ✅ Message data extracted to dc_tracker.json (619 messages)

## Next Steps

- Step 2: Create data models (Message, TradingAction)
- Step 3: Implement JSON message reader adapter
- Step 4: Build LLM-based extraction agent
- Step 5: Create monitoring dashboard

## Data

The `dc_tracker.json` file contains 619 messages extracted from Discord channel exports, with the following structure:
- `sender`: Message sender name
- `send_time`: Timestamp (e.g., "10/5/2024 12:25 PM")
- `message`: Message content (currently in Chinese, can be translated using OpenAI API)

