import gymnasium as gym
from market_sim.market import MarketSim
from market_sim.sim_config import SimConfig

class MarketEnv(gym.Env):
    def __init__(self, market_config: SimConfig, rem_product):
        super().__init__()
        self.config = market_config
        self.market = MarketSim(market_config)
        self.open_orders = set()
        self.closed_orders = set()

    def reset(self):
        self.market = MarketSim(self.market_config)
        self.open_orders = {}
        self.closed_orders = {}

        obv = self.market.state.to_array()
        return obv, {}


    def step(self, action):
        (order_type, side, price, quantity) = action
        if order_type!="wait":
            order_id, _ = self.market.step(order_type, side, price, quantity)
            self.open_orders.add(order_id)
    
        # compute rewards from waiting orders that were executed after previous step
        reward = 0
        mid_price = self.market.lob.get_mid_price()
        for (order_id, exec_price, exec_quantity) in self.market.executed_orders:
            if order_id in self.open_orders:
                # update 
                self.open_orders.remove(order_id)
                self.closed_orders.add(order_id)
                slippage = -(exec_price - mid_price) / mid_price * exec_quantity
                reward += slippage

        # Iterate background states
        self.market.executed_orders.clear()
        self.market.background_step()

        # terminate if all of the agent's product has been consumed by market or if the simulation is over.
        terminated = (self.market.remiaining_product==0  and len(self.open_orders)==0)
        truncated = len(self.market.state.remaining_steps)==0

        obv = self.market.state.to_array()
        return reward, obv, terminated, truncated, {}


