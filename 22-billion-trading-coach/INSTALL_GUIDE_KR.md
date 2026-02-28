# 🇰🇷 22-Billion 설치 가이드 (한국어)

## 📋 목차
1. [시스템 요구사항](#시스템-요구사항)
2. [빠른 설치](#빠른-설치)
3. [상세 설치 가이드](#상세-설치-가이드)
4. [TA-Lib 설치 (중요!)](#ta-lib-설치)
5. [API 키 설정](#api-키-설정)
6. [실행 방법](#실행-방법)
7. [문제 해결](#문제-해결)

---

## 시스템 요구사항

- **Python**: 3.8 이상
- **운영체제**: Windows 10/11, macOS, Linux (Ubuntu 18.04+)
- **메모리**: 최소 4GB RAM
- **인터넷**: 안정적인 인터넷 연결 필수

---

## 빠른 설치

### 1단계: 파일 다운로드
이 프로젝트 폴더를 다운로드하거나 압축을 풉니다.

### 2단계: 파이썬 라이브러리 설치
```bash
pip install -r requirements.txt
```

### 3단계: TA-Lib 설치 (아래 상세 가이드 참조)

### 4단계: 설정 파일 생성
```bash
cp config.example.json config.json
```

설정 파일을 열어서 API 키를 입력하세요.

### 5단계: 실행
```bash
python main.py
```

---

## 상세 설치 가이드

### 파이썬 확인
먼저 파이썬이 설치되어 있는지 확인하세요:

```bash
python --version
```

또는

```bash
python3 --version
```

Python 3.8 이상이 표시되어야 합니다.

### 필수 라이브러리 설치

프로젝트 폴더에서 다음 명령어를 실행하세요:

```bash
pip install -r requirements.txt
```

**설치되는 라이브러리:**
- `ccxt` - 거래소 API 통신
- `websocket-client` - 실시간 데이터 수신
- `numpy`, `pandas` - 데이터 처리
- `opencv-python` - 차트 캡처 및 분석
- `Pillow` - 이미지 처리
- `openai` - GPT-4o-mini API
- `pyttsx3` - 음성 알림

---

## TA-Lib 설치

**⚠️ 가장 중요한 단계입니다!**

TA-Lib은 기술적 지표 계산 라이브러리로, 일반 pip 설치만으로는 작동하지 않습니다.

### 🪟 Windows 사용자

#### 방법 1: 미리 컴파일된 파일 사용 (권장)

1. 이 사이트로 이동: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib

2. 본인의 파이썬 버전에 맞는 파일 다운로드:
   - **Python 3.11 64비트**: `TA_Lib‑0.4.28‑cp311‑cp311‑win_amd64.whl`
   - **Python 3.10 64비트**: `TA_Lib‑0.4.28‑cp310‑cp310‑win_amd64.whl`
   - **Python 3.9 64비트**: `TA_Lib‑0.4.28‑cp39‑cp39‑win_amd64.whl`

3. 다운로드 폴더에서 설치:
```bash
cd C:\Users\사용자이름\Downloads
pip install TA_Lib-0.4.28-cp311-cp311-win_amd64.whl
```

#### 방법 2: Anaconda 사용

Anaconda를 사용하시는 분:
```bash
conda install -c conda-forge ta-lib
```

### 🍎 macOS 사용자

**Homebrew 사용:**

1. Homebrew가 없다면 먼저 설치:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. TA-Lib 설치:
```bash
brew install ta-lib
pip install TA-Lib
```

### 🐧 Linux (Ubuntu/Debian) 사용자

```bash
# 시스템 라이브러리 설치
sudo apt-get update
sudo apt-get install build-essential wget

# TA-Lib C 라이브러리 다운로드 및 설치
cd /tmp
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install

# Python 래퍼 설치
pip install TA-Lib
```

### ✅ TA-Lib 설치 확인

다음 명령어로 확인:

```bash
python -c "import talib; print('TA-Lib 버전:', talib.__version__)"
```

오류 없이 버전이 출력되면 성공!

---

## API 키 설정

### 1. Binance API 키 발급

#### 실제 거래용 (주의!)
1. https://www.binance.com 로그인
2. [계정] → [API 관리]로 이동
3. "API 생성" 클릭
4. 2단계 인증 완료
5. **API Key**와 **Secret Key** 복사해서 안전한 곳에 보관

⚠️ **중요 보안 설정:**
- "출금 허용" 체크 해제 (반드시!)
- "선물 거래 활성화" 체크 (필요시)
- IP 주소 제한 설정 (가능하면)

#### 테스트용 (권장)
1. https://testnet.binancefuture.com 접속
2. GitHub 계정으로 로그인
3. 무료로 API 키 발급
4. 가짜 돈으로 안전하게 테스트!

### 2. OpenAI API 키 발급

1. https://platform.openai.com 가입/로그인
2. https://platform.openai.com/api-keys 로 이동
3. "Create new secret key" 클릭
4. 키 이름 입력 (예: "22-billion-trading")
5. **즉시 복사!** (다시 볼 수 없습니다)

**💰 비용:**
- GPT-4o-mini는 매우 저렴합니다
- 1,000번 분석해도 약 $1 정도
- 처음 가입시 무료 크레딧 제공

### 3. config.json 설정

```bash
cp config.example.json config.json
```

메모장이나 텍스트 에디터로 `config.json` 열기:

```json
{
  "binance": {
    "api_key": "여기에_바이낸스_API_키_입력",
    "api_secret": "여기에_바이낸스_시크릿_키_입력",
    "testnet": true
  },
  "openai": {
    "api_key": "여기에_OpenAI_API_키_입력",
    "model": "gpt-4o-mini"
  }
}
```

**⚠️ 주의사항:**
- 따옴표 안에 키를 입력하세요
- 앞뒤 공백 없이!
- `testnet: true`로 시작하세요 (안전!)

---

## 실행 방법

### 기본 실행

```bash
python main.py
```

### GUI 사용법

프로그램이 실행되면 GUI 창이 나타납니다:

1. **START 버튼 클릭**: 시장 분석 시작
2. **로그 확인**: 하단에서 실시간 분석 내용 확인
3. **신호 수신**: 조건이 맞으면 음성 알림과 함께 신호 표시
4. **STOP 버튼**: 분석 중지

### 음성 알림

신호가 발생하면 한국어로:
> "주인님, 데이터와 차트 모두 롱 포지션을 가리킵니다..."

---

## 문제 해결

### ❌ "TA-Lib를 찾을 수 없습니다"

**해결법:**
```bash
pip uninstall TA-Lib
pip install --no-cache-dir TA-Lib
```

여전히 안 되면 위의 [TA-Lib 설치](#ta-lib-설치) 섹션을 다시 확인하세요.

### ❌ "API 키가 유효하지 않습니다"

**해결법:**
1. `config.json` 파일 다시 확인
2. API 키 앞뒤에 공백이 있는지 확인
3. 따옴표가 제대로 있는지 확인
4. Binance 사이트에서 API 키 상태 확인

### ❌ "WebSocket 연결 실패"

**해결법:**
1. 인터넷 연결 확인
2. 방화벽 설정 확인
3. VPN 사용 (바이낸스가 차단된 지역)
4. testnet URL 확인

### ❌ "OpenAI API 오류"

**해결법:**
1. API 키가 정확한지 확인
2. OpenAI 계정에 크레딧이 있는지 확인
3. 처음 가입했다면 결제 정보 등록 필요

### ❌ GUI가 안 뜹니다

**Windows:**
일반적으로 문제없음

**Linux:**
```bash
sudo apt-get install python3-tk
```

**macOS:**
```bash
brew install python-tk
```

### ❌ "모듈을 찾을 수 없습니다"

```bash
pip install -r requirements.txt --upgrade
```

---

## 추가 팁

### 1. 처음 사용시

- **반드시 testnet으로 시작!**
- config.json에서 `"testnet": true` 확인
- 며칠간 신호를 관찰하고 정확도 확인
- 실제 돈 사용 전에 충분히 테스트

### 2. 성능 최적화

**분석 주기 조정:**
```json
"trading": {
  "update_interval": 1.0,  // 0.1초 → 1초로 늘리면 부하 감소
}
```

**AI 분석 빈도 조정:**
```json
"vision": {
  "analysis_interval": 60  // 최소 60초에 한 번만
}
```

### 3. 다른 코인 거래

```json
"trading": {
  "symbol": "ETH/USDT",  // 이더리움
  "symbol": "BNB/USDT",  // 바이낸스 코인
}
```

### 4. 더 긴 시간봉 사용

```json
"trading": {
  "timeframe": "5m",  // 5분봉
  "timeframe": "15m", // 15분봉
  "timeframe": "1h",  // 1시간봉
}
```

---

## 보안 주의사항

🔐 **절대 하지 말아야 할 것:**
- API 키를 다른 사람과 공유
- config.json을 GitHub에 업로드
- "출금 허용" 권한 활성화
- 테스트 없이 큰 금액 거래

✅ **꼭 해야 할 것:**
- API 키에 IP 제한 설정
- 2단계 인증(2FA) 활성화
- testnet으로 충분히 연습
- 손실을 감당할 수 있는 금액만 투자

---

## 자주 묻는 질문

**Q: 이 프로그램이 자동으로 거래하나요?**  
A: 아니요. 신호만 알려주는 "코치" 역할입니다. 실제 거래는 본인이 판단하고 실행해야 합니다.

**Q: 수익을 보장하나요?**  
A: 절대 아닙니다. 트레이딩은 항상 손실 위험이 있습니다.

**Q: 얼마나 정확한가요?**  
A: 시장 상황에 따라 다릅니다. 직접 테스트하고 판단하세요.

**Q: OpenAI API 비용이 얼마나 드나요?**  
A: GPT-4o-mini는 매우 저렴합니다. 하루 종일 사용해도 $1 이하입니다.

**Q: 코딩을 몰라도 사용할 수 있나요?**  
A: 네! 이 가이드를 따라하면 복사-붙여넣기만으로 실행 가능합니다.

---

## 연락처

문제가 해결되지 않으면:
1. 이 가이드를 처음부터 다시 읽어보세요
2. 오류 메시지를 정확히 확인하세요
3. Google에서 오류 메시지 검색
4. GitHub Issues에 질문 남기기

---

**행운을 빕니다! 📈💰**

*"최고의 트레이더는 시스템을 믿되, 맹목적으로 따르지 않는 사람입니다."*
