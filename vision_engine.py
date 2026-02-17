"""
22-Billion: Vision Engine
Captures chart screenshots and analyzes visual patterns using GPT-4o-mini
"""

import cv2
import numpy as np
from PIL import ImageGrab, Image
import base64
import io
import time
from datetime import datetime
from openai import OpenAI


class VisionEngine:
    """Chart capture and AI visual analysis engine"""
    
    def __init__(self, config):
        self.config = config
        self.vision_config = config['vision']
        self.openai_config = config['openai']
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.openai_config['api_key'])
        self.model = self.openai_config['model']
        
        self.enabled = self.vision_config['chart_capture_enabled']
        self.screen_region = self.vision_config['screen_region']
        
        self.last_analysis_time = 0
        self.analysis_interval = self.vision_config['analysis_interval']
        
    def capture_chart(self, save_path=None):
        """
        Capture chart from screen
        If screen_region is None, captures entire screen
        screen_region format: (x, y, width, height)
        """
        if not self.enabled:
            return None
        
        try:
            # Capture screenshot
            if self.screen_region:
                x, y, w, h = self.screen_region
                screenshot = ImageGrab.grab(bbox=(x, y, x+w, y+h))
            else:
                screenshot = ImageGrab.grab()
            
            # Save if path provided
            if save_path:
                screenshot.save(save_path)
                print(f"📸 Chart saved to {save_path}")
            
            return screenshot
            
        except Exception as e:
            print(f"❌ Error capturing chart: {e}")
            return None
    
    def analyze_chart_pattern(self, screenshot, signal_data, indicators):
        """
        Analyze chart pattern using GPT-4o-mini Vision
        
        Args:
            screenshot: PIL Image object
            signal_data: Signal information from technical indicators
            indicators: Technical indicator values
            
        Returns:
            Analysis result with AI recommendation
        """
        if not self.enabled or screenshot is None:
            return None
        
        # Rate limiting
        current_time = time.time()
        if current_time - self.last_analysis_time < self.analysis_interval:
            return None
        
        try:
            # Convert image to base64
            buffered = io.BytesIO()
            screenshot.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            # Prepare prompt
            prompt = self._create_analysis_prompt(signal_data, indicators)
            
            # Call GPT-4o-mini Vision API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{img_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=800,
                temperature=0.3,  # Lower temperature for more consistent analysis
            )
            
            analysis = response.choices[0].message.content
            
            self.last_analysis_time = current_time
            
            return {
                'timestamp': datetime.now().isoformat(),
                'analysis': analysis,
                'prompt': prompt,
                'model': self.model
            }
            
        except Exception as e:
            print(f"❌ Error analyzing chart: {e}")
            return None
    
    def _create_analysis_prompt(self, signal_data, indicators):
        """Create detailed prompt for GPT-4o-mini"""
        
        signal_type = signal_data.get('type', 'None')
        strength = signal_data.get('strength', 0)
        reasons = signal_data.get('reasons', [])
        
        rsi = indicators['rsi']
        bb = indicators['bb']
        ma = indicators['ma']
        macd = indicators['macd']
        atr = indicators['atr']
        
        prompt = f"""당신은 월가 헤지펀드의 수석 차티스트입니다. 아래 차트와 기술적 지표를 분석하여 트레이딩 판단을 내려주세요.

**현재 알고리즘 신호:**
- 신호 타입: {signal_type}
- 신호 강도: {strength}/100
- 근거: {', '.join(reasons)}

**기술적 지표 현황:**
- RSI(14): {rsi['value']:.2f} (과매도선: {rsi['oversold']}, 과매수선: {rsi['overbought']})
- 볼린저 밴드: 현재가 위치 {bb['position']:.1f}% (0=하단, 100=상단)
- 이동평균: {ma['trend']} 트렌드 (Fast: {ma['fast']:.2f}, Slow: {ma['slow']:.2f})
- MACD: {macd['trend']} (히스토그램: {macd['histogram']:.4f})
- ATR: {atr['value']:.2f} ({atr['percentage']:.2f}%)

**분석 요청사항:**
1. 차트 패턴 분석: 추세선, 지지/저항, 헤드앤숄더, 삼각수렴 등 시각적 패턴이 보이나요?
2. 알고리즘 신호 검증: 위 신호가 차트 패턴상으로도 타당한가요?
3. 리스크 평가: 현재 진입시 주요 리스크는 무엇인가요?
4. 손익비 최적화: 손절가와 목표가를 어디로 설정해야 1:2 이상의 손익비가 나올까요?
5. 최종 판단: 진입 추천/비추천 및 그 이유

**답변 형식:**
✅/❌ [진입 추천 여부]
- 패턴: [관찰된 패턴]
- 검증: [신호 타당성]
- 리스크: [주요 리스크 요인]
- 손절가: [구체적 가격]
- 목표가: [구체적 가격]
- 종합: [30자 이내 최종 판단]

간결하고 명확하게 답변해 주세요."""

        return prompt
    
    def quick_pattern_detection(self, screenshot):
        """
        Quick pattern detection using OpenCV (without AI)
        Detects basic visual patterns like trend lines, support/resistance
        """
        if screenshot is None:
            return {}
        
        try:
            # Convert PIL to OpenCV format
            img_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            
            # Edge detection
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            
            # Line detection using Hough Transform
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100,
                                   minLineLength=100, maxLineGap=10)
            
            if lines is None:
                return {'lines_detected': 0}
            
            # Analyze line angles
            angles = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
                angles.append(angle)
            
            angles = np.array(angles)
            
            # Classify trends
            uptrend_lines = np.sum((angles > 10) & (angles < 80))
            downtrend_lines = np.sum((angles < -10) & (angles > -80))
            horizontal_lines = np.sum(np.abs(angles) < 10)
            
            return {
                'lines_detected': len(lines),
                'uptrend_lines': int(uptrend_lines),
                'downtrend_lines': int(downtrend_lines),
                'horizontal_lines': int(horizontal_lines),
                'dominant_trend': self._determine_dominant_trend(uptrend_lines, downtrend_lines)
            }
            
        except Exception as e:
            print(f"❌ Error in quick pattern detection: {e}")
            return {}
    
    def _determine_dominant_trend(self, uptrend, downtrend):
        """Determine dominant trend from line analysis"""
        if uptrend > downtrend * 1.5:
            return 'bullish'
        elif downtrend > uptrend * 1.5:
            return 'bearish'
        else:
            return 'neutral'
    
    def create_annotated_chart(self, screenshot, signal_data, indicators):
        """
        Create annotated chart with technical levels
        (Optional: for debugging or logging purposes)
        """
        if screenshot is None:
            return None
        
        try:
            img_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # Add text annotations
            font = cv2.FONT_HERSHEY_SIMPLEX
            y_offset = 30
            
            # Signal info
            signal_text = f"Signal: {signal_data.get('type', 'None')} ({signal_data.get('strength', 0)}%)"
            cv2.putText(img_cv, signal_text, (10, y_offset), font, 0.7, (0, 255, 0), 2)
            
            y_offset += 30
            
            # RSI
            rsi = indicators['rsi']
            rsi_text = f"RSI: {rsi['value']:.2f}"
            color = (0, 0, 255) if rsi['is_oversold'] else (255, 0, 0) if rsi['is_overbought'] else (255, 255, 255)
            cv2.putText(img_cv, rsi_text, (10, y_offset), font, 0.7, color, 2)
            
            y_offset += 30
            
            # Trend
            ma = indicators['ma']
            trend_text = f"Trend: {ma['trend'].upper()}"
            cv2.putText(img_cv, trend_text, (10, y_offset), font, 0.7, (255, 255, 255), 2)
            
            # Convert back to PIL
            annotated = Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))
            
            return annotated
            
        except Exception as e:
            print(f"❌ Error creating annotated chart: {e}")
            return screenshot
