"""
================================================================================
👑 BASIT JARVIS AI — MULTI-TIER AI BRAIN & CLUSTER GATEWAY
================================================================================
Routes intelligence across local super-nodes, cloud LPUs, and token clusters:
1. ⚡ Groq LPU (llama-3.3-70b-versatile / gpt-oss-120b) — Sub-second (0.8s) instant response
2. 💻 Mistral Cloud (codestral-latest) — High-precision code generation
3. 🟢 Local RTX A6000 Super-Node (Ollama: qwen2.5-coder:32b / qwen3:latest)
4. 🟣 Remote RTX 5090 Super-Node (Kimi K3 1M-context: http://10.25.32.13:8080)
5. 🤗 Hugging Face 15-Token Serverless Cluster (HF_TOKEN_1 to HF_TOKEN_15)
6. 🎭 Anthropic Claude Master Suite (Claude 3.5 Sonnet / Extended Thinking)
7. 🤖 OpenAI GPT-4o
8. 🛡️ Intelligent Offline Fallback
"""

import os
import json
import time
import logging
import threading
import requests
from collections import OrderedDict
from typing import List, Dict, Optional, Any

# Load environment variables from E:\.env
try:
    from dotenv import load_dotenv
    if os.path.exists(r"E:\.env"):
        load_dotenv(r"E:\.env")
    elif os.path.exists(".env"):
        load_dotenv(".env")
except ImportError:
    pass

logger = logging.getLogger("Jarvis.AIBrain")


class AIBrain:
    def __init__(
        self,
        provider: str = "auto",
        openai_api_key: str = "",
        anthropic_api_key: str = "",
        model_openai: str = "gpt-4o",
        model_anthropic: str = "claude-3-5-sonnet-20241022",
        system_prompt: Optional[str] = None,
        cluster_cfg: Optional[Dict[str, Any]] = None
    ):
        self.provider = provider
        self.system_prompt = system_prompt or (
            "You are Basit Jarvis — the sovereign, ultra-intelligent, charismatic, and loyal AI personal assistant for your boss, Basit (also referred to as 'Basit bhai', 'Sir', or 'Boss'). "
            "Interact naturally, warmly, and proactively like a real brilliant human companion (a mix of Tony Stark's JARVIS and a high-level Silicon Valley executive). "
            "Bilingual Fluency: Speak fluent, natural Roman Urdu and English. If Basit speaks in Roman Urdu, reply in friendly, respectful Roman Urdu (e.g. 'Ji Basit bhai, bilkul...', 'Zabardast plan hai sir...'). If he speaks English, reply in sharp, sophisticated English. "
            "Conversational Dynamics: Never give dry robotic answers. Be engaging, thoughtful, witty, and helpful. "
            "Voice Mode: Keep voice responses concise (1-3 lively sentences) for normal conversation so dialogue flows smoothly, unless asked for deep explanations, code, or stories."
        )

        # Load API keys from environment / E:\.env
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.groq_api_key = os.getenv("GROQ_API_KEY", "")
        self.mistral_api_key = os.getenv("MISTRAL_API_KEY", "")
        self.anthropic_api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY", "")
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY", "")
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "")
        self.qwen_api_key = os.getenv("QWEN_API_KEY", "")

        # Cluster configuration
        cfg = cluster_cfg or {}
        self.gemini_model = cfg.get("gemini_model", "gemini-3.6-flash")
        self.rtx_a6000_url = cfg.get("rtx_a6000_url", "http://localhost:11434")
        self.rtx_a6000_model = cfg.get("rtx_a6000_model", "qwen2.5-coder:32b")
        self.rtx_5090_url = cfg.get("rtx_5090_url", "http://10.25.32.13:8080")
        self.rtx_5090_model = cfg.get("rtx_5090_model", "kimi-k3")
        self.groq_model = cfg.get("groq_model", "openai/gpt-oss-120b")
        self.mistral_model = cfg.get("mistral_model", "codestral-latest")
        self.model_openai = model_openai
        self.model_anthropic = model_anthropic

        # Load Hugging Face 15-token pool
        self.hf_tokens = []
        for i in range(1, 16):
            tok = os.getenv(f"HF_TOKEN_{i}")
            if tok:
                self.hf_tokens.append(tok)
        self._hf_index = 0

        # Cache setup
        self._cache = OrderedDict()
        self._cache_max = 50
        self._cache_ttl = 300  # 5 minutes


    # PRIMARY ASK ROUTER
    # --------------------------------------------------------------------------
    def ask(self, query: str, history: Optional[List[Dict[str, str]]] = None, task_type: str = "general") -> str:
        """
        Sends query to the best available AI engine with automatic failover.
        task_type options: 'general', 'code', 'research', 'fast'
        """
        logger.info(f"AI Brain query [task={task_type}]: '{query}'")

        # 1. Coding Tasks: Gemini 2.0 Flash -> Codestral -> Local Qwen 32B -> Groq -> Claude
        if task_type == "code":
            if self.gemini_api_key:
                resp = self._ask_gemini(query, history=history, model=self.gemini_model)
                if resp:
                    return resp
            if self.mistral_api_key:
                resp = self._ask_mistral(query, history=history)
                if resp:
                    return resp
            resp = self._ask_rtx_a6000(query, history=history)
            if resp:
                return resp
            if self.groq_api_key:
                resp = self._ask_groq(query, history=history)
                if resp:
                    return resp

        # 2. Deep Research: Gemini 2.0 (2M Context) -> Claude -> Kimi K3 -> Groq -> Mistral
        elif task_type == "research":
            if self.gemini_api_key:
                resp = self._ask_gemini(query, history=history, model=self.gemini_model)
                if resp:
                    return resp
            if self.anthropic_api_key:
                resp = self._ask_anthropic(query, history=history)
                if resp:
                    return resp
            resp = self._ask_rtx_5090(query, history=history)
            if resp:
                return resp

        # 3. Fast / General Voice: Gemini 2.0 Flash -> Groq (0.8s) -> Local RTX A6000 -> HF Pool -> Claude -> OpenAI
        if self.gemini_api_key:
            resp = self._ask_gemini(query, history=history, model=self.gemini_model)
            if resp:
                return resp
        if self.groq_api_key:
            resp = self._ask_groq(query, history=history)
            if resp:
                return resp

        # Check Local RTX A6000 Ollama Node
        resp = self._ask_rtx_a6000(query, history=history)
        if resp:
            return resp

        # Check Remote RTX 5090 Kimi K3 Node
        resp = self._ask_rtx_5090(query, history=history)
        if resp:
            return resp

        # Check Mistral
        if self.mistral_api_key:
            resp = self._ask_mistral(query, history=history)
            if resp:
                return resp

        # Check Anthropic Claude
        if self.anthropic_api_key:
            resp = self._ask_anthropic(query, history=history)
            if resp:
                return resp

        # Check OpenAI GPT
        if self.openai_api_key:
            resp = self._ask_openai(query, history=history)
            if resp:
                return resp

        # Check Hugging Face Burst Pool
        resp = self._ask_hf_burst(query)
        if resp:
            return resp

        # Offline rule fallback
        return self._local_rule_fallback(query)

    # --------------------------------------------------------------------------
    # ENGINE IMPLEMENTATIONS
    # --------------------------------------------------------------------------
    def _ask_gemini(self, query: str, history: Optional[List[Dict[str, str]]] = None, model: str = "gemini-3.6-flash", system_prompt: Optional[str] = None, max_tokens: int = 2500) -> Optional[str]:
        """Queries Google Gemini API with automatic fallback between official SDK and REST."""
        if not self.gemini_api_key:
            return None
        t0 = time.time()
        sys_inst = system_prompt or self.system_prompt

        candidate_models = [model, "gemini-3.6-flash", "gemini-2.5-flash", "gemini-1.5-flash"]
        seen_models = set()
        candidate_models = [m for m in candidate_models if not (m in seen_models or seen_models.add(m))]

        # 1. Try google-genai SDK
        for cand_model in candidate_models:
            try:
                from google import genai
                client = genai.Client(api_key=self.gemini_api_key)
                response = client.models.generate_content(
                    model=cand_model,
                    contents=query,
                    config={
                        "system_instruction": sys_inst,
                        "max_output_tokens": max_tokens,
                        "temperature": 0.7
                    }
                )
                if response and response.text:
                    logger.info(f"Gemini responded via google-genai in {round(time.time() - t0, 2)}s [{cand_model}]")
                    return response.text.strip()
            except Exception as e:
                logger.debug(f"google-genai SDK call error for {cand_model}: {e}")

        # 2. Try direct REST API
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.gemini_api_key}"
            payload = {
                "contents": [{"parts": [{"text": query}]}],
                "systemInstruction": {"parts": [{"text": sys_inst}]},
                "generationConfig": {
                    "maxOutputTokens": max_tokens,
                    "temperature": 0.7
                }
            }
            resp = requests.post(url, json=payload, timeout=20.0)
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        text = parts[0].get("text", "")
                        logger.info(f"Gemini responded via REST in {round(time.time() - t0, 2)}s [{model}]")
                        return text.strip()
            else:
                logger.debug(f"Gemini REST status {resp.status_code}: {resp.text[:120]}")
        except Exception as e:
            logger.debug(f"Gemini REST call failed: {e}")

        return None

    def _ask_groq(self, query: str, history: Optional[List[Dict[str, str]]] = None, max_tokens: int = 1500, system_prompt: Optional[str] = None) -> Optional[str]:
        """Queries Groq LPU for sub-second (0.8s) response."""
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            messages = [{"role": "system", "content": system_prompt or self.system_prompt}]
            if history:
                messages.extend(history[-6:])
            messages.append({"role": "user", "content": query})

            payload = {
                "model": self.groq_model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0.7
            }
            r = requests.post(url, json=payload, headers=headers, timeout=6.0)
            if r.status_code == 200:
                data = r.json()
                content = data["choices"][0]["message"]["content"].strip()
                logger.info(f"Groq response received ({len(content)} chars)")
                return content
            else:
                logger.debug(f"Groq API status {r.status_code}: {r.text}")
        except Exception as e:
            logger.debug(f"Groq query failed: {e}")
        return None

    def _ask_mistral(self, query: str, history: Optional[List[Dict[str, str]]] = None, max_tokens: int = 1024) -> Optional[str]:
        """Queries Mistral Codestral for precise coding."""
        try:
            url = "https://api.mistral.ai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.mistral_api_key}",
                "Content-Type": "application/json"
            }
            messages = [{"role": "system", "content": self.system_prompt}]
            if history:
                messages.extend(history[-6:])
            messages.append({"role": "user", "content": query})

            payload = {
                "model": self.mistral_model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0.3
            }
            r = requests.post(url, json=payload, headers=headers, timeout=8.0)
            if r.status_code == 200:
                data = r.json()
                content = data["choices"][0]["message"]["content"].strip()
                logger.info(f"Mistral response received ({len(content)} chars)")
                return content
            else:
                logger.debug(f"Mistral API status {r.status_code}: {r.text}")
        except Exception as e:
            logger.debug(f"Mistral query failed: {e}")
        return None

    def _ask_rtx_a6000(self, query: str, history: Optional[List[Dict[str, str]]] = None) -> Optional[str]:
        """Queries local NVIDIA RTX A6000 (Ollama: Qwen 2.5 Coder 32B)."""
        try:
            url = f"{self.rtx_a6000_url}/v1/chat/completions"
            messages = [{"role": "system", "content": self.system_prompt}]
            if history:
                messages.extend(history[-6:])
            messages.append({"role": "user", "content": query})

            payload = {
                "model": self.rtx_a6000_model,
                "messages": messages,
                "max_tokens": 1024,
                "temperature": 0.7
            }
            r = requests.post(url, json=payload, timeout=5.0)
            if r.status_code == 200:
                data = r.json()
                return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.debug(f"Local RTX A6000 Ollama offline or timed out: {e}")
        return None

    def _ask_rtx_5090(self, query: str, history: Optional[List[Dict[str, str]]] = None) -> Optional[str]:
        """Queries remote NVIDIA RTX 5090 cluster (Moonshot Kimi K3 1M-context)."""
        try:
            url = f"{self.rtx_5090_url}/v1/chat/completions"
            messages = [{"role": "system", "content": self.system_prompt}]
            if history:
                messages.extend(history[-6:])
            messages.append({"role": "user", "content": query})

            payload = {
                "model": self.rtx_5090_model,
                "messages": messages,
                "max_tokens": 1024,
                "temperature": 0.7
            }
            r = requests.post(url, json=payload, timeout=5.0)
            if r.status_code == 200:
                data = r.json()
                return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.debug(f"Remote RTX 5090 Kimi K3 cluster offline or timed out: {e}")
        return None

    def _ask_hf_burst(self, query: str) -> Optional[str]:
        """Queries serverless Hugging Face Inference API rotating through 15 tokens."""
        if not self.hf_tokens:
            return None

        # Round-robin token selector
        token = self.hf_tokens[self._hf_index % len(self.hf_tokens)]
        self._hf_index += 1

        url = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.3-70B-Instruct/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "meta-llama/Llama-3.3-70B-Instruct",
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": query}
            ],
            "max_tokens": 512,
            "temperature": 0.7
        }
        try:
            r = requests.post(url, json=payload, headers=headers, timeout=8.0)
            if r.status_code == 200:
                data = r.json()
                return data["choices"][0]["message"]["content"].strip()
            else:
                logger.debug(f"HF burst error {r.status_code}: {r.text[:100]}")
        except Exception as e:
            logger.debug(f"HF burst exception: {e}")
        return None

    def _ask_anthropic(self, query: str, history: Optional[List[Dict[str, str]]] = None) -> Optional[str]:
        """Queries Anthropic Claude API."""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.anthropic_api_key)
            messages = []
            if history:
                for h in history[-6:]:
                    messages.append({"role": h["role"], "content": h["content"]})
            messages.append({"role": "user", "content": query})

            response = client.messages.create(
                model=self.model_anthropic,
                system=self.system_prompt,
                messages=messages,
                max_tokens=1024
            )
            return response.content[0].text.strip()
        except Exception as e:
            logger.debug(f"Anthropic query error: {e}")
            return None

    def _ask_openai(self, query: str, history: Optional[List[Dict[str, str]]] = None) -> Optional[str]:
        """Queries OpenAI API."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            messages = [{"role": "system", "content": self.system_prompt}]
            if history:
                messages.extend(history[-6:])
            messages.append({"role": "user", "content": query})

            response = client.chat.completions.create(
                model=self.model_openai,
                messages=messages,
                max_tokens=1024,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.debug(f"OpenAI query error: {e}")
            return None

    def _local_rule_fallback(self, query: str) -> str:
        """Offline fallback responses when network is unavailable."""
        q = query.lower()
        if "who are you" in q or "kaun ho" in q:
            return "I am Basit Jarvis, your sovereign desktop AI companion and system controller."
        if "time" in q or "waqt" in q:
            import datetime
            return f"The current time is {datetime.datetime.now().strftime('%I:%M %p')}."
        if "date" in q or "taareekh" in q:
            import datetime
            return f"Today is {datetime.datetime.now().strftime('%A, %B %d, %Y')}."
        return f"I heard '{query}', sir. All cloud and local models were unreachable at this instant."

    # --------------------------------------------------------------------------
    # RESPONSE CACHE  &  PARALLEL RACING
    # --------------------------------------------------------------------------
    def _cache_get(self, key: str) -> Optional[str]:
        """Retrieve cached response if still valid (TTL: 5 min)."""
        if key in self._cache:
            ts, val = self._cache[key]
            if time.time() - ts < self._cache_ttl:
                self._cache.move_to_end(key)
                return val
            del self._cache[key]
        return None

    def _cache_put(self, key: str, value: str) -> None:
        """Store response in LRU cache, evicting oldest when full."""
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = (time.time(), value)
        while len(self._cache) > self._cache_max:
            self._cache.popitem(last=False)

    def estimate_tokens(self, text: str) -> int:
        """Rough token estimate (1 token ≈ 4 chars)."""
        return max(1, len(text) // 4)

    def ask_parallel(self, query: str, timeout: float = 8.0) -> str:
        """Fire Gemini + Groq simultaneously; return first successful response.

        Falls back to ``_local_rule_fallback`` if both engines time out.
        """
        result = [None]
        lock = threading.Lock()
        done = threading.Event()

        def try_engine(fn):
            try:
                resp = fn(query)
                if resp:
                    with lock:
                        if result[0] is None:
                            result[0] = resp
                            done.set()
            except Exception:
                pass

        fns = []
        if self.gemini_api_key:
            fns.append(lambda q=query: self._ask_gemini(q, max_tokens=2000))
        if self.groq_api_key:
            fns.append(lambda q=query: self._ask_groq(q, max_tokens=1500))

        threads = [
            threading.Thread(target=try_engine, args=(fn,), daemon=True)
            for fn in fns
        ]
        for t in threads:
            t.start()

        done.wait(timeout=timeout)
        return result[0] or self._local_rule_fallback(query)

    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    def get_cluster_status(self) -> Dict[str, Any]:
        """Probes status and latency of all integrated AI engines."""
        status = {}

        # 1. Groq
        if self.groq_api_key:
            t0 = time.time()
            try:
                r = requests.get("https://api.groq.com/openai/v1/models", headers={"Authorization": f"Bearer {self.groq_api_key}"}, timeout=2.0)
                status["groq"] = {"online": r.status_code == 200, "latency_ms": round((time.time() - t0) * 1000, 1), "model": self.groq_model}
            except Exception:
                status["groq"] = {"online": False, "model": self.groq_model}
        else:
            status["groq"] = {"online": False, "reason": "No API key"}

        # 2. Mistral
        if self.mistral_api_key:
            t0 = time.time()
            try:
                r = requests.get("https://api.mistral.ai/v1/models", headers={"Authorization": f"Bearer {self.mistral_api_key}"}, timeout=2.0)
                status["mistral"] = {"online": r.status_code == 200, "latency_ms": round((time.time() - t0) * 1000, 1), "model": self.mistral_model}
            except Exception:
                status["mistral"] = {"online": False, "model": self.mistral_model}
        else:
            status["mistral"] = {"online": False, "reason": "No API key"}

        # 3. Local RTX A6000
        try:
            t0 = time.time()
            r = requests.get(f"{self.rtx_a6000_url}/api/tags", timeout=1.0)
            status["rtx_a6000"] = {"online": r.status_code == 200, "latency_ms": round((time.time() - t0) * 1000, 1), "url": self.rtx_a6000_url, "model": self.rtx_a6000_model}
        except Exception:
            status["rtx_a6000"] = {"online": False, "url": self.rtx_a6000_url, "model": self.rtx_a6000_model}

        # 4. Remote RTX 5090
        try:
            t0 = time.time()
            r = requests.get(f"{self.rtx_5090_url}/health", timeout=1.0)
            status["rtx_5090"] = {"online": r.status_code == 200, "latency_ms": round((time.time() - t0) * 1000, 1), "url": self.rtx_5090_url, "model": self.rtx_5090_model}
        except Exception:
            status["rtx_5090"] = {"online": False, "url": self.rtx_5090_url, "model": self.rtx_5090_model}

        # 5. HF Token Pool
        status["hf_token_pool"] = {
            "active_tokens": len(self.hf_tokens),
            "online": len(self.hf_tokens) > 0
        }

        # 6. Google Gemini
        if self.gemini_api_key:
            t0 = time.time()
            try:
                r = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={self.gemini_api_key}", timeout=2.5)
                status["gemini"] = {"online": r.status_code == 200, "latency_ms": round((time.time() - t0) * 1000, 1), "model": self.gemini_model}
            except Exception:
                status["gemini"] = {"online": False, "model": self.gemini_model}
        else:
            status["gemini"] = {"online": False, "reason": "No API key"}

        # 7. Apache Spark
        try:
            from modules.spark_engine import BasitSparkEngine, PYSPARK_AVAILABLE
            spark_eng = BasitSparkEngine()
            status["spark"] = spark_eng.get_telemetry()
        except Exception:
            status["spark"] = {"status": "STANDBY"}

        # 8. Cloud Anthropic / OpenAI
        status["anthropic"] = {"configured": bool(self.anthropic_api_key), "model": self.model_anthropic}
        status["openai"] = {"configured": bool(self.openai_api_key), "model": self.model_openai}

        return status
