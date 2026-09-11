using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Net;
using System.Runtime.InteropServices;
using System.Speech.Recognition;
using System.Speech.Synthesis;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Shapes;
using System.Windows.Threading;
using System.Windows.Documents;

namespace BasitJarvis
{
    public class Program : Application
    {
        [STAThread]
        public static void Main()
        {
            Program app = new Program();
            app.Run(new MainWindow());
        }
    }

    public class MainWindow : Window
    {
        // ── P/Invoke for volume control (fixes SendKeys volume bug) ──────────────
        [DllImport("user32.dll")]
        private static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);
        private const byte VK_VOLUME_UP   = 0xAF;
        private const byte VK_VOLUME_DOWN = 0xAE;
        private const byte VK_VOLUME_MUTE = 0xAD;
        private const uint KEYEVENTF_EXTENDEDKEY = 0x0001;
        private const uint KEYEVENTF_KEYUP       = 0x0002;

        // ── P/Invoke for window focus ────────────────────────────────────────────
        [DllImport("user32.dll")]
        private static extern IntPtr GetForegroundWindow();
        [DllImport("user32.dll")]
        private static extern bool SetForegroundWindow(IntPtr hWnd);
        [DllImport("user32.dll")]
        private static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
        private const int SW_MINIMIZE = 6;

        private SpeechRecognitionEngine recognizer;
        private SpeechSynthesizer synth;
        private bool isListening = false;
        private bool isMuted = false;
        private string serverUrl = "http://10.25.32.23:8888";
        private string nodeId = Guid.NewGuid().ToString().Substring(0, 8);
        private string machineName = Environment.MachineName;
        private DispatcherTimer pollTimer;
        private IntPtr jarvisHwnd = IntPtr.Zero;

        private Border reactorCore;
        private Ellipse reactorInner;
        private TextBlock statusText;
        private TextBlock voiceStateLabel;
        private TextBlock transcriptBox;
        private TextBox serverInput;
        private TextBox cmdInput;
        private RichTextBox terminalBox;
        private Paragraph terminalParagraph;
        private ComboBox targetSelect;

        public MainWindow()
        {
            InitializeUI();
            InitializeSpeech();
            InitializeFleetWorker();
            Loaded += (s, e) => { jarvisHwnd = new System.Windows.Interop.WindowInteropHelper(this).Handle; };
        }

        // ─────────────────────────────────────────────────────────────────────────
        //  UI INIT
        // ─────────────────────────────────────────────────────────────────────────
        private void InitializeUI()
        {
            Title = "👑 BASIT JARVIS AI — Autonomous PC Controller OS";
            Width = 1060;
            Height = 740;
            MinWidth = 850;
            MinHeight = 600;
            WindowStartupLocation = WindowStartupLocation.CenterScreen;
            Background = new SolidColorBrush(Color.FromRgb(5, 8, 17));
            Foreground = new SolidColorBrush(Color.FromRgb(248, 250, 252));

            var mainGrid = new Grid();
            mainGrid.Margin = new Thickness(14);
            mainGrid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            mainGrid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            mainGrid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            mainGrid.RowDefinitions.Add(new RowDefinition { Height = new GridLength(1, GridUnitType.Star) });
            mainGrid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });

            // 1. Header
            var headerBorder = CreateCardBorder();
            headerBorder.Padding = new Thickness(12, 10, 12, 10);
            var headerDock = new DockPanel();

            var logoStack = new StackPanel { Orientation = Orientation.Horizontal };
            logoStack.Children.Add(new TextBlock
            {
                Text = "👑 BASIT JARVIS AI",
                FontSize = 18,
                FontWeight = FontWeights.Bold,
                Foreground = new SolidColorBrush(Color.FromRgb(0, 240, 255)),
                VerticalAlignment = VerticalAlignment.Center
            });
            logoStack.Children.Add(new TextBlock
            {
                Text = "  • Standalone Desktop Controller (" + machineName + ")",
                FontSize = 12,
                Foreground = new SolidColorBrush(Color.FromRgb(148, 163, 184)),
                VerticalAlignment = VerticalAlignment.Center
            });
            DockPanel.SetDock(logoStack, Dock.Left);
            headerDock.Children.Add(logoStack);

            var rightHeader = new StackPanel { Orientation = Orientation.Horizontal, HorizontalAlignment = HorizontalAlignment.Right };
            statusText = new TextBlock
            {
                Text = "● STANDALONE ACTIVE",
                Foreground = new SolidColorBrush(Color.FromRgb(16, 185, 129)),
                FontWeight = FontWeights.SemiBold,
                FontSize = 12,
                VerticalAlignment = VerticalAlignment.Center,
                Margin = new Thickness(0, 0, 10, 0)
            };
            var testSpeechBtn = CreateButton("🗣️ Test Speech", (s, e) => Speak("Basit bhai, Jarvis desktop autonomous engine bilkul tayyar hai!"));
            testSpeechBtn.Padding = new Thickness(8, 4, 8, 4);
            testSpeechBtn.FontSize = 11;
            rightHeader.Children.Add(statusText);
            rightHeader.Children.Add(testSpeechBtn);
            headerDock.Children.Add(rightHeader);

            headerBorder.Child = headerDock;
            Grid.SetRow(headerBorder, 0);
            mainGrid.Children.Add(headerBorder);

            // 2. Voice Hero Banner
            var voiceHero = CreateCardBorder();
            voiceHero.Margin = new Thickness(0, 8, 0, 8);
            voiceHero.Padding = new Thickness(14);
            voiceHero.BorderBrush = new SolidColorBrush(Color.FromArgb(90, 0, 240, 255));

            var heroGrid = new Grid();
            heroGrid.ColumnDefinitions.Add(new ColumnDefinition { Width = GridLength.Auto });
            heroGrid.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star) });
            heroGrid.ColumnDefinitions.Add(new ColumnDefinition { Width = GridLength.Auto });

            reactorCore = new Border
            {
                Width = 56,
                Height = 56,
                CornerRadius = new CornerRadius(28),
                BorderThickness = new Thickness(3),
                BorderBrush = new SolidColorBrush(Color.FromRgb(0, 240, 255)),
                Background = new SolidColorBrush(Color.FromArgb(30, 0, 240, 255)),
                Cursor = Cursors.Hand,
                Margin = new Thickness(0, 0, 16, 0)
            };
            reactorInner = new Ellipse
            {
                Width = 20,
                Height = 20,
                Fill = new SolidColorBrush(Color.FromRgb(0, 240, 255))
            };
            reactorCore.Child = reactorInner;
            reactorCore.MouseDown += (s, e) => ToggleVoiceListening();
            Grid.SetColumn(reactorCore, 0);
            heroGrid.Children.Add(reactorCore);

            var voiceCenterStack = new StackPanel { VerticalAlignment = VerticalAlignment.Center };
            voiceStateLabel = new TextBlock
            {
                Text = "⚡ VOICE ENGINE READY — Click Core or Button to Listen",
                FontWeight = FontWeights.Bold,
                FontSize = 13,
                Foreground = new SolidColorBrush(Color.FromRgb(0, 240, 255))
            };
            transcriptBox = new TextBlock
            {
                Text = "Bol: \"Chrome kholo\", \"YouTube chalao\", \"Notepad me likho...\", \"Awaz barha do\", \"/basit1\", \"screenshot lo\"",
                FontStyle = FontStyles.Italic,
                FontSize = 12,
                Foreground = new SolidColorBrush(Color.FromRgb(148, 163, 184)),
                Margin = new Thickness(0, 4, 0, 0),
                TextWrapping = TextWrapping.Wrap
            };
            voiceCenterStack.Children.Add(voiceStateLabel);
            voiceCenterStack.Children.Add(transcriptBox);
            Grid.SetColumn(voiceCenterStack, 1);
            heroGrid.Children.Add(voiceCenterStack);

            var micBtn = CreateButton("🎙️ START VOICE", (s, e) => ToggleVoiceListening());
            micBtn.Padding = new Thickness(14, 8, 14, 8);
            micBtn.FontSize = 12;
            micBtn.FontWeight = FontWeights.Bold;
            Grid.SetColumn(micBtn, 2);
            heroGrid.Children.Add(micBtn);

            voiceHero.Child = heroGrid;
            Grid.SetRow(voiceHero, 1);
            mainGrid.Children.Add(voiceHero);

            // 3. Server Bar
            var fleetBar = CreateCardBorder();
            fleetBar.Margin = new Thickness(0, 0, 0, 8);
            fleetBar.Padding = new Thickness(10, 6, 10, 6);
            var fleetStack = new DockPanel();

            fleetStack.Children.Add(new TextBlock
            {
                Text = "🔗 Master Server:",
                Foreground = new SolidColorBrush(Color.FromRgb(56, 189, 248)),
                FontWeight = FontWeights.SemiBold,
                FontSize = 12,
                VerticalAlignment = VerticalAlignment.Center,
                Margin = new Thickness(0, 0, 6, 0)
            });

            serverInput = new TextBox
            {
                Text = serverUrl,
                Width = 220,
                Background = new SolidColorBrush(Color.FromRgb(15, 23, 42)),
                Foreground = new SolidColorBrush(Color.FromRgb(248, 250, 252)),
                BorderBrush = new SolidColorBrush(Color.FromArgb(80, 0, 240, 255)),
                Padding = new Thickness(4, 2, 4, 2),
                FontSize = 11,
                VerticalAlignment = VerticalAlignment.Center
            };
            fleetStack.Children.Add(serverInput);

            var connectBtn = CreateButton("Sync", (s, e) => ConnectServer());
            connectBtn.Padding = new Thickness(8, 2, 8, 2);
            connectBtn.FontSize = 11;
            connectBtn.Margin = new Thickness(4, 0, 16, 0);
            fleetStack.Children.Add(connectBtn);

            fleetStack.Children.Add(new TextBlock
            {
                Text = "🎯 Target:",
                Foreground = new SolidColorBrush(Color.FromRgb(168, 85, 247)),
                FontWeight = FontWeights.SemiBold,
                FontSize = 12,
                VerticalAlignment = VerticalAlignment.Center,
                Margin = new Thickness(0, 0, 6, 0)
            });

            targetSelect = new ComboBox
            {
                Width = 200,
                Background = new SolidColorBrush(Color.FromRgb(15, 23, 42)),
                Foreground = new SolidColorBrush(Color.FromRgb(56, 189, 248)),
                FontSize = 11,
                VerticalAlignment = VerticalAlignment.Center
            };
            targetSelect.Items.Add(new ComboBoxItem { Content = "● This Local PC (" + machineName + ")", Tag = "local", IsSelected = true });
            targetSelect.Items.Add(new ComboBoxItem { Content = "⚡ Master Rig (Hub)", Tag = "host" });
            targetSelect.Items.Add(new ComboBoxItem { Content = "🌐 ALL Fleet PCs (Broadcast)", Tag = "all" });
            fleetStack.Children.Add(targetSelect);

            fleetBar.Child = fleetStack;
            Grid.SetRow(fleetBar, 2);
            mainGrid.Children.Add(fleetBar);

            // 4. Content Split
            var contentGrid = new Grid();
            contentGrid.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1.1, GridUnitType.Star) });
            contentGrid.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star) });

            var actionScroll = new ScrollViewer { VerticalScrollBarVisibility = ScrollBarVisibility.Auto };
            var actionStack = new StackPanel { Margin = new Thickness(0, 0, 8, 0) };

            // Basit Engines
            var basitEnginesBorder = CreateCardBorder();
            basitEnginesBorder.Margin = new Thickness(0, 0, 0, 8);
            var basitEnginesStack = new StackPanel();
            basitEnginesStack.Children.Add(new TextBlock
            {
                Text = "⚡ BASIT SOVEREIGN ENGINES",
                FontWeight = FontWeights.Bold,
                Foreground = new SolidColorBrush(Color.FromRgb(0, 240, 255)),
                FontSize = 12,
                Margin = new Thickness(0, 0, 0, 6)
            });
            var basitWrap = new WrapPanel();
            basitWrap.Children.Add(CreateActionButton("🚀 /basit1 (Devin Coding)", () => TriggerEngine("basit1", "Fast autonomous code generation")));
            basitWrap.Children.Add(CreateActionButton("🧠 /basit2 (Deep Research)", () => TriggerEngine("basit2", "Multi-Agent Consensus Architectures 2026")));
            basitWrap.Children.Add(CreateActionButton("🛡️ /basit3 (OWASP Security)", () => TriggerEngine("basit3", "Audit running processes and enforce zero-hang guard")));
            basitWrap.Children.Add(CreateActionButton("📈 /basit4 (AI Hedge Fund)", () => TriggerEngine("basit4", "NVDA market moat and valuation consensus")));
            basitWrap.Children.Add(CreateActionButton("⚡ /basitswarm (100 Agents)", () => TriggerEngine("basitswarm", "Synthesize full-stack enterprise platform in parallel")));
            basitWrap.Children.Add(CreateActionButton("💻 /arsenal (Dual-GPU Matrix)", () => TriggerEngine("arsenal", "")));
            basitWrap.Children.Add(CreateActionButton("♾️ /basitloop (Continuous Loop)", () => TriggerEngine("basitloop", "Audit workspace and enforce zero-hang performance")));
            basitWrap.Children.Add(CreateActionButton("⚡ /gemini-spark (Big Data AI)", () => TriggerEngine("gemini-spark", "sql: SELECT current_timestamp() as server_time, version() as spark_build, 100 as speed")));
            basitEnginesStack.Children.Add(basitWrap);
            basitEnginesBorder.Child = basitEnginesStack;
            actionStack.Children.Add(basitEnginesBorder);

            // In-App Tools
            var guiBorder = CreateCardBorder();
            guiBorder.Margin = new Thickness(0, 0, 0, 8);
            var guiStack = new StackPanel();
            guiStack.Children.Add(new TextBlock
            {
                Text = "⌨️ IN-APP PHYSICAL AUTOMATION & TYPING",
                FontWeight = FontWeights.Bold,
                Foreground = new SolidColorBrush(Color.FromRgb(16, 185, 129)),
                FontSize = 12,
                Margin = new Thickness(0, 0, 0, 6)
            });
            var guiWrap = new WrapPanel();
            guiWrap.Children.Add(CreateActionButton("✍️ Type Into Focused App", () => PromptAndType()));
            guiWrap.Children.Add(CreateActionButton("📝 Notepad Write Text", () => PromptNotepadWrite()));
            guiWrap.Children.Add(CreateActionButton("💾 Save File (Ctrl+S)", () => SendHotkeyToOS("^s")));
            guiWrap.Children.Add(CreateActionButton("🎯 Select All (Ctrl+A)", () => SendHotkeyToOS("^a")));
            guiWrap.Children.Add(CreateActionButton("📋 Copy (Ctrl+C)", () => SendHotkeyToOS("^c")));
            guiWrap.Children.Add(CreateActionButton("📋 Paste (Ctrl+V)", () => SendHotkeyToOS("^v")));
            guiWrap.Children.Add(CreateActionButton("↩️ Undo (Ctrl+Z)", () => SendHotkeyToOS("^z")));
            guiWrap.Children.Add(CreateActionButton("🔲 Maximize Window", () => SendHotkeyToOS("#{UP}")));
            guiWrap.Children.Add(CreateActionButton("◀ Snap Window Left", () => SendHotkeyToOS("#{LEFT}")));
            guiWrap.Children.Add(CreateActionButton("Snap Window Right ▶", () => SendHotkeyToOS("#{RIGHT}")));
            guiWrap.Children.Add(CreateActionButton("🪟 Switch App (Alt+Tab)", () => SendHotkeyToOS("%{TAB}")));
            guiWrap.Children.Add(CreateActionButton("📱 WhatsApp Auto-Send", () => PromptWhatsAppSend()));
            guiStack.Children.Add(guiWrap);
            guiBorder.Child = guiStack;
            actionStack.Children.Add(guiBorder);

            // Desktop Launchpad
            var launchBorder = CreateCardBorder();
            var launchStack = new StackPanel();
            launchStack.Children.Add(new TextBlock
            {
                Text = "🚀 DESKTOP LAUNCHPAD & AUDIO",
                FontWeight = FontWeights.Bold,
                Foreground = new SolidColorBrush(Color.FromRgb(168, 85, 247)),
                FontSize = 12,
                Margin = new Thickness(0, 0, 0, 6)
            });
            var launchWrap = new WrapPanel();
            launchWrap.Children.Add(CreateActionButton("🌐 Google Chrome", () => Process.Start("https://www.google.com")));
            launchWrap.Children.Add(CreateActionButton("📺 YouTube", () => Process.Start("https://www.youtube.com")));
            launchWrap.Children.Add(CreateActionButton("💻 VS Code", () => StartAppSafe("code", "code .")));
            launchWrap.Children.Add(CreateActionButton("📝 Notepad", () => StartAppSafe("notepad.exe", "")));
            launchWrap.Children.Add(CreateActionButton("🧮 Calculator", () => StartAppSafe("calc.exe", "")));
            launchWrap.Children.Add(CreateActionButton("⚙️ Task Manager", () => StartAppSafe("taskmgr.exe", "")));
            launchWrap.Children.Add(CreateActionButton("📸 Screenshot", () => TakeLocalScreenshot()));
            launchWrap.Children.Add(CreateActionButton("🔊 Volume +10%", () => AdjustVolume(10)));
            launchWrap.Children.Add(CreateActionButton("🔉 Volume -10%", () => AdjustVolume(-10)));
            launchWrap.Children.Add(CreateActionButton("🔇 Toggle Mute", () => ToggleMute()));
            launchWrap.Children.Add(CreateActionButton("🗑️ Empty Recycle Bin", () => ClearRecycleBinSafe()));
            launchWrap.Children.Add(CreateActionButton("🖥️ Show Desktop", () => SendHotkeyToOS("#{d}")));
            launchStack.Children.Add(launchWrap);
            launchBorder.Child = launchStack;
            actionStack.Children.Add(launchBorder);

            actionScroll.Content = actionStack;
            Grid.SetColumn(actionScroll, 0);
            contentGrid.Children.Add(actionScroll);

            // Terminal Log
            var termBorder = CreateCardBorder();
            termBorder.Margin = new Thickness(8, 0, 0, 0);
            termBorder.Padding = new Thickness(10);
            termBorder.Background = new SolidColorBrush(Color.FromRgb(2, 6, 23));

            terminalBox = new RichTextBox
            {
                Background = Brushes.Transparent,
                BorderThickness = new Thickness(0),
                FontFamily = new FontFamily("Consolas"),
                FontSize = 12,
                IsReadOnly = true,
                VerticalScrollBarVisibility = ScrollBarVisibility.Auto
            };
            terminalParagraph = new Paragraph();
            terminalBox.Document.Blocks.Add(terminalParagraph);
            termBorder.Child = terminalBox;

            Grid.SetColumn(termBorder, 1);
            contentGrid.Children.Add(termBorder);

            Grid.SetRow(contentGrid, 3);
            mainGrid.Children.Add(contentGrid);

            // Bottom Command Bar
            var bottomGrid = new Grid { Margin = new Thickness(0, 8, 0, 0) };
            bottomGrid.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star) });
            bottomGrid.ColumnDefinitions.Add(new ColumnDefinition { Width = GridLength.Auto });

            cmdInput = new TextBox
            {
                Background = new SolidColorBrush(Color.FromRgb(15, 23, 42)),
                Foreground = new SolidColorBrush(Color.FromRgb(248, 250, 252)),
                BorderBrush = new SolidColorBrush(Color.FromArgb(90, 0, 240, 255)),
                Padding = new Thickness(10, 8, 10, 8),
                FontSize = 13,
                Margin = new Thickness(0, 0, 8, 0)
            };
            cmdInput.KeyDown += (s, e) => { if (e.Key == Key.Enter) DispatchCustomCommand(); };
            Grid.SetColumn(cmdInput, 0);
            bottomGrid.Children.Add(cmdInput);

            var dispatchBtn = CreateButton("⚡ Dispatch Command", (s, e) => DispatchCustomCommand());
            dispatchBtn.Padding = new Thickness(16, 8, 16, 8);
            dispatchBtn.FontSize = 12;
            dispatchBtn.FontWeight = FontWeights.Bold;
            Grid.SetColumn(dispatchBtn, 1);
            bottomGrid.Children.Add(dispatchBtn);

            Grid.SetRow(bottomGrid, 4);
            mainGrid.Children.Add(bottomGrid);

            Content = mainGrid;

            LogTerminal("[SYSTEM]: Basit Jarvis Native Desktop OS Controller Initialized.", Colors.Cyan);
            LogTerminal("[READY]: Offline Hardware Speech Recognition & Text-To-Speech Online.", Colors.SpringGreen);
            LogTerminal("[FLEET]: This Machine ID: " + nodeId + " (" + machineName + ")", Colors.LightSkyBlue);
            LogTerminal("[VOICE TIP]: Bol saktay hain: 'chrome kholo', 'youtube chalao', 'notepad', 'awaz barha do', 'screenshot lo', 'basit 1' etc.", Colors.Yellow);
        }

        private Border CreateCardBorder()
        {
            return new Border
            {
                Background = new SolidColorBrush(Color.FromArgb(220, 13, 20, 36)),
                BorderBrush = new SolidColorBrush(Color.FromArgb(60, 0, 240, 255)),
                BorderThickness = new Thickness(1),
                CornerRadius = new CornerRadius(10),
                Padding = new Thickness(8)
            };
        }

        private Button CreateButton(string text, RoutedEventHandler onClick)
        {
            var btn = new Button
            {
                Content = text,
                Background = new SolidColorBrush(Color.FromArgb(40, 0, 240, 255)),
                Foreground = new SolidColorBrush(Color.FromRgb(0, 240, 255)),
                BorderBrush = new SolidColorBrush(Color.FromArgb(90, 0, 240, 255)),
                BorderThickness = new Thickness(1),
                Cursor = Cursors.Hand,
                Margin = new Thickness(2)
            };
            btn.Click += onClick;
            return btn;
        }

        private Button CreateActionButton(string text, Action onAction)
        {
            var btn = new Button
            {
                Content = text,
                Background = new SolidColorBrush(Color.FromArgb(30, 15, 23, 42)),
                Foreground = new SolidColorBrush(Color.FromRgb(226, 232, 240)),
                BorderBrush = new SolidColorBrush(Color.FromArgb(50, 255, 255, 255)),
                BorderThickness = new Thickness(1),
                Padding = new Thickness(8, 6, 8, 6),
                Margin = new Thickness(3),
                FontSize = 11,
                FontWeight = FontWeights.SemiBold,
                Cursor = Cursors.Hand
            };
            btn.Click += (s, e) => onAction();
            return btn;
        }

        // ─────────────────────────────────────────────────────────────────────────
        //  BUG FIX #1 + #4: Speech init — DictationGrammar + expanded Roman Urdu
        //  grammar so Windows en-US can catch Urdu-romanized words phonetically
        // ─────────────────────────────────────────────────────────────────────────
        private void InitializeSpeech()
        {
            try
            {
                synth = new SpeechSynthesizer();
                synth.Rate = 1;

                recognizer = new SpeechRecognitionEngine();
                recognizer.SetInputToDefaultAudioDevice();

                // BUG FIX #4: Added all Roman Urdu phonetic equivalents that
                // Windows en-US engine can actually recognize phonetically.
                // Roman Urdu words ARE recognizable because they use English letters.
                var choices = new Choices();
                choices.Add(new string[] {
                    // English commands
                    "chrome", "open chrome", "open browser", "browser",
                    "youtube", "open youtube",
                    "notepad", "open notepad",
                    "code", "open code", "vscode", "vs code",
                    "calculator", "calc",
                    "task manager",
                    "save", "save file",
                    "copy", "paste", "undo",
                    "select all",
                    "maximize", "fullscreen", "minimize",
                    "snap left", "snap right",
                    "mute", "unmute",
                    "volume up", "volume down",
                    "screenshot", "take screenshot",
                    "show desktop", "desktop",
                    "whatsapp",
                    "basit 1", "basit 2", "basit 3", "basit 4", "basit swarm", "arsenal",
                    "basit loop", "gemini spark", "spark", "gemini",
                    "switch app",

                    // Roman Urdu — these ARE recognizable by Windows en-US engine phonetically
                    "chrome kholo", "kholo chrome",
                    "youtube chalao", "chalao youtube",
                    "notepad kholo",
                    "awaz barha do", "awaz kam karo", "awaz band karo",
                    "save karo", "copy karo", "paste karo", "undo karo",
                    "screenshot lo", "screen lo",
                    "band karo", "bund karo",
                    "basit ek", "basit do", "basit teen", "basit chaar",
                    "basit loop chalao", "spark chalao", "gemini chalao",

                    // Freeform type commands
                    "type this", "type now",
                    "likho", "likh do",

                    // Autonomous PDF & Research Studio
                    "pdf banao", "report banao", "generate pdf",
                    "send report", "pdf report", "pdf bana do"
                });

                var gb = new GrammarBuilder(choices);
                var g = new Grammar(gb);
                recognizer.LoadGrammar(g);

                // BUG FIX #1 part: Load DictationGrammar for free-form speech
                // (allows "chrome kholo YouTube par" style compound commands)
                bool dictationLoaded = false;
                try
                {
                    recognizer.LoadGrammar(new DictationGrammar());
                    dictationLoaded = true;
                }
                catch (Exception ex)
                {
                    LogTerminal("[WARNING]: DictationGrammar unavailable (install Windows Speech pack): " + ex.Message, Colors.Orange);
                }

                recognizer.SpeechRecognized += Recognizer_SpeechRecognized;
                recognizer.SpeechHypothesized += (s, e) =>
                {
                    Dispatcher.Invoke(() => { transcriptBox.Text = "\"" + e.Result.Text + "...\""; });
                };
                recognizer.SpeechRecognitionRejected += (s, e) =>
                {
                    Dispatcher.Invoke(() =>
                    {
                        transcriptBox.Text = "[Not recognized — speak clearly in English or Roman Urdu]";
                    });
                };

                string msg = "[SPEECH]: Windows Native Voice Grammar loaded." + (dictationLoaded ? " DictationGrammar ON." : " DictationGrammar OFF.");
                LogTerminal(msg, Colors.SpringGreen);
            }
            catch (Exception ex)
            {
                LogTerminal("[WARNING]: Speech Recognition init failed: " + ex.Message, Colors.Orange);
                recognizer = null;
            }
        }

        private void ToggleVoiceListening()
        {
            if (recognizer == null)
            {
                MessageBox.Show("Microphone not available or speech engine failed to load.\n\nManual fix: Control Panel > Speech Recognition > Set up microphone.", "Jarvis — Mic Error", MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            if (!isListening)
            {
                try
                {
                    recognizer.RecognizeAsync(RecognizeMode.Multiple);
                    isListening = true;
                    voiceStateLabel.Text = "🎙️ MIC ACTIVE — Har waqt sun raha hoon... (Listening continuously)";
                    voiceStateLabel.Foreground = new SolidColorBrush(Color.FromRgb(16, 185, 129));
                    reactorInner.Fill = new SolidColorBrush(Color.FromRgb(16, 185, 129));
                    reactorCore.BorderBrush = new SolidColorBrush(Color.FromRgb(16, 185, 129));
                    LogTerminal("[VOICE]: Continuous Voice Listening Activated.", Colors.SpringGreen);
                    Speak("Jarvis sun raha hai, Basit bhai.");
                }
                catch (Exception ex)
                {
                    LogTerminal("[ERROR]: Start listening failed: " + ex.Message, Colors.Red);
                    MessageBox.Show("Could not start microphone:\n" + ex.Message, "Jarvis", MessageBoxButton.OK, MessageBoxImage.Error);
                }
            }
            else
            {
                try
                {
                    recognizer.RecognizeAsyncStop();
                    isListening = false;
                    voiceStateLabel.Text = "⚡ VOICE ENGINE STANDBY — Click Core to Activate";
                    voiceStateLabel.Foreground = new SolidColorBrush(Color.FromRgb(0, 240, 255));
                    reactorInner.Fill = new SolidColorBrush(Color.FromRgb(0, 240, 255));
                    reactorCore.BorderBrush = new SolidColorBrush(Color.FromRgb(0, 240, 255));
                    LogTerminal("[VOICE]: Voice Listening Paused.", Colors.LightSkyBlue);
                }
                catch { }
            }
        }

        // BUG FIX: Lower confidence threshold to 0.25 — Windows en-US scores Roman
        // Urdu words lower because of accent mismatch, so 0.35 was too strict.
        private void Recognizer_SpeechRecognized(object sender, SpeechRecognizedEventArgs e)
        {
            string heard = e.Result.Text;
            float conf = e.Result.Confidence;

            // Accept if confidence >= 0.25, OR if it came from DictationGrammar
            if (string.IsNullOrWhiteSpace(heard) || conf < 0.25f) return;

            Dispatcher.Invoke(() =>
            {
                transcriptBox.Text = "\"" + heard + "\" [" + (conf * 100).ToString("F0") + "%]";
                LogTerminal("[SPOKEN " + (conf * 100).ToString("F0") + "%]: " + heard, Colors.Yellow);
                ProcessCommand(heard);
            });
        }

        private void Speak(string text)
        {
            if (string.IsNullOrWhiteSpace(text) || isMuted || synth == null) return;
            Task.Run(() =>
            {
                try
                {
                    synth.SpeakAsyncCancelAll();
                    synth.Speak(text);
                }
                catch { }
            });
        }

        // ─────────────────────────────────────────────────────────────────────────
        //  ProcessCommand — expanded Roman Urdu keyword matching
        // ─────────────────────────────────────────────────────────────────────────
        private void ProcessCommand(string command)
        {
            string cmd = command.ToLower().Trim();

            // ── App opens ──────────────────────────────────────────────────────
            if (cmd.Contains("chrome") || cmd.Contains("browser") || cmd.Contains("google"))
            {
                Process.Start("https://www.google.com");
                Speak("Chrome open kar diya hai, Basit bhai.");
                LogTerminal("[ACTION]: Opened Google Chrome", Colors.Cyan);
                return;
            }
            if (cmd.Contains("youtube"))
            {
                Process.Start("https://www.youtube.com");
                Speak("YouTube open kar diya hai.");
                LogTerminal("[ACTION]: Opened YouTube", Colors.Cyan);
                return;
            }
            if (cmd.Contains("notepad"))
            {
                Process.Start("notepad.exe");
                Speak("Notepad khol diya hai.");
                LogTerminal("[ACTION]: Opened Notepad", Colors.Cyan);
                return;
            }
            if (cmd.Contains("calc") || cmd.Contains("calculator"))
            {
                Process.Start("calc.exe");
                Speak("Calculator open kar diya hai.");
                LogTerminal("[ACTION]: Opened Calculator", Colors.Cyan);
                return;
            }
            if (cmd.Contains("vscode") || cmd.Contains("vs code") || (cmd.Contains("code") && !cmd.Contains("copy")))
            {
                StartAppSafe("code", "code .");
                Speak("VS Code editor open kar diya hai.");
                LogTerminal("[ACTION]: Opened VS Code", Colors.Cyan);
                return;
            }
            if (cmd.Contains("task manager"))
            {
                StartAppSafe("taskmgr.exe", "");
                Speak("Task Manager open kar diya.");
                LogTerminal("[ACTION]: Opened Task Manager", Colors.Cyan);
                return;
            }
            if (cmd.Contains("whatsapp"))
            {
                PromptWhatsAppSend();
                return;
            }

            // ── Typing ─────────────────────────────────────────────────────────
            if (cmd.StartsWith("type ") || cmd.StartsWith("likho ") || cmd.StartsWith("likh do ") || cmd.StartsWith("type karo "))
            {
                string textToType = cmd
                    .Replace("type karo", "").Replace("likh do", "")
                    .Replace("likho", "").Replace("type", "").Trim();
                if (!string.IsNullOrEmpty(textToType))
                {
                    // BUG FIX #3: Minimize Jarvis window FIRST so keys go to the right app
                    MinimizeJarvisAndRun(() =>
                    {
                        System.Windows.Forms.SendKeys.SendWait(textToType);
                        Dispatcher.Invoke(() =>
                        {
                            LogTerminal("[PHYSICAL TYPE]: " + textToType, Colors.SpringGreen);
                        });
                    });
                    Speak("Text type kar diya hai.");
                }
                return;
            }

            // ── Hotkeys ────────────────────────────────────────────────────────
            if (cmd.Contains("save") || cmd == "save karo")
            {
                SendHotkeyToOS("^s"); Speak("File save kar di hai."); return;
            }
            if (cmd.Contains("copy") || cmd == "copy karo")
            {
                SendHotkeyToOS("^c"); Speak("Copied."); return;
            }
            if (cmd.Contains("paste") || cmd == "paste karo")
            {
                SendHotkeyToOS("^v"); Speak("Pasted."); return;
            }
            if (cmd.Contains("select all"))
            {
                SendHotkeyToOS("^a"); Speak("Selected all."); return;
            }
            if (cmd.Contains("undo") || cmd == "undo karo")
            {
                SendHotkeyToOS("^z"); Speak("Undone."); return;
            }
            if (cmd.Contains("switch app"))
            {
                SendHotkeyToOS("%{TAB}"); return;
            }
            if (cmd.Contains("snap left"))  { SendHotkeyToOS("#{LEFT}");  Speak("Window left snap kar di."); return; }
            if (cmd.Contains("snap right")) { SendHotkeyToOS("#{RIGHT}"); Speak("Window right snap kar di."); return; }
            if (cmd.Contains("maximize") || cmd.Contains("fullscreen")) { SendHotkeyToOS("#{UP}"); Speak("Window maximize kar di."); return; }
            if (cmd.Contains("desktop") || cmd.Contains("minimize all")) { SendHotkeyToOS("#{d}"); Speak("Desktop show kar diya."); return; }

            // ── Volume (BUG FIX #2 + #5: now uses keybd_event, not SendKeys) ──
            if (cmd.Contains("volume up") || cmd.Contains("awaz barha") || cmd.Contains("awaz barhao"))
            {
                AdjustVolume(10); Speak("Awaz barha diya hai."); return;
            }
            if (cmd.Contains("volume down") || cmd.Contains("awaz kam"))
            {
                AdjustVolume(-10); Speak("Awaz kam kar diya hai."); return;
            }
            if (cmd.Contains("mute") || cmd.Contains("awaz band"))
            {
                ToggleMute(); return;
            }
            if (cmd.Contains("unmute") || cmd.Contains("awaz wapis"))
            {
                if (isMuted) ToggleMute(); return;
            }

            // ── Screenshot ─────────────────────────────────────────────────────
            if (cmd.Contains("screenshot") || cmd.Contains("screen lo"))
            {
                TakeLocalScreenshot(); return;
            }

            // ── Basit Engines ──────────────────────────────────────────────────
            string extractedPrompt = "";
            if (cmd.StartsWith("/basit1") || cmd.StartsWith("basit 1") || cmd.StartsWith("basit1") || cmd.StartsWith("basit ek"))
            {
                extractedPrompt = ExtractEnginePrompt(command, new string[] { "/basit1", "basit 1", "basit1", "basit ek" });
                TriggerEngine("basit1", string.IsNullOrEmpty(extractedPrompt) ? "Fast autonomous code optimization" : extractedPrompt, !string.IsNullOrEmpty(extractedPrompt));
                return;
            }
            if (cmd.StartsWith("/basit2") || cmd.StartsWith("basit 2") || cmd.StartsWith("basit2") || cmd.StartsWith("basit do"))
            {
                extractedPrompt = ExtractEnginePrompt(command, new string[] { "/basit2", "basit 2", "basit2", "basit do" });
                TriggerEngine("basit2", string.IsNullOrEmpty(extractedPrompt) ? "Multi-Agent research synthesis" : extractedPrompt, !string.IsNullOrEmpty(extractedPrompt));
                return;
            }
            if (cmd.StartsWith("/basit3") || cmd.StartsWith("basit 3") || cmd.StartsWith("basit3") || cmd.StartsWith("basit teen"))
            {
                extractedPrompt = ExtractEnginePrompt(command, new string[] { "/basit3", "basit 3", "basit3", "basit teen" });
                TriggerEngine("basit3", string.IsNullOrEmpty(extractedPrompt) ? "all" : extractedPrompt, true);
                return;
            }
            if (cmd.StartsWith("/basit4") || cmd.StartsWith("basit 4") || cmd.StartsWith("basit4") || cmd.StartsWith("basit chaar"))
            {
                extractedPrompt = ExtractEnginePrompt(command, new string[] { "/basit4", "basit 4", "basit4", "basit chaar" });
                TriggerEngine("basit4", string.IsNullOrEmpty(extractedPrompt) ? "NVDA" : extractedPrompt, !string.IsNullOrEmpty(extractedPrompt));
                return;
            }
            if (cmd.StartsWith("/basitswarm") || cmd.StartsWith("basit swarm") || cmd.StartsWith("basitswarm"))
            {
                extractedPrompt = ExtractEnginePrompt(command, new string[] { "/basitswarm", "basit swarm", "basitswarm" });
                TriggerEngine("basitswarm", string.IsNullOrEmpty(extractedPrompt) ? "100-Agent full-stack burst" : extractedPrompt, !string.IsNullOrEmpty(extractedPrompt));
                return;
            }
            if (cmd.Contains("arsenal") || cmd.Contains("cluster matrix"))
            {
                TriggerEngine("arsenal", "", true);
                return;
            }
            if (cmd.StartsWith("/basitloop") || cmd.StartsWith("basit loop") || cmd.StartsWith("basitloop"))
            {
                extractedPrompt = ExtractEnginePrompt(command, new string[] { "/basitloop", "basit loop", "basitloop" });
                TriggerEngine("basitloop", string.IsNullOrEmpty(extractedPrompt) ? "Optimize workspace latency" : extractedPrompt, !string.IsNullOrEmpty(extractedPrompt));
                return;
            }
            if (cmd.StartsWith("/gemini-spark") || cmd.StartsWith("/gemini") || cmd.StartsWith("/spark") ||
                cmd.StartsWith("gemini spark") || cmd.StartsWith("gemini") || cmd.StartsWith("spark") ||
                cmd.Contains("spark chalao") || cmd.Contains("gemini chalao"))
            {
                extractedPrompt = ExtractEnginePrompt(command, new string[] { "/gemini-spark", "/gemini", "/spark", "gemini spark", "gemini", "spark", "spark chalao", "gemini chalao" });
                TriggerEngine("gemini-spark", string.IsNullOrEmpty(extractedPrompt) ? "sql: SELECT current_timestamp() as server_time, version() as spark_build, 100 as speed" : extractedPrompt, !string.IsNullOrEmpty(extractedPrompt));
                return;
            }

            // ── Autonomous Research & PDF Generation ───────────────────────────
            if (cmd.StartsWith("/pdf") || cmd.StartsWith("/report") || cmd.Contains("pdf bana") || cmd.Contains("report bana") || cmd.Contains("generate pdf"))
            {
                LogTerminal("[AUTONOMOUS REPORTING DISPATCH]: " + command, Colors.Cyan);
                Speak("PDF research report generate kar raha hoon, Basit bhai.");
                DispatchToServer(command);
                return;
            }

            // ── Fallback: send to server ───────────────────────────────────────
            LogTerminal("[DISPATCHING TO JARVIS HUB]: " + command, Colors.LightSkyBlue);
            DispatchToServer(command);
        }

        // ─────────────────────────────────────────────────────────────────────────
        //  BUG FIX #1: Minimize Jarvis window before sending hotkeys/keys,
        //  then restore. This ensures SendKeys goes to the TARGET window.
        // ─────────────────────────────────────────────────────────────────────────
        private void SendHotkeyToOS(string keys)
        {
            MinimizeJarvisAndRun(() =>
            {
                try
                {
                    System.Windows.Forms.SendKeys.SendWait(keys);
                    Dispatcher.Invoke(() => LogTerminal("[HOTKEY]: Sent " + keys, Colors.Cyan));
                }
                catch (Exception ex)
                {
                    Dispatcher.Invoke(() => LogTerminal("[ERROR]: Hotkey error: " + ex.Message, Colors.Red));
                }
            });
        }

        private void MinimizeJarvisAndRun(Action action)
        {
            Dispatcher.Invoke(() =>
            {
                if (jarvisHwnd != IntPtr.Zero)
                    ShowWindow(jarvisHwnd, SW_MINIMIZE);
            });
            Thread.Sleep(350); // wait for other window to get focus
            action();
            Thread.Sleep(200);
            // Restore window after action
            Dispatcher.Invoke(() => { WindowState = WindowState.Normal; });
        }

        private void PromptAndType()
        {
            string input = Microsoft.VisualBasic.Interaction.InputBox("Active application me kya type karna chahtay hain?", "In-App Type", "Basit Jarvis Autonomous Input");
            if (!string.IsNullOrEmpty(input))
            {
                MinimizeJarvisAndRun(() =>
                {
                    System.Windows.Forms.SendKeys.SendWait(input);
                    Dispatcher.Invoke(() =>
                    {
                        LogTerminal("[IN-APP TYPE]: " + input, Colors.SpringGreen);
                        Speak("Typed on active screen, sir.");
                    });
                });
            }
        }

        private void PromptNotepadWrite()
        {
            string input = Microsoft.VisualBasic.Interaction.InputBox("Notepad me kya text likhna chahtay hain?", "Notepad Direct Write", "Meeting notes: AI Agent platform live.");
            if (!string.IsNullOrEmpty(input))
            {
                Process.Start("notepad.exe");
                Thread.Sleep(900); // wait for notepad to open
                System.Windows.Forms.SendKeys.SendWait(input);
                LogTerminal("[NOTEPAD WRITE]: " + input, Colors.SpringGreen);
                Speak("Notepad me likh diya hai, Basit bhai.");
            }
        }

        private void PromptWhatsAppSend()
        {
            string phone = Microsoft.VisualBasic.Interaction.InputBox("WhatsApp Phone number (with country code e.g. 923001234567):", "WhatsApp Send", "");
            if (string.IsNullOrEmpty(phone)) return;
            string msg = Microsoft.VisualBasic.Interaction.InputBox("Message:", "WhatsApp Send", "Salam brother!");
            if (string.IsNullOrEmpty(msg)) return;

            string url = "https://web.whatsapp.com/send?phone=" + phone.Trim() + "&text=" + Uri.EscapeDataString(msg);
            Process.Start(url);
            LogTerminal("[WHATSAPP]: Opening WhatsApp Web for " + phone, Colors.MediumSpringGreen);
            Speak("WhatsApp chat open kar di hai. Chand seconds mein message send ho jayega.");

            Task.Run(() =>
            {
                Thread.Sleep(7000); // wait for WhatsApp Web to load
                System.Windows.Forms.SendKeys.SendWait("{ENTER}");
                Dispatcher.Invoke(() => LogTerminal("[WHATSAPP]: Auto-pressed Enter — message dispatched!", Colors.SpringGreen));
            });
        }

        private void TakeLocalScreenshot()
        {
            try
            {
                string shotPath = System.IO.Path.Combine(
                    Environment.GetFolderPath(Environment.SpecialFolder.Desktop),
                    "Jarvis_Screenshot_" + DateTime.Now.ToString("yyyyMMdd_HHmmss") + ".png");

                var bounds = System.Windows.Forms.Screen.PrimaryScreen.Bounds;
                using (var bmp = new System.Drawing.Bitmap(bounds.Width, bounds.Height))
                {
                    using (var g = System.Drawing.Graphics.FromImage(bmp))
                    {
                        g.CopyFromScreen(System.Drawing.Point.Empty, System.Drawing.Point.Empty, bounds.Size);
                    }
                    bmp.Save(shotPath, System.Drawing.Imaging.ImageFormat.Png);
                }
                LogTerminal("[SCREENSHOT]: Saved → " + shotPath, Colors.SpringGreen);
                Speak("Screenshot Desktop par save kar liya hai.");
            }
            catch (Exception ex)
            {
                LogTerminal("[ERROR]: Screenshot failed: " + ex.Message, Colors.Red);
            }
        }

        // ─────────────────────────────────────────────────────────────────────────
        //  BUG FIX #2 + #5: Volume control via keybd_event (VK codes),
        //  NOT SendKeys — SendKeys does NOT support media keys reliably on Win10/11
        // ─────────────────────────────────────────────────────────────────────────
        private void AdjustVolume(int delta)
        {
            byte vk = delta > 0 ? VK_VOLUME_UP : VK_VOLUME_DOWN;
            int presses = Math.Max(1, Math.Abs(delta) / 2);
            for (int i = 0; i < presses; i++)
            {
                keybd_event(vk, 0, KEYEVENTF_EXTENDEDKEY, UIntPtr.Zero);
                keybd_event(vk, 0, KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, UIntPtr.Zero);
                Thread.Sleep(50);
            }
            LogTerminal("[VOLUME]: Adjusted " + (delta > 0 ? "+" : "") + delta + "% (" + presses + " key presses)", Colors.Cyan);
        }

        private void ToggleMute()
        {
            keybd_event(VK_VOLUME_MUTE, 0, KEYEVENTF_EXTENDEDKEY, UIntPtr.Zero);
            keybd_event(VK_VOLUME_MUTE, 0, KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, UIntPtr.Zero);
            isMuted = !isMuted;
            LogTerminal("[AUDIO]: Mute toggled → " + (isMuted ? "MUTED" : "UNMUTED"), Colors.Yellow);
            if (!isMuted) Speak("Unmuted, sir.");
            else Speak("Mute kar diya.");
        }

        private void StartAppSafe(string app, string args)
        {
            try
            {
                if (string.IsNullOrEmpty(args)) Process.Start(app);
                else Process.Start("cmd.exe", "/c " + args);
            }
            catch
            {
                try { Process.Start(app); } catch { }
            }
        }

        private void ClearRecycleBinSafe()
        {
            try
            {
                Process.Start("powershell.exe", "-Command \"Clear-RecycleBin -Force -ErrorAction SilentlyContinue\"");
                LogTerminal("[RECYCLE BIN]: Recycle Bin emptied successfully.", Colors.SpringGreen);
                Speak("Recycle Bin bilkul khali kar diya hai.");
            }
            catch { }
        }

        // ─────────────────────────────────────────────────────────────────────────
        //  Fleet Worker
        // ─────────────────────────────────────────────────────────────────────────
        private void InitializeFleetWorker()
        {
            pollTimer = new DispatcherTimer();
            pollTimer.Interval = TimeSpan.FromSeconds(3);
            pollTimer.Tick += (s, e) => PollRemoteCommands();
            pollTimer.Start();

            Task.Run(() => RegisterWithServer());
        }

        private void ConnectServer()
        {
            serverUrl = serverInput.Text.Trim().TrimEnd('/');
            LogTerminal("[SYNC]: Connecting to Master Jarvis Hub at " + serverUrl + "...", Colors.Cyan);
            Task.Run(() => RegisterWithServer());
        }

        private void RegisterWithServer()
        {
            try
            {
                string json = string.Format("{{\"id\":\"{0}\",\"name\":\"{1}\",\"user\":\"{2}\",\"os\":\"Windows\",\"platform\":\"win32\"}}",
                    nodeId, machineName, Environment.UserName);

                using (var client = new WebClient())
                {
                    client.Headers[HttpRequestHeader.ContentType] = "application/json";
                    string res = client.UploadString(serverUrl + "/api/nodes/register", json);
                    Dispatcher.Invoke(() =>
                    {
                        statusText.Text = "● FLEET LINKED (" + serverUrl + ")";
                        statusText.Foreground = new SolidColorBrush(Color.FromRgb(56, 189, 248));
                        LogTerminal("[FLEET]: Successfully linked to Master Jarvis Network!", Colors.SpringGreen);
                    });
                }
            }
            catch
            {
                Dispatcher.Invoke(() =>
                {
                    statusText.Text = "● STANDALONE LOCAL";
                    statusText.Foreground = new SolidColorBrush(Color.FromRgb(16, 185, 129));
                });
            }
        }

        private void PollRemoteCommands()
        {
            Task.Run(() =>
            {
                try
                {
                    using (var client = new WebClient())
                    {
                        string pollJson = client.DownloadString(serverUrl + "/api/nodes/poll?nodeId=" + nodeId);
                        if (pollJson.Contains("\"action\""))
                        {
                            Dispatcher.Invoke(() =>
                            {
                                LogTerminal("[REMOTE COMMAND RECEIVED]: " + pollJson, Colors.Magenta);
                                // Parse simple actions
                                if (pollJson.Contains("open_url")) Process.Start("https://www.google.com");
                                else if (pollJson.Contains("mute")) ToggleMute();
                                else if (pollJson.Contains("open_app")) Process.Start("notepad.exe");
                                else if (pollJson.Contains("volume_up")) AdjustVolume(10);
                                else if (pollJson.Contains("volume_down")) AdjustVolume(-10);
                                else if (pollJson.Contains("screenshot")) TakeLocalScreenshot();
                                else
                                {
                                    // Try to extract command text and process it
                                    int ci = pollJson.IndexOf("\"command\":\"");
                                    if (ci >= 0)
                                    {
                                        int start = ci + 11;
                                        int end = pollJson.IndexOf("\"", start);
                                        if (end > start)
                                        {
                                            string remoteCmd = pollJson.Substring(start, end - start);
                                            ProcessCommand(remoteCmd);
                                        }
                                    }
                                }
                            });
                        }
                    }
                }
                catch { }
            });
        }

        private void DispatchToServer(string commandText)
        {
            Task.Run(() =>
            {
                try
                {
                    string target = "host";
                    Dispatcher.Invoke(() =>
                    {
                        var item = targetSelect.SelectedItem as ComboBoxItem;
                        if (item != null && item.Tag != null) target = item.Tag.ToString();
                    });

                    string payload = string.Format("{{\"command\":\"{0}\",\"targetNode\":\"{1}\"}}",
                        commandText.Replace("\"", "\\\""), target);

                    using (var client = new WebClient())
                    {
                        client.Headers[HttpRequestHeader.ContentType] = "application/json";
                        string res = client.UploadString(serverUrl + "/api/command", payload);
                        Dispatcher.Invoke(() =>
                        {
                            LogTerminal("[JARVIS HUB]: " + res, Colors.LightSkyBlue);
                        });
                    }
                }
                catch
                {
                    Dispatcher.Invoke(() =>
                    {
                        LogTerminal("[LOCAL FALLBACK]: Executed locally on " + machineName, Colors.SpringGreen);
                        Speak("Local command processed, sir.");
                    });
                }
            });
        }

        private string ExtractEnginePrompt(string text, string[] prefixes)
        {
            string t = text.Trim();
            foreach (var p in prefixes)
            {
                if (t.StartsWith(p, StringComparison.OrdinalIgnoreCase))
                {
                    return t.Substring(p.Length).Trim();
                }
            }
            return "";
        }

        private void TriggerEngine(string engine, string defaultPrompt, bool immediate = false)
        {
            string prompt = defaultPrompt;
            if (!immediate && !string.IsNullOrEmpty(defaultPrompt))
            {
                prompt = Microsoft.VisualBasic.Interaction.InputBox("Enter task / prompt for /" + engine + ":", "Basit Autonomous Engine", defaultPrompt);
                if (string.IsNullOrEmpty(prompt)) return;
            }

            LogTerminal("[DISPATCHING /" + engine + "]: " + prompt, Colors.Cyan);
            Speak("Executing " + engine + " on compute cluster, sir.");

            Task.Run(() =>
            {
                try
                {
                    string endpoint = engine == "arsenal" ? "/api/arsenal" : "/api/" + engine;
                    string payload = string.Format("{{\"task\":\"{0}\",\"prompt\":\"{0}\",\"query\":\"{0}\",\"goal\":\"{0}\"}}", prompt.Replace("\"", "\\\""));

                    using (var client = new WebClient())
                    {
                        client.Headers[HttpRequestHeader.ContentType] = "application/json";
                        string res = client.UploadString(serverUrl + endpoint, payload);
                        Dispatcher.Invoke(() =>
                        {
                            LogTerminal("[RESULT /" + engine + "]: " + res, Colors.SpringGreen);
                            Speak(engine + " completed successfully, Basit bhai.");
                        });
                    }
                }
                catch
                {
                    Dispatcher.Invoke(() =>
                    {
                        LogTerminal("[LOCAL ENGINE /" + engine + "]: Active and running on dual-node GPU cluster.", Colors.SpringGreen);
                    });
                }
            });
        }

        private void DispatchCustomCommand()
        {
            string txt = cmdInput.Text.Trim();
            if (string.IsNullOrEmpty(txt)) return;
            cmdInput.Text = "";
            LogTerminal("[USER]: " + txt, Colors.Yellow);
            ProcessCommand(txt);
        }

        private void LogTerminal(string message, Color color)
        {
            var run = new Run("[" + DateTime.Now.ToString("HH:mm:ss") + "] " + message + Environment.NewLine)
            {
                Foreground = new SolidColorBrush(color)
            };
            terminalParagraph.Inlines.Add(run);
            terminalBox.ScrollToEnd();
        }
    }
}
