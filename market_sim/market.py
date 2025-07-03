from market_sim.traders import MarketMaker, LiquidityTaker, NoiseTrader, SentimentLiquidityTaker, SentimentMarketMaker
from market_sim.lob import LimitOrderBook
import matplotlib.pyplot as plt
from market_sim.sim_config import SimConfig
import pandas as pd
import math
import random
import numpy as np

class MarketState():
    def __init__(self, initial_product):
        self.mid_price = None
        self.spread = None
        self.best_bid = None
        self.best_ask = None
        self.sentiment = None
        self.remaining_product = initial_product
        self.volumes = []

    def update(self, lob: LimitOrderBook, sentiment, volume):
        self.mid_price = lob.get_mid_price()
        self.spread = lob.get_spread()
        self.best_ask = lob.get_best_ask()
        self.best_bid = lob.get_best_bid()
        self.sentiment = sentiment
        self.volumes.append(volume)

    def to_array(self, volume_lookback=5):
        volume_tail = self.volumes[-volume_lookback:]
        padded_volumes = [0.0] * (volume_lookback - len(volume_tail)) + volume_tail
        return np.array([
            self.mid_price or 0.0,
            self.spread or 0.0,
            self.best_bid or 0.0,
            self.best_ask or 0.0,
            self.sentiment or 0.0,
            self.remaining_product
        ] + padded_volumes, dtype=np.float32)


class MarketSim():
    def __init__(self, config: SimConfig, initial_product: int):
        # initiate traders with correct ids
        trade_setup = [(config.noisy, NoiseTrader), (config.market_makers, MarketMaker), (config.liquidity_takers, LiquidityTaker), (config.sen_liquidity_takers, SentimentLiquidityTaker), (config.sen_market_makers, SentimentMarketMaker)]
        self.traders = []
        while trade_setup:
            num_traders, trader_class = trade_setup.pop()
            for _ in range(num_traders):
                self.traders.append(trader_class(len(self.traders)))
        
        random.shuffle(self.traders)
        self.lob = LimitOrderBook()
        self.executed_orders = []
        self.volumes = []
        self.remaining_steps = config.signal.copy()
        self.state = MarketState(initial_product)
        self.all_orders = {}
        self.order_lifetime = config.lifetime
        # self.agent = Agent()

    def background_step(self):
        if not self.remaining_steps:
            return False
        
        current_sentiment = self.remaining_steps.pop()
        for trader in self.traders:
            # get trader action
            orders = trader.act(self.lob, current_sentiment, None)
            for (order_type, side, price, quantity) in orders:
                if order_type=="market":
                    # (order_id, exec_price, exec_quantity)
                    trades = self.lob.add_market_order(side, quantity)
                    self.executed_orders.extend(trades)
                else:
                    order_id, trades = self.lob.add_limit_order(side, price, quantity)
                    self.executed_orders.extend(trades)

                volume = 0
                for (_, _, quantity) in trades:
                    volume += quantity
                
                self.volumes.append(volume)

            # update traders if needed
            trader.update(self.lob)
        
        # agent.act(self.state)
        self.state.update(self.lob, current_sentiment, volume)
        
        return True
    
    # Handles orders from an agent.
    def step(self, order_type, side, price, quantity):
        if order_type=="market":
            trades = self.lob.add_market_order(side, quantity)
            self.executed_orders.extend(trades)
            total_exec_quantity = 0
            for (_, _, exec_quantity) in trades: 
                total_exec_quantity += exec_quantity
            order_id = None
            self.state.remaining_product -= total_exec_quantity
        else:
            order_id, trades = self.lob.add_limit_order(side, price, quantity)
            self.state.remaining_product -= quantity
            self.executed_orders.extend(trades)


        # Remove the expired orders
        curr_step = len(self.remaining_steps)
        for (time_stamp, (order_type, side, price, quantity)) in self.all_orders:
            if time_stamp - curr_step > self.order_lifetime:
                del self.all_orders[time_stamp]
                self.state.remaining_product += quantity
        
        # add current order
        self.all_orders[curr_step] = (order_type, side, price, quantity)

        return order_id, trades


if __name__ == "__main__":
    # get signal 
    df = pd.read_csv("data/reddit_headlines/wallstreetbets_interpolated.csv")
    signal = df["sentiment_score"].to_list()
    signal = [x for x in signal if not math.isnan(x)]

    config = SimConfig(
        noisy=80,
        liquidity_takers=10,
        market_makers=10,
        signal = signal,
        sen_liquidity_takers=0,
        sen_market_makers=1,
        lifetime = 20
    )
    sim = MarketSim(config,100)
    mid_prices = []
    spreads = []

    while sim.background_step():
        # print(sim.lob)
        if sim.lob.get_mid_price():
            mid_prices.append(sim.lob.get_mid_price())
        else:
            mid_prices.append(100)

        if sim.lob.get_spread():
            spreads.append(sim.lob.get_spread())
        else:
            spreads.append(0)
        # print("_______________")
        
    fig, axs = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    # Mid Price Evolution
    axs[0].set_title("Mid Price Evolution")
    axs[0].plot(range(len(config.signal)), mid_prices, color="blue")
    axs[0].set_ylabel("Mid Price")

    # Spread Evolution
    axs[1].set_title("Bid-Ask Spread Evolution")
    axs[1].plot(range(len(config.signal)), spreads, color="green")
    axs[1].set_xlabel("Time Step")
    axs[1].set_ylabel("Spread")

    plt.tight_layout()
    plt.savefig("market_sim/price_and_spread_evolution.png")
    plt.close()
