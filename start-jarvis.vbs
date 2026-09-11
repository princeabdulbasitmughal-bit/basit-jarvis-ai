Dim WShell, oExec
Set WShell = CreateObject("WScript.Shell")
Do
    WShell.Run "cmd /c cd /d E:\basit-jarvis-ai && node server.js > E:\basit-jarvis-ai\logs\server.log 2>&1", 0, True
    WScript.Sleep 2000
Loop
