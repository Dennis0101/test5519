"""
22-Billion: Robust API Client
Resilient HTTP client with retry, backoff, and circuit breaker

FEATURES:
- Exponential backoff retry
- Circuit breaker pattern
- Connection pooling
- Rate limit handling
- Timeout management
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
from datetime import datetime, timedelta


class RobustAPIClient:
    """
    Production-grade API client with resilience patterns
    
    Features:
    - Auto-retry with exponential backoff
    - Circuit breaker (stops calling broken APIs)
    - Connection pooling (reuses connections)
    - Rate limit detection and backoff
    """
    
    def __init__(self, max_retries=3, backoff_factor=1.0, timeout=15):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.timeout = timeout
        
        # Create session with connection pooling
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],  # Retry on these errors
            allowed_methods=["HEAD", "GET", "OPTIONS"]  # Safe methods only
        )
        
        # Mount adapters with retry
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=20)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Circuit breaker state
        self.circuit_breaker = {}  # domain -> {failures, last_failure_time, is_open}
        self.circuit_reset_timeout = 60  # Reset after 60 seconds
        self.circuit_failure_threshold = 5  # Open after 5 failures
    
    def get(self, url, **kwargs):
        """
        Robust GET request with retry and circuit breaker
        
        Args:
            url: URL to request
            **kwargs: Additional arguments for requests.get()
            
        Returns:
            Response object or None on failure
        """
        # Extract domain for circuit breaker
        domain = self._get_domain(url)
        
        # Check circuit breaker
        if self._is_circuit_open(domain):
            print(f"🔴 Circuit breaker OPEN for {domain} - skipping request")
            return None
        
        # Set default timeout if not provided
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        
        try:
            response = self.session.get(url, **kwargs)
            
            # Check rate limit
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                print(f"⚠️ Rate limit hit for {domain}, waiting {retry_after}s")
                time.sleep(retry_after)
                # Try once more
                response = self.session.get(url, **kwargs)
            
            # Success - reset circuit breaker
            self._record_success(domain)
            
            return response
            
        except requests.exceptions.Timeout:
            print(f"⏱️ Timeout for {url}")
            self._record_failure(domain)
            return None
            
        except requests.exceptions.ConnectionError as e:
            print(f"🔌 Connection error for {domain}: {e}")
            self._record_failure(domain)
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Request error for {domain}: {e}")
            self._record_failure(domain)
            return None
    
    def _get_domain(self, url):
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return url
    
    def _is_circuit_open(self, domain):
        """Check if circuit breaker is open for domain"""
        if domain not in self.circuit_breaker:
            return False
        
        circuit = self.circuit_breaker[domain]
        
        if not circuit['is_open']:
            return False
        
        # Check if timeout has passed
        time_since_last_failure = time.time() - circuit['last_failure_time']
        
        if time_since_last_failure > self.circuit_reset_timeout:
            # Reset circuit breaker
            print(f"🔄 Circuit breaker RESET for {domain}")
            circuit['is_open'] = False
            circuit['failures'] = 0
            return False
        
        return True
    
    def _record_success(self, domain):
        """Record successful request"""
        if domain in self.circuit_breaker:
            self.circuit_breaker[domain]['failures'] = 0
            self.circuit_breaker[domain]['is_open'] = False
    
    def _record_failure(self, domain):
        """Record failed request and check if circuit should open"""
        if domain not in self.circuit_breaker:
            self.circuit_breaker[domain] = {
                'failures': 0,
                'last_failure_time': 0,
                'is_open': False
            }
        
        circuit = self.circuit_breaker[domain]
        circuit['failures'] += 1
        circuit['last_failure_time'] = time.time()
        
        # Check if should open circuit
        if circuit['failures'] >= self.circuit_failure_threshold:
            if not circuit['is_open']:
                print(f"🚨 Circuit breaker OPENED for {domain} after {circuit['failures']} failures")
            circuit['is_open'] = True
    
    def close(self):
        """Close session and cleanup"""
        if self.session:
            self.session.close()


# Global singleton instance
_api_client = None

def get_api_client():
    """Get global API client instance"""
    global _api_client
    if _api_client is None:
        _api_client = RobustAPIClient()
    return _api_client
