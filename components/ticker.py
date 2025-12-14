import tkinter as tk
from tkinter import ttk
import certifi
import ssl
import socket
import websocket
import json
import threading
from config import *

class CryptoTicker:
    """
    Reusable ticker component for a single cryptocurrency.
    Manages its own WebSocket connection and UI updates.
    """
    def __init__(self, parent, symbol, display_name, on_click=None):
        self.parent = parent
        self.symbol = symbol.lower()
        self.display_name = display_name
        self.on_click = on_click
        self.is_active = False
        self.ws = None

        self.ws = None

        # Create UI
        self.frame = tk.Frame(parent, relief="solid", borderwidth=1, bg="white")

        # Bind click events
        self.init_ui_elements()
        self.bind_click(self.frame)

    def bind_click(self, widget):
        widget.bind("<Button-1>", self.handle_click)
        for child in widget.winfo_children():
            self.bind_click(child)

    def handle_click(self, event):
        if self.on_click:
            self.on_click(self.symbol)

        # Add visual feedback? (Maybe change background slightly?)

    def init_ui_elements(self):
        # We moved UI creation to ensure we can bind events to them
        # Title
        l1 = tk.Label(self.frame, text=self.display_name, font=FONT_TITLE, bg="white", fg="black")
        l1.pack(pady=(15, 5)) # Add padding manually since tk.Frame doesn't have 'padding' arg
        self.bind_click(l1)
        self.title_label = l1

        # Price
        self.price_label = tk.Label(self.frame, text="--,---", font=FONT_PRICE, bg="white")
        self.price_label.pack(pady=10)
        self.bind_click(self.price_label)

        # Change
        self.change_label = tk.Label(self.frame, text="--", font=FONT_CHANGE, bg="white")
        self.change_label.pack()
        self.bind_click(self.change_label)

        # Volume
        self.volume_label = tk.Label(self.frame, text="Vol: --", font=FONT_CHANGE, bg="white", fg="gray")
        self.volume_label.pack(pady=(5, 15))
        self.bind_click(self.volume_label)

    def set_selected(self, selected):
        """Highlight the ticker if selected."""
        bg_color = "#e0e0e0" if selected else "white"
        self.frame.config(bg=bg_color)
        self.title_label.config(bg=bg_color)
        self.price_label.config(bg=bg_color)
        self.change_label.config(bg=bg_color)
        self.volume_label.config(bg=bg_color)

        if selected:
            self.frame.config(relief="sunken", borderwidth=2)
        else:
            self.frame.config(relief="solid", borderwidth=1)

    def start(self):
        """Start WebSocket connection in a separate thread."""
        if self.is_active:
            return

        self.is_active = True
        ws_url = f"{BINANCE_WS_URL}/{self.symbol}@ticker"

        # Create SSL context using certifi
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
        """Stop WebSocket connection."""
        self.is_active = False
        if self.ws:
            self.ws.close()
            self.ws = None

    def on_message(self, ws, message):
        """Handle incoming WebSocket messages."""
        if not self.is_active:
            return

        try:
            data = json.loads(message)
            price = float(data['c'])
            change = float(data['p'])
            percent = float(data['P'])
            volume = float(data['q']) # Quote asset volume (e.g. USDT volume)

            # Schedule UI update on the main thread
            self.parent.after(0, self.update_display, price, change, percent, volume)
        except Exception as e:
            print(f"Error parsing message: {e}")

    def update_display(self, price, change, percent, volume):
        """Update the UI with new price data."""
        if not self.is_active:
            return

        color = COLOR_UP if change >= 0 else COLOR_DOWN
        self.price_label.config(text=f"{price:,.2f}", fg=color)

        sign = "+" if change >= 0 else ""
        self.change_label.config(
            text=f"{sign}{change:,.2f} ({sign}{percent:.2f}%)",
            foreground=color
        )

        self.volume_label.config(text=f"Vol: {volume:,.0f}")

    def on_error(self, ws, error):
        print(f"WebSocket Error ({self.symbol}): {error}")

    def on_close(self, ws, status, msg):
        print(f"WebSocket Closed ({self.symbol})")

    def on_open(self, ws):
        print(f"WebSocket Connected ({self.symbol})")

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)

    def pack_forget(self):
        self.frame.pack_forget()
