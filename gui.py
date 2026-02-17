"""
22-Billion: GUI Interface
Simple Tkinter GUI with voice alerts using pyttsx3
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import pyttsx3
from datetime import datetime


class TradingGUI:
    """Simple and elegant GUI for 22-Billion Trading Coach"""
    
    def __init__(self, config, trading_brain):
        self.config = config
        self.trading_brain = trading_brain
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
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("22-Billion: Hybrid AI Trading Coach")
        self.root.geometry("900x700")
        self.root.configure(bg='#1e1e1e')
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Create GUI widgets"""
        
        # Title
        title_frame = tk.Frame(self.root, bg='#1e1e1e')
        title_frame.pack(pady=10)
        
        title_label = tk.Label(
            title_frame,
            text="💰 22-BILLION AI TRADING COACH",
            font=("Arial", 20, "bold"),
            fg='#00ff00',
            bg='#1e1e1e'
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="Data Engine + Vision Engine + AI Brain",
            font=("Arial", 10),
            fg='#888888',
            bg='#1e1e1e'
        )
        subtitle_label.pack()
        
        # Status frame
        status_frame = tk.Frame(self.root, bg='#2d2d2d')
        status_frame.pack(pady=10, padx=20, fill='x')
        
        self.status_label = tk.Label(
            status_frame,
            text="🔴 STOPPED",
            font=("Arial", 14, "bold"),
            fg='#ff4444',
            bg='#2d2d2d'
        )
        self.status_label.pack(pady=5)
        
        # Market info frame
        info_frame = tk.Frame(self.root, bg='#2d2d2d')
        info_frame.pack(pady=5, padx=20, fill='x')
        
        self.price_label = tk.Label(
            info_frame,
            text="Price: --",
            font=("Arial", 12),
            fg='#ffffff',
            bg='#2d2d2d'
        )
        self.price_label.pack(side='left', padx=10)
        
        self.rsi_label = tk.Label(
            info_frame,
            text="RSI: --",
            font=("Arial", 12),
            fg='#ffffff',
            bg='#2d2d2d'
        )
        self.rsi_label.pack(side='left', padx=10)
        
        self.signal_label = tk.Label(
            info_frame,
            text="Signal: --",
            font=("Arial", 12),
            fg='#ffffff',
            bg='#2d2d2d'
        )
        self.signal_label.pack(side='left', padx=10)
        
        # Control buttons
        button_frame = tk.Frame(self.root, bg='#1e1e1e')
        button_frame.pack(pady=10)
        
        self.start_button = tk.Button(
            button_frame,
            text="▶ START",
            font=("Arial", 12, "bold"),
            bg='#00aa00',
            fg='white',
            width=12,
            height=2,
            command=self.start_trading
        )
        self.start_button.pack(side='left', padx=5)
        
        self.stop_button = tk.Button(
            button_frame,
            text="⬛ STOP",
            font=("Arial", 12, "bold"),
            bg='#aa0000',
            fg='white',
            width=12,
            height=2,
            command=self.stop_trading,
            state='disabled'
        )
        self.stop_button.pack(side='left', padx=5)
        
        # Log area
        log_frame = tk.Frame(self.root, bg='#1e1e1e')
        log_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        log_label = tk.Label(
            log_frame,
            text="📋 Activity Log",
            font=("Arial", 11, "bold"),
            fg='#00ff00',
            bg='#1e1e1e'
        )
        log_label.pack(anchor='w')
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            font=("Courier", 9),
            bg='#0d0d0d',
            fg='#00ff00',
            insertbackground='white',
            height=20
        )
        self.log_text.pack(fill='both', expand=True)
        
        # Footer
        footer_label = tk.Label(
            self.root,
            text="⚠️ For educational purposes only | Always manage your risk",
            font=("Arial", 8),
            fg='#666666',
            bg='#1e1e1e'
        )
        footer_label.pack(pady=5)
        
    def start_trading(self):
        """Start the trading system"""
        if self.running:
            return
        
        self.running = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.status_label.config(text="🟢 RUNNING", fg='#00ff00')
        
        self.log("="*80)
        self.log("🚀 22-BILLION TRADING COACH STARTED")
        self.log("="*80)
        
        # Start data engine
        try:
            self.trading_brain.data_engine.start()
            self.log("✅ Data Engine started")
        except Exception as e:
            self.log(f"❌ Error starting Data Engine: {e}")
            self.stop_trading()
            return
        
        # Start analysis thread
        self.analysis_thread = threading.Thread(target=self._analysis_loop, daemon=True)
        self.analysis_thread.start()
        
        self.log("🔄 Market analysis loop started")
        self.log("")
        
        if self.voice_enabled:
            self.speak("22빌리언 트레이딩 코치 시작합니다")
        
    def stop_trading(self):
        """Stop the trading system"""
        if not self.running:
            return
        
        self.running = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.status_label.config(text="🔴 STOPPED", fg='#ff4444')
        
        self.log("")
        self.log("="*80)
        self.log("🛑 22-BILLION TRADING COACH STOPPED")
        self.log("="*80)
        
        # Stop data engine
        try:
            self.trading_brain.data_engine.stop()
            self.log("✅ Data Engine stopped")
        except Exception as e:
            self.log(f"❌ Error stopping Data Engine: {e}")
        
        if self.voice_enabled:
            self.speak("시스템을 종료합니다")
        
    def _analysis_loop(self):
        """Main analysis loop running in background thread"""
        import time
        
        update_interval = self.config['trading']['update_interval']
        last_update = 0
        
        while self.running:
            try:
                current_time = time.time()
                
                # Update market info display every 1 second
                if current_time - last_update >= 1.0:
                    self._update_market_display()
                    last_update = current_time
                
                # Run market analysis
                decision = self.trading_brain.analyze_market()
                
                if decision:
                    # Log decision
                    summary = self.trading_brain.format_decision_summary(decision)
                    self.log(summary)
                    
                    # Voice alert for approved signals
                    if decision['approved'] and self.voice_enabled:
                        briefing = self.trading_brain.get_voice_briefing(decision)
                        if briefing:
                            self.speak(briefing)
                
                time.sleep(update_interval)
                
            except Exception as e:
                self.log(f"❌ Error in analysis loop: {e}")
                time.sleep(5)
        
    def _update_market_display(self):
        """Update market information display"""
        try:
            market_data = self.trading_brain.data_engine.get_market_data()
            
            # Update price
            price = market_data['price']
            self.price_label.config(text=f"Price: ${price:,.2f}")
            
            # Update indicators if available
            indicators = self.trading_brain.technical_indicators.calculate_all(
                self.trading_brain.data_engine
            )
            
            if indicators:
                rsi = indicators['rsi']['value']
                rsi_color = '#ff4444' if rsi > 70 else '#00ff00' if rsi < 30 else '#ffffff'
                self.rsi_label.config(text=f"RSI: {rsi:.2f}", fg=rsi_color)
                
                signal = self.trading_brain.technical_indicators.generate_signal(
                    indicators, market_data
                )
                signal_text = f"Signal: {signal['type'] or 'NONE'} ({signal['strength']:.0f}%)"
                self.signal_label.config(text=signal_text)
                
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
        
        self.log("💰 22-Billion Hybrid AI Trading Coach")
        self.log("="*80)
        self.log("Welcome! Press START to begin market analysis.")
        self.log("")
        self.log("⚠️ Make sure you have:")
        self.log("  1. Created config.json from config.example.json")
        self.log("  2. Added your Binance and OpenAI API keys")
        self.log("  3. Installed TA-Lib properly (see README)")
        self.log("="*80)
        self.log("")
        
        self.root.mainloop()
    
    def _on_closing(self):
        """Handle window close event"""
        if self.running:
            if messagebox.askokcancel("Quit", "Trading system is running. Stop and quit?"):
                self.stop_trading()
                self.root.destroy()
        else:
            self.root.destroy()
