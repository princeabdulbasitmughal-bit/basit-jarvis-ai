"""
================================================================================
UNIT TESTS: BASIT JARVIS AI — AUTONOMOUS CONTENT CREATION SQUAD
================================================================================
"""

import os
import sys
import shutil
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.content_team import ContentTeam
from modules.nlu import NaturalLanguageUnderstanding


class TestContentTeam(unittest.TestCase):
    def setUp(self):
        self.test_vault = os.path.join(os.path.dirname(__file__), "test_vault")
        os.makedirs(self.test_vault, exist_ok=True)
        self.team = ContentTeam(vault_dir=self.test_vault)
        self.nlu = NaturalLanguageUnderstanding()

    def tearDown(self):
        if os.path.exists(self.test_vault):
            shutil.rmtree(self.test_vault)

    def test_generate_viral_hooks(self):
        hooks = self.team.generate_viral_hooks("E-commerce WhatsApp Bots", count=3)
        self.assertEqual(len(hooks), 3)
        for h in hooks:
            self.assertIn("framework", h)
            self.assertIn("hook", h)
            self.assertIn("target_platform", h)

    def test_generate_video_script(self):
        script = self.team.generate_video_script("Autonomous Software Development", duration_sec=60)
        self.assertIn("scenes", script)
        self.assertGreaterEqual(len(script["scenes"]), 3)
        self.assertEqual(script["format"], "9:16 Vertical Video (TikTok / Reels / Shorts)")

    def test_generate_carousel(self):
        carousel = self.team.generate_carousel("How to Scale B2B Lead Gen", slides_count=5)
        self.assertIn("slides", carousel)
        self.assertEqual(carousel["total_slides"], 5)
        self.assertEqual(carousel["slides"][0]["slide_number"], 1)

    def test_repurpose_idea(self):
        repurposed = self.team.repurpose_idea("AI Agents for Real Estate")
        assets = repurposed["assets"]
        self.assertIn("1_linkedin_post", assets)
        self.assertIn("2_twitter_thread", assets)
        self.assertIn("3_tiktok_short_script", assets)
        self.assertEqual(len(assets["2_twitter_thread"]), 7)

    def test_generate_30_day_calendar(self):
        calendar = self.team.generate_30_day_calendar("SaaS Founders")
        self.assertEqual(calendar["total_days"], 28)
        self.assertEqual(calendar["niche"], "SaaS Founders")

    def test_vault_persistence(self):
        self.team.generate_video_script("Persistence Check")
        files = self.team.list_vault_files()
        self.assertGreaterEqual(len(files), 1)

    def test_nlu_content_intents(self):
        # Hooks intent
        res = self.nlu.parse("generate viral hooks for ecommerce dropshipping")
        self.assertEqual(res[0]["intent"], "generate_hooks")
        self.assertIn("ecommerce", res[0]["entities"]["topic"])

        # Video script intent
        res = self.nlu.parse("create tiktok script for autonomous coding")
        self.assertEqual(res[0]["intent"], "generate_script")

        # Carousel intent
        res = self.nlu.parse("create carousel about ai automation")
        self.assertEqual(res[0]["intent"], "generate_carousel")

        # Calendar intent
        res = self.nlu.parse("create 30 day content calendar for digital marketing")
        self.assertEqual(res[0]["intent"], "generate_calendar")

        # Repurpose intent
        res = self.nlu.parse("repurpose content on python ai agents")
        self.assertEqual(res[0]["intent"], "repurpose_content")


if __name__ == "__main__":
    unittest.main()
