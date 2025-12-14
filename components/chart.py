import tkinter as tk
from tkinter import ttk
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading
from config import *
import datetime

import tkinter as tk
from tkinter import ttk
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading
from config import *
import datetime
import matplotlib.dates as mdates

class ChartPanel:
    def __init__(self, parent, symbol="btcusdt"):
        self.parent = parent
        self.symbol = symbol.upper()
        self.is_active = False

        self.frame = ttk.LabelFrame(parent, text=f"Chart ({self.symbol})", padding=10)

        # Matplotlib Figure with 2 subplots (Price, Volume)
        # sharex=True to align time axis
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.fig.patch.set_facecolor("white") # Main background (can be chart bg)

        # GridSpec for 70% Price, 30% Volume
        gs = self.fig.add_gridspec(2, 1, height_ratios=[3, 1], hspace=0.1)
        self.ax_price = self.fig.add_subplot(gs[0])
        self.ax_vol = self.fig.add_subplot(gs[1], sharex=self.ax_price)

        # Styling
        self.ax_price.set_facecolor("white")
        self.ax_vol.set_facecolor("white")

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.update_interval = 60000 # 1 minute refresh

    def start(self):
        if self.is_active: return
        self.is_active = True
        self.fetch_data()

    def stop(self):
        self.is_active = False

    def fetch_data(self):
        if not self.is_active: return

        threading.Thread(target=self._fetch_and_plot, daemon=True).start()

        # Schedule next update
        self.parent.after(self.update_interval, self.fetch_data)

    def _fetch_and_plot(self):
        try:
            url = f"{BINANCE_BASE_URL}/api/v3/klines"
            params = {
                "symbol": self.symbol,
                "interval": "1h",
                "limit": 50 # Increase limit for better chart
            }
            response = requests.get(url, params=params)
            data = response.json()

            # Parse data
            # [time, open, high, low, close, vol, ...]
            opens = []
            highs = []
            lows = []
            closes = []
            volumes = []
            times = []

            for candle in data:
                # Binance time is ms
                t = datetime.datetime.fromtimestamp(candle[0]/1000)
                times.append(t)
                opens.append(float(candle[1]))
                highs.append(float(candle[2]))
                lows.append(float(candle[3]))
                closes.append(float(candle[4]))
                volumes.append(float(candle[5]))

            # Plot on main thread
            self.parent.after(0, self.plot, times, opens, highs, lows, closes, volumes)

        except Exception as e:
            print(f"Chart Error: {e}")

    def plot(self, times, opens, highs, lows, closes, volumes):
        self.ax_price.clear()
        self.ax_vol.clear()

        # Convert times to matplotlib numbers for proper width handling if needed
        # But index-based plotting is often simpler for intraday gaps.
        # Using simple index for X-axis to keep candles uniform width.
        x_vals = range(len(times))

        up_color = "#0ECB81" # Green
        down_color = "#F6465D" # Red

        # Iterate to draw candles
        for i in x_vals:
            open_p = opens[i]
            close_p = closes[i]
            high_p = highs[i]
            low_p = lows[i]
            vol = volumes[i]

            color = up_color if close_p >= open_p else down_color

            # --- Candlestick ---
            # Wick (Line)
            self.ax_price.plot([i, i], [low_p, high_p], color=color, linewidth=1)

            # Body (Bar)
            height = abs(close_p - open_p)
            bottom = min(open_p, close_p)
            # Ensure height is visible even if flat
            if height == 0: height = min(high_p - low_p, close_p*0.0001) or 0.01 

            self.ax_price.bar(i, height, bottom=bottom, color=color, width=0.6, align='center')

            # --- Volume ---
            self.ax_vol.bar(i, vol, color=color, width=0.6, align='center')

        # Formatting Price Axis
        self.ax_price.set_title(f"{self.symbol} 1H Chart (Binance)", color="black", fontsize=10)
        self.ax_price.grid(True, linestyle='--', linewidth=0.5, alpha=0.5)
        # Last price line
        last_price = closes[-1]
        self.ax_price.axhline(last_price, color='blue', linestyle='--', linewidth=1, alpha=0.7)
        self.ax_price.text(x_vals[-1]+1, last_price, f"{last_price:,.2f}", color="blue", va='center', fontsize=8)

        # Formatting Volume Axis
        self.ax_vol.set_ylabel("Volume", fontsize=8)
        self.ax_vol.grid(True, linestyle='--', linewidth=0.5, alpha=0.5)

        # Format X Axis (Dates)
        # We need to map indexes back to formatting
        # Show only some ticks
        tick_step = max(1, len(times)//5)
        self.ax_vol.set_xticks(list(x_vals)[::tick_step])
        self.ax_vol.set_xticklabels([t.strftime('%H:%M') for t in times[::tick_step]], rotation=30, ha='right', fontsize=8)

        # Hide default labels on price axis X to avoid clutter
        plt.setp(self.ax_price.get_xticklabels(), visible=False)

        self.fig.tight_layout()
        self.canvas.draw()

    def change_symbol(self, new_symbol):
        if self.symbol == new_symbol: return
        self.stop()
        self.symbol = new_symbol.upper()
        self.frame.config(text=f"Chart ({self.symbol})")
        self.start()

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)

    def pack_forget(self):
        self.frame.pack_forget()
