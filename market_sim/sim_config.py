

class SimConfig():
    def __init__(self, noisy, liquidity_takers, market_makers, sen_market_makers, sen_liquidity_takers, signal, lifetime):
        self.noisy = noisy
        self.liquidity_takers = liquidity_takers
        self.market_makers = market_makers
        self.signal = signal
        self.sen_market_makers = sen_market_makers
        self.sen_liquidity_takers = sen_liquidity_takers
        self.lifetime = lifetime


