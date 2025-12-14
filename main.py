import tkinter as tk
from tkinter import ttk
from components.ticker import CryptoTicker
from components.orderbook import OrderBookPanel
from components.chart import ChartPanel
from components.trades import TradesPanel

import json
import os

PANEL_ORDER = ["btc", "eth", "sol", "bnb", "xrp"]

class MultiTickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Crypto Dashboard")
        self.root.geometry("1400x800") # Increased size for details

        self.prefs_file = "prefs.json"
        self.preferences = self.load_preferences()

        # Control Panel
        control_frame = ttk.Frame(root, padding=10)
        control_frame.pack(fill=tk.X)

        self.ticker_btns = {}
        for key in PANEL_ORDER:
            btn = ttk.Button(control_frame, text=f"Hide {key.upper()}",
                             command=lambda k=key: self.toggle_ticker(k))
            btn.pack(side=tk.LEFT, padx=5)
            self.ticker_btns[key] = btn

        # Details Label
        self.detail_var = tk.StringVar(value="Select a ticker to view details (Default: BTC)")
        ttk.Label(control_frame, textvariable=self.detail_var, font=("Arial", 12, "italic")).pack(side=tk.RIGHT, padx=20)

        # Ticker Panel
        self.ticker_frame = ttk.Frame(root, padding=20)
        self.ticker_frame.pack(fill=tk.X)

        # Create Tickers
        self.tickers = {}
        self.create_ticker("btc", "btcusdt", "BTC/USDT")
        self.create_ticker("eth", "ethusdt", "ETH/USDT")
        self.create_ticker("sol", "solusdt", "SOL/USDT")
        self.create_ticker("bnb", "bnbusdt", "BNB/USDT")
        self.create_ticker("xrp", "xrpusdt", "XRP/USDT")

        # Detail Panel (Bottom)
        self.detail_frame = ttk.Frame(root, padding=10, relief="sunken")
        self.detail_frame.pack(fill=tk.BOTH, expand=True)

        # Sub-panels
        # Order Book (Left)
        self.ob_panel = OrderBookPanel(self.detail_frame, "btcusdt")
        self.ob_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.ob_panel.start()

        # Chart (Center)
        self.chart_panel = ChartPanel(self.detail_frame, "btcusdt")
        self.chart_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.chart_panel.start()

        # Trades (Right)
        self.trades_panel = TradesPanel(self.detail_frame, "btcusdt")
        self.trades_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.trades_panel.start()

        self.active_symbol = "btcusdt"

        # Apply preferences
        self.apply_preferences()

    def create_ticker(self, key, symbol, name):
        """Helper to create and start a ticker."""
        # Pass click handler
        ticker = CryptoTicker(self.ticker_frame, symbol, name, on_click=self.on_ticker_click)
        ticker.start()
        self.tickers[key] = {"component": ticker, "visible": True}

    def on_ticker_click(self, symbol):
        """Handle ticker click event."""
        if self.active_symbol == symbol:
            return

        print(f"Switched details to: {symbol}")
        self.active_symbol = symbol
        self.detail_var.set(f"Viewing Details: {symbol.upper()}")

        # Update selection highlight
        for key in self.tickers:
            t = self.tickers[key]["component"]
            if t.symbol == symbol:
                t.set_selected(True)
            else:
                t.set_selected(False)

        # Update panels
        self.ob_panel.change_symbol(symbol)
        self.chart_panel.change_symbol(symbol)
        self.trades_panel.change_symbol(symbol)

    def toggle_ticker(self, key):
        """Toggle ticker visibility."""
        data = self.tickers[key]

        if data["visible"]:
            data["visible"] = False
        else:
            data["visible"] = True

        self.repack_all()
        self.update_button_text(key)
        self.save_preferences()

    def repack_all(self):
        """Ensure safe ordering when showing hidden tickers."""
        # Unpack all first
        for key in PANEL_ORDER:
            if key in self.tickers:
                self.tickers[key]["component"].pack_forget()

        # Repack visible ones in order
        for key in PANEL_ORDER:
            if key in self.tickers and self.tickers[key]["visible"]:
                self.tickers[key]["component"].pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)

    def update_button_text(self, key):
        btn = self.ticker_btns[key]
        name = key.upper()
        action = "Hide" if self.tickers[key]["visible"] else "Show"
        btn.config(text=f"{action} {name}")

    def load_preferences(self):
        if os.path.exists(self.prefs_file):
            try:
                with open(self.prefs_file, "r") as f:
                    return json.load(f)
            except:
                pass
        return {}

    def save_preferences(self):
        prefs = {k: self.tickers[k]["visible"] for k in self.tickers}
        with open(self.prefs_file, "w") as f:
            json.dump(prefs, f)

    def apply_preferences(self):
        """Restore visibility state."""
        for key in PANEL_ORDER:
            if key in self.tickers:
                # Default to True if not in prefs
                is_visible = self.preferences.get(key, True)
                self.tickers[key]["visible"] = is_visible
                self.update_button_text(key)

        self.repack_all()

    def on_closing(self):
        """Clean up resources when closing the app."""
        self.save_preferences()

        # Stop tickers
        for key in self.tickers:
            self.tickers[key]["component"].stop()

        # Stop detail panels
        self.ob_panel.stop()
        self.chart_panel.stop()
        self.trades_panel.stop()

        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MultiTickerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
