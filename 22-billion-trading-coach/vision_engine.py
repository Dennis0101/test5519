"""
22-Billion: Vision Engine
Captures chart screenshots and analyzes visual patterns using GPT-4o-mini
"""

import cv2
import numpy as np
import base64
import io
import time
from datetime import datetime
from openai import OpenAI

# PIL ImageGrab with fallback for headless servers
try:
    from PIL import ImageGrab, Image
    PIL_AVAILABLE = True
except ImportError:
    from PIL import Image
    PIL_AVAILABLE = False
    print("⚠️ PIL ImageGrab not available (headless server). Screenshot capture disabled.")


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
        
        FIXED: Handles headless servers gracefully
        """
        if not self.enabled:
            return None
        
        if not PIL_AVAILABLE:
            print("⚠️ Screenshot capture not available (headless environment)")
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
        ENHANCED: Analyze chart pattern using GPT-4o-mini Vision
        
        Optimizations:
        - Resize to HD (1280x720) for cost & speed
        - Black screen detection
        - Enhanced analysis
        
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
            # OPTIMIZATION 1: Resize image for cost & speed (HD quality)
            optimized_image = self._optimize_image_for_ai(screenshot)
            if optimized_image is None:
                print("⚠️ Image optimization failed")
                return None
            
            # OPTIMIZATION 2: Black screen detection
            if not self._validate_image_content(optimized_image):
                print("❌ Invalid image detected (black screen or blank)")
                return {
                    'timestamp': datetime.now().isoformat(),
                    'analysis': '❌ 화면 확인 필요: 차트 화면이 검은색이거나 비어있습니다',
                    'error': 'black_screen_detected',
                    'model': self.model
                }
            
            # Convert optimized image to base64
            buffered = io.BytesIO()
            optimized_image.save(buffered, format="JPEG", quality=85)  # JPEG for smaller size
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            original_size = len(base64.b64encode(io.BytesIO(
                screenshot.tobytes()).getvalue()).decode()) / 1024
            optimized_size = len(img_base64) / 1024
            print(f"📊 Image optimized: {original_size:.1f}KB → {optimized_size:.1f}KB (saved {original_size - optimized_size:.1f}KB)")
            
            # OPTIMIZATION 3: Enhanced prompt with conservative persona
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
                                    "url": f"data:image/jpeg;base64,{img_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=800,
                temperature=0.2,  # Even lower for conservative analysis
            )
            
            analysis = response.choices[0].message.content
            
            self.last_analysis_time = current_time
            
            return {
                'timestamp': datetime.now().isoformat(),
                'analysis': analysis,
                'prompt': prompt,
                'model': self.model,
                'image_size_kb': optimized_size
            }
            
        except Exception as e:
            print(f"❌ Error analyzing chart: {e}")
            return None
    
    def _optimize_image_for_ai(self, image):
        """
        OPTIMIZATION 1: Resize image to optimal size for AI analysis
        
        Target: 1280x720 (HD) - Perfect balance of:
        - Cost efficiency (smaller = cheaper)
        - Speed (2x faster processing)
        - Quality (AI can still see patterns clearly)
        
        Args:
            image: PIL Image object
            
        Returns:
            Optimized PIL Image or None
        """
        try:
            # Target dimensions (HD)
            target_width = 1280
            target_height = 720
            
            # Get current dimensions
            current_width, current_height = image.size
            
            # Calculate aspect ratio
            aspect_ratio = current_width / current_height
            target_aspect = target_width / target_height
            
            # Resize maintaining aspect ratio
            if aspect_ratio > target_aspect:
                # Image is wider - fit to width
                new_width = target_width
                new_height = int(target_width / aspect_ratio)
            else:
                # Image is taller - fit to height
                new_height = target_height
                new_width = int(target_height * aspect_ratio)
            
            # Use high-quality Lanczos resampling
            resized = image.resize((new_width, new_height), Image.LANCZOS)
            
            print(f"🔧 Image resized: {current_width}x{current_height} → {new_width}x{new_height}")
            
            return resized
            
        except Exception as e:
            print(f"❌ Error optimizing image: {e}")
            return None
    
    def _validate_image_content(self, image):
        """
        OPTIMIZATION 2: Detect black/blank screens
        
        Prevents wasting API calls on:
        - Sleep mode (black screen)
        - Window covered/minimized
        - Screen saver
        - Monitor off
        
        Args:
            image: PIL Image object
            
        Returns:
            True if image is valid, False if black/blank
        """
        try:
            # Convert to numpy array
            img_array = np.array(image)
            
            # Calculate mean brightness (0-255)
            mean_brightness = np.mean(img_array)
            
            # Calculate standard deviation (how varied the pixels are)
            std_dev = np.std(img_array)
            
            # Thresholds
            MIN_BRIGHTNESS = 15  # Too dark = likely black screen
            MIN_STD_DEV = 10     # Too uniform = blank/solid color
            
            # Check if image is too dark
            if mean_brightness < MIN_BRIGHTNESS:
                print(f"⚠️ Image too dark: brightness={mean_brightness:.1f} (min {MIN_BRIGHTNESS})")
                return False
            
            # Check if image is too uniform (blank)
            if std_dev < MIN_STD_DEV:
                print(f"⚠️ Image too uniform: std_dev={std_dev:.1f} (min {MIN_STD_DEV})")
                return False
            
            print(f"✅ Image validated: brightness={mean_brightness:.1f}, variance={std_dev:.1f}")
            return True
            
        except Exception as e:
            print(f"❌ Error validating image: {e}")
            return True  # Fail-safe: allow image if validation fails
    
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
        
        prompt = f"""[PERSONA INJECTION - 읽고 체화하세요]
당신은 손실을 극도로 혐오하는 보수적인 헤지펀드 매니저입니다.
- 10년 경력, 연평균 35% 수익률 유지
- 손실 트레이드는 전체의 18%만 허용
- "의심스러우면 하지 않는다"가 철학
- 고객 자산 $500M 운용 중 - 실수는 직업 생명 종말

[중요한 임무]
당신의 판단 하나가 실제 돈의 손실로 이어집니다. 
95% 확신이 서지 않으면 ❌로 판단하세요.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**현재 알고리즘 신호:**
- 신호 타입: {signal_type}
- 신호 강도: {strength}/100
- 근거: {', '.join(reasons)}

**기술적 지표 현황:**
- RSI(14): {rsi['value']:.2f} (과매도: {rsi['oversold']}, 과매수: {rsi['overbought']})
- 볼린저 밴드: {bb['position']:.1f}% 위치 (0=하단, 100=상단)
- 이동평균: {ma['trend']} (Fast: {ma['fast']:.2f}, Slow: {ma['slow']:.2f})
- MACD: {macd['trend']} (히스토그램: {macd['histogram']:.4f})
- ATR: {atr['value']:.2f} ({atr['percentage']:.2f}%)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**[CRITICAL] 반드시 확인해야 할 사항:**

1. 📊 차트 패턴 분석
   - 추세선, 지지/저항, 헤드앤숄더, 삼각수렴
   - 쐐기형, 플래그, 페넌트 등

2. 🔍 숨겨진 다이버전스 탐지 (매우 중요!)
   - RSI/MACD와 가격의 괴리 확인
   - Bullish Divergence: 가격↓ but RSI↑ (매수 신호)
   - Bearish Divergence: 가격↑ but RSI↓ (매도 경고)
   - Hidden Divergence도 체크 (추세 지속 신호)

3. ⚠️ 함정 패턴 경계
   - 불스트랩 (Bull Trap): 가짜 돌파 후 급락
   - 베어트랩 (Bear Trap): 가짜 붕괴 후 반등
   - 위코프 (Wyckoff): 큰손의 물량 털기/모으기

4. 🎯 진입 타이밍
   - 지금 당장 들어가야 하는가?
   - 아니면 조정 기다려야 하는가?
   - 리스크 대비 보상이 충분한가?

5. 🛡️ 최악의 시나리오
   - 진입 후 즉시 -5% 하락한다면?
   - 손절 후 계속 떨어진다면 어디까지?
   - 이 자리가 "덫"일 가능성은?

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**⚠️ 답변 형식 (엄격히 준수):**

✅/❌ [진입 추천 여부]
- 패턴: [관찰된 주요 패턴]
- 다이버전스: [있음/없음 + 상세]
- 검증: [신호가 신뢰할 만한가?]
- 리스크: [구체적인 위험 요소]
- 함정가능성: [Bull/Bear Trap 여부]
- 손절가: [숫자만, 예: 91500]
- 목표가: [숫자만, 예: 93500]
- 종합: [20자 이내 최종 판단]

**[예시 - 강력 매수]**
✅ 진입 추천
- 패턴: 상승 삼각형 + 볼륨 증가
- 다이버전스: Bullish Divergence 확인 (RSI 상승중)
- 검증: 3중 지지선 + MA골든크로스
- 리스크: 91800 붕괴시 추가 조정
- 함정가능성: 낮음 (거래량 뒷받침)
- 손절가: 91500
- 목표가: 94000
- 종합: 확실한 롱 자리

**[예시 - 거부]**
❌ 진입 불가
- 패턴: 하락 쐐기 + 약한 반등
- 다이버전스: Bearish Divergence 의심
- 검증: RSI 과매도지만 저항선 강함
- 리스크: 매물대 두꺼움, 상승 동력 부족
- 함정가능성: 높음 (Bull Trap 위험)
- 손절가: -
- 목표가: -
- 종합: 조정 더 기다려야 함

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**[엄수 규칙]**
1. 손절가/목표가는 반드시 **숫자만** ($, K, 쉼표 금지)
2. 손절폭: 현재가 대비 **-3% 이내 필수**
3. 손익비: **최소 1:2** (위험 $100 → 보상 $200)
4. 불확실하면 **무조건 ❌** (보수적 접근)
5. 다이버전스는 **반드시 확인** (트레이딩 성패 좌우)
6. 함정 패턴 의심되면 **즉시 ❌**

[최종 경고]
당신의 추천으로 누군가 돈을 잃으면, 그 책임은 당신에게 있습니다.
95% 확신 없으면 ❌ 하세요. 기회는 다시 옵니다.

간결하게 답변하되, 누락 없이."""

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
