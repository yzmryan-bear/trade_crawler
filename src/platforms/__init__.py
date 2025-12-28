"""Platform adapters for message sources (JSON, Discord, Telegram)."""

from .base import BasePlatformAdapter
from .json_adapter import JSONAdapter

__all__ = ["BasePlatformAdapter", "JSONAdapter"]
