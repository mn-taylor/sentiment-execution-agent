import random
from abc import ABC, abstractmethod
from market_sim.lob import LimitOrderBook

class Trader(ABC):
    def __init__(self, trader_id):
        self.trader_id = trader_id

    @abstractmethod
    def act(self, lob: LimitOrderBook, sentiment, state):
        """
            Defines the traders actions as a function of the lob
        """
        pass

    @abstractmethod
    def update(self, lob: LimitOrderBook):
        """
            Optionally update trader fields if needed
        """

class MarketMaker(Trader):
    def __init__(self, trader_id, risk_aversion=0.1):
        super().__init__(trader_id)
        self.risk_aversion = risk_aversion
        self.inventory = 0
        self.quantity = 10
        self.order_prob = 0.8 # Make sure not to spam orders

    def act(self, lob: LimitOrderBook, sentiment, state):
        mid = lob.get_mid_price() or 100
        best_bid = lob.get_best_bid() or (mid - 0.5)
        best_ask = lob.get_best_ask() or (mid + 0.5)

        lob_spread = best_ask - best_bid
        inventory_penalty = self.risk_aversion * self.inventory

        spread = max(lob_spread * 0.9, 0.1) # dont want to submit orders that are too tight
        bid_price = mid - spread / 2 - inventory_penalty
        ask_price = mid + spread / 2 + inventory_penalty

        # submit orders on both sides to profit off of the spread
        return ([("limit", "buy", bid_price, self.quantity)] if random.random() < self.order_prob else []) + ([("limit", "sell", ask_price, self.quantity)] if random.random() < self.order_prob else [])
           
    def update(self, lob: LimitOrderBook):
        pass
    

class LiquidityTaker(Trader):
    def __init__(self, trader_id, max_quantity=20):
        super().__init__(trader_id)
        self.max_quantity = max_quantity

    def act(self, lob: LimitOrderBook, sentiment, state):
        side = random.choice(["buy", "sell"])
        quantity = random.randint(1, self.max_quantity)
        return [("market", side, None, quantity)]
    
    def update(self, lob: LimitOrderBook):
        pass
    

class NoiseTrader(Trader):
    def __init__(self, trader_id, 
                 market_order_prob=0.3, 
                 price_deviation=1.0, 
                 max_quantity=10):
        super().__init__(trader_id)
        self.market_order_prob = market_order_prob
        self.price_deviation = price_deviation
        self.max_quantity = max_quantity


    def act(self, lob: LimitOrderBook, sentiment, state):
        # randomly submit market orders
        action_type = "market" if random.random() < self.market_order_prob else "limit"
        side = random.choice(["buy", "sell"])
        quantity = random.randint(1, self.max_quantity)

        if action_type == "market":
            return [("market", side, None, quantity)]
        else:
            mid = lob.get_mid_price() or 100
            price = random.uniform(mid - self.price_deviation, mid + self.price_deviation)
            return [("limit", side, price, quantity)]
        

    def update(self, lob: LimitOrderBook):
        pass


class SentimentMarketMaker(Trader):
    def __init__(self, trader_id, risk_aversion=0.1):
        super().__init__(trader_id)
        self.risk_aversion = risk_aversion
        self.inventory = 0
        self.quantity = 10
        self.order_prob = 0.8 # Make sure not to spam orders
        self.sentiment_sensitivity = 0.01

    def act(self, lob: LimitOrderBook, sentiment, state):
        mid = lob.get_mid_price() or 100
        delta = sentiment * self.sentiment_sensitivity
        best_bid = (lob.get_best_bid() or (mid - 0.5))
        best_ask = lob.get_best_ask() or (mid + 0.5)

        lob_spread = best_bid - best_ask
        inventory_penalty = self.risk_aversion * self.inventory

        spread = max(lob_spread * 0.9, 0.02) # dont want to submit orders that are too tight
        bid_price = mid - spread / 2 - inventory_penalty + delta
        ask_price = mid + spread / 2 - inventory_penalty + delta

        # submit orders on both sides to profit off of the spread
        return ([("limit", "buy", bid_price, self.quantity)] if random.random() < self.order_prob else []) + ([("limit", "sell", ask_price, self.quantity)] if random.random() < self.order_prob else [])
           
    def update(self, lob: LimitOrderBook):
        pass

class SentimentLiquidityTaker(Trader):
    def __init__(self, trader_id, max_quantity=20):
        super().__init__(trader_id)
        self.max_quantity = max_quantity

    def act(self, lob: LimitOrderBook, sentiment, state):
        if random.random() < (1 + sentiment)/2:
            side = "buy"
        else:
            side = "sell"
        quantity = random.randint(1, self.max_quantity)
        return [("market", side, None, quantity)]
    
    def update(self, lob: LimitOrderBook):
        pass