"""
22-Billion: Data Engine
Handles real-time data collection from Binance Futures using ccxt and WebSocket

ENHANCEMENTS:
- Zombie Mode: Auto-reconnect with heartbeat monitoring
- Thread Safety: Lock protection for race conditions
- Real-time Candle: Live updating of current candle
"""

import ccxt
import json
import threading
import time
from datetime import datetime
from collections import deque
import websocket
import numpy as np


class DataEngine:
    """Real-time market data engine using ccxt and WebSocket"""
    
    def __init__(self, config):
        self.config = config
        self.symbol = config['trading']['symbol']
        self.timeframe = config['trading']['timeframe']
        
        # Initialize Binance exchange
        self.exchange = ccxt.binance({
            'apiKey': config['binance']['api_key'],
            'secret': config['binance']['api_secret'],
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future',  # Use futures market
            }
        })
        
        if config['binance']['testnet']:
            self.exchange.set_sandbox_mode(True)
        
        # ENHANCEMENT 2: Thread Safety Lock (Race Condition Protection)
        self.data_lock = threading.Lock()
        
        # Data storage
        self.current_price = 0
        self.orderbook = {'bids': [], 'asks': []}
        self.klines = deque(maxlen=200)  # Store last 200 candles
        self.trades = deque(maxlen=100)
        
        # ENHANCEMENT 3: Current candle tracking
        self.current_candle = None  # Live updating candle
        
        # WebSocket
        self.ws = None
        self.ws_thread = None
        self.running = False
        
        # ENHANCEMENT 1: Heartbeat monitoring (Zombie Mode)
        self.last_data_time = time.time()
        self.heartbeat_interval = 5  # Alert if no data for 5 seconds
        self.heartbeat_thread = None
        self.reconnect_attempts = 0
        self.max_reconnect_delay = 60  # Max 60 seconds between reconnects
        
        # Volume analysis
        self.buy_volume = 0
        self.sell_volume = 0
        
    def start(self):
        """Start data collection with zombie mode enabled"""
        print("🚀 Starting Data Engine...")
        self.running = True
        self.reconnect_attempts = 0
        
        # Load initial historical data
        self._load_historical_data()
        
        # Start WebSocket connection (zombie mode - infinite retry)
        self.ws_thread = threading.Thread(target=self._run_websocket_zombie, daemon=True)
        self.ws_thread.start()
        
        # ENHANCEMENT 1: Start heartbeat monitor
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_monitor, daemon=True)
        self.heartbeat_thread.start()
        
        print("✅ Data Engine started successfully (Zombie Mode ON 🧟)")
        
    def stop(self):
        """Stop data collection"""
        print("🛑 Stopping Data Engine...")
        self.running = False
        if self.ws:
            self.ws.close()
        print("✅ Data Engine stopped")
    
    def change_timeframe(self, new_timeframe):
        """
        ENHANCEMENT v1.5.0: Dynamic timeframe change
        
        Safely changes timeframe while system is running.
        Like changing car wheels - must stop first!
        
        Args:
            new_timeframe: New timeframe string (e.g., '1m', '5m', '15m', '30m', '1h', '4h')
        
        Returns:
            True if successful, False otherwise
        """
        print(f"🔄 Changing timeframe: {self.timeframe} → {new_timeframe}")
        
        # Validate timeframe
        valid_timeframes = ['1m', '3m', '5m', '15m', '30m', '1h', '4h']
        if new_timeframe not in valid_timeframes:
            print(f"❌ Invalid timeframe: {new_timeframe}")
            return False
        
        if new_timeframe == self.timeframe:
            print(f"⚠️ Already using {new_timeframe}")
            return True
        
        try:
            # Save running state
            was_running = self.running
            
            # Step 1: Stop if running (safety first!)
            if was_running:
                print("🛑 Stopping data collection for timeframe change...")
                self.running = False
                if self.ws:
                    self.ws.close()
                time.sleep(1)  # Wait for threads to finish
            
            # Step 2: Clear old data
            with self.data_lock:
                print("🧹 Clearing old candle data...")
                self.klines.clear()
                self.current_candle = None
                self.buy_volume = 0
                self.sell_volume = 0
            
            # Step 3: Update timeframe
            self.timeframe = new_timeframe
            self.config['trading']['timeframe'] = new_timeframe
            print(f"✅ Timeframe updated to {new_timeframe}")
            
            # Step 4: Reload historical data for new timeframe
            print(f"📊 Loading historical data for {new_timeframe}...")
            self._load_historical_data()
            
            # Step 5: Restart if it was running before
            if was_running:
                print("🔄 Restarting data engine with new timeframe...")
                self.running = True
                self.reconnect_attempts = 0
                
                # Restart WebSocket thread
                self.ws_thread = threading.Thread(target=self._run_websocket_zombie, daemon=True)
                self.ws_thread.start()
                
                # Restart heartbeat if needed
                if not self.heartbeat_thread or not self.heartbeat_thread.is_alive():
                    self.heartbeat_thread = threading.Thread(target=self._heartbeat_monitor, daemon=True)
                    self.heartbeat_thread.start()
                
                print(f"✅ Data engine restarted with {new_timeframe}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error changing timeframe: {e}")
            return False
        
    def _load_historical_data(self):
        """Load initial historical klines data"""
        try:
            symbol_formatted = self.symbol.replace('/', '')
            ohlcv = self.exchange.fetch_ohlcv(self.symbol, self.timeframe, limit=200)
            
            for candle in ohlcv:
                timestamp, open_price, high, low, close, volume = candle
                self.klines.append({
                    'timestamp': timestamp,
                    'open': open_price,
                    'high': high,
                    'low': low,
                    'close': close,
                    'volume': volume
                })
            
            self.current_price = self.klines[-1]['close']
            print(f"📊 Loaded {len(self.klines)} historical candles. Current price: ${self.current_price:,.2f}")
            
        except Exception as e:
            print(f"❌ Error loading historical data: {e}")
            
    def _run_websocket_zombie(self):
        """
        ENHANCEMENT 1: Zombie Mode WebSocket (Never Dies!)
        
        Infinite loop with exponential backoff for reconnection.
        No recursion = No stack overflow risk.
        """
        symbol = self.symbol.replace('/', '').lower()  # btcusdt
        
        # Binance Futures WebSocket streams
        streams = [
            f"{symbol}@aggTrade",      # Aggregated trades
            f"{symbol}@depth20@100ms", # Order book (20 levels, 100ms update)
            f"{symbol}@kline_{self.timeframe}"  # Klines
        ]
        
        ws_url = f"wss://fstream.binance.com/stream?streams={'/'.join(streams)}"
        
        # ZOMBIE MODE: Infinite reconnection loop
        while self.running:
            try:
                print(f"🧟 Zombie Mode: Attempting connection (attempt #{self.reconnect_attempts + 1})")
                
                def on_message(ws, message):
                    try:
                        # Update heartbeat
                        self.last_data_time = time.time()
                        
                        data = json.loads(message)
                        stream = data.get('stream', '')
                        event_data = data.get('data', {})
                        
                        if 'aggTrade' in stream:
                            self._handle_trade(event_data)
                        elif 'depth' in stream:
                            self._handle_orderbook(event_data)
                        elif 'kline' in stream:
                            self._handle_kline(event_data)
                            
                    except Exception as e:
                        print(f"❌ WebSocket message error: {e}")
                        
                def on_error(ws, error):
                    print(f"❌ WebSocket error: {error}")
                    
                def on_close(ws, close_status_code, close_msg):
                    print(f"🔌 WebSocket closed: {close_msg}")
                    # Don't reconnect here - let zombie loop handle it
                    
                def on_open(ws):
                    print("🔗 WebSocket connected successfully")
                    self.reconnect_attempts = 0  # Reset on successful connection
                    
                self.ws = websocket.WebSocketApp(
                    ws_url,
                    on_message=on_message,
                    on_error=on_error,
                    on_close=on_close,
                    on_open=on_open
                )
                
                # This blocks until connection is lost
                self.ws.run_forever()
                
            except Exception as e:
                print(f"❌ WebSocket exception: {e}")
            
            # Connection lost - calculate backoff and reconnect
            if self.running:
                self.reconnect_attempts += 1
                
                # Exponential backoff: 1s, 2s, 4s, 8s, 16s, 32s, 60s (max)
                backoff_delay = min(2 ** (self.reconnect_attempts - 1), self.max_reconnect_delay)
                
                print(f"🧟 Zombie Mode: Reconnecting in {backoff_delay}s... (attempt #{self.reconnect_attempts})")
                time.sleep(backoff_delay)
            else:
                print("🛑 Zombie Mode: Shutting down gracefully")
                break
    
    def _heartbeat_monitor(self):
        """
        ENHANCEMENT 1: Heartbeat Monitor (CPR for WebSocket!)
        
        Checks if data is flowing. If not, performs CPR (reconnection).
        """
        print("❤️ Heartbeat monitor started")
        
        while self.running:
            time.sleep(self.heartbeat_interval)
            
            if not self.running:
                break
            
            # Check if data is flowing
            time_since_last_data = time.time() - self.last_data_time
            
            if time_since_last_data > self.heartbeat_interval:
                print(f"💔 FLATLINE DETECTED! No data for {time_since_last_data:.1f}s")
                print(f"🚑 Performing CPR (reconnection)...")
                
                # Force reconnection
                if self.ws:
                    try:
                        self.ws.close()
                    except:
                        pass
                
                # Reset heartbeat
                self.last_data_time = time.time()
        
        print("❤️ Heartbeat monitor stopped")
        
    def _handle_trade(self, data):
        """
        ENHANCEMENT 2: Thread-safe trade handler
        """
        try:
            price = float(data['p'])
            quantity = float(data['q'])
            is_buyer_maker = data['m']  # True if buyer is maker (sell order)
            
            # LOCK: Prevent race condition
            with self.data_lock:
                self.current_price = price
                
                # Track volume
                if is_buyer_maker:
                    self.sell_volume += quantity
                else:
                    self.buy_volume += quantity
                    
                self.trades.append({
                    'timestamp': data['T'],
                    'price': price,
                    'quantity': quantity,
                    'is_sell': is_buyer_maker
                })
            
        except Exception as e:
            print(f"❌ Error handling trade: {e}")
            
    def _handle_orderbook(self, data):
        """
        ENHANCEMENT 2: Thread-safe orderbook handler
        """
        try:
            # LOCK: Prevent race condition
            with self.data_lock:
                self.orderbook = {
                    'bids': [[float(bid[0]), float(bid[1])] for bid in data['b']],
                    'asks': [[float(ask[0]), float(ask[1])] for ask in data['a']]
                }
        except Exception as e:
            print(f"❌ Error handling orderbook: {e}")
            
    def _handle_kline(self, data):
        """
        ENHANCEMENT 2 & 3: Thread-safe + Real-time candle update
        
        Now updates BOTH completed candles AND current live candle!
        """
        try:
            kline = data['k']
            
            candle_data = {
                'timestamp': kline['t'],
                'open': float(kline['o']),
                'high': float(kline['h']),
                'low': float(kline['l']),
                'close': float(kline['c']),
                'volume': float(kline['v'])
            }
            
            # LOCK: Prevent race condition
            with self.data_lock:
                if kline['x']:
                    # Candle COMPLETED - add to history
                    self.klines.append(candle_data)
                    
                    # Reset current candle
                    self.current_candle = None
                    
                    # Reset volume counters on new candle
                    self.buy_volume = 0
                    self.sell_volume = 0
                    
                    print(f"📊 New candle completed: Close ${candle_data['close']:,.2f}")
                else:
                    # ENHANCEMENT 3: Candle UPDATING - track in real-time!
                    self.current_candle = candle_data
                    
                    # Also update last kline if exists (for smooth transitions)
                    if len(self.klines) > 0:
                        # Create a temporary merged view for analysis
                        # Last completed + current live = most accurate picture
                        pass  # Handled in get_closes() etc.
                
        except Exception as e:
            print(f"❌ Error handling kline: {e}")
            
    def get_closes(self):
        """
        ENHANCEMENT 2 & 3: Thread-safe + Include current live candle
        """
        with self.data_lock:
            if len(self.klines) == 0:
                return np.array([])
            
            closes = [k['close'] for k in self.klines]
            
            # ENHANCEMENT 3: Include current live candle!
            if self.current_candle:
                closes.append(self.current_candle['close'])
            
            return np.array(closes)
    
    def get_highs(self):
        """
        ENHANCEMENT 2 & 3: Thread-safe + Include current live candle
        """
        with self.data_lock:
            if len(self.klines) == 0:
                return np.array([])
            
            highs = [k['high'] for k in self.klines]
            
            # ENHANCEMENT 3: Include current live candle!
            if self.current_candle:
                highs.append(self.current_candle['high'])
            
            return np.array(highs)
    
    def get_lows(self):
        """
        ENHANCEMENT 2 & 3: Thread-safe + Include current live candle
        """
        with self.data_lock:
            if len(self.klines) == 0:
                return np.array([])
            
            lows = [k['low'] for k in self.klines]
            
            # ENHANCEMENT 3: Include current live candle!
            if self.current_candle:
                lows.append(self.current_candle['low'])
            
            return np.array(lows)
    
    def get_volumes(self):
        """
        ENHANCEMENT 2 & 3: Thread-safe + Include current live candle
        """
        with self.data_lock:
            if len(self.klines) == 0:
                return np.array([])
            
            volumes = [k['volume'] for k in self.klines]
            
            # ENHANCEMENT 3: Include current live candle!
            if self.current_candle:
                volumes.append(self.current_candle['volume'])
            
            return np.array(volumes)
    
    def get_orderbook_imbalance(self):
        """
        ENHANCEMENT 2: Thread-safe orderbook imbalance calculation
        """
        try:
            with self.data_lock:
                if not self.orderbook['bids'] or not self.orderbook['asks']:
                    return 0
                
                # Sum top 10 levels
                bid_volume = sum([bid[1] for bid in self.orderbook['bids'][:10]])
                ask_volume = sum([ask[1] for ask in self.orderbook['asks'][:10]])
                
                if ask_volume == 0:
                    return 1.0
                
                # Positive means more buying pressure
                imbalance = (bid_volume - ask_volume) / (bid_volume + ask_volume)
                return imbalance
            
        except Exception as e:
            print(f"❌ Error calculating orderbook imbalance: {e}")
            return 0
    
    def get_volume_ratio(self):
        """
        ENHANCEMENT 2: Thread-safe volume ratio
        """
        with self.data_lock:
            total = self.buy_volume + self.sell_volume
            if total == 0:
                return 1.0
            return self.buy_volume / total
    
    def get_market_data(self):
        """
        ENHANCEMENT 2: Thread-safe market data snapshot
        """
        with self.data_lock:
            return {
                'price': self.current_price,
                'orderbook_imbalance': self.get_orderbook_imbalance(),
                'volume_ratio': self.get_volume_ratio(),
                'bid_ask_spread': self._get_spread(),
                'num_candles': len(self.klines) + (1 if self.current_candle else 0),
                'has_live_candle': self.current_candle is not None
            }
    
    def _get_spread(self):
        """
        ENHANCEMENT 2: Thread-safe spread calculation
        """
        try:
            # Note: Already called within lock from get_market_data
            if self.orderbook['bids'] and self.orderbook['asks']:
                best_bid = self.orderbook['bids'][0][0]
                best_ask = self.orderbook['asks'][0][0]
                return (best_ask - best_bid) / best_bid * 100
        except:
            pass
        return 0
