"""
22-Billion: Technical Indicators
TA-Lib wrapper for calculating RSI, Bollinger Bands, Moving Averages, MACD
"""

import numpy as np
import talib


class TechnicalIndicators:
    """Calculate technical indicators using TA-Lib"""
    
    def __init__(self, config):
        self.config = config
        self.ind_config = config['indicators']
        
    def calculate_all(self, data_engine):
        """Calculate all technical indicators"""
        closes = data_engine.get_closes()
        highs = data_engine.get_highs()
        lows = data_engine.get_lows()
        volumes = data_engine.get_volumes()
        
        if len(closes) < 50:  # Need minimum data
            return None
        
        try:
            indicators = {
                'rsi': self._calculate_rsi(closes),
                'bb': self._calculate_bollinger_bands(closes),
                'ma': self._calculate_moving_averages(closes),
                'macd': self._calculate_macd(closes),
                'volume_ma': self._calculate_volume_ma(volumes),
                'atr': self._calculate_atr(highs, lows, closes),
            }
            
            return indicators
            
        except Exception as e:
            print(f"❌ Error calculating indicators: {e}")
            return None
    
    def _calculate_rsi(self, closes):
        """Calculate Relative Strength Index"""
        period = self.ind_config['rsi_period']
        rsi_values = talib.RSI(closes, timeperiod=period)
        
        return {
            'value': rsi_values[-1],
            'previous': rsi_values[-2] if len(rsi_values) > 1 else rsi_values[-1],
            'oversold': self.ind_config['rsi_oversold'],
            'overbought': self.ind_config['rsi_overbought'],
            'is_oversold': rsi_values[-1] < self.ind_config['rsi_oversold'],
            'is_overbought': rsi_values[-1] > self.ind_config['rsi_overbought'],
        }
    
    def _calculate_bollinger_bands(self, closes):
        """Calculate Bollinger Bands"""
        period = self.ind_config['bb_period']
        std = self.ind_config['bb_std']
        
        upper, middle, lower = talib.BBANDS(
            closes,
            timeperiod=period,
            nbdevup=std,
            nbdevdn=std,
            matype=0
        )
        
        current_price = closes[-1]
        bb_width = (upper[-1] - lower[-1]) / middle[-1] * 100
        
        # Calculate position within bands (0 = lower, 50 = middle, 100 = upper)
        bb_position = ((current_price - lower[-1]) / (upper[-1] - lower[-1]) * 100) if upper[-1] != lower[-1] else 50
        
        return {
            'upper': upper[-1],
            'middle': middle[-1],
            'lower': lower[-1],
            'width': bb_width,
            'position': bb_position,
            'squeeze': bb_width < 2,  # Squeeze when width < 2%
            'near_lower': current_price < lower[-1] * 1.005,  # Within 0.5% of lower
            'near_upper': current_price > upper[-1] * 0.995,  # Within 0.5% of upper
        }
    
    def _calculate_moving_averages(self, closes):
        """Calculate fast and slow moving averages"""
        fast_period = self.ind_config['ma_fast']
        slow_period = self.ind_config['ma_slow']
        
        ma_fast = talib.EMA(closes, timeperiod=fast_period)
        ma_slow = talib.EMA(closes, timeperiod=slow_period)
        
        # Golden cross / Death cross
        current_cross = ma_fast[-1] > ma_slow[-1]
        previous_cross = ma_fast[-2] > ma_slow[-2] if len(ma_fast) > 1 else current_cross
        
        golden_cross = (not previous_cross) and current_cross
        death_cross = previous_cross and (not current_cross)
        
        return {
            'fast': ma_fast[-1],
            'slow': ma_slow[-1],
            'trend': 'bullish' if ma_fast[-1] > ma_slow[-1] else 'bearish',
            'golden_cross': golden_cross,
            'death_cross': death_cross,
            'separation': abs(ma_fast[-1] - ma_slow[-1]) / ma_slow[-1] * 100
        }
    
    def _calculate_macd(self, closes):
        """Calculate MACD (Moving Average Convergence Divergence)"""
        fast = self.ind_config['macd_fast']
        slow = self.ind_config['macd_slow']
        signal = self.ind_config['macd_signal']
        
        macd_line, signal_line, histogram = talib.MACD(
            closes,
            fastperiod=fast,
            slowperiod=slow,
            signalperiod=signal
        )
        
        # Detect crossovers
        current_cross = macd_line[-1] > signal_line[-1]
        previous_cross = macd_line[-2] > signal_line[-2] if len(macd_line) > 1 else current_cross
        
        bullish_cross = (not previous_cross) and current_cross
        bearish_cross = previous_cross and (not current_cross)
        
        return {
            'macd': macd_line[-1],
            'signal': signal_line[-1],
            'histogram': histogram[-1],
            'bullish_cross': bullish_cross,
            'bearish_cross': bearish_cross,
            'trend': 'bullish' if histogram[-1] > 0 else 'bearish',
        }
    
    def _calculate_volume_ma(self, volumes):
        """Calculate volume moving average"""
        if len(volumes) < 20:
            return {'ratio': 1.0}
        
        volume_ma = talib.SMA(volumes, timeperiod=20)
        current_volume = volumes[-1]
        
        return {
            'current': current_volume,
            'ma': volume_ma[-1],
            'ratio': current_volume / volume_ma[-1] if volume_ma[-1] > 0 else 1.0,
            'high_volume': current_volume > volume_ma[-1] * 1.5,
        }
    
    def _calculate_atr(self, highs, lows, closes):
        """Calculate Average True Range (for stop loss calculation)"""
        atr = talib.ATR(highs, lows, closes, timeperiod=14)
        return {
            'value': atr[-1],
            'percentage': atr[-1] / closes[-1] * 100
        }
    
    def generate_signal(self, indicators, market_data):
        """
        Generate trading signal based on indicators and market data
        Returns: {'type': 'LONG'/'SHORT'/None, 'strength': 0-100, 'reasons': []}
        """
        if not indicators:
            return {'type': None, 'strength': 0, 'reasons': []}
        
        rsi = indicators['rsi']
        bb = indicators['bb']
        ma = indicators['ma']
        macd = indicators['macd']
        volume = indicators['volume_ma']
        
        orderbook_imbalance = market_data['orderbook_imbalance']
        
        # Scoring system
        long_score = 0
        short_score = 0
        reasons = []
        
        # RSI signals (30 points max)
        if rsi['is_oversold']:
            long_score += 30
            reasons.append(f"RSI oversold ({rsi['value']:.1f})")
        elif rsi['is_overbought']:
            short_score += 30
            reasons.append(f"RSI overbought ({rsi['value']:.1f})")
        
        # Bollinger Bands (25 points max)
        if bb['near_lower']:
            long_score += 25
            reasons.append("Price near lower Bollinger Band")
        elif bb['near_upper']:
            short_score += 25
            reasons.append("Price near upper Bollinger Band")
        
        # Moving Average trend (20 points max)
        if ma['trend'] == 'bullish':
            long_score += 20
            reasons.append(f"MA trend bullish (separation {ma['separation']:.2f}%)")
        else:
            short_score += 20
            reasons.append(f"MA trend bearish (separation {ma['separation']:.2f}%)")
        
        # MACD signals (15 points max)
        if macd['bullish_cross']:
            long_score += 15
            reasons.append("MACD bullish crossover")
        elif macd['bearish_cross']:
            short_score += 15
            reasons.append("MACD bearish crossover")
        elif macd['trend'] == 'bullish':
            long_score += 8
        else:
            short_score += 8
        
        # Order book imbalance (10 points max)
        if orderbook_imbalance > 0.3:  # Strong buy wall
            long_score += 10
            reasons.append(f"Strong buy wall (imbalance {orderbook_imbalance:.2f})")
        elif orderbook_imbalance < -0.3:  # Strong sell wall
            short_score += 10
            reasons.append(f"Strong sell wall (imbalance {orderbook_imbalance:.2f})")
        
        # High volume confirmation (bonus)
        if volume['high_volume']:
            if long_score > short_score:
                long_score += 5
                reasons.append(f"High volume confirmation ({volume['ratio']:.2f}x)")
            else:
                short_score += 5
                reasons.append(f"High volume confirmation ({volume['ratio']:.2f}x)")
        
        # Determine signal
        if long_score >= 50:  # Minimum 50 points for signal
            return {
                'type': 'LONG',
                'strength': min(long_score, 100),
                'reasons': reasons,
                'indicators': indicators
            }
        elif short_score >= 50:
            return {
                'type': 'SHORT',
                'strength': min(short_score, 100),
                'reasons': reasons,
                'indicators': indicators
            }
        else:
            return {
                'type': None,
                'strength': max(long_score, short_score),
                'reasons': ['Signal strength insufficient'],
                'indicators': indicators
            }
    
    def calculate_stop_loss_take_profit(self, entry_price, signal_type, atr, risk_reward_ratio=2.0):
        """
        Calculate stop loss and take profit levels
        """
        # Use ATR for stop loss distance (1.5x ATR)
        stop_distance = atr['value'] * 1.5
        
        if signal_type == 'LONG':
            stop_loss = entry_price - stop_distance
            take_profit = entry_price + (stop_distance * risk_reward_ratio)
        else:  # SHORT
            stop_loss = entry_price + stop_distance
            take_profit = entry_price - (stop_distance * risk_reward_ratio)
        
        return {
            'entry': entry_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'risk': abs(entry_price - stop_loss),
            'reward': abs(take_profit - entry_price),
            'risk_reward_ratio': risk_reward_ratio
        }
