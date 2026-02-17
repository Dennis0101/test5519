"""
22-Billion: Data Engine
Handles real-time data collection from Binance Futures using ccxt and WebSocket
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
        
        # Data storage
        self.current_price = 0
        self.orderbook = {'bids': [], 'asks': []}
        self.klines = deque(maxlen=200)  # Store last 200 candles
        self.trades = deque(maxlen=100)
        
        # WebSocket
        self.ws = None
        self.ws_thread = None
        self.running = False
        
        # Volume analysis
        self.buy_volume = 0
        self.sell_volume = 0
        
    def start(self):
        """Start data collection"""
        print("🚀 Starting Data Engine...")
        self.running = True
        
        # Load initial historical data
        self._load_historical_data()
        
        # Start WebSocket connection
        self.ws_thread = threading.Thread(target=self._run_websocket, daemon=True)
        self.ws_thread.start()
        
        print("✅ Data Engine started successfully")
        
    def stop(self):
        """Stop data collection"""
        print("🛑 Stopping Data Engine...")
        self.running = False
        if self.ws:
            self.ws.close()
        print("✅ Data Engine stopped")
        
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
            
    def _run_websocket(self):
        """Run WebSocket connection for real-time data"""
        symbol = self.symbol.replace('/', '').lower()  # btcusdt
        
        # Binance Futures WebSocket streams
        streams = [
            f"{symbol}@aggTrade",      # Aggregated trades
            f"{symbol}@depth20@100ms", # Order book (20 levels, 100ms update)
            f"{symbol}@kline_{self.timeframe}"  # Klines
        ]
        
        ws_url = f"wss://fstream.binance.com/stream?streams={'/'.join(streams)}"
        
        def on_message(ws, message):
            try:
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
            if self.running:
                # Reconnect after 5 seconds
                time.sleep(5)
                self._run_websocket()
                
        def on_open(ws):
            print("🔗 WebSocket connected successfully")
            
        self.ws = websocket.WebSocketApp(
            ws_url,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open
        )
        
        self.ws.run_forever()
        
    def _handle_trade(self, data):
        """Handle aggregated trade data"""
        try:
            price = float(data['p'])
            quantity = float(data['q'])
            is_buyer_maker = data['m']  # True if buyer is maker (sell order)
            
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
        """Handle order book data"""
        try:
            self.orderbook = {
                'bids': [[float(bid[0]), float(bid[1])] for bid in data['b']],
                'asks': [[float(ask[0]), float(ask[1])] for ask in data['a']]
            }
        except Exception as e:
            print(f"❌ Error handling orderbook: {e}")
            
    def _handle_kline(self, data):
        """Handle kline/candlestick data"""
        try:
            kline = data['k']
            
            if kline['x']:  # Only add completed candles
                self.klines.append({
                    'timestamp': kline['t'],
                    'open': float(kline['o']),
                    'high': float(kline['h']),
                    'low': float(kline['l']),
                    'close': float(kline['c']),
                    'volume': float(kline['v'])
                })
                
                # Reset volume counters on new candle
                self.buy_volume = 0
                self.sell_volume = 0
                
        except Exception as e:
            print(f"❌ Error handling kline: {e}")
            
    def get_closes(self):
        """Get array of closing prices"""
        if len(self.klines) == 0:
            return np.array([])
        return np.array([k['close'] for k in self.klines])
    
    def get_highs(self):
        """Get array of high prices"""
        if len(self.klines) == 0:
            return np.array([])
        return np.array([k['high'] for k in self.klines])
    
    def get_lows(self):
        """Get array of low prices"""
        if len(self.klines) == 0:
            return np.array([])
        return np.array([k['low'] for k in self.klines])
    
    def get_volumes(self):
        """Get array of volumes"""
        if len(self.klines) == 0:
            return np.array([])
        return np.array([k['volume'] for k in self.klines])
    
    def get_orderbook_imbalance(self):
        """Calculate order book imbalance (buy wall vs sell wall)"""
        try:
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
        """Get buy/sell volume ratio"""
        total = self.buy_volume + self.sell_volume
        if total == 0:
            return 1.0
        return self.buy_volume / total
    
    def get_market_data(self):
        """Get current market data snapshot"""
        return {
            'price': self.current_price,
            'orderbook_imbalance': self.get_orderbook_imbalance(),
            'volume_ratio': self.get_volume_ratio(),
            'bid_ask_spread': self._get_spread(),
            'num_candles': len(self.klines)
        }
    
    def _get_spread(self):
        """Calculate bid-ask spread"""
        try:
            if self.orderbook['bids'] and self.orderbook['asks']:
                best_bid = self.orderbook['bids'][0][0]
                best_ask = self.orderbook['asks'][0][0]
                return (best_ask - best_bid) / best_bid * 100
        except:
            pass
        return 0
