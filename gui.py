"""
22-Billion: GUI Interface
Cyberpunk-style GUI with voice alerts, panic button, and live status

ENHANCEMENTS:
- Panic Button: Spacebar for emergency stop
- Cyberpunk Dark Mode: #121212 + #00ff41 hacker style
- Live Status Indicators: Real-time connection status
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import pyttsx3
from datetime import datetime
import time


class TradingGUI:
    """Cyberpunk-style GUI for 22-Billion Trading Coach"""
    
    # ENHANCEMENT 2: Cyberpunk color scheme
    COLORS = {
        'bg_main': '#121212',        # Deep black background
        'bg_panel': '#1a1a1a',       # Slightly lighter panels
        'bg_dark': '#0a0a0a',        # Darker sections
        'neon_green': '#00ff41',     # Hacker green (primary)
        'neon_green_dim': '#00aa2b', # Dimmer green
        'neon_red': '#ff0040',       # Alert red
        'neon_orange': '#ff9500',    # Warning orange
        'neon_blue': '#00d9ff',      # Info blue
        'text_main': '#e0e0e0',      # Main text
        'text_dim': '#808080',       # Dimmed text
    }
    
    def __init__(self, config, trading_brain, news_analyzer=None, market_analyzer=None):
        self.config = config
        self.trading_brain = trading_brain
        self.news_analyzer = news_analyzer
        self.market_analyzer = market_analyzer
        self.voice_enabled = config['voice']['enabled']
        
        # Initialize text-to-speech
        if self.voice_enabled:
            try:
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', 150)  # Speed
                self.tts_engine.setProperty('volume', 0.9)  # Volume
            except Exception as e:
                print(f"⚠️ Voice engine initialization failed: {e}")
                self.voice_enabled = False
        
        # Running state
        self.running = False
        self.analysis_thread = None
        self.status_thread = None
        
        # ENHANCEMENT 3: Status tracking
        self.status_api = False
        self.status_data = False
        self.status_ai = False
        self.last_data_time = 0
        
        # Create main window with cyberpunk style
        self.root = tk.Tk()
        self.root.title("22-Billion: Hybrid AI Trading Coach [CYBERPUNK EDITION]")
        self.root.geometry("1000x750")
        self.root.configure(bg=self.COLORS['bg_main'])
        
        # ENHANCEMENT 1: Panic button (Spacebar)
        self.root.bind('<space>', self._panic_button)
        
        self._create_widgets()
        
    def _create_widgets(self):
        """ENHANCED: Create cyberpunk-style GUI widgets with status indicators"""
        
        # ENHANCEMENT 3: Top bar with live status indicators
        topbar_frame = tk.Frame(self.root, bg=self.COLORS['bg_panel'], height=40)
        topbar_frame.pack(fill='x', padx=0, pady=0)
        topbar_frame.pack_propagate(False)
        
        # Left side: Title
        title_left = tk.Label(
            topbar_frame,
            text="◢ 22-BILLION ◣",
            font=("Courier New", 12, "bold"),
            fg=self.COLORS['neon_green'],
            bg=self.COLORS['bg_panel']
        )
        title_left.pack(side='left', padx=20)
        
        # Right side: Status indicators
        status_container = tk.Frame(topbar_frame, bg=self.COLORS['bg_panel'])
        status_container.pack(side='right', padx=20)
        
        # API Status
        self.status_api_light = tk.Label(
            status_container,
            text="●",
            font=("Arial", 16),
            fg=self.COLORS['neon_red'],
            bg=self.COLORS['bg_panel']
        )
        self.status_api_light.pack(side='left', padx=2)
        tk.Label(
            status_container,
            text="API",
            font=("Courier New", 8),
            fg=self.COLORS['text_dim'],
            bg=self.COLORS['bg_panel']
        ).pack(side='left', padx=(0, 10))
        
        # Data Status
        self.status_data_light = tk.Label(
            status_container,
            text="●",
            font=("Arial", 16),
            fg=self.COLORS['neon_red'],
            bg=self.COLORS['bg_panel']
        )
        self.status_data_light.pack(side='left', padx=2)
        tk.Label(
            status_container,
            text="DATA",
            font=("Courier New", 8),
            fg=self.COLORS['text_dim'],
            bg=self.COLORS['bg_panel']
        ).pack(side='left', padx=(0, 10))
        
        # AI Status
        self.status_ai_light = tk.Label(
            status_container,
            text="●",
            font=("Arial", 16),
            fg=self.COLORS['neon_red'],
            bg=self.COLORS['bg_panel']
        )
        self.status_ai_light.pack(side='left', padx=2)
        tk.Label(
            status_container,
            text="AI",
            font=("Courier New", 8),
            fg=self.COLORS['text_dim'],
            bg=self.COLORS['bg_panel']
        ).pack(side='left')
        
        # Main title banner
        title_frame = tk.Frame(self.root, bg=self.COLORS['bg_main'])
        title_frame.pack(pady=15)
        
        title_label = tk.Label(
            title_frame,
            text="▓▓▓ 22-BILLION AI TRADING COACH ▓▓▓",
            font=("Courier New", 18, "bold"),
            fg=self.COLORS['neon_green'],
            bg=self.COLORS['bg_main']
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="[ CYBERPUNK EDITION ] Data • Vision • AI Brain",
            font=("Courier New", 9),
            fg=self.COLORS['text_dim'],
            bg=self.COLORS['bg_main']
        )
        subtitle_label.pack()
        
        # Status frame
        status_frame = tk.Frame(self.root, bg=self.COLORS['bg_panel'], bd=2, relief='solid')
        status_frame.pack(pady=10, padx=20, fill='x')
        
        self.status_label = tk.Label(
            status_frame,
            text="◤ SYSTEM OFFLINE ◥",
            font=("Courier New", 14, "bold"),
            fg=self.COLORS['neon_red'],
            bg=self.COLORS['bg_panel']
        )
        self.status_label.pack(pady=8)
        
        # Market info frame
        info_frame = tk.Frame(self.root, bg=self.COLORS['bg_panel'], bd=1, relief='solid')
        info_frame.pack(pady=5, padx=20, fill='x')
        
        self.price_label = tk.Label(
            info_frame,
            text="PRICE: ---.--",
            font=("Courier New", 11, "bold"),
            fg=self.COLORS['neon_blue'],
            bg=self.COLORS['bg_panel']
        )
        self.price_label.pack(side='left', padx=15, pady=5)
        
        self.rsi_label = tk.Label(
            info_frame,
            text="RSI: --",
            font=("Courier New", 11, "bold"),
            fg=self.COLORS['text_main'],
            bg=self.COLORS['bg_panel']
        )
        self.rsi_label.pack(side='left', padx=15)
        
        self.signal_label = tk.Label(
            info_frame,
            text="SIGNAL: NONE",
            font=("Courier New", 11, "bold"),
            fg=self.COLORS['text_main'],
            bg=self.COLORS['bg_panel']
        )
        self.signal_label.pack(side='left', padx=15)
        
        # Control buttons
        button_frame = tk.Frame(self.root, bg=self.COLORS['bg_main'])
        button_frame.pack(pady=15)
        
        self.start_button = tk.Button(
            button_frame,
            text="▶ ENGAGE",
            font=("Courier New", 12, "bold"),
            bg=self.COLORS['neon_green_dim'],
            fg='black',
            activebackground=self.COLORS['neon_green'],
            width=14,
            height=2,
            bd=0,
            command=self.start_trading
        )
        self.start_button.pack(side='left', padx=5)
        
        self.stop_button = tk.Button(
            button_frame,
            text="⬛ DISENGAGE",
            font=("Courier New", 12, "bold"),
            bg='#660000',
            fg=self.COLORS['text_main'],
            activebackground=self.COLORS['neon_red'],
            width=14,
            height=2,
            bd=0,
            command=self.stop_trading,
            state='disabled'
        )
        self.stop_button.pack(side='left', padx=5)
        
        # ENHANCEMENT 1: Panic button indicator
        panic_label = tk.Label(
            button_frame,
            text="[SPACEBAR = PANIC! 🚨]",
            font=("Courier New", 9, "bold"),
            fg=self.COLORS['neon_orange'],
            bg=self.COLORS['bg_main']
        )
        panic_label.pack(side='left', padx=20)
        
        # ENHANCEMENT v1.5.0: Timeframe Selector
        timeframe_frame = tk.Frame(self.root, bg=self.COLORS['bg_panel'], bd=1, relief='solid')
        timeframe_frame.pack(pady=10, padx=20, fill='x')
        
        # Timeframe label
        tf_label = tk.Label(
            timeframe_frame,
            text="⏱ TIMEFRAME:",
            font=("Courier New", 10, "bold"),
            fg=self.COLORS['neon_blue'],
            bg=self.COLORS['bg_panel']
        )
        tf_label.pack(side='left', padx=15, pady=8)
        
        # Timeframe buttons
        self.timeframe_buttons = {}
        timeframes = ['1m', '3m', '5m', '15m', '30m', '1h', '4h']
        current_tf = self.config['trading']['timeframe']
        
        for tf in timeframes:
            # Determine if this is the current timeframe
            is_current = (tf == current_tf)
            
            btn = tk.Button(
                timeframe_frame,
                text=tf,
                font=("Courier New", 9, "bold"),
                bg=self.COLORS['neon_green'] if is_current else self.COLORS['bg_dark'],
                fg='black' if is_current else self.COLORS['text_main'],
                activebackground=self.COLORS['neon_green'],
                width=5,
                height=1,
                bd=0,
                command=lambda t=tf: self.change_timeframe(t)
            )
            btn.pack(side='left', padx=3, pady=5)
            self.timeframe_buttons[tf] = btn
        
        # Current timeframe display
        self.current_tf_label = tk.Label(
            timeframe_frame,
            text=f"[Current: {current_tf}]",
            font=("Courier New", 9),
            fg=self.COLORS['neon_green'],
            bg=self.COLORS['bg_panel']
        )
        self.current_tf_label.pack(side='left', padx=15)
        
        # ENHANCEMENT v1.6.0: News & Market Intelligence Panel
        intel_frame = tk.Frame(self.root, bg=self.COLORS['bg_panel'], bd=1, relief='solid')
        intel_frame.pack(pady=5, padx=20, fill='x')
        
        intel_label = tk.Label(
            intel_frame,
            text="🌍 MARKET INTELLIGENCE:",
            font=("Courier New", 9, "bold"),
            fg=self.COLORS['neon_blue'],
            bg=self.COLORS['bg_panel']
        )
        intel_label.pack(side='left', padx=15, pady=5)
        
        # Market sentiment display
        self.market_summary_label = tk.Label(
            intel_frame,
            text="시장: 로딩중...",
            font=("Courier New", 9),
            fg=self.COLORS['text_main'],
            bg=self.COLORS['bg_panel']
        )
        self.market_summary_label.pack(side='left', padx=10)
        
        # Separator
        tk.Label(
            intel_frame,
            text="|",
            font=("Courier New", 9),
            fg=self.COLORS['text_dim'],
            bg=self.COLORS['bg_panel']
        ).pack(side='left', padx=5)
        
        # News sentiment display
        self.news_summary_label = tk.Label(
            intel_frame,
            text="뉴스: 로딩중...",
            font=("Courier New", 9),
            fg=self.COLORS['text_main'],
            bg=self.COLORS['bg_panel']
        )
        self.news_summary_label.pack(side='left', padx=10)
        
        # Log area
        log_frame = tk.Frame(self.root, bg=self.COLORS['bg_main'])
        log_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        log_label = tk.Label(
            log_frame,
            text="▓▓▓ SYSTEM LOG ▓▓▓",
            font=("Courier New", 10, "bold"),
            fg=self.COLORS['neon_green'],
            bg=self.COLORS['bg_main']
        )
        log_label.pack(anchor='w')
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            font=("Courier New", 9),
            bg=self.COLORS['bg_dark'],
            fg=self.COLORS['neon_green'],
            insertbackground=self.COLORS['neon_green'],
            selectbackground=self.COLORS['neon_green_dim'],
            selectforeground='black',
            height=22,
            bd=2,
            relief='solid'
        )
        self.log_text.pack(fill='both', expand=True)
        
        # Footer with cyberpunk style
        footer_frame = tk.Frame(self.root, bg=self.COLORS['bg_panel'])
        footer_frame.pack(fill='x', pady=5)
        
        footer_label = tk.Label(
            footer_frame,
            text="[!] EDUCATIONAL USE ONLY | MANAGE YOUR RISK | NO GUARANTEES [!]",
            font=("Courier New", 8),
            fg=self.COLORS['text_dim'],
            bg=self.COLORS['bg_panel']
        )
        footer_label.pack(pady=3)
        
    def _panic_button(self, event=None):
        """
        ENHANCEMENT 1: PANIC BUTTON (Spacebar)
        
        Emergency stop - like ejection seat in fighter jet!
        """
        if not self.running:
            return
        
        # Flash visual warning
        self.status_label.config(
            text="◤◤◤ !!! PANIC STOP !!! ◥◥◥",
            fg=self.COLORS['neon_red']
        )
        self.root.update()
        
        # Log panic
        self.log("")
        self.log("="*80)
        self.log("🚨🚨🚨 PANIC BUTTON ACTIVATED! 🚨🚨🚨")
        self.log("="*80)
        
        # Voice alert
        if self.voice_enabled:
            self.speak("긴급 정지!")
        
        # Emergency stop
        self.stop_trading()
        
        self.log("✅ Emergency stop completed")
    
    def start_trading(self):
        """Start the trading system with status monitoring"""
        if self.running:
            return
        
        self.running = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.status_label.config(
            text="◤ SYSTEM ONLINE ◥",
            fg=self.COLORS['neon_green']
        )
        
        self.log("="*80)
        self.log("▓▓▓ 22-BILLION TRADING COACH ENGAGED ▓▓▓")
        self.log("="*80)
        self.log("")
        self.log("🚨 PANIC BUTTON: Press SPACEBAR for emergency stop")
        self.log("")
        
        # Start data engine
        try:
            self.trading_brain.data_engine.start()
            self.log("✅ Data Engine started (Zombie Mode)")
            self.status_api = True
        except Exception as e:
            self.log(f"❌ Error starting Data Engine: {e}")
            self.stop_trading()
            return
        
        # Start analysis thread
        self.analysis_thread = threading.Thread(target=self._analysis_loop, daemon=True)
        self.analysis_thread.start()
        
        # ENHANCEMENT 3: Start status monitor thread
        self.status_thread = threading.Thread(target=self._status_monitor, daemon=True)
        self.status_thread.start()
        
        self.log("🔄 Market analysis loop started")
        self.log("📊 Status monitor started")
        self.log("")
        
        if self.voice_enabled:
            self.speak("시스템 가동")
        
    def stop_trading(self):
        """Stop the trading system"""
        if not self.running:
            return
        
        self.running = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.status_label.config(
            text="◤ SYSTEM OFFLINE ◥",
            fg=self.COLORS['neon_red']
        )
        
        # Reset status lights
        self.status_api = False
        self.status_data = False
        self.status_ai = False
        self._update_status_lights()
        
        self.log("")
        self.log("="*80)
        self.log("▓▓▓ 22-BILLION TRADING COACH DISENGAGED ▓▓▓")
        self.log("="*80)
        
        # Stop data engine
        try:
            self.trading_brain.data_engine.stop()
            self.log("✅ Data Engine stopped")
        except Exception as e:
            self.log(f"❌ Error stopping Data Engine: {e}")
        
        if self.voice_enabled:
            self.speak("시스템 종료")
    
    def change_timeframe(self, new_timeframe):
        """
        ENHANCEMENT v1.5.0: Dynamic timeframe change
        
        Allows user to switch timeframe during operation.
        Safely stops, reconfigures, and optionally restarts.
        
        Args:
            new_timeframe: New timeframe string (e.g., '1m', '5m', '15m', '30m', '1h', '4h')
        """
        current_tf = self.config['trading']['timeframe']
        
        # Check if already on this timeframe
        if new_timeframe == current_tf:
            self.log(f"⚠️ Already using {new_timeframe} timeframe")
            return
        
        # Warning if system is running
        if self.running:
            self.log("")
            self.log("="*80)
            self.log(f"⚠️ TIMEFRAME CHANGE REQUEST: {current_tf} → {new_timeframe}")
            self.log("="*80)
            self.log("⚠️ Changing timeframe requires system restart for safety")
            self.log("🛑 Stopping system automatically...")
            self.log("")
            
            # Stop trading first (like changing car wheels - must stop first!)
            self.stop_trading()
            time.sleep(0.5)  # Brief pause for clean shutdown
        
        # Change timeframe in data engine
        self.log(f"🔄 Changing timeframe to {new_timeframe}...")
        
        try:
            # Update data engine timeframe
            success = self.trading_brain.data_engine.change_timeframe(new_timeframe)
            
            if success:
                # Update config
                self.config['trading']['timeframe'] = new_timeframe
                
                # Update UI - highlight new timeframe button
                self._update_timeframe_buttons(new_timeframe)
                
                # Update display label
                self.current_tf_label.config(text=f"[Current: {new_timeframe}]")
                
                # Log success
                self.log(f"✅ Timeframe changed to {new_timeframe}")
                self.log(f"📊 Historical data reloaded for {new_timeframe}")
                self.log("")
                self.log("💡 Press ENGAGE to start trading with new timeframe")
                self.log("")
                
                # Voice notification
                if self.voice_enabled:
                    timeframe_ko = self._get_timeframe_korean(new_timeframe)
                    self.speak(f"{timeframe_ko}으로 변경되었습니다. 다시 시작하세요.")
            else:
                self.log(f"❌ Failed to change timeframe to {new_timeframe}")
                
        except Exception as e:
            self.log(f"❌ Error changing timeframe: {e}")
    
    def _update_timeframe_buttons(self, new_timeframe):
        """Update timeframe button highlights"""
        for tf, btn in self.timeframe_buttons.items():
            if tf == new_timeframe:
                # Highlight current
                btn.config(
                    bg=self.COLORS['neon_green'],
                    fg='black'
                )
            else:
                # Normal state
                btn.config(
                    bg=self.COLORS['bg_dark'],
                    fg=self.COLORS['text_main']
                )
    
    def _get_timeframe_korean(self, timeframe):
        """Convert timeframe to Korean pronunciation"""
        korean_map = {
            '1m': '1분봉',
            '3m': '3분봉',
            '5m': '5분봉',
            '15m': '15분봉',
            '30m': '30분봉',
            '1h': '1시간봉',
            '4h': '4시간봉'
        }
        return korean_map.get(timeframe, timeframe)
        
    def _analysis_loop(self):
        """
        ENHANCED v1.6.0: Main analysis loop with news & market intelligence
        """
        import time
        
        update_interval = self.config['trading']['update_interval']
        last_update = 0
        last_news_update = 0
        last_market_update = 0
        
        # Update news every 5 minutes
        news_interval = 300
        # Update market every 10 minutes
        market_interval = 600
        
        while self.running:
            try:
                current_time = time.time()
                
                # Update market info display every 1 second
                if current_time - last_update >= 1.0:
                    self._update_market_display()
                    last_update = current_time
                
                # Update news analysis (every 5 minutes)
                if self.news_analyzer and (current_time - last_news_update >= news_interval):
                    self._update_news_intelligence()
                    last_news_update = current_time
                
                # Update market analysis (every 10 minutes)
                if self.market_analyzer and (current_time - last_market_update >= market_interval):
                    self._update_market_intelligence()
                    last_market_update = current_time
                
                # Run market analysis
                decision = self.trading_brain.analyze_market()
                
                if decision:
                    # ENHANCEMENT: Compact summary in log
                    compact = self.trading_brain.get_compact_summary(decision)
                    self.log("")
                    self.log("━" * 70)
                    self.log(f"🎯 신호: {compact}")
                    self.log("━" * 70)
                    
                    # Full details only if approved
                    if decision['approved']:
                        summary = self.trading_brain.format_decision_summary(decision)
                        self.log(summary)
                        
                        # Voice alert
                        if self.voice_enabled:
                            briefing = self.trading_brain.get_voice_briefing(decision)
                            if briefing:
                                self.speak(briefing)
                    else:
                        # Rejected - show reason only
                        main_risk = decision['risks'][0] if decision['risks'] else '조건 미달'
                        self.log(f"   사유: {main_risk}")
                        self.log("")
                
                time.sleep(update_interval)
                
            except Exception as e:
                self.log(f"❌ Error in analysis loop: {e}")
                time.sleep(5)
    
    def _update_news_intelligence(self):
        """
        ENHANCEMENT v1.6.0: Update news analysis
        """
        try:
            # Get latest news
            news_items = self.news_analyzer.get_latest_news(limit=5)
            
            if news_items:
                self.log("")
                self.log("📰 뉴스 업데이트...")
                
                # Analyze sentiment
                sentiment = self.news_analyzer.analyze_news_sentiment(news_items)
                
                # Update GUI
                compact_news = self.news_analyzer.get_compact_news_summary()
                self.root.after(0, lambda: self.news_summary_label.config(text=compact_news))
                
                # Log concise summary
                self.log(f"   {sentiment['sentiment']} [{sentiment['score']}] - {sentiment['summary']}")
                self.log("")
                
        except Exception as e:
            print(f"⚠️ News update error: {e}")
    
    def _update_market_intelligence(self):
        """
        ENHANCEMENT v1.6.0: Update market analysis
        """
        try:
            # Get market overview
            market = self.market_analyzer.get_market_overview()
            
            self.log("")
            self.log("🌍 시장 분석 업데이트...")
            
            # Update GUI
            compact_market = self.market_analyzer.get_compact_market_summary()
            self.root.after(0, lambda: self.market_summary_label.config(text=compact_market))
            
            # Log concise summary
            self.log(f"   {market['market_sentiment']} - {market['summary']}")
            self.log("")
            
        except Exception as e:
            print(f"⚠️ Market update error: {e}")
        
    def _status_monitor(self):
        """
        ENHANCEMENT 3: Real-time status monitor
        
        Updates status lights every second
        """
        while self.running:
            try:
                # Check API connection (Data engine running)
                self.status_api = self.trading_brain.data_engine.running
                
                # Check data flow (received data in last 10 seconds)
                current_time = time.time()
                data_age = current_time - self.trading_brain.data_engine.last_data_time
                self.status_data = data_age < 10  # Green if data within 10s
                
                # Check AI brain (has indicators calculated)
                try:
                    indicators = self.trading_brain.technical_indicators.calculate_all(
                        self.trading_brain.data_engine
                    )
                    self.status_ai = indicators is not None
                except:
                    self.status_ai = False
                
                # Update lights in main thread
                self.root.after(0, self._update_status_lights)
                
                time.sleep(1)  # Update every second
                
            except Exception as e:
                print(f"⚠️ Status monitor error: {e}")
                time.sleep(1)
    
    def _update_status_lights(self):
        """Update status indicator lights (must be called from main thread)"""
        # API Light
        self.status_api_light.config(
            fg=self.COLORS['neon_green'] if self.status_api else self.COLORS['neon_red']
        )
        
        # Data Light
        self.status_data_light.config(
            fg=self.COLORS['neon_green'] if self.status_data else self.COLORS['neon_red']
        )
        
        # AI Light
        self.status_ai_light.config(
            fg=self.COLORS['neon_green'] if self.status_ai else self.COLORS['neon_red']
        )
    
    def _update_market_display(self):
        """ENHANCED: Update market display with cyberpunk styling"""
        try:
            market_data = self.trading_brain.data_engine.get_market_data()
            
            # Update price with cyberpunk style
            price = market_data['price']
            self.price_label.config(text=f"PRICE: ${price:,.2f}")
            
            # Update indicators if available
            indicators = self.trading_brain.technical_indicators.calculate_all(
                self.trading_brain.data_engine
            )
            
            if indicators:
                rsi = indicators['rsi']['value']
                # Cyberpunk color scheme
                if rsi > 70:
                    rsi_color = self.COLORS['neon_red']
                elif rsi < 30:
                    rsi_color = self.COLORS['neon_green']
                else:
                    rsi_color = self.COLORS['neon_blue']
                
                self.rsi_label.config(text=f"RSI: {rsi:.2f}", fg=rsi_color)
                
                signal = self.trading_brain.technical_indicators.generate_signal(
                    indicators, market_data
                )
                
                signal_type = signal['type'] or 'NONE'
                signal_strength = signal['strength']
                
                # Color based on signal type
                if signal_type == 'LONG':
                    signal_color = self.COLORS['neon_green']
                elif signal_type == 'SHORT':
                    signal_color = self.COLORS['neon_red']
                else:
                    signal_color = self.COLORS['text_dim']
                
                signal_text = f"SIGNAL: {signal_type} [{signal_strength:.0f}%]"
                self.signal_label.config(text=signal_text, fg=signal_color)
                
        except Exception as e:
            pass  # Silently fail for display updates
    
    def log(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        # Update GUI in main thread
        self.root.after(0, self._append_log, log_message)
    
    def _append_log(self, message):
        """Append to log text widget (must be called from main thread)"""
        self.log_text.insert(tk.END, message)
        self.log_text.see(tk.END)
    
    def speak(self, text):
        """Speak text using TTS"""
        if not self.voice_enabled:
            return
        
        def _speak_thread():
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"⚠️ TTS error: {e}")
        
        # Run TTS in separate thread to avoid blocking
        threading.Thread(target=_speak_thread, daemon=True).start()
    
    def run(self):
        """Start the GUI main loop"""
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        self.log("▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓")
        self.log("▓▓▓        22-BILLION HYBRID AI TRADING COACH              ▓▓▓")
        self.log("▓▓▓         [ CYBERPUNK EDITION v1.6.0 ]                   ▓▓▓")
        self.log("▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓")
        self.log("")
        self.log("╔═══════════════════════════════════════════════════════════════════╗")
        self.log("║  🆕 NEW: Real-time News & Market Intelligence                    ║")
        self.log("║  Welcome to the Matrix. Press ENGAGE to begin.                   ║")
        self.log("╚═══════════════════════════════════════════════════════════════════╝")
        self.log("")
        self.log("🚨 PANIC: SPACEBAR = Emergency stop")
        self.log("📊 TIMEFRAME: Click buttons to switch (1m-4h)")
        self.log("🌍 INTELLIGENCE: Auto-updates news & market analysis")
        self.log("")
        self.log("📊 STATUS: [●] API [●] DATA [●] AI (GREEN=OK, RED=Error)")
        self.log("")
        self.log("═══════════════════════════════════════════════════════════════════")
        self.log("✅ SYSTEM READY")
        self.log("═══════════════════════════════════════════════════════════════════")
        self.log("")
        
        # ENHANCEMENT v1.6.0: Auto-start feature
        auto_start = self.config.get('trading', {}).get('auto_start', False)
        if auto_start:
            self.log("🚀 AUTO-START enabled in config")
            self.log("   Starting in 3 seconds...")
            self.root.after(3000, self.start_trading)
        
        self.root.mainloop()
    
    def _on_closing(self):
        """Handle window close event"""
        if self.running:
            if messagebox.askokcancel("Quit", "Trading system is running. Stop and quit?"):
                self.stop_trading()
                self.root.destroy()
        else:
            self.root.destroy()
