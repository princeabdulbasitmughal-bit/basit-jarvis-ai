"""
================================================================================
UNIT & INTEGRATION TEST SUITE — BASIT JARVIS AI VOICE ASSISTANT
================================================================================
Verifies all 13 core pillars:
- NLU single and compound command parsing
- Context memory & pronoun resolution
- Macros loading & action dispatch
- Security layer & confirmation gates
- System control state & utilities
- End-to-end command execution
"""

import os
import sys
import unittest
import numpy as np

# Add parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.nlu import NaturalLanguageUnderstanding
from modules.context_memory import ContextMemory
from modules.macros import MacroEngine
from modules.security import SecurityLayer
from modules.system_control import SystemControl
from modules.multi_app_automation import MultiAppAutomation
from jarvis import BasitJarvis


class TestBasitJarvis(unittest.TestCase):
    def setUp(self):
        self.nlu = NaturalLanguageUnderstanding()
        self.memory = ContextMemory(persist_path=os.path.join(os.path.dirname(__file__), "test_context.json"))
        self.security = SecurityLayer()
        self.macros = MacroEngine()

    def tearDown(self):
        test_ctx = os.path.join(os.path.dirname(__file__), "test_context.json")
        if os.path.exists(test_ctx):
            try:
                os.remove(test_ctx)
            except Exception:
                pass

    # ---------------------------------------------------------
    # 1. NLU PARSING TESTS
    # ---------------------------------------------------------
    def test_nlu_open_app(self):
        intents = self.nlu.parse("open chrome")
        self.assertEqual(len(intents), 1)
        self.assertEqual(intents[0]["intent"], "open_app")
        self.assertEqual(intents[0]["entities"]["app"], "chrome")

    def test_nlu_compound_command(self):
        """User: 'open chrome and search cats'"""
        intents = self.nlu.parse("open chrome and search cats")
        self.assertEqual(len(intents), 2)
        self.assertEqual(intents[0]["intent"], "open_app")
        self.assertEqual(intents[1]["intent"], "web_search")
        self.assertEqual(intents[1]["entities"]["query"], "cats")

    def test_nlu_volume_control(self):
        intents = self.nlu.parse("set volume to 80")
        self.assertEqual(len(intents), 1)
        self.assertEqual(intents[0]["intent"], "set_volume")
        self.assertEqual(intents[0]["entities"]["value"], 80)

    def test_nlu_mute_unmute(self):
        mute_res = self.nlu.parse("mute volume")
        self.assertEqual(mute_res[0]["intent"], "set_volume")
        self.assertEqual(mute_res[0]["entities"]["action"], "mute")

    def test_nlu_brightness_control(self):
        intents = self.nlu.parse("set brightness to 60")
        self.assertEqual(len(intents), 1)
        self.assertEqual(intents[0]["intent"], "set_brightness")
        self.assertEqual(intents[0]["entities"]["value"], 60)

    def test_nlu_macro_intent(self):
        intents = self.nlu.parse("start coding mode")
        self.assertEqual(len(intents), 1)
        self.assertEqual(intents[0]["intent"], "run_macro")
        self.assertEqual(intents[0]["entities"]["macro_name"], "coding mode")

        intents_content = self.nlu.parse("start content mode")
        self.assertEqual(intents_content[0]["intent"], "run_macro")
        self.assertEqual(intents_content[0]["entities"]["macro_name"], "content mode")

    def test_nlu_screenshot(self):
        intents = self.nlu.parse("take a screenshot")
        self.assertEqual(len(intents), 1)
        self.assertEqual(intents[0]["intent"], "take_screenshot")

    def test_nlu_window_management(self):
        intents = self.nlu.parse("show desktop")
        self.assertEqual(len(intents), 1)
        self.assertEqual(intents[0]["intent"], "minimize_all")

        intents_min = self.nlu.parse("minimize")
        self.assertEqual(intents_min[0]["intent"], "minimize_active")

        intents_max = self.nlu.parse("maximize")
        self.assertEqual(intents_max[0]["intent"], "maximize_active")

    def test_nlu_media_control(self):
        intents = self.nlu.parse("pause music")
        self.assertEqual(len(intents), 1)
        self.assertEqual(intents[0]["intent"], "media_play_pause")

        intents_next = self.nlu.parse("next track")
        self.assertEqual(intents_next[0]["intent"], "media_next")

    def test_nlu_keyboard_input(self):
        intents = self.nlu.parse("type Hello Basit")
        self.assertEqual(len(intents), 1)
        self.assertEqual(intents[0]["intent"], "type_text")
        self.assertEqual(intents[0]["entities"]["text"], "Hello Basit")

        intents_press = self.nlu.parse("press enter")
        self.assertEqual(len(intents_press), 1)
        self.assertEqual(intents_press[0]["intent"], "press_key")
        self.assertEqual(intents_press[0]["entities"]["key"], "enter")

    def test_nlu_file_search(self):
        intents = self.nlu.parse("search file financial_report in desktop")
        self.assertEqual(len(intents), 1)
        self.assertEqual(intents[0]["intent"], "search_file")
        self.assertEqual(intents[0]["entities"]["filename"], "financial_report")

    # ---------------------------------------------------------
    # 2. CONTEXT MEMORY TESTS
    # ---------------------------------------------------------
    def test_context_memory_recording(self):
        self.memory.record_turn("open vscode", "open_app", {"app": "vscode"}, "Opening vscode, sir.")
        self.assertEqual(self.memory.last_app, "vscode")
        resolved = self.memory.resolve_reference("close that app")
        self.assertEqual(resolved, "vscode")

    def test_context_memory_file_recall(self):
        self.memory.record_turn("search file invoice.pdf", "search_file", {"filename": "invoice.pdf"}, "Found file.")
        self.assertEqual(self.memory.last_file, "invoice.pdf")
        resolved = self.memory.resolve_reference("open that file again")
        self.assertEqual(resolved, "invoice.pdf")

    def test_context_memory_topic_recall(self):
        self.memory.record_turn("generate hooks for AI automation", "generate_hooks", {"topic": "AI automation"}, "Generated hooks.")
        self.assertEqual(self.memory.last_topic, "AI automation")
        resolved = self.memory.resolve_reference("write a script for that topic")
        self.assertEqual(resolved, "AI automation")

    # ---------------------------------------------------------
    # 3. SECURITY LAYER TESTS
    # ---------------------------------------------------------
    def test_security_sensitive_detection(self):
        self.assertTrue(self.security.is_sensitive("shutdown"))
        self.assertTrue(self.security.is_sensitive("delete this folder"))
        self.assertFalse(self.security.is_sensitive("open chrome"))

    def test_security_confirmation_flow(self):
        dummy_action = {"intent": "shutdown_system"}
        self.security.request_confirmation(dummy_action)
        # Verify confirm returns action
        confirmed = self.security.check_confirmation("yes confirm it")
        self.assertIsNotNone(confirmed)
        self.assertEqual(confirmed["intent"], "shutdown_system")

    def test_security_cancellation_flow(self):
        dummy_action = {"intent": "shutdown_system"}
        self.security.request_confirmation(dummy_action)
        cancelled = self.security.check_confirmation("no cancel that")
        self.assertIsNone(cancelled)

    # ---------------------------------------------------------
    # 4. MACRO ENGINE TESTS
    # ---------------------------------------------------------
    def test_macros_loaded(self):
        self.assertIn("coding mode", self.macros.macros)
        self.assertIn("work mode", self.macros.macros)
        self.assertIn("focus mode", self.macros.macros)
        self.assertIn("content mode", self.macros.macros)

    def test_macro_execution_dispatcher(self):
        executed_actions = []
        engine = MacroEngine(action_executor=lambda act: executed_actions.append(act))
        success = engine.execute_macro("focus mode")
        self.assertTrue(success)
        self.assertGreater(len(executed_actions), 0)

    # ---------------------------------------------------------
    # 5. SYSTEM CONTROL STATUS TESTS
    # ---------------------------------------------------------
    def test_system_status(self):
        sys_ctrl = SystemControl()
        stats = sys_ctrl.get_system_status()
        self.assertIn("cpu_percent", stats)
        self.assertIn("ram_percent", stats)
        self.assertIn("disk_percent", stats)

    # ---------------------------------------------------------
    # 6. END-TO-END ORCHESTRATOR INTEGRATION TEST
    # ---------------------------------------------------------
    def test_orchestrator_process_command(self):
        from unittest.mock import patch
        with patch("modules.stt.SpeechToText._init_model", return_value=None), \
             patch("modules.multi_app_automation.webbrowser.open", return_value=True), \
             patch("modules.tts.TextToSpeech.speak", return_value=None), \
             patch.object(SystemControl, "set_volume", return_value=True):
            jarvis = BasitJarvis()
            # Test web search processing without launching real browser
            reply = jarvis.process_command("search python tutorial on google")
            self.assertTrue("Searching" in reply or "python" in reply)

            # Test volume command
            reply_vol = jarvis.process_command("set volume to 50")
            self.assertIn("Volume", reply_vol)


if __name__ == "__main__":
    unittest.main(verbosity=2)
