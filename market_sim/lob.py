from sortedcontainers import SortedDict
from collections import deque

class LimitOrderBook:
    def __init__(self):
        self.bids = SortedDict(lambda x: -x)
        self.asks = SortedDict()
        self.order_id_counter = 0
        self.orders = {} # (side, price, quantity)

    def add_limit_order(self, side, price, quantity):
        order_id = self.order_id_counter
        self.order_id_counter += 1

        book = self.bids if side=="buy" else self.asks
        if price not in book: # check for new price
            book[price] = deque()

        book[price].append({"id": order_id, "quantity": quantity})
        self.orders[order_id] = (side, price, quantity)
        return order_id    

    def add_market_order(self, side, quantity):
        trades = []
        book = self.asks if side=="buy" else self.bids # take from the opposite side
        remaining = quantity

        while remaining > 0 and book:
            best_price = next(iter(book))
            order_queue = book[best_price]

            while order_queue and remaining > 0:
                top_order = order_queue[0]
                trade_quantity = min(top_order["quantity"], remaining)
                trades.append((best_price, trade_quantity))

                top_order["quantity"] -= trade_quantity
                remaining -= trade_quantity

                if top_order["quantity"]==0: # fulfilled order
                    order_queue.pop_left()

            if not order_queue: # No more orders
                del book[best_price]

        return trades # (price, quantity)
    
    def cancel_order(self, order_id):
        if order_id not in self.orders:
            return False

        side, price, _ = self.orders[order_id]
        book = self.bids if side == "buy" else self.asks
        if price in book:
            book[price] = deque([x for x in book[price] if x["id"]!=order_id])
            if not book[price]:
                del book[price]

        del self.orders[order_id]
        return True
    
    def get_best_bid(self):
        return next(iter(self.bids)) if self.bids else None
    
    def get_best_ask(self):
        return next(iter(self.asks)) if self.asks else None
    
    def get_mid_price(self):
        best_bid = self.get_best_bid()
        best_ask = self.get_best_ask()
        if best_bid is None or best_ask is None:
            return None
        
        return 0.5 * (best_bid + best_ask)
    

    def get_volume_at_price(self, side, price):
        book = self.bids if side =="buy" else self.asks
        if price not in book:
            return 0
        return sum(order["quantity"] for order in book[price])
    

    def get_book_snapshot(self, depth=1):
        bid_levels = list(self.bids.items())[:depth]
        ask_levels = list(self.asks.items())[:depth]

        return {
            "bids": [(p, sum(o["quantity"] for o in q)) for p, q in bid_levels],
            "asks": [(p, sum(o["quantity"] for o in q)) for p, q in ask_levels]
        }
    
                                 



    
    

