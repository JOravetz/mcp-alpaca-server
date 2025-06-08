"""
Trading-specific data models and state management for Alpaca MCP Server.

This module provides comprehensive data models for trading operations, portfolio analysis,
risk management, and market condition tracking. All models are designed to support
prompt workflows and can be instantiated with sample data for testing.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Union, Any, Set
import json
from collections import defaultdict
import threading
from abc import ABC, abstractmethod


# =============================================================================
# Enums and Constants
# =============================================================================

class MarketStatus(Enum):
    OPEN = "open"
    CLOSED = "closed"
    PRE_MARKET = "pre_market"
    AFTER_MARKET = "after_market"


class AssetClass(Enum):
    EQUITY = "equity"
    OPTION = "option"
    CRYPTO = "crypto"
    FOREX = "forex"


class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    TRAILING_STOP = "trailing_stop"


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"


class TradingStrategy(Enum):
    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"
    BREAKOUT = "breakout"
    EARNINGS_PLAY = "earnings_play"
    DIVIDEND_CAPTURE = "dividend_capture"
    ARBITRAGE = "arbitrage"
    SWING_TRADE = "swing_trade"
    DAY_TRADE = "day_trade"
    OPTIONS_STRATEGY = "options_strategy"


class VolatilityLevel(Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    VERY_HIGH = "very_high"


# =============================================================================
# Core Data Models
# =============================================================================

@dataclass
class Money:
    """Represents a monetary amount with currency."""
    amount: Decimal
    currency: str = "USD"
    
    def __str__(self) -> str:
        return f"${self.amount:,.2f}"
    
    def __add__(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError(f"Cannot add {self.currency} and {other.currency}")
        return Money(self.amount + other.amount, self.currency)
    
    def __sub__(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError(f"Cannot subtract {self.currency} and {other.currency}")
        return Money(self.amount - other.amount, self.currency)
    
    def to_float(self) -> float:
        return float(self.amount)


@dataclass
class PriceData:
    """Current price information for an asset."""
    symbol: str
    price: Decimal
    timestamp: datetime
    bid: Optional[Decimal] = None
    ask: Optional[Decimal] = None
    volume: Optional[int] = None
    change: Optional[Decimal] = None
    change_percent: Optional[Decimal] = None
    
    @property
    def spread(self) -> Optional[Decimal]:
        if self.bid and self.ask:
            return self.ask - self.bid
        return None
    
    @property
    def mid_price(self) -> Optional[Decimal]:
        if self.bid and self.ask:
            return (self.bid + self.ask) / 2
        return None


@dataclass
class AccountSummary:
    """Summary of account balance and key metrics."""
    account_id: str
    cash: Money
    buying_power: Money
    equity: Money
    last_equity: Money
    long_market_value: Money
    short_market_value: Money
    portfolio_value: Money
    positions_count: int
    open_orders_count: int
    day_trade_count: int
    pattern_day_trader: bool
    multiplier: Decimal
    created_at: datetime
    updated_at: datetime
    
    @property
    def unrealized_pl(self) -> Money:
        """Calculate unrealized P&L."""
        return Money(self.equity.amount - self.last_equity.amount)
    
    @property
    def margin_used(self) -> Money:
        """Calculate margin currently used."""
        return Money(self.equity.amount - self.cash.amount)
    
    @property
    def available_margin(self) -> Money:
        """Calculate available margin."""
        return Money(self.buying_power.amount - self.cash.amount)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'account_id': self.account_id,
            'cash': str(self.cash),
            'buying_power': str(self.buying_power),
            'equity': str(self.equity),
            'portfolio_value': str(self.portfolio_value),
            'positions_count': self.positions_count,
            'open_orders_count': self.open_orders_count,
            'day_trade_count': self.day_trade_count,
            'pattern_day_trader': self.pattern_day_trader,
            'unrealized_pl': str(self.unrealized_pl),
            'margin_used': str(self.margin_used)
        }


@dataclass
class PositionAnalysis:
    """Detailed analysis of a trading position."""
    symbol: str
    asset_class: AssetClass
    quantity: Decimal
    avg_entry_price: Decimal
    current_price: Decimal
    market_value: Money
    cost_basis: Money
    unrealized_pl: Money
    unrealized_pl_percent: Decimal
    side: OrderSide
    created_at: datetime
    updated_at: datetime
    
    # Risk metrics
    portfolio_weight: Optional[Decimal] = None
    beta: Optional[Decimal] = None
    volatility: Optional[Decimal] = None
    var_1d: Optional[Money] = None  # 1-day Value at Risk
    max_drawdown: Optional[Decimal] = None
    
    # Performance metrics
    holding_period_days: Optional[int] = None
    annualized_return: Optional[Decimal] = None
    sharpe_ratio: Optional[Decimal] = None
    
    @property
    def is_profitable(self) -> bool:
        return self.unrealized_pl.amount > 0
    
    @property
    def risk_level(self) -> RiskLevel:
        """Determine risk level based on position characteristics."""
        if self.portfolio_weight and self.portfolio_weight > Decimal('0.20'):
            return RiskLevel.HIGH
        elif self.unrealized_pl_percent < Decimal('-0.10'):
            return RiskLevel.HIGH
        elif self.volatility and self.volatility > Decimal('0.30'):
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def calculate_position_size(self, target_risk_percent: Decimal, 
                              stop_loss_percent: Decimal) -> Decimal:
        """Calculate optimal position size given risk parameters."""
        if stop_loss_percent <= 0:
            return Decimal('0')
        return target_risk_percent / stop_loss_percent
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'symbol': self.symbol,
            'quantity': str(self.quantity),
            'current_price': str(self.current_price),
            'market_value': str(self.market_value),
            'unrealized_pl': str(self.unrealized_pl),
            'unrealized_pl_percent': f"{self.unrealized_pl_percent:.2%}",
            'side': self.side.value,
            'portfolio_weight': f"{self.portfolio_weight:.2%}" if self.portfolio_weight else None,
            'risk_level': self.risk_level.value,
            'is_profitable': self.is_profitable
        }


@dataclass
class MarketConditions:
    """Current market conditions and environment analysis."""
    timestamp: datetime
    market_status: MarketStatus
    
    # Market indices
    spy_price: Optional[Decimal] = None
    spy_change_percent: Optional[Decimal] = None
    qqq_price: Optional[Decimal] = None
    qqq_change_percent: Optional[Decimal] = None
    iwm_price: Optional[Decimal] = None
    iwm_change_percent: Optional[Decimal] = None
    
    # Volatility measures
    vix_level: Optional[Decimal] = None
    vix_change: Optional[Decimal] = None
    overall_volatility: VolatilityLevel = VolatilityLevel.NORMAL
    
    # Sector performance
    sector_performance: Dict[str, Decimal] = field(default_factory=dict)
    
    # Market sentiment indicators
    advance_decline_ratio: Optional[Decimal] = None
    new_highs: Optional[int] = None
    new_lows: Optional[int] = None
    
    # Economic indicators
    interest_rate_trend: Optional[str] = None
    economic_calendar_events: List[str] = field(default_factory=list)
    
    @property
    def market_sentiment(self) -> str:
        """Determine overall market sentiment."""
        if not self.spy_change_percent:
            return "neutral"
        
        if self.spy_change_percent > Decimal('0.02'):
            return "bullish"
        elif self.spy_change_percent < Decimal('-0.02'):
            return "bearish"
        else:
            return "neutral"
    
    @property
    def is_high_volatility_environment(self) -> bool:
        """Check if current environment is high volatility."""
        return (self.vix_level and self.vix_level > Decimal('25')) or \
               self.overall_volatility in [VolatilityLevel.HIGH, VolatilityLevel.VERY_HIGH]
    
    def get_best_performing_sectors(self, limit: int = 3) -> List[tuple]:
        """Get top performing sectors."""
        return sorted(self.sector_performance.items(), 
                     key=lambda x: x[1], reverse=True)[:limit]
    
    def get_worst_performing_sectors(self, limit: int = 3) -> List[tuple]:
        """Get worst performing sectors."""
        return sorted(self.sector_performance.items(), 
                     key=lambda x: x[1])[:limit]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'market_status': self.market_status.value,
            'market_sentiment': self.market_sentiment,
            'spy_change_percent': f"{self.spy_change_percent:.2%}" if self.spy_change_percent else None,
            'vix_level': str(self.vix_level) if self.vix_level else None,
            'volatility_level': self.overall_volatility.value,
            'is_high_volatility': self.is_high_volatility_environment,
            'top_sectors': self.get_best_performing_sectors(),
            'worst_sectors': self.get_worst_performing_sectors()
        }


@dataclass
class TradingOpportunity:
    """Identified trading opportunity with analysis."""
    symbol: str
    strategy: TradingStrategy
    side: OrderSide
    confidence: Decimal  # 0.0 to 1.0
    risk_level: RiskLevel
    
    # Price targets
    entry_price: Optional[Decimal] = None
    target_price: Optional[Decimal] = None
    stop_loss: Optional[Decimal] = None
    
    # Analysis
    rationale: str = ""
    technical_indicators: Dict[str, Any] = field(default_factory=dict)
    fundamental_factors: List[str] = field(default_factory=list)
    
    # Risk/Reward
    risk_reward_ratio: Optional[Decimal] = None
    max_loss_percent: Optional[Decimal] = None
    expected_return_percent: Optional[Decimal] = None
    
    # Timing
    time_horizon: Optional[str] = None  # "intraday", "swing", "position"
    expiration: Optional[datetime] = None
    
    # Market context
    market_conditions: Optional[MarketConditions] = None
    
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def is_valid(self) -> bool:
        """Check if opportunity is still valid."""
        if self.expiration and datetime.now() > self.expiration:
            return False
        return self.confidence > Decimal('0.5')
    
    @property
    def priority_score(self) -> Decimal:
        """Calculate priority score for ranking opportunities."""
        score = self.confidence
        
        # Adjust for risk/reward
        if self.risk_reward_ratio:
            score *= min(self.risk_reward_ratio / 2, Decimal('2.0'))
        
        # Adjust for risk level
        risk_multipliers = {
            RiskLevel.LOW: Decimal('1.2'),
            RiskLevel.MEDIUM: Decimal('1.0'),
            RiskLevel.HIGH: Decimal('0.8'),
            RiskLevel.EXTREME: Decimal('0.5')
        }
        score *= risk_multipliers.get(self.risk_level, Decimal('1.0'))
        
        return score
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'symbol': self.symbol,
            'strategy': self.strategy.value,
            'side': self.side.value,
            'confidence': f"{self.confidence:.1%}",
            'risk_level': self.risk_level.value,
            'entry_price': str(self.entry_price) if self.entry_price else None,
            'target_price': str(self.target_price) if self.target_price else None,
            'stop_loss': str(self.stop_loss) if self.stop_loss else None,
            'risk_reward_ratio': str(self.risk_reward_ratio) if self.risk_reward_ratio else None,
            'time_horizon': self.time_horizon,
            'priority_score': f"{self.priority_score:.2f}",
            'is_valid': self.is_valid,
            'rationale': self.rationale
        }


@dataclass
class RiskMetrics:
    """Portfolio risk analysis and metrics."""
    portfolio_value: Money
    cash_percentage: Decimal
    
    # Concentration risk
    largest_position_weight: Decimal
    top_5_concentration: Decimal
    number_of_positions: int
    
    # Correlation and diversification
    average_correlation: Optional[Decimal] = None
    sector_concentration: Dict[str, Decimal] = field(default_factory=dict)
    
    # Volatility metrics
    portfolio_beta: Optional[Decimal] = None
    portfolio_volatility: Optional[Decimal] = None
    var_1d: Optional[Money] = None  # 1-day Value at Risk
    var_5d: Optional[Money] = None  # 5-day Value at Risk
    
    # Drawdown metrics
    max_drawdown: Optional[Decimal] = None
    current_drawdown: Optional[Decimal] = None
    
    # Leverage and margin
    margin_usage: Decimal = Decimal('0')
    leverage_ratio: Decimal = Decimal('1')
    
    # Greeks (for options positions)
    portfolio_delta: Optional[Decimal] = None
    portfolio_gamma: Optional[Decimal] = None
    portfolio_theta: Optional[Decimal] = None
    portfolio_vega: Optional[Decimal] = None
    
    updated_at: datetime = field(default_factory=datetime.now)
    
    @property
    def overall_risk_level(self) -> RiskLevel:
        """Determine overall portfolio risk level."""
        high_risk_factors = 0
        
        # Check concentration risk
        if self.largest_position_weight > Decimal('0.25'):
            high_risk_factors += 2
        elif self.largest_position_weight > Decimal('0.15'):
            high_risk_factors += 1
            
        # Check diversification
        if self.number_of_positions < 5:
            high_risk_factors += 1
            
        # Check volatility
        if self.portfolio_volatility and self.portfolio_volatility > Decimal('0.25'):
            high_risk_factors += 1
            
        # Check leverage
        if self.leverage_ratio > Decimal('2.0'):
            high_risk_factors += 2
        elif self.leverage_ratio > Decimal('1.5'):
            high_risk_factors += 1
            
        # Determine risk level
        if high_risk_factors >= 4:
            return RiskLevel.EXTREME
        elif high_risk_factors >= 3:
            return RiskLevel.HIGH
        elif high_risk_factors >= 2:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    @property
    def is_well_diversified(self) -> bool:
        """Check if portfolio is well diversified."""
        return (self.number_of_positions >= 10 and 
                self.largest_position_weight <= Decimal('0.10') and
                self.top_5_concentration <= Decimal('0.40'))
    
    def calculate_position_limit(self, risk_tolerance: Decimal) -> Decimal:
        """Calculate maximum position size as percentage of portfolio."""
        base_limit = Decimal('0.05')  # 5% base limit
        
        # Adjust based on diversification
        if self.number_of_positions > 20:
            base_limit = Decimal('0.10')
        elif self.number_of_positions < 5:
            base_limit = Decimal('0.03')
            
        # Adjust based on risk tolerance
        return min(base_limit * risk_tolerance, Decimal('0.25'))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'portfolio_value': str(self.portfolio_value),
            'overall_risk_level': self.overall_risk_level.value,
            'largest_position_weight': f"{self.largest_position_weight:.2%}",
            'top_5_concentration': f"{self.top_5_concentration:.2%}",
            'number_of_positions': self.number_of_positions,
            'cash_percentage': f"{self.cash_percentage:.2%}",
            'portfolio_volatility': f"{self.portfolio_volatility:.2%}" if self.portfolio_volatility else None,
            'max_drawdown': f"{self.max_drawdown:.2%}" if self.max_drawdown else None,
            'leverage_ratio': str(self.leverage_ratio),
            'is_well_diversified': self.is_well_diversified,
            'var_1d': str(self.var_1d) if self.var_1d else None
        }


# =============================================================================
# State Management Classes
# =============================================================================

class StateManager(ABC):
    """Abstract base class for state management."""
    
    @abstractmethod
    def get_state(self) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def update_state(self, **kwargs) -> None:
        pass
    
    @abstractmethod
    def clear_state(self) -> None:
        pass


class MarketConditionsManager(StateManager):
    """Manages current market conditions state."""
    
    def __init__(self):
        self._lock = threading.Lock()
        self._conditions: Optional[MarketConditions] = None
        self._last_update: Optional[datetime] = None
        self._cache_duration = timedelta(minutes=5)
    
    def get_state(self) -> Dict[str, Any]:
        with self._lock:
            if self._conditions:
                return {
                    'conditions': self._conditions.to_dict(),
                    'last_update': self._last_update.isoformat() if self._last_update else None,
                    'is_stale': self.is_stale()
                }
            return {}
    
    def update_state(self, conditions: MarketConditions) -> None:
        with self._lock:
            self._conditions = conditions
            self._last_update = datetime.now()
    
    def clear_state(self) -> None:
        with self._lock:
            self._conditions = None
            self._last_update = None
    
    def get_conditions(self) -> Optional[MarketConditions]:
        with self._lock:
            return self._conditions
    
    def is_stale(self) -> bool:
        """Check if cached conditions are stale."""
        if not self._last_update:
            return True
        return datetime.now() - self._last_update > self._cache_duration


class StreamingSessionManager(StateManager):
    """Manages active streaming sessions."""
    
    def __init__(self):
        self._lock = threading.Lock()
        self._active_sessions: Dict[str, Dict[str, Any]] = {}
        self._session_stats: Dict[str, Dict[str, int]] = defaultdict(lambda: {
            'messages_received': 0,
            'errors': 0,
            'reconnections': 0
        })
    
    def get_state(self) -> Dict[str, Any]:
        with self._lock:
            return {
                'active_sessions': dict(self._active_sessions),
                'session_stats': dict(self._session_stats),
                'total_sessions': len(self._active_sessions)
            }
    
    def update_state(self, session_id: str, **kwargs) -> None:
        with self._lock:
            if session_id not in self._active_sessions:
                self._active_sessions[session_id] = {
                    'created_at': datetime.now(),
                    'status': 'active'
                }
            self._active_sessions[session_id].update(kwargs)
    
    def clear_state(self) -> None:
        with self._lock:
            self._active_sessions.clear()
            self._session_stats.clear()
    
    def add_session(self, session_id: str, symbols: List[str], 
                   session_type: str = 'quotes') -> None:
        """Add a new streaming session."""
        with self._lock:
            self._active_sessions[session_id] = {
                'symbols': symbols,
                'type': session_type,
                'created_at': datetime.now(),
                'status': 'active',
                'last_message': None
            }
    
    def remove_session(self, session_id: str) -> None:
        """Remove a streaming session."""
        with self._lock:
            self._active_sessions.pop(session_id, None)
            self._session_stats.pop(session_id, None)
    
    def update_session_stats(self, session_id: str, stat_type: str) -> None:
        """Update statistics for a session."""
        with self._lock:
            if stat_type in self._session_stats[session_id]:
                self._session_stats[session_id][stat_type] += 1


class AnalysisResultsManager(StateManager):
    """Manages recent analysis results and caching."""
    
    def __init__(self, max_results: int = 100):
        self._lock = threading.Lock()
        self._results: Dict[str, Any] = {}
        self._timestamps: Dict[str, datetime] = {}
        self._max_results = max_results
        self._cache_duration = timedelta(hours=1)
    
    def get_state(self) -> Dict[str, Any]:
        with self._lock:
            return {
                'total_results': len(self._results),
                'recent_analyses': list(self._results.keys())[-10:],
                'oldest_result': min(self._timestamps.values()).isoformat() if self._timestamps else None,
                'newest_result': max(self._timestamps.values()).isoformat() if self._timestamps else None
            }
    
    def update_state(self, key: str, result: Any) -> None:
        with self._lock:
            self._results[key] = result
            self._timestamps[key] = datetime.now()
            self._cleanup_old_results()
    
    def clear_state(self) -> None:
        with self._lock:
            self._results.clear()
            self._timestamps.clear()
    
    def get_result(self, key: str) -> Optional[Any]:
        """Get a cached result if it exists and is not stale."""
        with self._lock:
            if key in self._results and key in self._timestamps:
                if datetime.now() - self._timestamps[key] <= self._cache_duration:
                    return self._results[key]
                else:
                    # Remove stale result
                    self._results.pop(key, None)
                    self._timestamps.pop(key, None)
            return None
    
    def _cleanup_old_results(self) -> None:
        """Remove old results to maintain cache size."""
        if len(self._results) > self._max_results:
            # Remove oldest results
            sorted_items = sorted(self._timestamps.items(), key=lambda x: x[1])
            to_remove = len(self._results) - self._max_results
            
            for key, _ in sorted_items[:to_remove]:
                self._results.pop(key, None)
                self._timestamps.pop(key, None)


# =============================================================================
# Utility Functions
# =============================================================================

def calculate_position_size(account_value: Money, risk_percent: Decimal,
                          entry_price: Decimal, stop_loss: Decimal) -> int:
    """
    Calculate optimal position size based on risk management parameters.
    
    Args:
        account_value: Total account value
        risk_percent: Maximum risk as percentage of account (e.g., 0.02 for 2%)
        entry_price: Planned entry price
        stop_loss: Stop loss price
        
    Returns:
        Number of shares to buy
    """
    if stop_loss <= 0 or entry_price <= 0:
        return 0
        
    risk_per_share = abs(entry_price - stop_loss)
    if risk_per_share == 0:
        return 0
        
    max_risk_amount = account_value.amount * risk_percent
    position_size = int(max_risk_amount / risk_per_share)
    
    return max(0, position_size)


def calculate_portfolio_metrics(positions: List[PositionAnalysis],
                              total_value: Money) -> Dict[str, Any]:
    """
    Calculate comprehensive portfolio metrics.
    
    Args:
        positions: List of position analyses
        total_value: Total portfolio value
        
    Returns:
        Dictionary of portfolio metrics
    """
    if not positions or total_value.amount <= 0:
        return {}
    
    # Basic metrics
    total_unrealized_pl = sum([pos.unrealized_pl.amount for pos in positions])
    profitable_positions = [pos for pos in positions if pos.is_profitable]
    losing_positions = [pos for pos in positions if not pos.is_profitable]
    
    # Concentration metrics
    position_weights = [
        pos.market_value.amount / total_value.amount for pos in positions
    ]
    largest_position = max(position_weights) if position_weights else Decimal('0')
    top_5_positions = sorted(position_weights, reverse=True)[:5]
    top_5_concentration = sum(top_5_positions)
    
    # Sector analysis
    sector_exposure = defaultdict(Decimal)
    for pos in positions:
        # This would need to be enhanced with actual sector mapping
        sector = "Unknown"  # Placeholder
        sector_exposure[sector] += pos.market_value.amount / total_value.amount
    
    return {
        'total_positions': len(positions),
        'profitable_positions': len(profitable_positions),
        'losing_positions': len(losing_positions),
        'win_rate': len(profitable_positions) / len(positions) * 100,
        'total_unrealized_pl': Money(total_unrealized_pl),
        'largest_position_weight': largest_position,
        'top_5_concentration': top_5_concentration,
        'average_position_size': total_value.amount / len(positions),
        'sector_exposure': dict(sector_exposure)
    }


def assess_market_risk(conditions: MarketConditions,
                      portfolio_beta: Optional[Decimal] = None) -> RiskLevel:
    """
    Assess overall market risk based on current conditions.
    
    Args:
        conditions: Current market conditions
        portfolio_beta: Portfolio beta for market sensitivity
        
    Returns:
        Overall market risk level
    """
    risk_factors = 0
    
    # Volatility risk
    if conditions.is_high_volatility_environment:
        risk_factors += 2
    elif conditions.overall_volatility == VolatilityLevel.HIGH:
        risk_factors += 1
    
    # Market sentiment risk
    if conditions.market_sentiment == "bearish":
        risk_factors += 1
    
    # VIX risk
    if conditions.vix_level:
        if conditions.vix_level > Decimal('30'):
            risk_factors += 2
        elif conditions.vix_level > Decimal('20'):
            risk_factors += 1
    
    # Portfolio beta risk
    if portfolio_beta and portfolio_beta > Decimal('1.3'):
        risk_factors += 1
    
    # Market hours risk
    if conditions.market_status in [MarketStatus.PRE_MARKET, MarketStatus.AFTER_MARKET]:
        risk_factors += 1
    
    # Determine overall risk
    if risk_factors >= 5:
        return RiskLevel.EXTREME
    elif risk_factors >= 3:
        return RiskLevel.HIGH
    elif risk_factors >= 2:
        return RiskLevel.MEDIUM
    else:
        return RiskLevel.LOW


def create_sample_data() -> Dict[str, Any]:
    """
    Create sample data for testing and demonstration purposes.
    
    Returns:
        Dictionary containing sample instances of all models
    """
    now = datetime.now()
    
    # Sample account
    account = AccountSummary(
        account_id="test_account_123",
        cash=Money(Decimal('25000.00')),
        buying_power=Money(Decimal('50000.00')),
        equity=Money(Decimal('85000.00')),
        last_equity=Money(Decimal('82000.00')),
        long_market_value=Money(Decimal('60000.00')),
        short_market_value=Money(Decimal('0.00')),
        portfolio_value=Money(Decimal('85000.00')),
        positions_count=8,
        open_orders_count=2,
        day_trade_count=1,
        pattern_day_trader=False,
        multiplier=Decimal('4.0'),
        created_at=now - timedelta(days=30),
        updated_at=now
    )
    
    # Sample positions
    positions = [
        PositionAnalysis(
            symbol="AAPL",
            asset_class=AssetClass.EQUITY,
            quantity=Decimal('100'),
            avg_entry_price=Decimal('180.50'),
            current_price=Decimal('185.25'),
            market_value=Money(Decimal('18525.00')),
            cost_basis=Money(Decimal('18050.00')),
            unrealized_pl=Money(Decimal('475.00')),
            unrealized_pl_percent=Decimal('0.0263'),
            side=OrderSide.BUY,
            created_at=now - timedelta(days=5),
            updated_at=now,
            portfolio_weight=Decimal('0.218'),
            beta=Decimal('1.25'),
            volatility=Decimal('0.28')
        ),
        PositionAnalysis(
            symbol="MSFT",
            asset_class=AssetClass.EQUITY,
            quantity=Decimal('75'),
            avg_entry_price=Decimal('340.00'),
            current_price=Decimal('338.75'),
            market_value=Money(Decimal('25406.25')),
            cost_basis=Money(Decimal('25500.00')),
            unrealized_pl=Money(Decimal('-93.75')),
            unrealized_pl_percent=Decimal('-0.0037'),
            side=OrderSide.BUY,
            created_at=now - timedelta(days=3),
            updated_at=now,
            portfolio_weight=Decimal('0.299'),
            beta=Decimal('0.95'),
            volatility=Decimal('0.25')
        )
    ]
    
    # Sample market conditions
    market_conditions = MarketConditions(
        timestamp=now,
        market_status=MarketStatus.OPEN,
        spy_price=Decimal('450.25'),
        spy_change_percent=Decimal('0.0125'),
        vix_level=Decimal('18.5'),
        vix_change=Decimal('-0.5'),
        overall_volatility=VolatilityLevel.NORMAL,
        sector_performance={
            'Technology': Decimal('0.015'),
            'Healthcare': Decimal('0.008'),
            'Finance': Decimal('-0.005'),
            'Energy': Decimal('0.025'),
            'Consumer': Decimal('0.002')
        },
        advance_decline_ratio=Decimal('1.25'),
        new_highs=45,
        new_lows=28
    )
    
    # Sample trading opportunity
    opportunity = TradingOpportunity(
        symbol="TSLA",
        strategy=TradingStrategy.BREAKOUT,
        side=OrderSide.BUY,
        confidence=Decimal('0.75'),
        risk_level=RiskLevel.MEDIUM,
        entry_price=Decimal('245.00'),
        target_price=Decimal('265.00'),
        stop_loss=Decimal('235.00'),
        rationale="Strong breakout above resistance with high volume",
        risk_reward_ratio=Decimal('2.0'),
        time_horizon="swing",
        market_conditions=market_conditions
    )
    
    # Sample risk metrics
    risk_metrics = RiskMetrics(
        portfolio_value=Money(Decimal('85000.00')),
        cash_percentage=Decimal('0.294'),
        largest_position_weight=Decimal('0.299'),
        top_5_concentration=Decimal('0.75'),
        number_of_positions=8,
        portfolio_beta=Decimal('1.08'),
        portfolio_volatility=Decimal('0.22'),
        var_1d=Money(Decimal('2125.00')),
        max_drawdown=Decimal('0.08'),
        leverage_ratio=Decimal('1.7')
    )
    
    return {
        'account_summary': account,
        'positions': positions,
        'market_conditions': market_conditions,
        'trading_opportunity': opportunity,
        'risk_metrics': risk_metrics,
        'portfolio_metrics': calculate_portfolio_metrics(positions, account.portfolio_value)
    }


# =============================================================================
# Global State Managers (Singletons)
# =============================================================================

# Global instances for state management
market_conditions_manager = MarketConditionsManager()
streaming_session_manager = StreamingSessionManager()
analysis_results_manager = AnalysisResultsManager()


def get_global_state() -> Dict[str, Any]:
    """Get combined global state from all managers."""
    return {
        'market_conditions': market_conditions_manager.get_state(),
        'streaming_sessions': streaming_session_manager.get_state(),
        'analysis_results': analysis_results_manager.get_state(),
        'timestamp': datetime.now().isoformat()
    }


if __name__ == "__main__":
    # Demo usage
    sample_data = create_sample_data()
    
    print("=== Sample Account Summary ===")
    print(json.dumps(sample_data['account_summary'].to_dict(), indent=2))
    
    print("\n=== Sample Position Analysis ===")
    for pos in sample_data['positions']:
        print(json.dumps(pos.to_dict(), indent=2))
        print()
    
    print("=== Sample Market Conditions ===")
    print(json.dumps(sample_data['market_conditions'].to_dict(), indent=2))
    
    print("\n=== Sample Trading Opportunity ===")
    print(json.dumps(sample_data['trading_opportunity'].to_dict(), indent=2))
    
    print("\n=== Sample Risk Metrics ===")
    print(json.dumps(sample_data['risk_metrics'].to_dict(), indent=2))
    
    print("\n=== Global State ===")
    print(json.dumps(get_global_state(), indent=2))