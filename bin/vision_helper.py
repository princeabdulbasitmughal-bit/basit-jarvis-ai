"""
Basit Jarvis AI - Sovereign Screen Vision & Perception Engine
Uses local Qwen2.5-VL via Ollama on RTX A6000
"""
import os
import io
import base64
import json
import urllib.request
import urllib.error
import pyautogui
from PIL import Image

def get_active_window():
    try:
        import ctypes
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
        return buff.value or "Unknown Window"
    except Exception:
        return "Desktop / Explorer"

def analyze_screen(custom_prompt="Describe what is visible on this computer screen in 1-2 concise sentences for Basit."):
    active_win = get_active_window()
    
    # 1. Capture screen via nircmd (100% reliable across all session types)
    tmp_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "screenshots", "_vision_tmp.png")
    nircmd_path = os.path.join(os.path.dirname(__file__), "nircmd.exe")
    
    if os.path.exists(nircmd_path):
        import subprocess
        subprocess.run([nircmd_path, "savescreenshot", tmp_path], check=False)
    
    if os.path.exists(tmp_path):
        screen = Image.open(tmp_path)
    else:
        try:
            screen = pyautogui.screenshot()
        except Exception:
            return {
                "status": "fallback",
                "active_window": active_win,
                "analysis": f"Screen par is waqt '{active_win}' active hai, Basit bhai."
            }

    # 2. Downscale for fast VLM inference (max dimension 640px)
    screen.thumbnail((640, 640), Image.Resampling.LANCZOS)
    if screen.mode in ("RGBA", "P"):
        screen = screen.convert("RGB")
    
    # 3. Save to memory buffer as JPEG
    buf = io.BytesIO()
    screen.save(buf, format='JPEG', quality=80)
    img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    # 4. Query local Qwen2.5-VL via Ollama
    req_data = json.dumps({
        "model": "qwen2.5-vl:latest",
        "prompt": f"System: You are Basit Jarvis, an ultra-intelligent personal AI assistant. The current foreground window title is '{active_win}'. Answer concisely in 1-2 sentences in natural Roman Urdu or English.\nUser: {custom_prompt}",
        "images": [img_b64],
        "stream": False
    }).encode('utf-8')
    
    try:
        req = urllib.request.Request(
            "http://localhost:11434/api/generate",
            data=req_data,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=12) as response:
            res_json = json.loads(response.read().decode('utf-8'))
            answer = res_json.get("response", "").strip()
            return {
                "status": "ok",
                "active_window": active_win,
                "analysis": answer
            }
    except Exception as e:
        # Fallback to active window perception
        return {
            "status": "fallback",
            "active_window": active_win,
            "analysis": f"Screen par is waqt '{active_win}' open hai, Basit bhai."
        }

if __name__ == '__main__':
    res = analyze_screen()
    print(json.dumps(res, ensure_ascii=False))
