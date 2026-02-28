"""
22-Billion: News Analyzer
Real-time crypto news collection and AI sentiment analysis

FEATURES:
- Real-time news from multiple sources
- AI-powered sentiment analysis (GPT-4o-mini)
- Impact scoring (0-100)
- Concise summaries
"""

import requests
import time
from datetime import datetime, timedelta
from openai import OpenAI
import json


class NewsAnalyzer:
    """Collect and analyze crypto news in real-time"""
    
    def __init__(self, config):
        self.config = config
        self.openai_config = config['openai']
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.openai_config['api_key'])
        self.model = self.openai_config['model']
        
        # News cache
        self.news_cache = []
        self.last_update = 0
        self.update_interval = 300  # Update every 5 minutes
        
        # Analysis cache
        self.latest_analysis = None
        
    def get_latest_news(self, symbol='BTC', limit=5):
        """
        Get latest crypto news from multiple sources
        
        Uses free APIs:
        - CoinGecko trending
        - CryptoCompare news
        - Alternative.me sentiment
        """
        current_time = time.time()
        
        # Return cached if recent
        if current_time - self.last_update < self.update_interval and self.news_cache:
            return self.news_cache
        
        news_items = []
        
        try:
            # Source 1: CryptoCompare News API (Free, no key needed)
            news_items.extend(self._get_cryptocompare_news(symbol, limit=3))
            
            # Source 2: CoinGecko trending (Free)
            news_items.extend(self._get_coingecko_trending())
            
            # Limit total news items
            news_items = news_items[:limit]
            
            self.news_cache = news_items
            self.last_update = current_time
            
            return news_items
            
        except Exception as e:
            print(f"⚠️ Error fetching news: {e}")
            return self.news_cache  # Return cached on error
    
    def _get_cryptocompare_news(self, symbol, limit=3):
        """Get news from CryptoCompare (free API)"""
        try:
            url = "https://min-api.cryptocompare.com/data/v2/news/?lang=EN"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('Type') == 100 and 'Data' in data:
                    news_list = []
                    
                    for item in data['Data'][:limit]:
                        # Filter for BTC-related news
                        categories = item.get('categories', '').lower()
                        title = item.get('title', '').lower()
                        
                        if symbol.lower() in categories or symbol.lower() in title or 'bitcoin' in title:
                            news_list.append({
                                'source': 'CryptoCompare',
                                'title': item.get('title', 'No title'),
                                'body': item.get('body', '')[:200],  # First 200 chars
                                'url': item.get('url', ''),
                                'published': datetime.fromtimestamp(item.get('published_on', 0)),
                                'categories': item.get('categories', ''),
                            })
                    
                    return news_list[:limit]
            
            return []
            
        except Exception as e:
            print(f"⚠️ CryptoCompare news error: {e}")
            return []
    
    def _get_coingecko_trending(self):
        """Get trending coins from CoinGecko (free API)"""
        try:
            url = "https://api.coingecko.com/api/v3/search/trending"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'coins' in data:
                    trending_list = []
                    
                    for item in data['coins'][:3]:
                        coin = item.get('item', {})
                        trending_list.append({
                            'source': 'CoinGecko',
                            'title': f"🔥 Trending: {coin.get('name', 'Unknown')} ({coin.get('symbol', '')})",
                            'body': f"Market cap rank: #{coin.get('market_cap_rank', 'N/A')}",
                            'url': f"https://www.coingecko.com/en/coins/{coin.get('id', '')}",
                            'published': datetime.now(),
                            'categories': 'trending',
                        })
                    
                    return trending_list
            
            return []
            
        except Exception as e:
            print(f"⚠️ CoinGecko trending error: {e}")
            return []
    
    def analyze_news_sentiment(self, news_items):
        """
        Analyze news sentiment using GPT-4o-mini
        
        Returns: {
            'sentiment': 'BULLISH'/'BEARISH'/'NEUTRAL',
            'score': 0-100,
            'summary': 'Brief summary',
            'impact': 'HIGH'/'MEDIUM'/'LOW'
        }
        """
        if not news_items:
            return {
                'sentiment': 'NEUTRAL',
                'score': 50,
                'summary': 'No recent news',
                'impact': 'LOW'
            }
        
        try:
            # Prepare news summary for AI
            news_text = self._format_news_for_ai(news_items)
            
            # Create prompt
            prompt = f"""당신은 암호화폐 시장 분석 전문가입니다. 아래 최신 뉴스들을 분석하여 시장 심리를 판단하세요.

**최신 뉴스:**
{news_text}

**분석 요청:**
1. 전체적인 시장 심리 (BULLISH/BEARISH/NEUTRAL)
2. 영향도 (HIGH/MEDIUM/LOW)
3. 핵심 요약 (1-2문장, 30자 이내)
4. 점수 (0-100, 50=중립, 0=극단적 약세, 100=극단적 강세)

**답변 형식 (엄수):**
심리: [BULLISH/BEARISH/NEUTRAL]
영향도: [HIGH/MEDIUM/LOW]
점수: [0-100 숫자만]
요약: [핵심만 30자 이내]

예시:
심리: BULLISH
영향도: MEDIUM
점수: 65
요약: 기관 매수세 증가, 규제 완화 기대감

간결하게!"""

            # Call GPT-4o-mini
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=200,
                temperature=0.3,
            )
            
            analysis_text = response.choices[0].message.content
            
            # Parse response
            result = self._parse_sentiment_response(analysis_text)
            
            self.latest_analysis = {
                **result,
                'timestamp': datetime.now(),
                'news_count': len(news_items)
            }
            
            return self.latest_analysis
            
        except Exception as e:
            print(f"⚠️ News sentiment analysis error: {e}")
            return {
                'sentiment': 'NEUTRAL',
                'score': 50,
                'summary': 'Analysis unavailable',
                'impact': 'LOW'
            }
    
    def _format_news_for_ai(self, news_items):
        """Format news for AI analysis"""
        formatted = []
        
        for i, news in enumerate(news_items[:5], 1):
            title = news.get('title', 'No title')
            body = news.get('body', '')[:100]
            source = news.get('source', 'Unknown')
            
            formatted.append(f"{i}. [{source}] {title}\n   {body}...")
        
        return '\n\n'.join(formatted)
    
    def _parse_sentiment_response(self, text):
        """Parse AI sentiment response"""
        import re
        
        # Default values
        result = {
            'sentiment': 'NEUTRAL',
            'score': 50,
            'summary': 'No clear trend',
            'impact': 'LOW'
        }
        
        try:
            # Extract sentiment
            sentiment_match = re.search(r'심리\s*:\s*(BULLISH|BEARISH|NEUTRAL)', text, re.IGNORECASE)
            if sentiment_match:
                result['sentiment'] = sentiment_match.group(1).upper()
            
            # Extract impact
            impact_match = re.search(r'영향도\s*:\s*(HIGH|MEDIUM|LOW)', text, re.IGNORECASE)
            if impact_match:
                result['impact'] = impact_match.group(1).upper()
            
            # Extract score
            score_match = re.search(r'점수\s*:\s*([0-9]+)', text)
            if score_match:
                result['score'] = int(score_match.group(1))
            
            # Extract summary
            summary_match = re.search(r'요약\s*:\s*(.+?)(?:\n|$)', text)
            if summary_match:
                result['summary'] = summary_match.group(1).strip()
            
        except Exception as e:
            print(f"⚠️ Error parsing sentiment: {e}")
        
        return result
    
    def get_compact_news_summary(self):
        """Get concise news summary for display"""
        if not self.latest_analysis:
            return "뉴스: 분석 대기중"
        
        sentiment = self.latest_analysis['sentiment']
        score = self.latest_analysis['score']
        summary = self.latest_analysis['summary']
        impact = self.latest_analysis['impact']
        
        # Emoji based on sentiment
        emoji = '🟢' if sentiment == 'BULLISH' else '🔴' if sentiment == 'BEARISH' else '🟡'
        
        # Impact indicator
        impact_emoji = '⚠️' if impact == 'HIGH' else '📊' if impact == 'MEDIUM' else '📉'
        
        return f"{emoji} {sentiment} [{score}] {impact_emoji} {summary}"
