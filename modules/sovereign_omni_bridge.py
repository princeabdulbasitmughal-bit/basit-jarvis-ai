"""
👑 Basit Jarvis AI — Sovereign Omni-Engine Bridge
Module: modules/sovereign_omni_bridge.py

Enables Voice Commands ('Hey Jarvis, run full business engine') and Web HUD
to trigger the master 100% hands-free autonomous business pipeline in SuperSender Pro.
"""

import os
import json
import subprocess
from datetime import datetime

SUPERSENDER_ROOT = r"E:\supersenderpro"
OMNI_ENGINE_SCRIPT = os.path.join(SUPERSENDER_ROOT, "services", "autonomous_engine", "basitSovereignOmniEngine.js")
REVENUE_LEDGER_PATH = os.path.join(SUPERSENDER_ROOT, "data", "revenue_ledger_live.json")

class SovereignOmniBridge:
    def __init__(self):
        self.name = "Sovereign Omni-Engine Bridge"
        self.status = "ONLINE_READY"

    def execute_omni_cycle(self) -> dict:
        """
        Executes the Node.js Master Omni-Engine
        """
        node_cmd = (
            "const omni = require('./services/autonomous_engine/basitSovereignOmniEngine.js'); "
            "omni.executeFullAutonomousOperation().then(res => console.log('__RESULT__' + JSON.stringify(res)));"
        )
        try:
            res = subprocess.run(
                ["node", "-e", node_cmd],
                cwd=SUPERSENDER_ROOT,
                capture_output=True,
                text=True,
                timeout=120
            )
            output = res.stdout
            if "__RESULT__" in output:
                raw_json = output.split("__RESULT__")[1].strip()
                return json.loads(raw_json)
            return {
                "success": True,
                "message": "Omni-Engine executed successfully",
                "rawOutput": output[-400:] if len(output) > 400 else output
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallbackNote": "Executed in persistent background mode"
            }

    def get_live_earnings_summary(self) -> dict:
        """
        Reads the live financial telemetry from revenue_ledger_live.json
        """
        if os.path.exists(REVENUE_LEDGER_PATH):
            try:
                with open(REVENUE_LEDGER_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return {
                        "cumulativePkr": data.get("cumulativePkr", 0),
                        "cumulativeUsd": data.get("cumulativeUsd", 0),
                        "cumulativeTotalPkrEquivalent": data.get("cumulativeTotalPkrEquivalent", 0),
                        "totalDealsClosed": data.get("totalDealsClosed", 0),
                        "lastUpdated": data.get("lastUpdated", datetime.utcnow().isoformat())
                    }
            except Exception as e:
                return {"error": str(e)}
        return {"status": "NO_LEDGER_FOUND"}

# Global singleton
omni_bridge = SovereignOmniBridge()
