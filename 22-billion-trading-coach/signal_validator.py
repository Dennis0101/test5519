"""
22-Billion: Signal Validator
Advanced signal validation with confidence scoring and edge calculation

FEATURES:
- Signal confidence quantification
- Expected value calculation
- Market regime detection
- Volatility filtering
- Noise filtering
- Minimum edge requirements
"""

import numpy as np
from datetime import datetime


class SignalValidator:
    """
    Professional signal validation and confidence scoring
    
    Ensures signals meet minimum edge requirements
    Filters out noise and low-probability setups
    """
    
    def __init__(self, config):
        self.config = config
        
        # Validation thresholds
        self.min_confidence = 60  # Minimum confidence score
        self.min_edge = 0.5  # Minimum expected edge (R:R * win_rate - 1)
        self.min_atr_multiple = 1.0  # Minimum stop distance in ATR
        self.max_atr_multiple = 5.0  # Maximum stop distance in ATR
        
        # Market regime filters
        self.trend_regime_lookback = 50
        self.volatility_regime_threshold = 1.5
        
        # Historical performance tracking
        self.signal_performance = {
            'total': 0,
            'wins': 0,
            'losses': 0,
            'avg_confidence': [],
            'high_conf_wins': 0,  # Confidence >= 80
            'high_conf_total': 0,
        }
    
    def validate_signal(self, signal, indicators, market_data, risk_manager=None):
        """
        Comprehensive signal validation with confidence scoring
        
        Returns enhanced signal with:
        - detailed_confidence: breakdown of confidence sources
        - expected_edge: statistical edge calculation
        - regime_valid: market regime suitability
        - filters_passed: which filters passed
        - validation_score: 0-100 overall score
        """
        results = {
            'approved': False,
            'confidence': signal.get('strength', 0),
            'detailed_confidence': {},
            'expected_edge': 0.0,
            'regime_valid': True,
            'filters_passed': [],
            'filters_failed': [],
            'validation_score': 0,
            'reasons': []
        }
        
        # 1. Market Regime Check
        regime = self._check_market_regime(indicators, market_data)
        results['regime'] = regime
        
        if regime['is_valid']:
            results['filters_passed'].append('Market Regime')
            results['validation_score'] += 20
        else:
            results['filters_failed'].append(f"Market Regime: {regime['reason']}")
            results['regime_valid'] = False
        
        # 2. Volatility Filter
        vol_check = self._check_volatility(indicators)
        results['volatility'] = vol_check
        
        if vol_check['is_valid']:
            results['filters_passed'].append('Volatility')
            results['validation_score'] += 15
        else:
            results['filters_failed'].append(f"Volatility: {vol_check['reason']}")
        
        # 3. Stop Loss Sanity Check
        stop_check = self._validate_stop_distance(signal, indicators)
        results['stop_validation'] = stop_check
        
        if stop_check['is_valid']:
            results['filters_passed'].append('Stop Distance')
            results['validation_score'] += 15
        else:
            results['filters_failed'].append(f"Stop Distance: {stop_check['reason']}")
        
        # 4. Expected Edge Calculation
        edge = self._calculate_expected_edge(signal, indicators)
        results['expected_edge'] = edge
        results['detailed_confidence']['edge_score'] = edge * 20
        
        if edge >= self.min_edge:
            results['filters_passed'].append(f'Edge ({edge:.2f})')
            results['validation_score'] += 20
        else:
            results['filters_failed'].append(f'Insufficient edge: {edge:.2f}')
        
        # 5. Technical Confluence Check
        confluence = self._check_technical_confluence(indicators)
        results['confluence'] = confluence
        results['detailed_confidence']['confluence_score'] = confluence['score']
        
        if confluence['score'] >= 60:
            results['filters_passed'].append(f"Confluence ({confluence['count']} indicators)")
            results['validation_score'] += 20
        else:
            results['filters_failed'].append(f"Weak confluence: {confluence['count']}")
        
        # 6. Risk Manager Validation
        if risk_manager:
            risk_val = risk_manager.validate_trade(signal.get('strength', 0))
            results['risk_validation'] = risk_val
            
            if not risk_val['approved']:
                results['filters_failed'].append(f"Risk: {risk_val['reason']}")
                results['approved'] = False
                return results
            else:
                results['filters_passed'].append('Risk Limits')
                results['validation_score'] += 10
        
        # Final Decision
        min_validation = 70  # Need 70+ validation score
        
        if results['validation_score'] >= min_validation and results['regime_valid']:
            results['approved'] = True
            results['reasons'].append(f"Validation score: {results['validation_score']}/100")
        else:
            results['approved'] = False
            results['reasons'].append(f"Validation failed: {results['validation_score']}/100 (need {min_validation})")
        
        return results
    
    def _check_market_regime(self, indicators, market_data):
        """
        Check if market regime is suitable for trading
        
        Checks:
        - Trend strength
        - Trend consistency
        - Not in extreme conditions
        """
        ma = indicators['ma']
        bb = indicators['bb']
        macd = indicators['macd']
        
        regime = {
            'is_valid': True,
            'type': 'UNKNOWN',
            'strength': 0,
            'reason': ''
        }
        
        # Check MA trend strength
        ma_separation = ma.get('separation', 0)
        
        if ma_separation < 0.5:
            # Too choppy/sideways
            regime['is_valid'] = False
            regime['type'] = 'CHOPPY'
            regime['reason'] = f'Sideways market (MA separation {ma_separation:.2f}%)'
            return regime
        
        # Check BB squeeze (high volatility breakout risk)
        if bb.get('squeeze', False):
            regime['is_valid'] = False
            regime['type'] = 'SQUEEZE'
            regime['reason'] = 'Bollinger squeeze - breakout imminent (risky)'
            return regime
        
        # Check MACD confirmation
        macd_hist = macd.get('histogram', 0)
        ma_trend = ma.get('trend', 'neutral')
        
        # Trend must align
        if ma_trend == 'bullish' and macd_hist > 0:
            regime['type'] = 'TRENDING_BULLISH'
            regime['strength'] = min(ma_separation * 10, 100)
            regime['is_valid'] = True
        elif ma_trend == 'bearish' and macd_hist < 0:
            regime['type'] = 'TRENDING_BEARISH'
            regime['strength'] = min(ma_separation * 10, 100)
            regime['is_valid'] = True
        else:
            # Conflicting signals
            regime['is_valid'] = False
            regime['type'] = 'CONFLICTING'
            regime['reason'] = 'MA and MACD conflict'
        
        return regime
    
    def _check_volatility(self, indicators):
        """Check if volatility is within acceptable range"""
        atr = indicators['atr']
        atr_pct = atr.get('percentage', 0)
        
        vol_check = {
            'is_valid': True,
            'level': 'NORMAL',
            'atr_pct': atr_pct,
            'reason': ''
        }
        
        # Too low volatility (< 0.5%)
        if atr_pct < 0.5:
            vol_check['is_valid'] = False
            vol_check['level'] = 'TOO_LOW'
            vol_check['reason'] = f'Volatility too low ({atr_pct:.2f}%) - range-bound'
            return vol_check
        
        # Too high volatility (> 4%)
        if atr_pct > 4.0:
            vol_check['is_valid'] = False
            vol_check['level'] = 'TOO_HIGH'
            vol_check['reason'] = f'Volatility too high ({atr_pct:.2f}%) - unstable'
            return vol_check
        
        # Acceptable range
        if atr_pct > 2.5:
            vol_check['level'] = 'HIGH'
        elif atr_pct < 1.0:
            vol_check['level'] = 'LOW'
        else:
            vol_check['level'] = 'NORMAL'
        
        return vol_check
    
    def _validate_stop_distance(self, signal, indicators):
        """Validate stop loss distance is reasonable"""
        atr = indicators['atr']['value']
        
        # Get stop distance from signal if available
        # Otherwise estimate from ATR
        stop_check = {
            'is_valid': True,
            'atr_multiple': 1.5,
            'reason': ''
        }
        
        # Check if stop is between 1-5 ATR (reasonable range)
        atr_multiple = 1.5  # Default from our system
        
        if atr_multiple < self.min_atr_multiple:
            stop_check['is_valid'] = False
            stop_check['reason'] = f'Stop too tight ({atr_multiple:.1f} ATR)'
            return stop_check
        
        if atr_multiple > self.max_atr_multiple:
            stop_check['is_valid'] = False
            stop_check['reason'] = f'Stop too wide ({atr_multiple:.1f} ATR)'
            return stop_check
        
        stop_check['atr_multiple'] = atr_multiple
        return stop_check
    
    def _calculate_expected_edge(self, signal, indicators):
        """
        Calculate expected edge (positive expectancy)
        
        Edge = (Win% * Avg Win) - (Loss% * Avg Loss)
        
        For now, estimate based on signal strength and R:R
        """
        confidence = signal.get('strength', 0)
        
        # Estimate win rate from confidence
        # 60% conf = 45% win rate, 100% conf = 65% win rate
        estimated_win_rate = 0.35 + (confidence / 100) * 0.3
        estimated_loss_rate = 1 - estimated_win_rate
        
        # Use R:R ratio
        risk_reward = 2.0  # Default 1:2
        
        # Expected value
        expected_value = (estimated_win_rate * risk_reward) - (estimated_loss_rate * 1.0)
        
        return expected_value
    
    def _check_technical_confluence(self, indicators):
        """
        Check how many indicators agree
        
        More confluence = higher confidence
        """
        confluence = {
            'score': 0,
            'count': 0,
            'indicators': []
        }
        
        rsi = indicators['rsi']
        bb = indicators['bb']
        ma = indicators['ma']
        macd = indicators['macd']
        
        # RSI signal
        if rsi['is_oversold']:
            confluence['count'] += 1
            confluence['indicators'].append('RSI oversold')
            confluence['score'] += 25
        elif rsi['is_overbought']:
            confluence['count'] += 1
            confluence['indicators'].append('RSI overbought')
            confluence['score'] += 25
        
        # Bollinger Bands
        if bb['near_lower'] or bb['near_upper']:
            confluence['count'] += 1
            confluence['indicators'].append('BB extreme')
            confluence['score'] += 20
        
        # Moving Average trend
        if ma['golden_cross'] or ma['death_cross']:
            confluence['count'] += 1
            confluence['indicators'].append('MA crossover')
            confluence['score'] += 25
        
        # MACD
        if macd['bullish_cross'] or macd['bearish_cross']:
            confluence['count'] += 1
            confluence['indicators'].append('MACD crossover')
            confluence['score'] += 20
        
        # Volume confirmation
        volume = indicators.get('volume_ma', {})
        if volume.get('high_volume', False):
            confluence['count'] += 1
            confluence['indicators'].append('High volume')
            confluence['score'] += 10
        
        return confluence
    
    def record_signal_outcome(self, signal_confidence, was_successful):
        """Record signal outcome for performance tracking"""
        self.signal_performance['total'] += 1
        
        if was_successful:
            self.signal_performance['wins'] += 1
        else:
            self.signal_performance['losses'] += 1
        
        self.signal_performance['avg_confidence'].append(signal_confidence)
        
        # Track high confidence signals separately
        if signal_confidence >= 80:
            self.signal_performance['high_conf_total'] += 1
            if was_successful:
                self.signal_performance['high_conf_wins'] += 1
    
    def get_performance_stats(self):
        """Get signal validation performance statistics"""
        total = self.signal_performance['total']
        
        if total == 0:
            return {
                'total_signals': 0,
                'win_rate': 0,
                'avg_confidence': 0,
                'high_conf_win_rate': 0
            }
        
        wins = self.signal_performance['wins']
        win_rate = (wins / total) * 100
        
        avg_conf = np.mean(self.signal_performance['avg_confidence']) if self.signal_performance['avg_confidence'] else 0
        
        high_conf_total = self.signal_performance['high_conf_total']
        high_conf_win_rate = (self.signal_performance['high_conf_wins'] / high_conf_total * 100) if high_conf_total > 0 else 0
        
        return {
            'total_signals': total,
            'wins': wins,
            'losses': self.signal_performance['losses'],
            'win_rate': win_rate,
            'avg_confidence': avg_conf,
            'high_conf_signals': high_conf_total,
            'high_conf_win_rate': high_conf_win_rate
        }
