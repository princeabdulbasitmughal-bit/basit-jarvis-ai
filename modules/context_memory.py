"""
============================================================
MODULE 6: CONTEXT MEMORY (Session & Multi-Turn History)
============================================================
Remembers prior commands, entities, and context within a session.
Enables natural interactions like:
- 'Open that file again'
- 'Close it'
- 'Search that on YouTube instead'
"""

import os
import json
import time
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("Jarvis.ContextMemory")


class ContextMemory:
    def __init__(self, max_history: int = 25, persist_path: Optional[str] = None):
        self.max_history = max_history
        self.persist_path = persist_path or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "context_state.json"
        )

        self.last_app: Optional[str] = None
        self.last_file: Optional[str] = None
        self.last_url: Optional[str] = None
        self.last_query: Optional[str] = None
        self.last_macro: Optional[str] = None
        self.last_topic: Optional[str] = None
        self.history: List[Dict[str, Any]] = []

        self._load_state()

    def record_turn(self, user_text: str, intent: str, entities: Dict[str, Any], response: str):
        """Records a completed turn into memory."""
        turn = {
            "timestamp": time.time(),
            "user": user_text,
            "intent": intent,
            "entities": entities,
            "jarvis": response
        }
        self.history.append(turn)
        if len(self.history) > self.max_history:
            self.history.pop(0)

        # Update entity pointers
        if "app" in entities:
            self.last_app = entities["app"]
        if "filename" in entities or "path" in entities:
            self.last_file = entities.get("path") or entities.get("filename")
        if "query" in entities:
            self.last_query = entities["query"]
        if "url" in entities:
            self.last_url = entities["url"]
        if "macro_name" in entities:
            self.last_macro = entities["macro_name"]
        if "topic" in entities or "niche" in entities or "idea" in entities:
            self.last_topic = entities.get("topic") or entities.get("niche") or entities.get("idea")

        self._persist_state()

    def resolve_reference(self, phrase: str) -> Optional[str]:
        """Resolves pronouns like 'that file', 'it', 'that app', 'that topic'."""
        lower = phrase.lower()
        if "file" in lower and self.last_file:
            return self.last_file
        if ("app" in lower or "program" in lower or "it" in lower) and self.last_app:
            return self.last_app
        if "query" in lower or "search" in lower and self.last_query:
            return self.last_query
        if ("topic" in lower or "that" in lower or "concept" in lower) and self.last_topic:
            return self.last_topic
        return None

    def get_conversation_history(self, limit: int = 10) -> List[Dict[str, str]]:
        """Returns format suitable for LLM message buffers."""
        formatted = []
        for turn in self.history[-limit:]:
            formatted.append({"role": "user", "content": turn.get("user", "")})
            formatted.append({"role": "assistant", "content": turn.get("jarvis", "")})
        return formatted

    def clear(self):
        """Clears memory."""
        self.history.clear()
        self.last_app = None
        self.last_file = None
        self.last_query = None
        self.last_url = None
        self.last_macro = None
        self.last_topic = None
        self._persist_state()
        logger.info("Context memory cleared.")

    def _persist_state(self):
        try:
            state = {
                "last_app": self.last_app,
                "last_file": self.last_file,
                "last_query": self.last_query,
                "last_url": self.last_url,
                "last_macro": self.last_macro,
                "last_topic": self.last_topic,
                "history": self.history[-self.max_history:]
            }
            with open(self.persist_path, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logger.debug(f"Failed to persist context memory: {e}")

    def _load_state(self):
        if os.path.exists(self.persist_path):
            try:
                with open(self.persist_path, "r", encoding="utf-8") as f:
                    state = json.load(f)
                    self.last_app = state.get("last_app")
                    self.last_file = state.get("last_file")
                    self.last_query = state.get("last_query")
                    self.last_url = state.get("last_url")
                    self.last_macro = state.get("last_macro")
                    self.last_topic = state.get("last_topic")
                    self.history = state.get("history", [])
                logger.info(f"Loaded {len(self.history)} previous turns from context memory.")
            except Exception as e:
                logger.warning(f"Could not load context state: {e}")
