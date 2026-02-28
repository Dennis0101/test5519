"""
22-Billion: Structured Logging
Professional logging system with rotation and levels

FEATURES:
- Structured JSON logging
- Log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- File rotation (prevents huge files)
- Performance logging
- Trade logging
"""

import logging
import logging.handlers
import json
from datetime import datetime
from pathlib import Path


class StructuredLogger:
    """
    Professional structured logging system
    
    Features:
    - Multiple log levels
    - JSON structured format for analysis
    - File rotation (10MB max, 5 backups)
    - Console and file output
    - Performance tracking
    """
    
    def __init__(self, name='22-billion', log_dir='logs'):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create loggers
        self.app_logger = self._create_logger('app', 'application.log')
        self.trade_logger = self._create_logger('trades', 'trades.log')
        self.error_logger = self._create_logger('errors', 'errors.log')
        self.performance_logger = self._create_logger('performance', 'performance.log')
    
    def _create_logger(self, logger_name, filename):
        """Create logger with rotation"""
        logger = logging.getLogger(f"{self.name}.{logger_name}")
        logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate handlers
        if logger.handlers:
            return logger
        
        # File handler with rotation (10MB, 5 backups)
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / filename,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def info(self, message, **kwargs):
        """Log info message"""
        self._log(self.app_logger, logging.INFO, message, **kwargs)
    
    def warning(self, message, **kwargs):
        """Log warning message"""
        self._log(self.app_logger, logging.WARNING, message, **kwargs)
    
    def error(self, message, **kwargs):
        """Log error message"""
        self._log(self.error_logger, logging.ERROR, message, **kwargs)
    
    def critical(self, message, **kwargs):
        """Log critical message"""
        self._log(self.error_logger, logging.CRITICAL, message, **kwargs)
    
    def log_trade(self, trade_data):
        """Log trade execution"""
        trade_msg = json.dumps(trade_data, default=str)
        self.trade_logger.info(f"TRADE: {trade_msg}")
    
    def log_performance(self, metric_name, value, **kwargs):
        """Log performance metric"""
        perf_data = {
            'metric': metric_name,
            'value': value,
            'timestamp': datetime.now().isoformat(),
            **kwargs
        }
        perf_msg = json.dumps(perf_data)
        self.performance_logger.info(perf_msg)
    
    def _log(self, logger, level, message, **kwargs):
        """Internal logging with structured data"""
        if kwargs:
            structured = {
                'message': message,
                'data': kwargs,
                'timestamp': datetime.now().isoformat()
            }
            logger.log(level, json.dumps(structured, default=str))
        else:
            logger.log(level, message)


# Global logger instance
_logger = None

def get_logger():
    """Get global logger instance"""
    global _logger
    if _logger is None:
        _logger = StructuredLogger()
    return _logger
