Set WshShell = CreateObject("WScript.Shell")
' Launch server minimized/hidden
WshShell.Run "python server.py", 0, False
WScript.Sleep 2000
' Open dashboard in default browser
WshShell.Run "http://localhost:8888"
' Launch jarvis voice assistant
WshShell.Run "python jarvis.py", 1, True
