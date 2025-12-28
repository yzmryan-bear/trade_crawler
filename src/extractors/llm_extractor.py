"""LLM-based trading action extractor."""

import os
import json
from typing import List, Optional
from datetime import datetime

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

from ..models.message import Message
from ..models.trading_action import TradingAction, ActionType


class LLMExtractor:
    """Extract trading actions from messages using LLM."""
    
    def __init__(
        self,
        model: str = "gpt-4o-mini",
        provider: str = "openai",
        api_key: Optional[str] = None
    ):
        """Initialize LLM extractor.
        
        Args:
            model: Model name (e.g., "gpt-4o-mini", "claude-3-opus-20240229")
            provider: LLM provider ("openai" or "anthropic")
            api_key: API key (if None, reads from environment)
        """
        self.model = model
        self.provider = provider.lower()
        
        if api_key:
            self.api_key = api_key
        else:
            if self.provider == "openai":
                self.api_key = os.getenv("OPENAI_API_KEY")
            elif self.provider == "anthropic":
                self.api_key = os.getenv("ANTHROPIC_API_KEY")
            else:
                self.api_key = None
        
        if not self.api_key:
            raise ValueError(f"API key not found for provider: {self.provider}")
        
        # Initialize client
        if self.provider == "openai":
            if not HAS_OPENAI:
                raise ImportError("OpenAI library not installed. Install with: pip install openai")
            self.client = OpenAI(api_key=self.api_key)
        elif self.provider == "anthropic":
            if not HAS_ANTHROPIC:
                raise ImportError("Anthropic library not installed. Install with: pip install anthropic")
            self.client = anthropic.Anthropic(api_key=self.api_key)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def extract(self, message: Message) -> List[TradingAction]:
        """Extract trading actions from a message.
        
        Args:
            message: Message object to extract actions from
        
        Returns:
            List of TradingAction objects (may be empty if no actions found)
        """
        prompt = self._create_extraction_prompt(message.message)
        
        try:
            if self.provider == "openai":
                response = self._extract_with_openai(prompt)
            else:  # anthropic
                response = self._extract_with_anthropic(prompt)
            
            actions = self._parse_response(response, message)
            return actions
        except Exception as e:
            print(f"Error extracting actions from message: {e}")
            return []
    
    def _create_extraction_prompt(self, message_text: str) -> str:
        """Create prompt for LLM extraction."""
        return f"""You are a trading action extraction system. Extract all trading actions (buy/sell) from the following message.

Message:
{message_text}

Return a JSON array of trading actions. Each action should have:
- action_type: "buy" or "sell" or "hold" or "unknown"
- symbol: Stock symbol (e.g., "AAPL", "TSLA", "QQQ")
- price: Price per share (float, optional)
- quantity: Number of shares (integer, optional)
- confidence: Confidence score 0.0-1.0

If no trading action is found, return an empty array [].

Examples:
- "Buy 100 shares of AAPL at $150" -> {{"action_type": "buy", "symbol": "AAPL", "price": 150.0, "quantity": 100, "confidence": 0.95}}
- "sell qqq 492 from 483" -> {{"action_type": "sell", "symbol": "QQQ", "price": 492.0, "quantity": null, "confidence": 0.9}}
- "I'm thinking about buying TSLA" -> {{"action_type": "unknown", "symbol": "TSLA", "price": null, "quantity": null, "confidence": 0.3}}

Return ONLY valid JSON, no other text."""
    
    def _extract_with_openai(self, prompt: str) -> str:
        """Extract using OpenAI API."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a trading action extraction system. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            response_format={"type": "json_object"} if "gpt-4" in self.model.lower() else None
        )
        return response.choices[0].message.content
    
    def _extract_with_anthropic(self, prompt: str) -> str:
        """Extract using Anthropic API."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text
    
    def _parse_response(self, response_text: str, message: Message) -> List[TradingAction]:
        """Parse LLM response into TradingAction objects."""
        actions = []
        
        try:
            # Try to extract JSON from response
            response_text = response_text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1]) if len(lines) > 2 else response_text
            
            # Parse JSON
            data = json.loads(response_text)
            
            # Handle both single object and array responses
            if isinstance(data, dict):
                # Single action
                if "actions" in data:
                    actions_data = data["actions"]
                elif "action_type" in data or "symbol" in data:
                    actions_data = [data]
                else:
                    actions_data = []
            elif isinstance(data, list):
                actions_data = data
            else:
                actions_data = []
            
            # Convert to TradingAction objects
            for action_data in actions_data:
                try:
                    action_type_str = action_data.get("action_type", "unknown").lower()
                    try:
                        action_type = ActionType(action_type_str)
                    except ValueError:
                        action_type = ActionType.UNKNOWN
                    
                    symbol = action_data.get("symbol", "").upper().strip()
                    if not symbol:
                        continue
                    
                    action = TradingAction(
                        action_type=action_type,
                        symbol=symbol,
                        price=action_data.get("price"),
                        quantity=action_data.get("quantity"),
                        confidence=float(action_data.get("confidence", 0.5)),
                        raw_message=message.message,
                        extracted_at=datetime.now().isoformat()
                    )
                    
                    if action.is_valid():
                        actions.append(action)
                except Exception as e:
                    print(f"Error parsing action: {e}, data: {action_data}")
                    continue
                    
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON response: {e}")
            print(f"Response was: {response_text[:200]}")
        except Exception as e:
            print(f"Error parsing response: {e}")
        
        return actions

