"""
================================================================================
BASIT JARVIS AI -- INTELLIGENT CONTEXT ENHANCER
================================================================================
Enriches prompts before sending to AI engines for higher quality responses.
"""
import re
from datetime import datetime
from typing import Dict, Any, List, Optional

URDU_MARKERS = [
    'karo', 'karna', 'batao', 'bhai', 'yaar', 'sir', 'chalao', 'dalo',
    'likho', 'banao', 'dikhao', 'samjhao', 'chekc', 'check', 'kya', 'hai',
    'mera', 'meri', 'hum', 'ap', 'aap', 'ek', 'sb', 'sab', 'ab', 'now'
]

CODE_MARKERS = [
    'code', 'function', 'class', 'api', 'fastapi', 'flask', 'script',
    'python', 'javascript', 'typescript', 'react', 'implement', 'build',
    'create', 'generate code', 'write code', 'module', 'endpoint'
]

FINANCE_MARKERS = [
    'stock', 'price', 'market', 'invest', 'nvda', 'btc', 'eth', 'tsla',
    'aapl', 'msft', 'crypto', 'forex', 'trading', 'portfolio', 'hedge'
]

RESEARCH_MARKERS = [
    'research', 'analyze', 'explain', 'what is', 'how does', 'why does',
    'compare', 'difference', 'best', 'pros and cons', 'survey', 'review'
]


class ContextEnhancer:
    def __init__(self):
        self.today = datetime.now().strftime('%A, %B %d, %Y')
        self.time_now = datetime.now().strftime('%H:%M')

    def detect_language(self, text: str) -> str:
        text_lower = text.lower()
        urdu_count = sum(1 for w in URDU_MARKERS if w in text_lower)
        if urdu_count >= 2:
            return 'urdu' if all(c.isascii() for c in text) else 'mixed'
        return 'english'

    def extract_intent(self, prompt: str) -> Dict[str, str]:
        p = prompt.lower()
        intents = []
        if any(m in p for m in CODE_MARKERS):
            intents.append('coding')
        if any(m in p for m in FINANCE_MARKERS):
            intents.append('finance')
        if any(m in p for m in RESEARCH_MARKERS):
            intents.append('research')
        if '?' in prompt:
            intents.append('question')
        if any(w in p for w in ['email', 'pdf', 'report', 'send']):
            intents.append('action')

        complexity = 'high' if len(prompt) > 300 else ('medium' if len(prompt) > 80 else 'low')
        topic = 'technical' if any(m in p for m in CODE_MARKERS + FINANCE_MARKERS) else 'general'

        return {
            'intent': ', '.join(intents) or 'general',
            'language': self.detect_language(prompt),
            'topic': topic,
            'complexity': complexity
        }

    def enhance(self, prompt: str, engine: str, history: List[Dict] = None) -> str:
        intent = self.extract_intent(prompt)
        additions = []

        # Language instruction
        if intent['language'] in ('urdu', 'mixed'):
            additions.append('[LANG: Respond naturally in Roman Urdu mixed with English, as a loyal AI friend.]')

        # Code enhancement
        if 'coding' in intent['intent']:
            additions.append('[CODE: Provide complete, production-ready code with error handling, type hints, and docstrings.]')

        # Finance enhancement
        if 'finance' in intent['intent']:
            additions.append(f'[DATE: Today is {self.today}. Use this for market context.]')

        # Research enhancement
        if 'research' in intent['intent'] or 'question' in intent['intent']:
            additions.append('[RESEARCH: Be thorough and data-backed. Cite specific facts and numbers.]')

        # Engine-specific context
        engine_ctx = {
            'basit1': '[ENGINE: You are Basit1 (Devin/OpenHands), an expert software engineer.]',
            'basit2': '[ENGINE: You are Basit2, a world-class research analyst with 2M context.]',
            'basit3': '[ENGINE: You are Basit3, an OWASP-certified security expert.]',
            'basit4': '[ENGINE: You are Basit4, managing a $500M AI hedge fund.]',
            'basitswarm': '[ENGINE: You are BasitSwarm, coordinating 100 parallel AI agents.]',
            'gemini-spark': '[ENGINE: You combine Google Gemini 2.0 AI with Apache Spark 4.2 distributed computing.]',
        }
        if engine in engine_ctx:
            additions.append(engine_ctx[engine])

        # History context (last 3 messages)
        if history:
            last3 = history[-3:]
            ctx_str = ' | '.join(f"{h.get('role','?')}: {str(h.get('content',''))[:80]}" for h in last3)
            additions.append(f'[CONTEXT: {ctx_str}]')

        if additions:
            return '\n'.join(additions) + '\n\n' + prompt
        return prompt

    def format_response(self, response: str, engine: str) -> str:
        if not response:
            return ''
        # Clean up excessive blank lines
        response = re.sub(r'\n{3,}', '\n\n', response.strip())
        # Ensure code blocks are properly formatted
        response = re.sub(r'```(\w+)?\n', r'```\1\n', response)
        return response


if __name__ == '__main__':
    ce = ContextEnhancer()
    test_prompts = [
        ('FastAPI JWT auth endpoint banao', 'basit1'),
        ('NVDA stock analysis karo', 'basit4'),
        ('What is LangGraph?', 'basit2'),
    ]
    for prompt, engine in test_prompts:
        intent = ce.extract_intent(prompt)
        enhanced = ce.enhance(prompt, engine)
        print(f'PROMPT: {prompt}')
        print(f'INTENT: {intent}')
        print(f'ENHANCED (first 200): {enhanced[:200]}')
        print('---')
