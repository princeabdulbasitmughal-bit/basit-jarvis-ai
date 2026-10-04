"""
Comprehensive Audit & Benchmark Test Suite for ConversationalBrain
(E:\basit-jarvis-ai\modules\conversational_brain.py)

Tests:
1. Math Calculations (Accuracy, Syntax parsing, Bilingual English/Urdu math operators)
2. Jokes & Humor (Triggering, Diversity, Bilingual text)
3. Greetings (Bilingual English/Urdu, Time-of-day slots, edge-case triggers)
4. Bilingual Processing (English vs Roman Urdu across all categories & engine routings)
5. Note Extraction (Entity extraction fidelity, notes.json persistence, data structure)
6. Latency & Throughput Benchmark (P50, P90, P95, P99, Min, Max, Mean across 500+ calls)
7. Edge Cases & Pattern Collision Analysis
"""

import os
import sys
import re
import json
import time
import statistics
import unittest
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from modules.conversational_brain import (
    ConversationalBrain,
    ACTION_PATTERNS,
    BOREDOM_TRIGGERS,
    THANKS_TRIGGERS,
    GREETING_TRIGGERS,
)

def run_audit():
    print("=" * 80)
    print("👑 BASIT JARVIS AI — CONVERSATIONAL BRAIN IN-DEPTH AUDIT & BENCHMARK")
    print("=" * 80)

    brain = ConversationalBrain()
    audit_report = {
        "timestamp": datetime.now().isoformat(),
        "categories": {},
        "edge_cases": [],
        "latency_stats": {},
        "overall_status": "PASS"
    }

    # =========================================================================
    # 1. MATH CALCULATIONS AUDIT
    # =========================================================================
    print("\n" + "=" * 50)
    print("SECTION 1: MATH CALCULATIONS AUDIT")
    print("=" * 50)

    math_test_cases = [
        # Direct operators
        {"input": "calculate 25 * 4 + 10", "expected": 110, "desc": "Standard arithmetic order"},
        {"input": "calculate 100 / 4", "expected": 25.0, "desc": "Standard float division"},
        {"input": "calculate 2 ^ 8", "expected": 256, "desc": "Power operator (^)"},
        {"input": "calculate (5 + 3) * 10", "expected": 80, "desc": "Parentheses precedence"},
        {"input": "50 + 25", "expected": 75, "desc": "Pure digits + operator format"},
        {"input": "1000 - 450", "expected": 550, "desc": "Pure digits - operator format"},
        {"input": "20 * 30", "expected": 600, "desc": "Pure digits * operator format"},
        {"input": "144 / 12", "expected": 12.0, "desc": "Pure digits / operator format"},
        
        # English words
        {"input": "calculate 50 plus 25", "expected": 75, "desc": "English 'plus'"},
        {"input": "100 divided by 5", "expected": 20.0, "desc": "English 'divided by'"},
        {"input": "20 times 6", "expected": 120, "desc": "English 'times'"},
        {"input": "80 minus 35", "expected": 45, "desc": "English 'minus'"},
        {"input": "calculate 2 power 5", "expected": 32, "desc": "English 'power'"},
        {"input": "10 multiplied by 5", "expected": 50, "desc": "English 'multiplied by'"},

        # Roman Urdu words
        {"input": "hisab karo 15 jama 25", "expected": 40, "desc": "Urdu 'hisab karo' + 'jama'"},
        {"input": "25 zarab 4 kitna hota hai", "expected": 100, "desc": "Urdu 'zarab' + 'kitna hota hai'"},
        {"input": "100 taqseem 5 kitna hota hai", "expected": 20.0, "desc": "Urdu 'taqseem' + 'kitna hota hai'"},
        {"input": "50 tafriq 20", "expected": 30, "desc": "Urdu 'tafriq'"},
        {"input": "nikalo 30 into 4", "expected": 120, "desc": "Urdu 'nikalo' + 'into'"},
        {"input": "100 * 25 + 500 calculate karo", "expected": 3000, "desc": "Urdu suffix 'calculate karo'"},
        {"input": "50 + 50 kitne hote hain", "expected": 100, "desc": "Urdu suffix 'kitne hote hain'"},
        {"input": "10 ghaat 3", "expected": 1000, "desc": "Urdu 'ghaat' (exponent)"},
    ]

    math_results = []
    math_latencies = []

    for tc in math_test_cases:
        t0 = time.perf_counter()
        resp = brain.respond(tc["input"])
        lat = (time.perf_counter() - t0) * 1000
        math_latencies.append(lat)

        ans_text = resp.get("response", "")
        act = resp.get("action_taken")

        # Check if expected number is in answer
        expected_str = str(tc["expected"])
        passed = (act == "calculate") and (f"**{expected_str}**" in ans_text or str(tc["expected"]) in ans_text)
        
        math_results.append({
            "input": tc["input"],
            "desc": tc["desc"],
            "expected": tc["expected"],
            "actual_response": ans_text,
            "action": act,
            "passed": passed,
            "latency_ms": round(lat, 3)
        })
        print(f"[{'PASS' if passed else 'FAIL'}] {tc['desc']}: '{tc['input']}' -> {ans_text} ({lat:.2f}ms)")

    # Edge cases in Math
    print("\n--- Math Edge Cases ---")
    div_zero = brain.respond("calculate 10 / 0")
    print(f"Division by zero test: {div_zero.get('response')}")
    
    invalid_math = brain.respond("calculate abc + def")
    print(f"Invalid math syntax: {invalid_math.get('response')}")

    math_pass_count = sum(1 for r in math_results if r["passed"])
    audit_report["categories"]["math"] = {
        "total": len(math_results),
        "passed": math_pass_count,
        "accuracy_pct": round(math_pass_count / len(math_results) * 100, 2),
        "avg_latency_ms": round(statistics.mean(math_latencies), 3),
        "p95_latency_ms": round(statistics.quantiles(math_latencies, n=20)[18], 3),
        "details": math_results
    }

    # =========================================================================
    # 2. JOKES & HUMOR AUDIT
    # =========================================================================
    print("\n" + "=" * 50)
    print("SECTION 2: JOKES & HUMOR AUDIT")
    print("=" * 50)

    joke_inputs = [
        ("koi joke sunao", "Urdu trigger: 'koi joke sunao'"),
        ("latifa sunao", "Urdu trigger: 'latifa sunao'"),
        ("chutkula sunao", "Urdu trigger: 'chutkula sunao'"),
        ("tell me a joke", "English trigger: 'tell me a joke'"),
        ("make me laugh", "English trigger: 'make me laugh'"),
        ("koi mazah wali baat sunao", "Urdu trigger: 'mazah wali baat'"),
        ("ek joke sunao", "Urdu trigger: 'ek joke sunao'"),
    ]

    joke_results = []
    joke_latencies = []
    seen_jokes = set()

    for inp, desc in joke_inputs:
        t0 = time.perf_counter()
        resp = brain.respond(inp)
        lat = (time.perf_counter() - t0) * 1000
        joke_latencies.append(lat)

        ans = resp.get("response", "")
        act = resp.get("action_taken")
        passed = (act == "tell_joke") and (len(ans) > 20)
        if passed:
            seen_jokes.add(ans)

        joke_results.append({
            "input": inp,
            "desc": desc,
            "response": ans,
            "action": act,
            "passed": passed,
            "latency_ms": round(lat, 3)
        })
        print(f"[{'PASS' if passed else 'FAIL'}] {desc}: '{inp}' -> {ans[:70]}... ({lat:.2f}ms)")

    # Diversity check: sample 20 jokes
    sampled_pool = set()
    for _ in range(25):
        r = brain._tell_joke()
        sampled_pool.add(r)
    print(f"\nJoke Pool Diversity: Found {len(sampled_pool)} distinct jokes out of 25 samplings.")

    joke_pass_count = sum(1 for r in joke_results if r["passed"])
    audit_report["categories"]["jokes"] = {
        "total": len(joke_results),
        "passed": joke_pass_count,
        "accuracy_pct": round(joke_pass_count / len(joke_results) * 100, 2),
        "pool_size": len(sampled_pool),
        "avg_latency_ms": round(statistics.mean(joke_latencies), 3),
        "details": joke_results
    }

    # =========================================================================
    # 3. GREETINGS AUDIT
    # =========================================================================
    print("\n" + "=" * 50)
    print("SECTION 3: GREETINGS AUDIT (TIME & BILINGUAL)")
    print("=" * 50)

    greeting_inputs = [
        # Roman Urdu greetings
        ("salam", "Urdu: 'salam'"),
        ("assalam o alaikum", "Urdu: 'assalam o alaikum'"),
        ("kya haal hai", "Urdu: 'kya haal hai'"),
        ("kaise ho bhai", "Urdu: 'kaise ho'"),
        ("kia hal hai", "Urdu: 'kia hal hai'"),
        ("aur sunao sab theek", "Urdu: 'aur sunao' + 'sab theek'"),
        ("adaab", "Urdu: 'adaab'"),

        # English greetings
        ("hello jarvis", "English: 'hello jarvis'"),
        ("hey jarvis", "English: 'hey jarvis'"),
        ("good morning", "English: 'good morning'"),
        ("good night", "English: 'good night'"),
        ("how are you", "English: 'how are you'"),
        ("what's up", "English: 'what's up'"),
        ("hi there", "English: 'hi there'"),
        ("hi", "Edge case: isolated 'hi'"),
    ]

    greeting_results = []
    greeting_latencies = []

    for inp, desc in greeting_inputs:
        t0 = time.perf_counter()
        resp = brain.respond(inp)
        lat = (time.perf_counter() - t0) * 1000
        greeting_latencies.append(lat)

        ans = resp.get("response", "")
        act = resp.get("action_taken")
        # For greeting, action_taken should be "conversation"
        passed = (act == "conversation") and (ans is not None and len(ans) > 5)

        greeting_results.append({
            "input": inp,
            "desc": desc,
            "response": ans,
            "action": act,
            "passed": passed,
            "latency_ms": round(lat, 3)
        })
        print(f"[{'PASS' if passed else 'FAIL'}] {desc}: '{inp}' -> '{ans}' ({lat:.2f}ms)")

    greeting_pass_count = sum(1 for r in greeting_results if r["passed"])
    audit_report["categories"]["greetings"] = {
        "total": len(greeting_results),
        "passed": greeting_pass_count,
        "accuracy_pct": round(greeting_pass_count / len(greeting_results) * 100, 2),
        "avg_latency_ms": round(statistics.mean(greeting_latencies), 3),
        "details": greeting_results
    }

    # =========================================================================
    # 4. URDU/ENGLISH BILINGUAL PROCESSING & ENGINE ROUTING
    # =========================================================================
    print("\n" + "=" * 50)
    print("SECTION 4: BILINGUAL PROCESSING & INTENT ROUTING")
    print("=" * 50)

    bilingual_test_cases = [
        # Gratitude (Urdu vs English)
        {"input": "shukriya bhai bahut achha kaam kiya", "lang": "Urdu", "expected_act": "conversation", "expected_engine": None, "desc": "Urdu gratitude"},
        {"input": "thank you so much jarvis", "lang": "English", "expected_act": "conversation", "expected_engine": None, "desc": "English gratitude"},
        {"input": "jazakallah khair", "lang": "Urdu", "expected_act": "conversation", "expected_engine": None, "desc": "Urdu gratitude (Jazakallah)"},

        # Boredom / Emotional (Urdu vs English)
        {"input": "bore ho raha hoon kuch batao", "lang": "Urdu", "expected_act": "conversation", "expected_engine": None, "desc": "Urdu boredom"},
        {"input": "khali baitha hoon yaar", "lang": "Urdu", "expected_act": "conversation", "expected_engine": None, "desc": "Urdu boredom (khali baitha)"},

        # Code Generation Routing (English vs Urdu -> basit1)
        {"input": "generate python code for jwt authentication", "lang": "English", "expected_act": None, "expected_engine": "basit1", "desc": "English code gen routing"},
        {"input": "python script banao file backup ke liye", "lang": "Urdu", "expected_act": None, "expected_engine": "basit1", "desc": "Urdu code gen routing"},
        {"input": "code banao ek REST API ka", "lang": "Urdu", "expected_act": None, "expected_engine": "basit1", "desc": "Urdu code generation pattern"},

        # Research Routing (English vs Urdu -> basit2)
        {"input": "research quantum computing algorithms", "lang": "English", "expected_act": None, "expected_engine": "basit2", "desc": "English research routing"},
        {"input": "artificial intelligence ke baray mein research karo", "lang": "Urdu", "expected_act": None, "expected_engine": "basit2", "desc": "Urdu research routing"},
        {"input": "explain docker containers and kubernetes difference", "lang": "English", "expected_act": "route_to_engine", "expected_engine": "basit2", "desc": "English explanation routing"},

        # Security Routing (English vs Urdu -> basit3)
        {"input": "run security audit on our server", "lang": "English", "expected_act": "route_to_engine", "expected_engine": "basit3", "desc": "English security routing"},
        {"input": "vulnerability scan karo system ka", "lang": "Urdu", "expected_act": "route_to_engine", "expected_engine": "basit3", "desc": "Urdu vulnerability scan routing"},

        # Financial / Market Routing (English vs Urdu -> basit4)
        {"input": "what is current btc price and trend", "lang": "English", "expected_act": "route_to_engine", "expected_engine": "basit4", "desc": "English crypto routing"},
        {"input": "nvda stock trading analysis batao", "lang": "Urdu", "expected_act": "route_to_engine", "expected_engine": "basit4", "desc": "Urdu stock routing"},

        # System Status (English vs Urdu)
        {"input": "system status check", "lang": "English", "expected_act": "system_status", "expected_engine": None, "desc": "English system status"},
        {"input": "computer ka kaisa hal hai", "lang": "Urdu", "expected_act": "system_status", "expected_engine": None, "desc": "Urdu system status"},
    ]

    bilingual_results = []
    bilingual_latencies = []

    for tc in bilingual_test_cases:
        t0 = time.perf_counter()
        resp = brain.respond(tc["input"])
        lat = (time.perf_counter() - t0) * 1000
        bilingual_latencies.append(lat)

        act = resp.get("action_taken")
        eng = resp.get("needs_engine")

        engine_matches = (eng == tc["expected_engine"])
        action_matches = True
        if tc["expected_act"] is not None:
            action_matches = (act == tc["expected_act"])

        passed = engine_matches and action_matches
        bilingual_results.append({
            "input": tc["input"],
            "lang": tc["lang"],
            "desc": tc["desc"],
            "actual_action": act,
            "expected_action": tc["expected_act"],
            "actual_engine": eng,
            "expected_engine": tc["expected_engine"],
            "passed": passed,
            "latency_ms": round(lat, 3)
        })
        print(f"[{'PASS' if passed else 'FAIL'}] [{tc['lang']}] {tc['desc']}: act={act}, eng={eng} ({lat:.2f}ms)")

    bilingual_pass_count = sum(1 for r in bilingual_results if r["passed"])
    audit_report["categories"]["bilingual"] = {
        "total": len(bilingual_results),
        "passed": bilingual_pass_count,
        "accuracy_pct": round(bilingual_pass_count / len(bilingual_results) * 100, 2),
        "avg_latency_ms": round(statistics.mean(bilingual_latencies), 3),
        "details": bilingual_results
    }

    # =========================================================================
    # 5. NOTE EXTRACTION & PERSISTENCE AUDIT
    # =========================================================================
    print("\n" + "=" * 50)
    print("SECTION 5: NOTE EXTRACTION & PERSISTENCE AUDIT")
    print("=" * 50)

    notes_path = os.path.join(BASE_DIR, 'notes.json')
    initial_note_count = 0
    if os.path.exists(notes_path):
        try:
            with open(notes_path, encoding='utf-8') as f:
                initial_note_count = len(json.load(f))
        except Exception:
            initial_note_count = 0

    note_test_cases = [
        {"input": "note buy groceries and almond milk", "expected_content": "buy groceries and almond milk", "desc": "Simple English note"},
        {"input": "naya note kal subah 9 baje client meeting hai", "expected_content": "kal subah 9 baje client meeting hai", "desc": "Urdu 'naya note' prefix"},
        {"input": "likho check server memory logs every 2 hours", "expected_content": "check server memory logs every 2 hours", "desc": "Urdu 'likho' keyword"},
        {"input": "save this: deploy staging build before 6 PM", "expected_content": "deploy staging build before 6 PM", "desc": "English 'save this:' prefix"},
        {"input": "store karo API keys rotate karni hain kal", "expected_content": "API keys rotate karni hain kal", "desc": "Urdu 'store karo' prefix"},
    ]

    note_results = []
    note_latencies = []

    for tc in note_test_cases:
        t0 = time.perf_counter()
        resp = brain.respond(tc["input"])
        lat = (time.perf_counter() - t0) * 1000
        note_latencies.append(lat)

        ans = resp.get("response", "")
        act = resp.get("action_taken")

        # Verify action
        is_note_action = (act == "create_note")

        # Verify in notes.json
        saved_properly = False
        saved_item = None
        if os.path.exists(notes_path):
            with open(notes_path, encoding='utf-8') as f:
                all_notes = json.load(f)
                for n in reversed(all_notes):
                    if tc["expected_content"].lower() in n.get("content", "").lower():
                        saved_properly = True
                        saved_item = n
                        break

        passed = is_note_action and saved_properly
        note_results.append({
            "input": tc["input"],
            "desc": tc["desc"],
            "expected_content": tc["expected_content"],
            "saved_content": saved_item.get("content") if saved_item else None,
            "has_timestamp": "timestamp" in saved_item if saved_item else False,
            "has_id": "id" in saved_item if saved_item else False,
            "passed": passed,
            "latency_ms": round(lat, 3)
        })
        print(f"[{'PASS' if passed else 'FAIL'}] {tc['desc']}: Extracted='{saved_item.get('content') if saved_item else 'NONE'}' ({lat:.2f}ms)")

    note_pass_count = sum(1 for r in note_results if r["passed"])
    audit_report["categories"]["note_extraction"] = {
        "total": len(note_results),
        "passed": note_pass_count,
        "accuracy_pct": round(note_pass_count / len(note_results) * 100, 2),
        "avg_latency_ms": round(statistics.mean(note_latencies), 3),
        "details": note_results
    }

    # =========================================================================
    # 6. LATENCY & THROUGHPUT BENCHMARK (500 ITERATIONS)
    # =========================================================================
    print("\n" + "=" * 50)
    print("SECTION 6: STRESS & LATENCY BENCHMARK (500 CALLS)")
    print("=" * 50)

    # Pure NLU & conversational intent benchmark (excluding psutil 500ms block)
    benchmark_corpus = [
        "calculate 125 * 8 + 350",
        "koi joke sunao",
        "salam jarvis bhai",
        "shukriya bohat khoob",
        "generate python code for fast api",
        "research agentic ai patterns",
        "25 zarab 4 kitna hota hai",
        "tell me a joke",
        "good morning boss",
        "note kal meeting 3 baje hai",
    ]

    benchmark_latencies = []
    t_start = time.perf_counter()
    iterations = 500

    for i in range(iterations):
        query = benchmark_corpus[i % len(benchmark_corpus)]
        t0 = time.perf_counter()
        brain.respond(query)
        lat = (time.perf_counter() - t0) * 1000
        benchmark_latencies.append(lat)

    total_duration = time.perf_counter() - t_start
    throughput = iterations / total_duration

    sorted_lats = sorted(benchmark_latencies)
    p50 = sorted_lats[int(0.50 * iterations)]
    p90 = sorted_lats[int(0.90 * iterations)]
    p95 = sorted_lats[int(0.95 * iterations)]
    p99 = sorted_lats[int(0.99 * iterations)]
    mean_lat = statistics.mean(benchmark_latencies)
    min_lat = min(benchmark_latencies)
    max_lat = max(benchmark_latencies)

    print(f"Total Requests: {iterations}")
    print(f"Total Time: {total_duration:.3f} s")
    print(f"Throughput: {throughput:.1f} req/sec")
    print(f"Min Latency: {min_lat:.3f} ms")
    print(f"Mean Latency: {mean_lat:.3f} ms")
    print(f"Median (P50): {p50:.3f} ms")
    print(f"P90: {p90:.3f} ms")
    print(f"P95: {p95:.3f} ms")
    print(f"P99: {p99:.3f} ms")
    print(f"Max Latency: {max_lat:.3f} ms")

    audit_report["latency_stats"] = {
        "iterations": iterations,
        "throughput_rps": round(throughput, 1),
        "min_ms": round(min_lat, 3),
        "mean_ms": round(mean_lat, 3),
        "p50_ms": round(p50, 3),
        "p90_ms": round(p90, 3),
        "p95_ms": round(p95, 3),
        "p99_ms": round(p99, 3),
        "max_ms": round(max_lat, 3),
    }

    # =========================================================================
    # 7. CODE & REGEX AUDIT FINDINGS (EDGE CASES & BUGS)
    # =========================================================================
    print("\n" + "=" * 50)
    print("SECTION 7: CODE AUDIT FINDINGS")
    print("=" * 50)

    # Finding 1: Duplicate dictionary keys in ACTION_PATTERNS
    # In Python dict definition, "set_reminder" appears twice: lines 148-152 and lines 164-169.
    # The second key completely overwrites the first!
    print("Analyzing ACTION_PATTERNS definitions...")
    raw_file = open(os.path.join(BASE_DIR, 'modules', 'conversational_brain.py'), encoding='utf-8').read()
    reminder_matches = [m.start() for m in re.finditer(r'["\']set_reminder["\']\s*:', raw_file)]
    if len(reminder_matches) > 1:
        msg = f"FOUND BUG: 'set_reminder' is defined {len(reminder_matches)} times in ACTION_PATTERNS dictionary. Python dictionaries silently overwrite earlier duplicate keys, causing loss of patterns."
        print(f"⚠️  {msg}")
        audit_report["edge_cases"].append({"id": "BUG-01", "severity": "MEDIUM", "description": msg})

    # Finding 2: Isolated 'hi' trigger bug
    # GREETING_TRIGGERS contains 'hi ' with a space, so bare 'hi' without spaces or trailing chars fails detection
    bare_hi_result = brain.respond("hi")
    if bare_hi_result.get("action_taken") != "conversation":
        msg = "FOUND BUG: GREETING_TRIGGERS has 'hi ' (with a trailing space) instead of word boundary match. Bare greeting 'hi' is not recognized as a greeting!"
        print(f"⚠️  {msg}")
        audit_report["edge_cases"].append({"id": "BUG-02", "severity": "LOW", "description": msg})

    # Finding 3: 'save changes' git commit vs create note collision
    # create_note pattern: r"(?:save|sacha\s+karo|store)\s+(?:karo\s+)?(?:yeh|this)?\s*:?\s*(?P<content>.+)"
    # git_commit pattern: r"(?:commit|save\s+changes|changes\s+save\s+karo)..."
    # Because create_note is tested before git_commit in ACTION_PATTERNS, 'save changes...' gets captured as a note!
    git_test = brain.respond("save changes fix auth bug")
    if git_test.get("action_taken") == "create_note":
        msg = "FOUND COLLISION: 'save changes fix auth bug' was matched as 'create_note' because create_note regex precedes git_commit in ACTION_PATTERNS."
        print(f"⚠️  {msg}")
        audit_report["edge_cases"].append({"id": "BUG-03", "severity": "MEDIUM", "description": msg})

    # Finding 4: Boredom trigger preempting jokes
    boredom_joke_test = brain.respond("bore ho raha hoon koi joke sunao")
    if boredom_joke_test.get("action_taken") == "conversation" and "joke" not in str(boredom_joke_test.get("response")).lower():
        msg = "FOUND PREEMPTION: detect_emotion() runs before detect_action(). User saying 'bore ho raha hoon koi joke sunao' triggers generic boredom response instead of telling a joke."
        print(f"⚠️  {msg}")
        audit_report["edge_cases"].append({"id": "BUG-04", "severity": "LOW", "description": msg})

    # Output Summary JSON
    print("\n" + "=" * 80)
    print("AUDIT SUMMARY REPORT:")
    print("=" * 80)
    summary_display = {
        "accuracy_by_category": {k: f"{v['accuracy_pct']}% ({v['passed']}/{v['total']})" for k, v in audit_report["categories"].items()},
        "latency_stats": audit_report["latency_stats"],
        "issues_identified_count": len(audit_report["edge_cases"]),
        "issues": audit_report["edge_cases"]
    }
    print(json.dumps(summary_display, indent=2))

    return audit_report

if __name__ == "__main__":
    run_audit()
