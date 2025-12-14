import tkinter as tk
from tkinter import ttk
import threading
import json
import ssl
import certifi
import websocket
from config import *
import datetime

class TradesPanel:
    def __init__(self, parent, symbol="btcusdt"):
        self.parent = parent
        self.symbol = symbol.lower()
        self.is_active = False
        self.ws = None

        self.frame = ttk.LabelFrame(parent, text=f"Recent Trades ({self.symbol.upper()})", padding=10)

        # Treeview for details
        columns = ("time", "price", "qty")
        self.tree = ttk.Treeview(self.frame, columns=columns, show="headings", height=10)
        self.tree.heading("time", text="Time")
        self.tree.heading("price", text="Price")
        self.tree.heading("qty", text="Qty")

        self.tree.column("time", width=80)
        self.tree.column("price", width=100)
        self.tree.column("qty", width=100)

        self.tree.pack(fill=tk.BOTH, expand=True)

    def start(self):
        if self.is_active: return
        self.is_active = True

        ws_url = f"{BINANCE_WS_URL}/{self.symbol}@trade"

        ssl_context = ssl.create_default_context(cafile=certifi.where())
        self.ws = websocket.WebSocketApp(
            ws_url,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
             on_open=self.on_open
        )

        threading.Thread(target=self.ws.run_forever, kwargs={"sslopt": {"context": ssl_context}}, daemon=True).start()

    def stop(self):
        self.is_active = False
        if self.ws:
            self.ws.close()
            self.ws = None

    def on_message(self, ws, message):
        if not self.is_active: return
        try:
            data = json.loads(message)
            self.frame.after(0, self.add_trade, data)
        except Exception as e:
            print(f"Trade Error: {e}")

    def add_trade(self, data):
        # Data: e, E, s, t, p, q, b, a, T, m, M
        # p = price, q = quantity, T = trade time, m = isBuyerMaker (True=Sell, False=Buy)

        price = float(data['p'])
        qty = float(data['q'])
        timestamp = data['T']
        is_buyer_maker = data['m']

        time_str = datetime.datetime.fromtimestamp(timestamp/1000).strftime('%H:%M:%S')

        color = COLOR_DOWN if is_buyer_maker else COLOR_UP # Maker=Sell -> Red, Maker=Buy(Taker=Sell) -> Red? 
        # isBuyerMaker = True -> The maker was a buyer. The taker was a seller. So it's a SELL trade ( Red ).
        # isBuyerMaker = False -> The maker was a seller. The taker was a buyer. So it's a BUY trade ( Green ).

        tag = "sell" if is_buyer_maker else "buy"

        item = self.tree.insert("", 0, values=(time_str, f"{price:,.2f}", f"{qty:,.4f}"), tags=(tag,))

        # Keep list short
        if len(self.tree.get_children()) > 20:
            self.tree.delete(self.tree.get_children()[-1])

        self.tree.tag_configure("buy", foreground=COLOR_UP)
        self.tree.tag_configure("sell", foreground=COLOR_DOWN)

    def change_symbol(self, new_symbol):
        if self.symbol == new_symbol: return
        self.stop()
        self.symbol = new_symbol
        self.frame.config(text=f"Recent Trades ({self.symbol.upper()})")
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.start()

    def on_error(self, ws, error):
        print(f"Trade WS Error: {error}")

    def on_close(self, ws, status, msg):
        print("Trade WS Closed")

    def on_open(self, ws):
        print("Trade WS Connected")

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)

    def pack_forget(self):
        self.frame.pack_forget()
