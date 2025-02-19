"""
Trading signal definitions for the Fractrade platform.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from decimal import Decimal
import json

class TradeType(Enum):
    PERP = "PERP"
    SPOT = "SPOT"
    EVM = "EVM"


class SignalType(Enum):
    TRADE = "TRADE"


class Side(Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP_LOSS"      # Stop loss order
    TAKE_PROFIT = "TAKE_PROFIT"  # Take profit order


@dataclass
class TradingSignal:
    """Trading signal with all information needed to execute a trade."""
    # Core fields
    signal_id: str
    timestamp: datetime
    type: SignalType
    trade_type: TradeType
    symbol: str
    side: Side
    order_type: OrderType
    
    # Sizing
    amount_capital_percent: Decimal
    fixed_size: Optional[Decimal] = None
    leverage: Optional[Decimal] = None
    
    # Pricing
    limit_price: Optional[Decimal] = None
    stop_price: Optional[Decimal] = None
    take_profit_price: Optional[Decimal] = None
    slippage: Optional[Decimal] = None
    
    # EVM specific
    network: Optional[str] = None
    contract_address: Optional[str] = None
    dex_id: Optional[str] = None
    
    # Position management
    reduce_only: bool = False
    
    # Signal metadata
    message: str
    source: Optional[str] = None
    strategy_name: Optional[str] = None
    timeframe: Optional[str] = None
    exchange: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate and initialize the signal."""
        if not 0 < self.amount_capital_percent <= 100:
            raise ValueError("amount_capital_percent must be between 0 and 100")
        
        if self.trade_type == TradeType.EVM and not self.contract_address:
            raise ValueError("contract_address is required for EVM trades")
        
        if self.order_type in [OrderType.LIMIT] and self.limit_price is None:
            raise ValueError("limit_price is required for LIMIT and POST_ONLY orders")

        if self.order_type == OrderType.STOP_LOSS and self.stop_price is None:
            raise ValueError("stop_price is required for STOP_LOSS orders")
            
        if self.order_type == OrderType.TAKE_PROFIT and self.take_profit_price is None:
            raise ValueError("take_profit_price is required for TAKE_PROFIT orders")
        
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert signal to dictionary format."""
        data = {
            field: getattr(self, field)
            for field in self.__dataclass_fields__
            if getattr(self, field) is not None
        }
        
        for field, value in data.items():
            if isinstance(value, Enum):
                data[field] = value.value
            elif isinstance(value, datetime):
                data[field] = value.isoformat() + 'Z'
            elif isinstance(value, Decimal):
                data[field] = str(value)
                
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TradingSignal':
        """Create a signal from dictionary data."""
        # Convert string enums to Enum instances
        enum_fields = {
            'type': SignalType,
            'trade_type': TradeType,
            'side': Side,
            'order_type': OrderType,
        }
        
        for field, enum_class in enum_fields.items():
            if field in data:
                data[field] = enum_class[data[field]]
                
        # Convert numeric strings to Decimal
        decimal_fields = [
            'amount_capital_percent', 'fixed_size', 'leverage',
            'limit_price', 'stop_price', 'take_profit_price',
            'slippage'
        ]
        for field in decimal_fields:
            if field in data and data[field] is not None:
                data[field] = Decimal(str(data[field]))
                
        return cls(**data)


    def to_json(self) -> str:
        """Directly serialize to JSON string."""
        return json.dumps(self.to_dict(), cls=FracJSONEncoder)

    @classmethod 
    def from_json(cls, json_str: str) -> 'TradingSignal':
        """Create instance directly from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)


# Example usage
if __name__ == "__main__":
    signal_dict = {
        "signal_id": "123e4567-e89b-12d3-a456-426614174000",
        "timestamp": "2024-02-19T12:00:00Z",
        "type": "TRADE",
        "trade_type": "PERP",
        "symbol": "ETH-USDT",
        "side": "BUY",
        "order_type": "LIMIT",
        "amount_capital_percent": "10.0",
        "fixed_size": "1.5",
        "leverage": "10.0",
        "limit_price": "2000.0",
        "message": "ETH breakout trade",
    }
    
    signal = TradingSignal.from_dict(signal_dict)
    print(f"Created signal: {signal}")