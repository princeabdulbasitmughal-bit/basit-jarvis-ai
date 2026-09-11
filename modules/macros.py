"""
============================================================
MODULE 9: CUSTOM COMMAND MACROS (Multi-Action Sequences)
============================================================
Allows user-defined custom macros and workflow routines.
Example:
- 'start coding mode' -> Opens VS Code + Terminal + Chrome + sets volume.
- 'focus mode' -> Kills music + dims screen + sets DND.
"""

import os
import json
import time
import logging
from typing import Dict, Any, List, Optional, Callable

logger = logging.getLogger("Jarvis.Macros")


class MacroEngine:
    def __init__(self, macros_path: Optional[str] = None, action_executor: Optional[Callable[[Dict[str, Any]], None]] = None):
        self.macros_path = macros_path or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "macros.json"
        )
        self.action_executor = action_executor
        self.macros: Dict[str, Any] = {}
        self.load_macros()

    def load_macros(self):
        """Loads macros from macros.json."""
        if os.path.exists(self.macros_path):
            try:
                with open(self.macros_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.macros = data.get("macros", {})
                logger.info(f"Loaded {len(self.macros)} macros from {self.macros_path}")
            except Exception as e:
                logger.error(f"Error loading macros: {e}")
                self.macros = {}
        else:
            logger.warning(f"Macros file not found at {self.macros_path}")

    def execute_macro(self, macro_name: str) -> bool:
        """Executes the action sequence for a given macro."""
        macro_name_clean = macro_name.lower().strip()
        matched_macro = None

        # Exact match or substring
        for name, macro in self.macros.items():
            if name.lower() == macro_name_clean or name.lower() in macro_name_clean or macro_name_clean in name.lower():
                matched_macro = macro
                break

        if not matched_macro:
            logger.warning(f"Macro '{macro_name}' not found.")
            return False

        actions = matched_macro.get("actions", [])
        logger.info(f"Executing macro '{macro_name}' ({len(actions)} actions)...")

        for action in actions:
            try:
                if self.action_executor:
                    self.action_executor(action)
                else:
                    logger.info(f"Mock execute action: {action}")
                time.sleep(0.3)  # Brief pause between sequential OS actions
            except Exception as e:
                logger.error(f"Error executing action {action}: {e}")

        return True

    def add_macro(self, name: str, description: str, actions: List[Dict[str, Any]]) -> bool:
        """Adds and persists a new macro."""
        self.macros[name] = {
            "description": description,
            "actions": actions
        }
        try:
            with open(self.macros_path, "w", encoding="utf-8") as f:
                json.dump({"macros": self.macros}, f, indent=2)
            logger.info(f"Saved new macro: '{name}'")
            return True
        except Exception as e:
            logger.error(f"Failed to save macro: {e}")
            return False
