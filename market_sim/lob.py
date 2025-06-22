from sortedcontainers import SortedDict
from collections import deque

class LimitOrderBook:
    def __init__(self):
        self.bids = SortedDict(lambda x: -x)
        self.asks = SortedDict()
        self.order_id_counter = 0
        self.orders = {} # (side, price, quantity, is_agent)

    def add_limit_order(self, side, price, quantity):
        order_id = self.order_id_counter
        self.order_id_counter += 1

        remaining_quantity, trades = self.match_orders(side, quantity, price, order_id)
        if remaining_quantity>0:
            book = self.bids if side=="buy" else self.asks
            if price not in book: # check for new price
                book[price] = deque()
            book[price].append({"id": order_id, "quantity": remaining_quantity})
            self.orders[order_id] = (side, price, remaining_quantity)
        else:
            self.orders[order_id] = (side, price, quantity)
        
        return order_id, trades

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
                trades.append((top_order["id"], best_price, trade_quantity))

                top_order["quantity"] -= trade_quantity
                remaining -= trade_quantity

                if top_order["quantity"]==0: # fulfilled order
                    order_queue.popleft()

            if not order_queue: # No more orders
                del book[best_price]

        return trades # (id, price, quantity)
    
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
    
    
    def match_orders(self, side, quantity, price, order_id):
        opposite_book = self.asks if side=="buy" else self.bids
        remaining_quantity = quantity
        trades = []

        def is_match(p):
            return p <= price if side == "buy" else p >= price
        
        for opp_price in list(opposite_book.keys()):
            if not is_match(opp_price):
                break

            current_level = opposite_book[opp_price]
            while current_level and remaining_quantity>0:
                head = current_level[0]
                match_qty = min(remaining_quantity, head["quantity"])
                trades.append((order_id, opp_price, match_qty))
                trades.append((head["id"], opp_price, match_qty))

                head["quantity"] -= match_qty
                remaining_quantity -= match_qty

                if head["quantity"] == 0:
                    current_level.popleft()

            if not current_level: # all orders filled
                del opposite_book[opp_price]

            if remaining_quantity==0:
                break

        return remaining_quantity, trades
            
    
    def __str__(self):
        def format_side(side):
            lines = []
            book = self.bids if side=="buy" else self.asks
            for price in book:
                total_qty = self.get_volume_at_price(side, price)
                lines.append(f"{price:.2f} x {total_qty}")
            return "\n".join(lines)

        result = []
        result.append("Asks:")
        result.append(format_side("sell") or "None")
        result.append("Bids:")
        result.append(format_side("buy") or "None")
        return "\n".join(result)
    

if __name__ == '__main__':
    lob = LimitOrderBook()
    lob.add_limit_order("sell", 100, 10)
    lob.add_limit_order("buy", 90, 10)
    lob.add_limit_order("buy", 80, 10)

    lob.add_limit_order("buy", 110, 5)

    print(lob)

                                 



    
    

