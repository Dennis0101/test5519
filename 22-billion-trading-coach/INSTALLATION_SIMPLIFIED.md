# 🚀 22-Billion - 초간단 설치 가이드 (5분 완성)

## 1단계: Python 패키지 설치 (1분)

```bash
pip install -r requirements.txt
```

## 2단계: TA-Lib 설치 (3분)

### Windows
1. https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
2. 본인 Python 버전에 맞는 .whl 다운로드
3. `pip install TA_Lib-0.4.28-cp311-cp311-win_amd64.whl`

### macOS
```bash
brew install ta-lib
pip install TA-Lib
```

### Linux
```bash
sudo apt-get update
sudo apt-get install build-essential wget
cd /tmp
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
pip install TA-Lib
```

## 3단계: API 키 설정 (1분)

```bash
cp config.example.json config.json
nano config.json  # 또는 메모장으로 열기
```

**필수 입력 3가지:**
1. Binance API key (테스트넷: https://testnet.binancefuture.com)
2. Binance API secret
3. OpenAI API key (https://platform.openai.com/api-keys)

```json
{
  "binance": {
    "api_key": "여기에_입력",
    "api_secret": "여기에_입력",
    "testnet": true
  },
  "openai": {
    "api_key": "여기에_입력"
  }
}
```

## 4단계: 실행! (1초)

```bash
python main.py
```

## 5단계: 사용법 (초간단)

1. **ENGAGE** 버튼 클릭
2. 상태등 확인: ●API ●DATA ●AI (모두 초록색이면 정상)
3. 뉴스/시장 패널 자동 업데이트 확인
4. 신호 모니터링 (한 줄 요약으로 표시)
5. **스페이스바** = 긴급 정지 (언제든지!)

---

## ⚡ 빠른 체크리스트

- [ ] `pip install -r requirements.txt` 완료
- [ ] TA-Lib 설치 완료
- [ ] `python test_imports.py` 실행 → 모두 ✅
- [ ] config.json 생성 및 API 키 입력
- [ ] `python main.py` 실행
- [ ] ENGAGE 버튼 클릭
- [ ] ●●● 모두 초록색 확인
- [ ] 뉴스/시장 패널 업데이트 확인

---

## 🎯 핵심 기능 요약

**자동으로 해주는 것:**
- ✅ 실시간 데이터 수집 (100ms)
- ✅ 기술적 지표 계산 (RSI, BB, MA, MACD)
- ✅ 차트 패턴 분석 (AI vision)
- ✅ 뉴스 수집 및 분석 (5분마다)
- ✅ 시장 분석 (공포탐욕, BTC점유율)
- ✅ 신호 생성 및 검증 (4단계)
- ✅ 음성 알림 (한국어)

**당신이 하는 것:**
- 신호 확인 후 실제 거래는 본인이 판단

**비상시:**
- **스페이스바** = 즉시 정지 (0.1초)

---

## 💡 추천 설정 (초보자)

```json
{
  "trading": {
    "symbol": "BTC/USDT",
    "timeframe": "15m",        // 15분봉 (균형잡힌 선택)
    "auto_start": false        // 수동 시작 (안전)
  },
  "vision": {
    "chart_capture_enabled": false  // 차트 캡처 끄기 (처음엔 불필요)
  },
  "intelligence": {
    "news_enabled": true,      // 뉴스 분석 켜기 (추천!)
    "market_analysis_enabled": true  // 시장 분석 켜기 (추천!)
  }
}
```

---

## ⚠️ 중요 주의사항

1. **반드시 testnet부터!** (`"testnet": true`)
2. 실전 전 2-3일 관찰 (신호 정확도 확인)
3. 1-2%만 위험 부담 (절대 과도한 레버리지 금지)
4. 신호는 참고용 (최종 판단은 본인)
5. 의심되면 스페이스바! (안전 제일)

---

**설치 시간:** 5분  
**사용 난이도:** ⭐☆☆☆☆ (매우 쉬움)  
**효과:** ⭐⭐⭐⭐⭐ (프로 수준)  

이제 시작하세요! 💰🚀
