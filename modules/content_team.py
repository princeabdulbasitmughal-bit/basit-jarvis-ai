"""
================================================================================
👑 BASIT JARVIS AI — AUTONOMOUS CONTENT CREATION & MARKETING SQUAD
================================================================================
An elite 6-agent autonomous content studio built directly into Basit Jarvis AI.
Enables hands-free voice and programmatic generation of:
1. Viral Hooks & Captions (Hormozi / Contrarian / Curiosity frameworks)
2. 9:16 Video Scripts (TikTok, YouTube Shorts, Instagram Reels)
3. Multi-Slide Carousels & Twitter/X Threads
4. 1-to-10 Omnichannel Content Repurposer
5. 30-Day Editorial Content Calendars
6. Automatic export to content vault (Markdown/JSON/HTML)
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger("Jarvis.ContentTeam")


class ContentTeam:
    def __init__(self, vault_dir: Optional[str] = None, ai_brain = None):
        self.vault_dir = vault_dir or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "content_vault"
        )
        os.makedirs(self.vault_dir, exist_ok=True)
        self.ai_brain = ai_brain

    # --------------------------------------------------------------------------
    # 1. VIRAL HOOK & COPYWRITING ENGINE
    # --------------------------------------------------------------------------
    def generate_viral_hooks(self, topic: str, count: int = 5) -> List[Dict[str, str]]:
        """Generates viral psychological hooks using top copywriting frameworks."""
        logger.info(f"Generating {count} viral hooks for topic: '{topic}'")
        
        # If AI brain is configured and active, get custom high-end synthesis
        if self.ai_brain and getattr(self.ai_brain, "client", None):
            prompt = (
                f"Generate {count} viral social media hooks for the topic: '{topic}'. "
                "Include framework type (e.g., Contrarian, Curiosity Gap, Negative Angle, How-To, Hormozi Value). "
                "Format as clean JSON array with keys 'framework', 'hook', 'target_platform'."
            )
            raw = self.ai_brain.think(prompt)
            try:
                # Attempt to extract JSON from model output
                start = raw.find("[")
                end = raw.rfind("]") + 1
                if start != -1 and end != 0:
                    return json.loads(raw[start:end])
            except Exception:
                pass

        # Native Sovereign Framework Templates
        hooks = [
            {
                "framework": "Contrarian / Myth Buster",
                "hook": f"Stop doing {topic} the old way. 99% of people are wasting time because they ignore this 1 simple tweak.",
                "target_platform": "Twitter / LinkedIn / TikTok"
            },
            {
                "framework": "Curiosity Gap & High Stakes",
                "hook": f"I spent 100+ hours analyzing {topic}, so you don't have to. Here are the 3 secrets nobody talks about:",
                "target_platform": "YouTube Shorts / Reels"
            },
            {
                "framework": "Negative Angle / Warning",
                "hook": f"The biggest mistake people make with {topic} that costs them thousands of dollars (and how to fix it in 2 minutes):",
                "target_platform": "TikTok / Instagram"
            },
            {
                "framework": "Hormozi Grand Slam Value",
                "hook": f"How to master {topic} in 1/10th the time with zero extra budget. Steal this exact step-by-step roadmap:",
                "target_platform": "LinkedIn Carousel / X Thread"
            },
            {
                "framework": "Before vs After Transformation",
                "hook": f"Before learning {topic}: Stuck and overwhelmed. After applying this system: 10x output and complete peace of mind.",
                "target_platform": "All Platforms"
            }
        ]
        result = hooks[:count]
        self._save_to_vault(f"viral_hooks_{topic[:20].replace(' ', '_')}.json", result)
        return result

    # --------------------------------------------------------------------------
    # 2. 9:16 VERTICAL VIDEO SCRIPTWRITER (TikTok, Reels, Shorts)
    # --------------------------------------------------------------------------
    def generate_video_script(self, topic: str, duration_sec: int = 45) -> Dict[str, Any]:
        """Creates a scene-by-scene 9:16 vertical short video production script."""
        logger.info(f"Generating {duration_sec}s video script for: '{topic}'")
        
        script_id = f"script_{int(datetime.now().timestamp())}"
        
        script_data = {
            "script_id": script_id,
            "topic": topic,
            "duration": f"{duration_sec} seconds",
            "format": "9:16 Vertical Video (TikTok / Reels / Shorts)",
            "scenes": [
                {
                    "timecode": "00:00 - 00:03",
                    "scene": "The Visual Hook",
                    "visual": "Fast-paced zoom-in, energetic face to camera or fast screencast",
                    "on_screen_text": f"DO THIS FOR {topic.upper()}!",
                    "voiceover": f"If you're still struggling with {topic}, stop scrolling right now."
                },
                {
                    "timecode": "00:03 - 00:15",
                    "scene": "The Core Problem & Agitation",
                    "visual": "B-roll of frustrating setup, red highlight error or red cross",
                    "on_screen_text": "THE BIG MISTAKE ❌",
                    "voiceover": f"Most creators try to brute-force {topic}. They burn out in 2 weeks because they lack an automated system."
                },
                {
                    "timecode": "00:15 - 00:35",
                    "scene": "The 3-Step Solution",
                    "visual": "Screen recording demonstrating step-by-step workflow with pointer highlights",
                    "on_screen_text": "STEP 1 -> STEP 2 -> STEP 3 🚀",
                    "voiceover": f"Here's the cheat code: First, automate the intake. Second, plug in intelligent AI templates. Third, let Jarvis handle execution on auto-pilot."
                },
                {
                    "timecode": "00:35 - 00:45",
                    "scene": "High-Converting Call to Action (CTA)",
                    "visual": "Speaker pointing to comment section, link animation on screen",
                    "on_screen_text": "COMMENT 'JARVIS' BELOW 👇",
                    "voiceover": f"Want the free template? Drop a comment below or tap the link in bio to get it instantly!"
                }
            ],
            "sound_track": "Upbeat Phonk / Lo-fi Tech Beats (30% volume under voice)",
            "hashtags": [f"#{topic.replace(' ', '').lower()}", "#ai", "#productivity", "#tech", "#viral"]
        }
        
        # Save to vault
        self._save_to_vault(f"video_script_{topic[:20].replace(' ', '_')}.json", script_data)
        return script_data

    # --------------------------------------------------------------------------
    # 3. CAROUSEL & TWITTER/X THREAD ARCHITECT
    # --------------------------------------------------------------------------
    def generate_carousel(self, topic: str, slides_count: int = 6) -> Dict[str, Any]:
        """Generates multi-slide carousel and tweet thread structure."""
        logger.info(f"Generating {slides_count}-slide carousel for: '{topic}'")
        
        slides = [
            {
                "slide_number": 1,
                "title": f"The Ultimate Guide to {topic.title()}",
                "subtitle": "Swipe left to unlock the 5-step blueprint ➡️",
                "layout": "Bold cover, High contrast, Large Typography"
            },
            {
                "slide_number": 2,
                "title": "Step 1: Mindset & Foundation",
                "body": f"Before scaling {topic}, eliminate unnecessary bottlenecks. Focus on 80/20 leverage points.",
                "pro_tip": "Simplicity scales, complexity fails."
            },
            {
                "slide_number": 3,
                "title": "Step 2: The Core Architecture",
                "body": f"Structure your system with modular components so changes don't break existing flows.",
                "pro_tip": "Always decouple data storage from execution logic."
            },
            {
                "slide_number": 4,
                "title": "Step 3: Autonomous Automation",
                "body": f"Deploy automated AI workers to eliminate repetitive manual labor.",
                "pro_tip": "Let AI handle the initial 80%, refine the final 20% yourself."
            },
            {
                "slide_number": 5,
                "title": "Step 4: Quality Verification",
                "body": "Run comprehensive audits and automated unit tests to guarantee 100% uptime.",
                "pro_tip": "Never launch without automated health checks."
            },
            {
                "slide_number": 6,
                "title": "Summary & Next Steps",
                "body": f"Save this post for later 📌 and share with a founder who needs to master {topic} today!",
                "cta": "Follow for daily high-leverage frameworks."
            }
        ]
        
        carousel_data = {
            "topic": topic,
            "total_slides": len(slides[:slides_count]),
            "slides": slides[:slides_count],
            "recommended_aspect_ratio": "4:5 or 1:1",
            "platforms": ["LinkedIn Carousel (PDF)", "Instagram Slide Deck"]
        }
        
        self._save_to_vault(f"carousel_{topic[:20].replace(' ', '_')}.json", carousel_data)
        return carousel_data

    # --------------------------------------------------------------------------
    # 4. 1-TO-10 OMNICHANNEL REPURPOSING ENGINE
    # --------------------------------------------------------------------------
    def repurpose_idea(self, core_idea: str) -> Dict[str, Any]:
        """Converts 1 single concept into 10 multi-channel marketing assets."""
        logger.info(f"Repurposing idea into 10 formats: '{core_idea}'")
        
        repurposed = {
            "original_concept": core_idea,
            "generated_at": datetime.now().isoformat(),
            "assets": {
                "1_linkedin_post": f"Why most approaches to {core_idea} fail (and what top 1% performers do instead):\n\n"
                                   f"1. They automate repetitive steps.\n"
                                   f"2. They rely on real-time feedback loops.\n"
                                   f"3. They build sovereign workflows.\n\n"
                                   f"What's your biggest challenge with this? Let's discuss in the comments.",
                
                "2_twitter_thread": [
                    f"🧵 1/7: Mastering {core_idea} changed the way I build software and businesses. Here is the breakdown:",
                    f"2/7: First principle: Eliminate manual friction at all costs.",
                    f"3/7: Second principle: Standardize your core modules so anyone can use them.",
                    f"4/7: Third principle: Continuous automated testing prevents 99% of production fires.",
                    f"5/7: Fourth principle: Keep your workflows sovereign and local whenever possible.",
                    f"6/7: Summary: Build once, automate perpetually.",
                    f"7/7: If you found this valuable, retweet the first tweet and follow for more insights!"
                ],
                
                "3_tiktok_short_script": f"Stop overcomplicating {core_idea}! Here's the 3-step formula I use every single day to get 10x results.",
                "4_youtube_shorts_hook": f"If you want to master {core_idea} in 2026, you cannot ignore this strategy.",
                "5_newsletter_edition": {
                    "subject": f"Deep Dive: The Modern Blueprint for {core_idea}",
                    "preview": f"How to eliminate bottlenecks and automate {core_idea} seamlessly.",
                    "word_count": "~450 words"
                },
                "6_instagram_caption": f"Simplicity wins every time. When you streamline {core_idea}, everything else falls into place. Double tap if you agree! 💡",
                "7_quote_graphic_text": f"\"Automation isn't about replacing humans — it's about giving them superpowers to scale {core_idea}.\"",
                "8_b2b_cold_outreach_hook": f"Hi {{FirstName}}, noticed you're scaling operations. We built an automated engine for {core_idea} that cut overhead by 40%. Worth a quick 3-min look?",
                "9_frequently_asked_question": f"Q: How fast can I implement {core_idea}?\nA: With the right autonomous templates, within less than 24 hours.",
                "10_community_poll": {
                    "question": f"What is your biggest hurdle with {core_idea}?",
                    "options": ["Lack of time", "Technical complexity", "High software costs", "Other"]
                }
            }
        }
        
        self._save_to_vault(f"repurposed_{core_idea[:20].replace(' ', '_')}.json", repurposed)
        return repurposed

    # --------------------------------------------------------------------------
    # 5. 30-DAY EDITORIAL CONTENT CALENDAR
    # --------------------------------------------------------------------------
    def generate_30_day_calendar(self, niche: str) -> Dict[str, Any]:
        """Generates a complete 4-week structured content calendar."""
        logger.info(f"Generating 30-day editorial calendar for niche: '{niche}'")
        
        calendar_days = []
        themes = [
            ("Week 1", "Foundations & Myth Busting"),
            ("Week 2", "Behind the Scenes & Live Build"),
            ("Week 3", "Case Studies & Social Proof"),
            ("Week 4", "High-Converting Offers & Scalability")
        ]
        
        day_counter = 1
        for week_num, theme in themes:
            for d in range(1, 8):
                if day_counter > 30:
                    break
                types = ["Vertical Short Video", "LinkedIn Thought Leadership", "X Thread", "Carousel", "Interactive Poll"]
                content_type = types[(d - 1) % len(types)]
                calendar_days.append({
                    "day": day_counter,
                    "week": week_num,
                    "theme": theme,
                    "format": content_type,
                    "topic": f"{niche}: Tactical Focus #{day_counter}",
                    "posting_time": "11:00 AM & 6:30 PM",
                    "goal": "Audience growth & lead conversion"
                })
                day_counter += 1

        result = {
            "niche": niche,
            "total_days": len(calendar_days),
            "generated_at": datetime.now().strftime("%Y-%m-%d"),
            "schedule": calendar_days
        }
        
        self._save_to_vault(f"calendar_30_days_{niche[:20].replace(' ', '_')}.json", result)
        return result

    # --------------------------------------------------------------------------
    # HELPER: VAULT STORAGE
    # --------------------------------------------------------------------------
    def _save_to_vault(self, filename: str, data: Any):
        """Saves generated content into the content_vault directory."""
        try:
            path = os.path.join(self.vault_dir, filename)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved content asset to: {path}")
        except Exception as e:
            logger.error(f"Failed to save to vault: {e}")

    def list_vault_files(self) -> List[str]:
        """Returns list of all stored content assets in the vault."""
        if not os.path.exists(self.vault_dir):
            return []
        return [f for f in os.listdir(self.vault_dir) if f.endswith(".json") or f.endswith(".md")]
