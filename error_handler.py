"""
22-Billion: Error Handler
Centralized error handling and recovery system

FEATURES:
- Graceful error handling
- Auto-recovery mechanisms
- Error logging
- User-friendly messages
"""

import traceback
from datetime import datetime


class ErrorHandler:
    """Centralized error handling system"""
    
    def __init__(self, log_callback=None):
        self.log_callback = log_callback
        self.error_count = 0
        self.last_errors = []
        
    def handle_error(self, error, context="Unknown", critical=False):
        """
        Handle error with context and logging
        
        Args:
            error: Exception object
            context: String describing where error occurred
            critical: If True, this is a critical error
            
        Returns:
            User-friendly error message
        """
        self.error_count += 1
        
        # Create error record
        error_record = {
            'timestamp': datetime.now(),
            'context': context,
            'error': str(error),
            'type': type(error).__name__,
            'critical': critical
        }
        
        # Store in recent errors (max 10)
        self.last_errors.append(error_record)
        if len(self.last_errors) > 10:
            self.last_errors.pop(0)
        
        # Create user-friendly message
        user_message = self._create_user_message(error, context, critical)
        
        # Log if callback provided
        if self.log_callback:
            self.log_callback(user_message)
        
        # Print to console
        print(f"⚠️ {context}: {error}")
        
        if critical:
            print(f"❌ CRITICAL ERROR - Stack trace:")
            traceback.print_exc()
        
        return user_message
    
    def _create_user_message(self, error, context, critical):
        """Create user-friendly error message"""
        
        if critical:
            emoji = "❌"
            prefix = "치명적 오류"
        else:
            emoji = "⚠️"
            prefix = "일시적 오류"
        
        # Map contexts to Korean
        context_map = {
            'WebSocket': '웹소켓 연결',
            'API': 'API 호출',
            'News': '뉴스 수집',
            'Market': '시장 분석',
            'Vision': '차트 분석',
            'Technical': '기술적 지표',
            'Data': '데이터 처리',
        }
        
        context_ko = context_map.get(context, context)
        
        # Common errors with solutions
        error_str = str(error).lower()
        
        if 'timeout' in error_str or 'connection' in error_str:
            solution = "인터넷 연결을 확인하세요. 좀비 모드가 자동으로 재연결합니다."
        elif 'api key' in error_str or 'authentication' in error_str:
            solution = "API 키를 확인하세요 (config.json)."
        elif 'rate limit' in error_str:
            solution = "API 호출 제한에 도달했습니다. 잠시 후 자동으로 재시도합니다."
        elif 'not found' in error_str or '404' in error_str:
            solution = "데이터를 찾을 수 없습니다. 캐시 데이터를 사용합니다."
        else:
            solution = "시스템은 계속 작동합니다. 로그를 확인하세요."
        
        return f"{emoji} {prefix} - {context_ko}: {solution}"
    
    def get_error_summary(self):
        """Get summary of recent errors"""
        if not self.last_errors:
            return "✅ 오류 없음"
        
        recent = self.last_errors[-3:]  # Last 3 errors
        summary_lines = [f"최근 오류 {len(self.last_errors)}개:"]
        
        for err in recent:
            time_str = err['timestamp'].strftime("%H:%M:%S")
            summary_lines.append(f"  [{time_str}] {err['context']}: {err['type']}")
        
        return "\n".join(summary_lines)
    
    def is_healthy(self):
        """Check if system is healthy (few errors)"""
        recent_errors = [e for e in self.last_errors 
                        if (datetime.now() - e['timestamp']).seconds < 300]  # Last 5 minutes
        
        return len(recent_errors) < 5  # Less than 5 errors in 5 minutes = healthy
