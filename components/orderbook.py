import tkinter as tk
from tkinter import ttk
import threading
import json
import ssl
import certifi
import websocket
from config import *

class OrderBookPanel:
    def __init__(self, parent, symbol="btcusdt"):
        self.parent = parent
        self.symbol = symbol.lower()
        self.is_active = False
        self.ws = None

        self.frame = ttk.LabelFrame(parent, text=f"Order Book ({self.symbol.upper()})", padding=10)

        # Grid layout for Bids and Asks
        # Headers
        ttk.Label(self.frame, text="Price (USDT)", font=("Arial", 10, "bold"), foreground="gray").grid(row=0, column=0)
        ttk.Label(self.frame, text="Qty", font=("Arial", 10, "bold"), foreground="gray").grid(row=0, column=1)
        ttk.Label(self.frame, text="Price (USDT)", font=("Arial", 10, "bold"), foreground="gray").grid(row=0, column=2)
        ttk.Label(self.frame, text="Qty", font=("Arial", 10, "bold"), foreground="gray").grid(row=0, column=3)

        # Placeholders
        self.bid_labels = [] # (price_label, qty_label)
        self.ask_labels = [] # (price_label, qty_label)

        for i in range(10):
            # Bids (Green)
            bp = ttk.Label(self.frame, text="--", foreground=COLOR_UP)
            bq = ttk.Label(self.frame, text="--")
            bp.grid(row=i+1, column=0, padx=5)
            bq.grid(row=i+1, column=1, padx=5)
            self.bid_labels.append((bp, bq))

            # Asks (Red)
            ap = ttk.Label(self.frame, text="--", foreground=COLOR_DOWN)
            aq = ttk.Label(self.frame, text="--")
            ap.grid(row=i+1, column=2, padx=5)
            aq.grid(row=i+1, column=3, padx=5)
            self.ask_labels.append((ap, aq))

    def start(self):
        if self.is_active: return
        self.is_active = True

        # Partial Depth Stream: <symbol>@depth<levels>@1000ms
        ws_url = f"{BINANCE_WS_URL}/{self.symbol}@depth10@1000ms"

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
            self.frame.after(0, self.update_ui, data)
        except Exception as e:
            print(f"OrderBook Error: {e}")

    def update_ui(self, data):
        bids = data.get('bids', [])
        asks = data.get('asks', [])

        # Update Bids
        for i, (price, qty) in enumerate(bids[:10]):
            pl, ql = self.bid_labels[i]
            pl.config(text=f"{float(price):.2f}")
            ql.config(text=f"{float(qty):.4f}")

        # Update Asks
        for i, (price, qty) in enumerate(asks[:10]):
            pl, ql = self.ask_labels[i]
            pl.config(text=f"{float(price):.2f}")
            ql.config(text=f"{float(qty):.4f}")

    def change_symbol(self, new_symbol):
        if self.symbol == new_symbol: return

        self.stop()
        self.symbol = new_symbol
        self.frame.config(text=f"Order Book ({self.symbol.upper()})")
        self.start()

    def on_error(self, ws, error):
        print(f"OrderBook WS Error: {error}")

    def on_close(self, ws, status, msg):
        print("OrderBook WS Closed")

    def on_open(self, ws):
        print("OrderBook WS Connected")

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)

    def pack_forget(self):
        self.frame.pack_forget()
