"""
================================================================================
👑 BASIT JARVIS AI — BRIDGE SCRIPT (jarvis_bridge.py)
================================================================================
server.js is script ko call karta hai with user's raw command.
Returns JSON: { handled: bool, response, speak, action_taken, needs_engine }

Usage: python modules/jarvis_bridge.py "Ali ko WhatsApp karo kal meeting 5 baje"
"""

import sys
import os
import json

# Force UTF-8 for emoji/Urdu output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"handled": False, "error": "No command provided"}))
        return

    user_input = " ".join(sys.argv[1:]).strip()

    try:
        from modules.conversational_brain import ConversationalBrain
        brain = ConversationalBrain()
        result = brain.respond(user_input)

        # Determine if brain actually handled it
        if result.get("response") is not None and result.get("action_taken") not in ("ai_conversation", "route_to_engine", None):
            # Brain handled it completely
            out = {
                "handled": True,
                "response": result["response"],
                "speak": result.get("speak") or str(result["response"])[:100],
                "action_taken": result.get("action_taken"),
                "needs_engine": None
            }
        elif result.get("needs_engine"):
            # Brain says route to a specific engine
            out = {
                "handled": False,
                "response": result.get("response"),
                "speak": result.get("speak"),
                "action_taken": result.get("action_taken"),
                "needs_engine": result["needs_engine"]
            }
        elif result.get("action_taken") == "conversation" and result.get("response"):
            # Emotional/conversational response — brain handled it
            out = {
                "handled": True,
                "response": result["response"],
                "speak": result.get("speak") or result["response"],
                "action_taken": "conversation",
                "needs_engine": None
            }
        else:
            # Not handled — let server.js continue normally
            out = {
                "handled": False,
                "response": None,
                "action_taken": result.get("action_taken"),
                "needs_engine": result.get("needs_engine")
            }

        print(json.dumps(out, ensure_ascii=False))

    except Exception as e:
        # On any error — don't handle, let server.js proceed
        print(json.dumps({
            "handled": False,
            "error": str(e)[:200]
        }))

if __name__ == "__main__":
    main()
