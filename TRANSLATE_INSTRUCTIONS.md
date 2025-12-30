# Translate Messages to English

The `dc_tracker.json` file currently contains messages in Chinese. To translate them to English:

## Option 1: Using Environment Variable

```bash
export OPENAI_API_KEY="your-openai-api-key-here"
python3 scripts/translate_json_messages.py
```

## Option 2: Using .env File

1. Create a `.env` file in the project root:
   ```
   OPENAI_API_KEY=your-openai-api-key-here
   ```

2. Run the translation script:
   ```bash
   python3 scripts/translate_json_messages.py
   ```

## What It Does

- Reads messages from `dc_tracker.json`
- Translates Chinese messages to English
- Updates the `message` field with English translation
- Preserves original Chinese in `original_message` field
- Saves back to `dc_tracker.json`

## Cost Estimate

- ~619 messages
- Using `gpt-4o-mini` model
- Estimated cost: ~$0.10-0.50 (depending on message length)

The script shows progress every 10 messages and will preserve the original file structure.

