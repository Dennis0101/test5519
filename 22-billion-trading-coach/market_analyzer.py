"""
22-Billion: Market Analyzer
Analyzes overall crypto market conditions

FEATURES:
- Fear & Greed Index
- BTC Dominance
- Market cap trends
- Global market sentiment
"""

import time
from datetime import datetime
from api_client import get_api_client


class MarketAnalyzer:
    """Analyze overall crypto market conditions"""
    
    def __init__(self, config):
        self.config = config
        
        # Market data cache
        self.fear_greed_index = None
        self.btc_dominance = None
        self.market_cap_data = None
        
        self.last_update = 0
        self.update_interval = 600  # Update every 10 minutes
    
    def get_market_overview(self):
        """
        Get comprehensive market overview
        
        Returns: {
            'fear_greed': {...},
            'btc_dominance': float,
            'market_sentiment': 'BULLISH'/'BEARISH'/'NEUTRAL',
            'summary': 'Concise market state'
        }
        """
        current_time = time.time()
        
        # Update if stale
        if current_time - self.last_update > self.update_interval:
            self._update_market_data()
            self.last_update = current_time
        
        # Compile overview
        overview = {
            'fear_greed': self.fear_greed_index,
            'btc_dominance': self.btc_dominance,
            'market_sentiment': self._determine_market_sentiment(),
            'summary': self._generate_market_summary(),
            'timestamp': datetime.now()
        }
        
        return overview
    
    def _update_market_data(self):
        """Update all market data from various APIs"""
        try:
            # Update Fear & Greed Index
            self.fear_greed_index = self._get_fear_greed_index()
            
            # Update BTC Dominance
            self.btc_dominance = self._get_btc_dominance()
            
            # Update Market Cap data
            self.market_cap_data = self._get_global_market_data()
            
        except Exception as e:
            print(f"⚠️ Error updating market data: {e}")
    
    def _get_fear_greed_index(self):
        """
        Get Fear & Greed Index from Alternative.me
        Free API, no key required
        """
        try:
            url = "https://api.alternative.me/fng/"
            # FIXED: Use robust API client
            api_client = get_api_client()
            response = api_client.get(url)
            
            if response and response.status_code == 200:
                data = response.json()
                
                if 'data' in data and len(data['data']) > 0:
                    fng_data = data['data'][0]
                    
                    value = int(fng_data.get('value', 50))
                    classification = fng_data.get('value_classification', 'Neutral')
                    
                    return {
                        'value': value,
                        'classification': classification,
                        'timestamp': fng_data.get('timestamp', '')
                    }
            
            return None
            
        except Exception as e:
            print(f"⚠️ Fear & Greed API error: {e}")
            return None
    
    def _get_btc_dominance(self):
        """
        Get BTC dominance from CoinGecko
        """
        try:
            url = "https://api.coingecko.com/api/v3/global"
            # FIXED: Use robust API client
            api_client = get_api_client()
            response = api_client.get(url)
            
            if response and response.status_code == 200:
                data = response.json()
                
                if 'data' in data:
                    dominance = data['data'].get('market_cap_percentage', {}).get('btc', 0)
                    return round(dominance, 2)
            
            return None
            
        except Exception as e:
            print(f"⚠️ BTC Dominance API error: {e}")
            return None
    
    def _get_global_market_data(self):
        """Get global crypto market data"""
        try:
            url = "https://api.coingecko.com/api/v3/global"
            # FIXED: Use robust API client
            api_client = get_api_client()
            response = api_client.get(url)
            
            if response and response.status_code == 200:
                data = response.json()
                
                if 'data' in data:
                    global_data = data['data']
                    
                    return {
                        'total_market_cap': global_data.get('total_market_cap', {}).get('usd', 0),
                        'total_volume_24h': global_data.get('total_volume', {}).get('usd', 0),
                        'market_cap_change_24h': global_data.get('market_cap_change_percentage_24h_usd', 0),
                        'active_cryptocurrencies': global_data.get('active_cryptocurrencies', 0),
                    }
            
            return None
            
        except Exception as e:
            print(f"⚠️ Global market data error: {e}")
            return None
    
    def _determine_market_sentiment(self):
        """Determine overall market sentiment from data"""
        bullish_score = 0
        bearish_score = 0
        
        # Fear & Greed Index
        if self.fear_greed_index:
            fng_value = self.fear_greed_index['value']
            
            if fng_value >= 70:  # Greed
                bullish_score += 2
            elif fng_value >= 55:  # Slight greed
                bullish_score += 1
            elif fng_value <= 30:  # Fear
                bearish_score += 2
            elif fng_value <= 45:  # Slight fear
                bearish_score += 1
        
        # BTC Dominance (higher = safer, often bearish for alts)
        if self.btc_dominance:
            if self.btc_dominance >= 50:
                bearish_score += 1  # BTC dominance rising = alt fear
            else:
                bullish_score += 1  # BTC dominance falling = alt season
        
        # Market Cap Change
        if self.market_cap_data:
            mc_change = self.market_cap_data.get('market_cap_change_24h', 0)
            
            if mc_change >= 3:
                bullish_score += 2
            elif mc_change >= 1:
                bullish_score += 1
            elif mc_change <= -3:
                bearish_score += 2
            elif mc_change <= -1:
                bearish_score += 1
        
        # Determine sentiment
        if bullish_score > bearish_score + 1:
            return 'BULLISH'
        elif bearish_score > bullish_score + 1:
            return 'BEARISH'
        else:
            return 'NEUTRAL'
    
    def _generate_market_summary(self):
        """Generate concise market summary"""
        parts = []
        
        # Fear & Greed
        if self.fear_greed_index:
            fng = self.fear_greed_index['value']
            classification = self.fear_greed_index['classification']
            parts.append(f"공포탐욕: {fng} ({classification})")
        
        # BTC Dominance
        if self.btc_dominance:
            parts.append(f"BTC점유율: {self.btc_dominance:.1f}%")
        
        # Market cap change
        if self.market_cap_data:
            mc_change = self.market_cap_data.get('market_cap_change_24h', 0)
            direction = '상승' if mc_change > 0 else '하락'
            parts.append(f"시총 24h: {direction} {abs(mc_change):.1f}%")
        
        if not parts:
            return "시장 데이터 로딩중"
        
        return ' | '.join(parts)
    
    def get_compact_market_summary(self):
        """Get ultra-compact market summary for GUI"""
        if not self.fear_greed_index and not self.btc_dominance:
            return "시장: 분석중..."
        
        sentiment = self._determine_market_sentiment()
        
        # Emoji
        emoji = '🟢' if sentiment == 'BULLISH' else '🔴' if sentiment == 'BEARISH' else '🟡'
        
        # Key metric
        fng = self.fear_greed_index['value'] if self.fear_greed_index else 50
        btc_dom = f"{self.btc_dominance:.0f}%" if self.btc_dominance else "N/A"
        
        return f"{emoji} {sentiment} | 공포탐욕:{fng} | BTC:{btc_dom}"
