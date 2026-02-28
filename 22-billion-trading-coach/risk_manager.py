"""
22-Billion: Risk Manager
Critical risk management and account protection system

FEATURES:
- Position sizing based on account and volatility
- Daily loss limits with auto-shutdown
- Consecutive loss tracking and circuit breaker
- ATR-based dynamic position sizing
- Emergency kill switch
- Risk metrics tracking
"""

from datetime import datetime, timedelta
import json
from pathlib import Path


class RiskManager:
    """
    Professional risk management system
    
    Protects account from:
    - Overleveraging
    - Consecutive losses
    - High volatility periods
    - Daily loss limits
    - Abnormal market conditions
    """
    
    def __init__(self, config):
        self.config = config
        
        # Risk parameters
        self.account_balance = config.get('risk', {}).get('account_balance', 10000)  # Default $10k
        self.max_risk_per_trade_pct = config.get('risk', {}).get('max_risk_per_trade', 1.0)  # 1% default
        self.max_daily_loss_pct = config.get('risk', {}).get('max_daily_loss', 5.0)  # 5% default
        self.max_consecutive_losses = config.get('risk', {}).get('max_consecutive_losses', 3)  # 3 losses
        
        # State tracking
        self.daily_pnl = 0.0
        self.trade_count = 0
        self.win_count = 0
        self.loss_count = 0
        self.consecutive_losses = 0
        self.consecutive_wins = 0
        
        # Today's tracking
        self.today = datetime.now().date()
        self.daily_trades = []
        
        # Kill switch
        self.kill_switch_active = False
        self.kill_switch_reason = None
        
        # Load state from file if exists
        self._load_state()
    
    def calculate_position_size(self, entry_price, stop_loss, atr_value, current_volatility=None):
        """
        Calculate safe position size based on risk parameters
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            atr_value: Current ATR (volatility)
            current_volatility: Optional market volatility multiplier
            
        Returns:
            {
                'position_size': float (in base currency),
                'position_size_usd': float (in USD),
                'risk_amount': float (max loss in USD),
                'leverage': float (recommended leverage),
                'approved': bool (if size is safe)
            }
        """
        # Check kill switch
        if self.kill_switch_active:
            return {
                'position_size': 0,
                'position_size_usd': 0,
                'risk_amount': 0,
                'leverage': 0,
                'approved': False,
                'reason': f'Kill switch active: {self.kill_switch_reason}'
            }
        
        # Check daily loss limit
        daily_loss_pct = (self.daily_pnl / self.account_balance) * 100
        if daily_loss_pct <= -self.max_daily_loss_pct:
            self._activate_kill_switch(f'Daily loss limit reached: {daily_loss_pct:.2f}%')
            return {
                'position_size': 0,
                'position_size_usd': 0,
                'risk_amount': 0,
                'leverage': 0,
                'approved': False,
                'reason': 'Daily loss limit exceeded'
            }
        
        # Check consecutive losses
        if self.consecutive_losses >= self.max_consecutive_losses:
            return {
                'position_size': 0,
                'position_size_usd': 0,
                'risk_amount': 0,
                'leverage': 0,
                'approved': False,
                'reason': f'Consecutive losses limit ({self.consecutive_losses})'
            }
        
        # Calculate risk amount
        max_risk_usd = self.account_balance * (self.max_risk_per_trade_pct / 100)
        
        # Adjust for volatility
        if current_volatility and current_volatility > 1.5:
            # High volatility - reduce risk
            max_risk_usd *= 0.7
            volatility_adjusted = True
        else:
            volatility_adjusted = False
        
        # Adjust for consecutive losses (reduce size after losses)
        if self.consecutive_losses > 0:
            reduction_factor = 0.8 ** self.consecutive_losses  # 0.8, 0.64, 0.512...
            max_risk_usd *= reduction_factor
            loss_adjusted = True
        else:
            loss_adjusted = False
        
        # Calculate position size
        stop_distance = abs(entry_price - stop_loss)
        stop_distance_pct = (stop_distance / entry_price) * 100
        
        if stop_distance == 0:
            return {
                'position_size': 0,
                'position_size_usd': 0,
                'risk_amount': 0,
                'leverage': 0,
                'approved': False,
                'reason': 'Invalid stop distance (zero)'
            }
        
        # Position size = Risk Amount / Stop Distance
        position_size_usd = max_risk_usd / (stop_distance_pct / 100)
        
        # Safety check: Don't exceed account balance
        max_position = self.account_balance * 2  # Max 2x leverage for safety
        if position_size_usd > max_position:
            position_size_usd = max_position
            actual_risk = (stop_distance / entry_price) * position_size_usd
        else:
            actual_risk = max_risk_usd
        
        # Calculate recommended leverage
        leverage = position_size_usd / self.account_balance
        
        return {
            'position_size': position_size_usd / entry_price,  # In base currency
            'position_size_usd': position_size_usd,
            'risk_amount': actual_risk,
            'leverage': leverage,
            'stop_distance_pct': stop_distance_pct,
            'approved': True,
            'volatility_adjusted': volatility_adjusted if current_volatility else False,
            'loss_adjusted': loss_adjusted,
            'reason': 'Position approved'
        }
    
    def validate_trade(self, signal_confidence, market_volatility=None):
        """
        Validate if trade should be taken based on risk rules
        
        Args:
            signal_confidence: Signal confidence score (0-100)
            market_volatility: Optional volatility multiplier
            
        Returns:
            {
                'approved': bool,
                'reason': str,
                'adjustments': []
            }
        """
        reasons = []
        adjustments = []
        
        # Check kill switch
        if self.kill_switch_active:
            return {
                'approved': False,
                'reason': f'Kill switch active: {self.kill_switch_reason}',
                'adjustments': []
            }
        
        # Check daily loss limit
        daily_loss_pct = (self.daily_pnl / self.account_balance) * 100
        if daily_loss_pct <= -self.max_daily_loss_pct:
            self._activate_kill_switch(f'Daily loss: {daily_loss_pct:.2f}%')
            return {
                'approved': False,
                'reason': f'Daily loss limit reached: {daily_loss_pct:.2f}%',
                'adjustments': []
            }
        
        # Check consecutive losses
        if self.consecutive_losses >= self.max_consecutive_losses:
            reasons.append(f'Consecutive losses: {self.consecutive_losses}')
            return {
                'approved': False,
                'reason': f'Too many consecutive losses ({self.consecutive_losses})',
                'adjustments': ['Wait for winning trade to resume']
            }
        
        # Check volatility
        if market_volatility and market_volatility > 2.0:
            reasons.append('Extreme volatility detected')
            adjustments.append('Reduce position size by 50%')
        
        # Check if close to daily limit
        if daily_loss_pct <= -(self.max_daily_loss_pct * 0.7):
            reasons.append(f'Approaching daily limit ({daily_loss_pct:.1f}%)')
            adjustments.append('Reduce position size by 30%')
        
        # Check signal confidence minimum
        min_confidence = 60 + (self.consecutive_losses * 5)  # Increase after losses
        if signal_confidence < min_confidence:
            return {
                'approved': False,
                'reason': f'Confidence too low: {signal_confidence:.1f}% < {min_confidence}%',
                'adjustments': []
            }
        
        return {
            'approved': True,
            'reason': 'Trade validated',
            'adjustments': adjustments
        }
    
    def record_trade(self, entry_price, exit_price, position_size, trade_type='LONG'):
        """
        Record trade result and update statistics
        
        Args:
            entry_price: Entry price
            exit_price: Exit price  
            position_size: Position size in base currency
            trade_type: 'LONG' or 'SHORT'
        """
        # Calculate P&L
        if trade_type == 'LONG':
            pnl = (exit_price - entry_price) * position_size
        else:  # SHORT
            pnl = (entry_price - exit_price) * position_size
        
        pnl_pct = (pnl / (entry_price * position_size)) * 100
        
        # Update daily P&L
        self.daily_pnl += pnl
        
        # Update counters
        self.trade_count += 1
        
        if pnl > 0:
            self.win_count += 1
            self.consecutive_wins += 1
            self.consecutive_losses = 0  # Reset
        else:
            self.loss_count += 1
            self.consecutive_losses += 1
            self.consecutive_wins = 0  # Reset
        
        # Record trade
        trade_record = {
            'timestamp': datetime.now().isoformat(),
            'entry_price': entry_price,
            'exit_price': exit_price,
            'position_size': position_size,
            'type': trade_type,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'daily_pnl': self.daily_pnl,
            'consecutive_losses': self.consecutive_losses,
            'consecutive_wins': self.consecutive_wins
        }
        
        self.daily_trades.append(trade_record)
        
        # Save state
        self._save_state()
        
        # Check if need to activate kill switch
        self._check_risk_limits()
        
        return trade_record
    
    def _activate_kill_switch(self, reason):
        """Activate kill switch - stops all trading"""
        self.kill_switch_active = True
        self.kill_switch_reason = reason
        print(f"🚨 KILL SWITCH ACTIVATED: {reason}")
        self._save_state()
    
    def reset_kill_switch(self):
        """Manual kill switch reset (requires user confirmation)"""
        self.kill_switch_active = False
        self.kill_switch_reason = None
        print("✅ Kill switch reset")
        self._save_state()
    
    def reset_daily_stats(self):
        """Reset daily statistics (called at start of new day)"""
        today = datetime.now().date()
        
        if today != self.today:
            # New day - reset
            print(f"📊 New trading day: {today}")
            print(f"   Yesterday P&L: ${self.daily_pnl:.2f}")
            
            self.today = today
            self.daily_pnl = 0.0
            self.daily_trades = []
            
            # Don't reset consecutive losses (they carry over)
            
            self._save_state()
    
    def _check_risk_limits(self):
        """Check if risk limits have been breached"""
        # Daily loss limit
        daily_loss_pct = (self.daily_pnl / self.account_balance) * 100
        
        if daily_loss_pct <= -self.max_daily_loss_pct:
            self._activate_kill_switch(f'Daily loss limit: {daily_loss_pct:.2f}%')
    
    def get_risk_status(self):
        """Get current risk status summary"""
        daily_loss_pct = (self.daily_pnl / self.account_balance) * 100
        win_rate = (self.win_count / self.trade_count * 100) if self.trade_count > 0 else 0
        
        # Risk level
        if self.kill_switch_active:
            risk_level = 'CRITICAL'
        elif daily_loss_pct <= -(self.max_daily_loss_pct * 0.7):
            risk_level = 'HIGH'
        elif self.consecutive_losses >= 2:
            risk_level = 'ELEVATED'
        else:
            risk_level = 'NORMAL'
        
        return {
            'account_balance': self.account_balance,
            'daily_pnl': self.daily_pnl,
            'daily_pnl_pct': daily_loss_pct,
            'daily_limit_remaining': self.max_daily_loss_pct + daily_loss_pct,
            'trade_count': self.trade_count,
            'win_count': self.win_count,
            'loss_count': self.loss_count,
            'win_rate': win_rate,
            'consecutive_losses': self.consecutive_losses,
            'consecutive_wins': self.consecutive_wins,
            'kill_switch_active': self.kill_switch_active,
            'kill_switch_reason': self.kill_switch_reason,
            'risk_level': risk_level,
            'can_trade': not self.kill_switch_active and daily_loss_pct > -self.max_daily_loss_pct
        }
    
    def get_compact_status(self):
        """Get one-line risk status for GUI"""
        status = self.get_risk_status()
        
        pnl = status['daily_pnl']
        pnl_pct = status['daily_pnl_pct']
        trades = status['trade_count']
        winrate = status['win_rate']
        
        # Emoji based on P&L
        if pnl > 0:
            emoji = '🟢'
        elif pnl < 0:
            emoji = '🔴'
        else:
            emoji = '⚪'
        
        # Risk level indicator
        risk_emoji = {
            'NORMAL': '✅',
            'ELEVATED': '⚠️',
            'HIGH': '🔶',
            'CRITICAL': '🚨'
        }.get(status['risk_level'], '❓')
        
        return f"{risk_emoji} PnL:{pnl:+.2f}({pnl_pct:+.1f}%) | 거래:{trades} | 승률:{winrate:.0f}%"
    
    def _save_state(self):
        """Save risk manager state to file"""
        state_file = Path('logs/risk_state.json')
        state_file.parent.mkdir(exist_ok=True)
        
        state = {
            'date': self.today.isoformat(),
            'account_balance': self.account_balance,
            'daily_pnl': self.daily_pnl,
            'trade_count': self.trade_count,
            'win_count': self.win_count,
            'loss_count': self.loss_count,
            'consecutive_losses': self.consecutive_losses,
            'consecutive_wins': self.consecutive_wins,
            'kill_switch_active': self.kill_switch_active,
            'kill_switch_reason': self.kill_switch_reason,
            'daily_trades': self.daily_trades
        }
        
        try:
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save risk state: {e}")
    
    def _load_state(self):
        """Load risk manager state from file"""
        state_file = Path('logs/risk_state.json')
        
        if not state_file.exists():
            return
        
        try:
            with open(state_file, 'r') as f:
                state = json.load(f)
            
            # Check if same day
            saved_date = datetime.fromisoformat(state['date']).date()
            
            if saved_date == self.today:
                # Same day - restore state
                self.daily_pnl = state.get('daily_pnl', 0.0)
                self.trade_count = state.get('trade_count', 0)
                self.win_count = state.get('win_count', 0)
                self.loss_count = state.get('loss_count', 0)
                self.consecutive_losses = state.get('consecutive_losses', 0)
                self.consecutive_wins = state.get('consecutive_wins', 0)
                self.kill_switch_active = state.get('kill_switch_active', False)
                self.kill_switch_reason = state.get('kill_switch_reason', None)
                self.daily_trades = state.get('daily_trades', [])
                
                print(f"📊 Risk state restored: PnL ${self.daily_pnl:.2f}, Trades: {self.trade_count}")
            else:
                # New day - stats already reset
                print(f"📊 New trading day started")
                
        except Exception as e:
            print(f"⚠️ Could not load risk state: {e}")
