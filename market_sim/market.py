from traders import MarketMaker, LiquidityTaker, NoiseTrader, SentimentLiquidityTaker, SentimentMarketMaker
from lob import LimitOrderBook
import matplotlib.pyplot as plt
from sim_config import SimConfig
import pandas as pd
import math

class MarketSim():
    def __init__(self, config: SimConfig):
        # initiate traders with correct ids
        trade_setup = [(config.noisy, NoiseTrader), (config.market_makers, MarketMaker), (config.liquidity_takers, LiquidityTaker), (config.sen_liquidity_takers, SentimentLiquidityTaker), (config.sen_market_makers, SentimentMarketMaker)]
        self.traders = []
        while trade_setup:
            num_traders, trader_class = trade_setup.pop()
            for _ in range(num_traders):
                self.traders.append(trader_class(len(self.traders)))
        
        self.lob = LimitOrderBook()
        self.executed_orders = []
        self.remaining_steps = config.signal.copy()

    def step(self):
        if not self.remaining_steps:
            return False
        
        current_sentiment = self.remaining_steps.pop()
        for trader in self.traders:
            # get trader action
            orders = trader.act(self.lob, current_sentiment)
            for (order_type, side, price, quantity) in orders:
                if order_type=="market":
                    trades = self.lob.add_market_order(side, quantity)
                    self.executed_orders.extend(trades)
                else:
                    order_id, trades = self.lob.add_limit_order(side, price, quantity)
                    self.executed_orders.extend(trades)

            # update traders if needed
            trader.update(self.lob)
        
        
        return True

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
    )
    sim = MarketSim(config)
    mid_prices = []
    spreads = []

    while sim.step():
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
