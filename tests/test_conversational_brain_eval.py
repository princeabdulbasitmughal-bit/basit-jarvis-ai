"""
Evaluation script for Conversational Brain (modules/conversational_brain.py)
Tests:
1. Emotion Detection (Boredom, Thanks, Greeting, Neutral)
2. Greetings (Morning, Day, Night time slots)
3. Jokes & Humor response handling
4. Math Calculation & parsing
5. Note creation and file persistence
6. PDF-to-Word conversion workflow
"""

import os
import sys
import json
import time
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from modules.conversational_brain import ConversationalBrain, BOREDOM_TRIGGERS, THANKS_TRIGGERS, GREETING_TRIGGERS

def run_tests():
    print("=" * 60)
    print("CONVERSATIONAL BRAIN EVALUATION")
    print("=" * 60)
    
    brain = ConversationalBrain()
    results = {}

    # ----------------------------------------------------
    # 1. EMOTION DETECTION
    # ----------------------------------------------------
    print("\n--- 1. Testing Emotion Detection ---")
    test_emotions = [
        ("yaar main bore ho raha hoon", "boredom"),
        ("khali baitha hoon kuch kaam nahi", "boredom"),
        ("shukriya bhai bohat maza aaya", "thanks"),
        ("thank you so much jarvis", "thanks"),
        ("salam bhai kaise ho", "greeting"),
        ("good morning jarvis", "greeting"),
        ("what is python programming", "neutral"),
    ]
    
    emotion_success = 0
    t0 = time.perf_counter()
    for phrase, expected in test_emotions:
        detected = brain.detect_emotion(phrase)
        matched = detected == expected
        if matched:
            emotion_success += 1
        print(f"Phrase: '{phrase}' -> Detected: '{detected}' | Expected: '{expected}' | {'PASS' if matched else 'FAIL'}")
    latency_emotion = (time.perf_counter() - t0) / len(test_emotions) * 1000
    results["emotion_detection"] = {
        "status": "Working" if emotion_success == len(test_emotions) else "Degraded",
        "passed": f"{emotion_success}/{len(test_emotions)}",
        "latency_ms": round(latency_emotion, 3)
    }

    # ----------------------------------------------------
    # 2. GREETINGS
    # ----------------------------------------------------
    print("\n--- 2. Testing Greetings (Time-aware) ---")
    greeting_tests = ["hello jarvis", "assalam o alaikum", "good morning", "kya haal hai"]
    greetings_ok = True
    t0 = time.perf_counter()
    for g in greeting_tests:
        resp = brain.respond(g)
        print(f"Input: '{g}' -> Response: '{resp.get('response')}' | Action: {resp.get('action_taken')}")
        if not resp.get("response") or resp.get("action_taken") != "conversation":
            greetings_ok = False
    latency_greeting = (time.perf_counter() - t0) / len(greeting_tests) * 1000
    results["greetings"] = {
        "status": "Working" if greetings_ok else "Degraded",
        "latency_ms": round(latency_greeting, 3)
    }

    # ----------------------------------------------------
    # 3. JOKES / HUMOR
    # ----------------------------------------------------
    print("\n--- 3. Testing Jokes / Humor Queries ---")
    joke_tests = [
        "koi joke sunao",
        "tell me a joke",
        "bore ho raha hoon koi mazahiya baat batao",
    ]
    t0 = time.perf_counter()
    joke_outputs = []
    for jt in joke_tests:
        resp = brain.respond(jt)
        print(f"Input: '{jt}' -> Response: '{resp.get('response')}' | Action: {resp.get('action_taken')} | NeedsEngine: {resp.get('needs_engine')}")
        joke_outputs.append(resp)
    latency_joke = (time.perf_counter() - t0) / len(joke_tests) * 1000
    # Evaluate: if boredom is detected or it routes to AI conversation
    has_response = any(r.get("response") for r in joke_outputs)
    results["jokes"] = {
        "status": "Working" if has_response else "Degraded",
        "latency_ms": round(latency_joke, 3),
        "note": "Boredom trigger catches boredom humor requests; others route to AI brain conversation"
    }

    # ----------------------------------------------------
    # 4. MATH CALCULATIONS
    # ----------------------------------------------------
    print("\n--- 4. Testing Math Calculation ---")
    math_tests = [
        ("calculate 25 * 4 + 50", "150"),
        ("hisab karo 1000 / 8", "125.0"),
        ("calculate 2^10", "1024"),
        ("50 + 25", "75"),
    ]
    math_passed = 0
    t0 = time.perf_counter()
    for expr_input, expected_val in math_tests:
        resp = brain.respond(expr_input)
        ans = resp.get("response", "")
        passed = expected_val in ans
        if passed:
            math_passed += 1
        print(f"Input: '{expr_input}' -> Response: '{ans}' | Expected: {expected_val} | {'PASS' if passed else 'FAIL'}")
    latency_math = (time.perf_counter() - t0) / len(math_tests) * 1000
    results["math"] = {
        "status": "Working" if math_passed == len(math_tests) else "Degraded",
        "passed": f"{math_passed}/{len(math_tests)}",
        "latency_ms": round(latency_math, 3)
    }

    # ----------------------------------------------------
    # 5. NOTE CREATION
    # ----------------------------------------------------
    print("\n--- 5. Testing Note Creation ---")
    test_note_content = f"Capability evaluation test note created at {datetime.now().isoformat()}"
    t0 = time.perf_counter()
    resp_note = brain.respond(f"note karo {test_note_content}")
    latency_note = (time.perf_counter() - t0) * 1000
    print(f"Note Response: {resp_note.get('response')}")
    
    notes_path = os.path.join(BASE_DIR, 'notes.json')
    note_saved = False
    if os.path.exists(notes_path):
        try:
            notes = json.load(open(notes_path, encoding='utf-8'))
            note_saved = any(test_note_content in n.get("content", "") for n in notes)
        except Exception as e:
            print(f"Error reading notes.json: {e}")
            
    print(f"Note verified in notes.json: {note_saved}")
    results["note_creation"] = {
        "status": "Working" if note_saved else "Not Working",
        "latency_ms": round(latency_note, 3)
    }

    # ----------------------------------------------------
    # 6. PDF-TO-WORD CONVERSION
    # ----------------------------------------------------
    print("\n--- 6. Testing PDF-to-Word Conversion ---")
    test_pdf_dir = os.path.join(BASE_DIR, "reports")
    os.makedirs(test_pdf_dir, exist_ok=True)
    test_pdf_path = os.path.join(test_pdf_dir, "jarvis_eval_sample.pdf")
    
    # Generate simple test PDF using PyMuPDF (fitz)
    import fitz
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Basit Jarvis AI Test Document", fontsize=18)
    page.insert_text((50, 80), "This is an automated test page for verifying PDF to Word conversion.", fontsize=12)
    page.insert_text((50, 110), f"Timestamp: {datetime.now().isoformat()}", fontsize=10)
    doc.save(test_pdf_path)
    doc.close()
    print(f"Generated sample PDF at: {test_pdf_path}")

    # Set last_pdf on brain and test _pdf_to_word
    brain.last_pdf = test_pdf_path
    t0 = time.perf_counter()
    resp_pdf = brain._pdf_to_word()
    latency_pdf = (time.perf_counter() - t0) * 1000
    print(f"PDF Conversion Response: {resp_pdf}")
    
    expected_docx = test_pdf_path.replace(".pdf", ".docx")
    pdf_converted = os.path.exists(expected_docx) and os.path.getsize(expected_docx) > 0
    print(f"Generated DOCX exists ({expected_docx}): {pdf_converted}")
    
    results["pdf_to_word"] = {
        "status": "Working" if pdf_converted else "Not Working",
        "file_created": expected_docx if pdf_converted else None,
        "latency_ms": round(latency_pdf, 3)
    }

    print("\n" + "=" * 60)
    print("CONVERSATIONAL BRAIN TEST SUMMARY:")
    print(json.dumps(results, indent=2))
    print("=" * 60)
    return results

if __name__ == "__main__":
    run_tests()
