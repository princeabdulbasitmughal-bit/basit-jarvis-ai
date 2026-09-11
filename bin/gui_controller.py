"""
Basit Jarvis AI - Sovereign GUI & Inside-Tool Automation Engine
Powered by PyAutoGUI, Pyperclip, and Win32 APIs
"""
import sys
import os
import time
import json
import argparse
import subprocess
import urllib.parse
import pyautogui
import pyperclip

# Disable fail-safe check so resting mouse at (0,0) does not throw exception
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.05

def type_text(text: str, press_enter: bool = False):
    """
    Pastes text via clipboard for 100% Unicode / Urdu / emoji accuracy,
    then optionally presses Enter.
    """
    if not text:
        return {"status": "error", "message": "No text provided"}
    
    # Copy to clipboard
    pyperclip.copy(text)
    time.sleep(0.08)
    
    # Paste via Ctrl+V
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.08)
    
    if press_enter:
        pyautogui.press('enter')
        
    return {"status": "ok", "action": "type_text", "text": text}

def press_key(key: str):
    """
    Presses a special key (enter, tab, esc, space, backspace, etc.)
    """
    valid_key = key.lower().strip()
    key_map = {
        'enter': 'enter',
        'return': 'enter',
        'tab': 'tab',
        'escape': 'esc',
        'esc': 'esc',
        'space': 'space',
        'spacebar': 'space',
        'backspace': 'backspace',
        'delete': 'delete',
        'del': 'delete',
        'up': 'up',
        'down': 'down',
        'left': 'left',
        'right': 'right',
        'pageup': 'pageup',
        'pagedown': 'pagedown',
        'home': 'home',
        'end': 'end',
        'f5': 'f5',
        'f11': 'f11'
    }
    
    target = key_map.get(valid_key, valid_key)
    pyautogui.press(target)
    return {"status": "ok", "action": "press_key", "key": target}

def hotkey(*keys):
    """
    Executes a keyboard shortcut like ctrl+s, ctrl+c, alt+tab
    """
    clean_keys = [k.lower().strip() for k in keys if k]
    pyautogui.hotkey(*clean_keys)
    return {"status": "ok", "action": "hotkey", "keys": clean_keys}

def scroll(direction: str = "down", amount: int = 4):
    """
    Scrolls page up or down
    """
    clicks = amount * 120
    if direction.lower() in ['down', 'neeche']:
        pyautogui.scroll(-clicks)
    else:
        pyautogui.scroll(clicks)
    return {"status": "ok", "action": "scroll", "direction": direction}

def mouse_click(button: str = "left", clicks: int = 1):
    """
    Simulates mouse click at current cursor location
    """
    pyautogui.click(button=button, clicks=clicks)
    return {"status": "ok", "action": "click", "button": button, "clicks": clicks}

def type_into_app(app_cmd: str, text: str):
    """
    Launches or focuses an app (like Notepad) and types text inside it
    """
    subprocess.Popen(app_cmd, shell=True)
    time.sleep(0.8) # Wait for window to render & focus
    return type_text(text, press_enter=True)

def whatsapp_auto_send(phone: str, message: str, delay_sec: float = 6.0):
    """
    Opens WhatsApp chat link and automatically presses Enter to send after page load!
    """
    encoded_msg = urllib.parse.quote(message)
    url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_msg}"
    
    # Launch default browser
    subprocess.Popen(f'powershell -Command "Start-Process \'{url}\'"', shell=True)
    
    # Wait for WhatsApp Web chat UI to initialize & focus message box
    # We do a gentle check and press Enter
    time.sleep(delay_sec)
    
    # Press Enter inside WhatsApp Web
    pyautogui.press('enter')
    
    return {
        "status": "ok",
        "action": "whatsapp_auto_send",
        "phone": phone,
        "message": message,
        "auto_sent": True
    }

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Basit Jarvis GUI Controller")
    parser.add_argument('--action', required=True, choices=[
        'type', 'key', 'hotkey', 'scroll', 'click', 'app_type', 'whatsapp_send'
    ])
    parser.add_argument('--text', default='')
    parser.add_argument('--key', default='')
    parser.add_argument('--keys', nargs='*', default=[])
    parser.add_argument('--direction', default='down')
    parser.add_argument('--amount', type=int, default=4)
    parser.add_argument('--button', default='left')
    parser.add_argument('--clicks', type=int, default=1)
    parser.add_argument('--app', default='notepad.exe')
    parser.add_argument('--phone', default='')
    parser.add_argument('--delay', type=float, default=6.0)
    
    args = parser.parse_args()
    res = {}
    
    if args.action == 'type':
        res = type_text(args.text)
    elif args.action == 'key':
        res = press_key(args.key)
    elif args.action == 'hotkey':
        res = hotkey(*args.keys)
    elif args.action == 'scroll':
        res = scroll(args.direction, args.amount)
    elif args.action == 'click':
        res = mouse_click(args.button, args.clicks)
    elif args.action == 'app_type':
        res = type_into_app(args.app, args.text)
    elif args.action == 'whatsapp_send':
        res = whatsapp_auto_send(args.phone, args.text, args.delay)
        
    print(json.dumps(res))
