"""
================================================================================
TEST SUITE: BASIT SLASH COMMANDS, BILINGUAL NLU, & FULL PC CONTROLLER
================================================================================
Verifies:
1. /basit1, /basit2, /basit3, /basitloop slash and voice command parsing
2. Roman Urdu & Urdu voice parsing (Chrome kholo, Volume barhao, Screenshot lo)
3. BasitEngines execution & fallback routing
4. SystemControl Shell and Git execution
5. Process Guard & Zombie Sweeper
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.nlu import NaturalLanguageUnderstanding
from modules.system_control import SystemControl
from modules.ai_brain import AIBrain
from modules.basit_engines import BasitEngines, Basit1Coder, Basit2Researcher, Basit3Guardian, BasitLoopEngine
from jarvis import BasitJarvis


class TestBasitCommands(unittest.TestCase):
    def setUp(self):
        self.nlu = NaturalLanguageUnderstanding()
        self.system = SystemControl()
        self.brain = AIBrain()
        self.engines = BasitEngines(ai_brain=self.brain)

    # --------------------------------------------------------------------------
    # 1. SLASH COMMAND NLU PARSING
    # --------------------------------------------------------------------------
    def test_basit1_parsing(self):
        # Slash format
        intents = self.nlu.parse("/basit1 create a python fastAPI server")
        self.assertEqual(intents[0]["intent"], "basit1_code")
        self.assertIn("fastapi", intents[0]["entities"]["prompt"].lower())

        # Voice format
        intents_voice = self.nlu.parse("basit 1 create a calculator")
        self.assertEqual(intents_voice[0]["intent"], "basit1_code")

        intents_code = self.nlu.parse("code karo write a binary search algorithm")
        self.assertEqual(intents_code[0]["intent"], "basit1_code")

    def test_basit2_parsing(self):
        # Slash format
        intents = self.nlu.parse("/basit2 quantum computing breakthroughs 2026")
        self.assertEqual(intents[0]["intent"], "basit2_research")
        self.assertIn("quantum", intents[0]["entities"]["query"].lower())

        # Voice format
        intents_voice = self.nlu.parse("basit 2 research transformer models")
        self.assertEqual(intents_voice[0]["intent"], "basit2_research")

    def test_basit3_parsing(self):
        # Slash format
        intents = self.nlu.parse("/basit3 sweep zombies")
        self.assertEqual(intents[0]["intent"], "basit3_guardian")

        # Voice format
        intents_sec = self.nlu.parse("security audit check this project")
        self.assertEqual(intents_sec[0]["intent"], "basit3_guardian")

    def test_basitloop_parsing(self):
        # Slash format
        intents = self.nlu.parse("/basitloop build an analytics dashboard")
        self.assertEqual(intents[0]["intent"], "basit_loop")
        self.assertIn("analytics", intents[0]["entities"]["goal"].lower())

        # Voice format
        intents_voice = self.nlu.parse("basit loop optimize performance")
        self.assertEqual(intents_voice[0]["intent"], "basit_loop")

    # --------------------------------------------------------------------------
    # 2. BILINGUAL URDU / ROMAN URDU NLU PARSING
    # --------------------------------------------------------------------------
    def test_urdu_open_close_app(self):
        intents_open = self.nlu.parse("chrome kholo")
        self.assertEqual(intents_open[0]["intent"], "open_app")
        self.assertEqual(intents_open[0]["entities"]["app"], "chrome")

        intents_close = self.nlu.parse("vscode band karo")
        self.assertEqual(intents_close[0]["intent"], "close_app")
        self.assertEqual(intents_close[0]["entities"]["app"], "vscode")

    def test_urdu_volume_brightness(self):
        intents_vol = self.nlu.parse("awaz 75 kardo")
        self.assertEqual(intents_vol[0]["intent"], "set_volume")
        self.assertEqual(intents_vol[0]["entities"]["value"], 75)

        intents_vol_up = self.nlu.parse("awaz barhao")
        self.assertEqual(intents_vol_up[0]["intent"], "change_volume")
        self.assertGreater(intents_vol_up[0]["entities"]["delta"], 0)

        intents_mute = self.nlu.parse("awaz band kardo")
        self.assertEqual(intents_mute[0]["intent"], "set_volume")
        self.assertEqual(intents_mute[0]["entities"]["action"], "mute")

        intents_bright = self.nlu.parse("roshni 80 kardo")
        self.assertEqual(intents_bright[0]["intent"], "set_brightness")
        self.assertEqual(intents_bright[0]["entities"]["value"], 80)

    def test_urdu_desktop_screenshot_power(self):
        intents_desk = self.nlu.parse("desktop dikhao")
        self.assertEqual(intents_desk[0]["intent"], "minimize_all")

        intents_ss = self.nlu.parse("screenshot lo")
        self.assertEqual(intents_ss[0]["intent"], "take_screenshot")

        intents_lock = self.nlu.parse("pc lock kardo")
        self.assertEqual(intents_lock[0]["intent"], "lock_system")

        intents_status = self.nlu.parse("system status batao")
        self.assertEqual(intents_status[0]["intent"], "system_status")

    def test_urdu_web_search(self):
        intents = self.nlu.parse("youtube per python tutorial search karo")
        self.assertEqual(intents[0]["intent"], "web_search")
        self.assertEqual(intents[0]["entities"]["engine"], "youtube")
        self.assertEqual(intents[0]["entities"]["query"], "python tutorial")

    def test_folder_navigation(self):
        intents = self.nlu.parse("downloads folder kholo")
        self.assertEqual(intents[0]["intent"], "open_folder")
        self.assertEqual(intents[0]["entities"]["folder"], "downloads")

    def test_git_command_parsing(self):
        intents = self.nlu.parse("git status")
        self.assertEqual(intents[0]["intent"], "run_git_command")
        self.assertEqual(intents[0]["entities"]["args"], "status")

    # --------------------------------------------------------------------------
    # 3. SYSTEM CONTROL TERMINAL & PROCESS GUARD
    # --------------------------------------------------------------------------
    def test_shell_command_execution(self):
        res = self.system.run_shell_command("Write-Output 'Basit Jarvis'")
        self.assertTrue(res["success"])
        self.assertIn("Basit Jarvis", res["output"])

    def test_git_command_execution(self):
        res = self.system.run_git_command("--version")
        self.assertTrue(res["success"])
        self.assertIn("git version", res["output"].lower())

    def test_zombie_process_sweep(self):
        killed = self.system.sweep_zombies()
        self.assertIsInstance(killed, int)

    # --------------------------------------------------------------------------
    # 4. BASIT ENGINES DISPATCHER
    # --------------------------------------------------------------------------
    def test_basit_engines_dispatch_mock(self):
        with patch.object(self.brain, "ask", return_value="def hello(): return 'world'"):
            res = self.engines.dispatch("basit1", "write a hello function")
            self.assertEqual(res["engine"], "/basit1")
            self.assertIn("hello", res["response"])

        with patch.object(self.brain, "ask", return_value="Deep research on AI agents: ..."):
            res2 = self.engines.dispatch("basit2", "AI agents 2026")
            self.assertEqual(res2["engine"], "/basit2")
            self.assertIn("Deep research", res2["report"])

        res3 = self.engines.dispatch("basit3", "audit")
        self.assertEqual(res3["engine"], "/basit3")
        self.assertIn("security_audit", res3["details"])

    # --------------------------------------------------------------------------
    # 5. END-TO-END JARVIS ORCHESTRATOR DISPATCH
    # --------------------------------------------------------------------------
    def test_jarvis_e2e_basit_commands(self):
        with patch("modules.stt.SpeechToText._init_model", return_value=None), \
             patch("modules.tts.TextToSpeech.speak", return_value=None), \
             patch.object(self.brain, "ask", return_value="Generated Code"):
            jarvis = BasitJarvis()

            # Voice /basit1
            resp1 = jarvis.process_command("/basit1 write quicksort in python")
            self.assertTrue(bool(resp1))

            # Urdu Command
            resp2 = jarvis.process_command("awaz 65 kardo")
            self.assertIn("65", resp2)

            # Folder Command
            with patch.object(jarvis.system, "open_folder", return_value=True):
                resp3 = jarvis.process_command("desktop folder kholo")
                self.assertIn("desktop", resp3.lower())

            # Note Taking Command
            resp4 = jarvis.process_command("take a note: test simple note")
            self.assertIn("Note saved", resp4)

    # --------------------------------------------------------------------------
    # 6. QUICK NOTES & CLIPBOARD SYSTEM TESTS
    # --------------------------------------------------------------------------
    def test_quick_notes_system(self):
        note = self.system.take_quick_note("Buy groceries for dinner")
        self.assertIn("text", note)
        self.assertEqual(note["text"], "Buy groceries for dinner")
        notes = self.system.get_all_notes()
        self.assertGreater(len(notes), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
