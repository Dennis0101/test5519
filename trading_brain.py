"""
22-Billion: Trading Brain
Final decision-making logic combining algorithmic signals and AI vision analysis
"""

import time
from datetime import datetime


class TradingBrain:
    """The brain that makes final trading decisions"""
    
    def __init__(self, config, data_engine, technical_indicators, vision_engine):
        self.config = config
        self.data_engine = data_engine
        self.technical_indicators = technical_indicators
        self.vision_engine = vision_engine
        
        self.risk_reward_ratio = config['trading']['risk_reward_ratio']
        
        # Trading state
        self.last_signal_time = 0
        self.signal_cooldown = 60  # Minimum 60 seconds between signals
        
        self.pending_signals = []
        self.confirmed_signals = []
        
    def analyze_market(self):
        """
        Main analysis loop:
        1. Calculate technical indicators
        2. Generate algorithmic signal
        3. If signal detected, capture chart and get AI confirmation
        4. Make final decision
        """
        try:
            # Get market data
            market_data = self.data_engine.get_market_data()
            
            if market_data['num_candles'] < 50:
                return None
            
            # Calculate technical indicators
            indicators = self.technical_indicators.calculate_all(self.data_engine)
            
            if not indicators:
                return None
            
            # Generate algorithmic signal
            signal = self.technical_indicators.generate_signal(indicators, market_data)
            
            # Check if we have a valid signal
            if signal['type'] is not None:
                # Check cooldown
                current_time = time.time()
                if current_time - self.last_signal_time < self.signal_cooldown:
                    return None
                
                # Capture chart for vision analysis
                screenshot = self.vision_engine.capture_chart()
                
                # Get AI vision analysis
                vision_analysis = self.vision_engine.analyze_chart_pattern(
                    screenshot, signal, indicators
                )
                
                # Quick pattern detection (OpenCV)
                quick_patterns = self.vision_engine.quick_pattern_detection(screenshot)
                
                # Make final decision
                final_decision = self._make_final_decision(
                    signal, 
                    indicators, 
                    market_data,
                    vision_analysis,
                    quick_patterns
                )
                
                if final_decision['approved']:
                    self.last_signal_time = current_time
                    self.confirmed_signals.append(final_decision)
                    
                    # Create annotated chart for logging
                    if screenshot:
                        annotated = self.vision_engine.create_annotated_chart(
                            screenshot, signal, indicators
                        )
                        if annotated:
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            annotated.save(f"signals/signal_{timestamp}.png")
                
                return final_decision
            
            return None
            
        except Exception as e:
            print(f"❌ Error in market analysis: {e}")
            return None
    
    def _make_final_decision(self, signal, indicators, market_data, vision_analysis, quick_patterns):
        """
        Combine all inputs to make final trading decision
        
        Decision criteria:
        1. Algorithmic signal strength >= 50
        2. Order book supports the direction
        3. AI vision analysis confirms (if available)
        4. Quick pattern detection doesn't contradict
        """
        current_price = market_data['price']
        signal_type = signal['type']
        signal_strength = signal['strength']
        
        # Initial approval based on algorithmic signal
        approved = signal_strength >= 50
        confidence = signal_strength
        
        reasons = list(signal['reasons'])
        risks = []
        
        # Check order book confirmation
        orderbook_imbalance = market_data['orderbook_imbalance']
        
        if signal_type == 'LONG':
            if orderbook_imbalance < -0.2:  # Strong sell wall
                confidence -= 15
                risks.append("Strong sell wall in order book")
            elif orderbook_imbalance > 0.2:  # Strong buy wall
                confidence += 10
                reasons.append("Order book supports long position")
        else:  # SHORT
            if orderbook_imbalance > 0.2:  # Strong buy wall
                confidence -= 15
                risks.append("Strong buy wall in order book")
            elif orderbook_imbalance < -0.2:  # Strong sell wall
                confidence += 10
                reasons.append("Order book supports short position")
        
        # Quick pattern check
        if quick_patterns:
            pattern_trend = quick_patterns.get('dominant_trend', 'neutral')
            
            if signal_type == 'LONG' and pattern_trend == 'bearish':
                confidence -= 10
                risks.append("Visual patterns show bearish trend")
            elif signal_type == 'SHORT' and pattern_trend == 'bullish':
                confidence -= 10
                risks.append("Visual patterns show bullish trend")
            elif signal_type == 'LONG' and pattern_trend == 'bullish':
                confidence += 5
                reasons.append("Visual patterns confirm bullish trend")
            elif signal_type == 'SHORT' and pattern_trend == 'bearish':
                confidence += 5
                reasons.append("Visual patterns confirm bearish trend")
        
        # AI Vision analysis (most important)
        ai_recommendation = None
        ai_stop_loss = None
        ai_take_profit = None
        
        if vision_analysis:
            analysis_text = vision_analysis['analysis']
            
            # Parse AI response
            if '✅' in analysis_text:
                ai_recommendation = 'APPROVE'
                confidence += 15
                reasons.append("AI Vision confirms entry")
            elif '❌' in analysis_text:
                ai_recommendation = 'REJECT'
                confidence -= 30
                risks.append("AI Vision rejects entry")
                approved = False
            
            # Try to extract stop loss and take profit from AI analysis
            ai_levels = self._extract_price_levels(analysis_text)
            if ai_levels:
                ai_stop_loss = ai_levels.get('stop_loss')
                ai_take_profit = ai_levels.get('take_profit')
        
        # Calculate stop loss and take profit
        position_sizing = self.technical_indicators.calculate_stop_loss_take_profit(
            current_price,
            signal_type,
            indicators['atr'],
            self.risk_reward_ratio
        )
        
        # Use AI levels if available and reasonable
        if ai_stop_loss and ai_take_profit:
            # Validate AI levels
            if signal_type == 'LONG':
                if ai_stop_loss < current_price < ai_take_profit:
                    position_sizing['stop_loss'] = ai_stop_loss
                    position_sizing['take_profit'] = ai_take_profit
                    reasons.append("Using AI-recommended levels")
            else:  # SHORT
                if ai_stop_loss > current_price > ai_take_profit:
                    position_sizing['stop_loss'] = ai_stop_loss
                    position_sizing['take_profit'] = ai_take_profit
                    reasons.append("Using AI-recommended levels")
        
        # Final approval check
        if confidence < 40:
            approved = False
            risks.append("Confidence too low after all checks")
        
        # Compile final decision
        decision = {
            'approved': approved,
            'timestamp': datetime.now().isoformat(),
            'signal_type': signal_type,
            'confidence': min(max(confidence, 0), 100),  # Clamp to 0-100
            'current_price': current_price,
            'entry_price': position_sizing['entry'],
            'stop_loss': position_sizing['stop_loss'],
            'take_profit': position_sizing['take_profit'],
            'risk_reward_ratio': position_sizing['risk_reward_ratio'],
            'reasons': reasons,
            'risks': risks,
            'indicators': {
                'rsi': indicators['rsi']['value'],
                'bb_position': indicators['bb']['position'],
                'ma_trend': indicators['ma']['trend'],
                'macd_histogram': indicators['macd']['histogram'],
            },
            'market_data': market_data,
            'ai_analysis': vision_analysis['analysis'] if vision_analysis else None,
            'ai_recommendation': ai_recommendation,
            'quick_patterns': quick_patterns,
        }
        
        return decision
    
    def _extract_price_levels(self, ai_text):
        """
        Extract stop loss and take profit prices from AI analysis
        Returns dict with 'stop_loss' and 'take_profit' or None
        """
        try:
            import re
            
            # Look for patterns like "손절가: 91500" or "목표가: 93000"
            stop_loss_match = re.search(r'손절가:?\s*[\$]?([0-9,]+(?:\.[0-9]+)?)', ai_text)
            take_profit_match = re.search(r'목표가:?\s*[\$]?([0-9,]+(?:\.[0-9]+)?)', ai_text)
            
            if stop_loss_match and take_profit_match:
                stop_loss = float(stop_loss_match.group(1).replace(',', ''))
                take_profit = float(take_profit_match.group(1).replace(',', ''))
                
                return {
                    'stop_loss': stop_loss,
                    'take_profit': take_profit
                }
            
            return None
            
        except Exception as e:
            print(f"⚠️ Error extracting price levels: {e}")
            return None
    
    def format_decision_summary(self, decision):
        """Format decision for display/logging"""
        if not decision:
            return "No signal"
        
        if not decision['approved']:
            return f"❌ Signal rejected - {', '.join(decision['risks'])}"
        
        summary = f"""
{'='*60}
🎯 22-BILLION TRADING SIGNAL
{'='*60}
신호: {decision['signal_type']} 
신뢰도: {decision['confidence']:.1f}%
현재가: ${decision['current_price']:,.2f}

진입가: ${decision['entry_price']:,.2f}
손절가: ${decision['stop_loss']:,.2f}
목표가: ${decision['take_profit']:,.2f}
손익비: 1:{decision['risk_reward_ratio']:.1f}

📊 기술적 지표:
- RSI: {decision['indicators']['rsi']:.2f}
- BB 위치: {decision['indicators']['bb_position']:.1f}%
- MA 추세: {decision['indicators']['ma_trend']}
- MACD: {decision['indicators']['macd_histogram']:.4f}

✅ 진입 근거:
{chr(10).join(f'  • {reason}' for reason in decision['reasons'])}

⚠️ 리스크 요인:
{chr(10).join(f'  • {risk}' for risk in decision['risks']) if decision['risks'] else '  • 없음'}

🤖 AI 분석:
{decision['ai_analysis'] if decision['ai_analysis'] else '  • 분석 없음'}

시간: {decision['timestamp']}
{'='*60}
"""
        return summary
    
    def get_voice_briefing(self, decision):
        """Generate voice briefing text"""
        if not decision or not decision['approved']:
            return None
        
        signal_type_ko = "롱" if decision['signal_type'] == 'LONG' else "숏"
        
        briefing = f"""
        주인님, 데이터와 차트 모두 {signal_type_ko} 포지션을 가리킵니다.
        신뢰도 {decision['confidence']:.0f}퍼센트입니다.
        진입가 {decision['entry_price']:,.0f}, 
        손절가 {decision['stop_loss']:,.0f}, 
        목표가 {decision['take_profit']:,.0f}입니다.
        승률 높은 자리입니다!
        """
        
        return briefing.strip()
