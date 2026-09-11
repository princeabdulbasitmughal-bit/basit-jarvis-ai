Set fso = CreateObject("Scripting.FileSystemObject")
Set WshShell = CreateObject("WScript.Shell")

scriptDir = "E:\basit-jarvis-ai\"
WshShell.CurrentDirectory = scriptDir

' 1. Find pythonw.exe or python.exe
pythonPath = ""
If fso.FileExists("C:\Users\absh5\AppData\Local\Programs\Python\Python311\pythonw.exe") Then
    pythonPath = "C:\Users\absh5\AppData\Local\Programs\Python\Python311\pythonw.exe"
ElseIf fso.FileExists("C:\Users\absh5\AppData\Local\Programs\Python\Python311\python.exe") Then
    pythonPath = "C:\Users\absh5\AppData\Local\Programs\Python\Python311\python.exe"
Else
    pythonPath = "pythonw.exe"
End If

' 2. Launch server quietly without console window
serverCmd = """" & pythonPath & """ """ & scriptDir & "server.py"""
WshShell.Run serverCmd, 0, False

' 3. Wait 2 seconds for server to bind port 8888
WScript.Sleep 2500

' 4. Open dashboard in default browser
WshShell.Run "http://127.0.0.1:8888"
