Here is a comprehensive **README.md** for your project, written in English and based on the provided source code.

-----

# 📈 Crypto Dashboard App

A professional, real-time cryptocurrency monitoring dashboard built with **Python** and **Tkinter**. This application connects directly to the **Binance API** via WebSockets and REST services to provide live market data.

## ✨ Features

  * **Real-time Price Tickers:** Tracks live prices, 24h price changes (percentage and absolute), and 24h trading volume for major pairs like BTC, ETH, SOL, BNB, and XRP.
  * **Interactive Navigation:** Users can click on any ticker card to instantly switch the detailed view (Chart, Order Book, and Trades) to that specific cryptocurrency.
  * **Live Candlestick Charts:** Displays 1-hour interval candlestick data and volume bars using **Matplotlib**. The chart includes a blue reference line for the last price.
  * **Dynamic Order Book:** Shows the top 10 real-time bids and asks (prices and quantities) directly from the Binance order book stream.
  * **Recent Trade History:** A live-scrolling list of the latest trades, color-coded for buys (green) and sells (red).
  * **UI Customization:** Includes buttons to show or hide specific tickers to clean up the dashboard workspace.
  * **Persistent Settings:** Automatically saves your ticker visibility preferences to a `prefs.json` file, restoring your layout the next time you open the app.

-----

## 🏗️ Project Structure

The application is designed using a modular component-based architecture:

  * **`main.py`**: The entry point of the application. It handles the layout, component synchronization, and user preferences.
  * **`config.py`**: Centralized configuration for Binance API URLs, professional color schemes (Binance Green/Red), and UI fonts.
  * **`ticker.py`**: A reusable component for individual price cards with dedicated WebSocket connections.
  * **`chart.py`**: Manages data fetching for K-lines and rendering the Matplotlib candlestick interface.
  * **`orderbook.py`**: Connects to the Binance Depth stream to display the limit order book.
  * **`trades.py`**: Handles the individual trade stream and updates the historical trade table.

-----

## 🛠️ Prerequisites

To run this application, you need to install the following Python libraries:

```bash
pip install requests websocket-client matplotlib certifi
```

-----

## 🚀 Getting Started

1.  **Clone the repository** and ensure all files (`main.py`, `config.py`, and components) are in their respective directories as defined in the imports.
2.  **Launch the application**:
    ```bash
    python main.py
    ```
3.  **Interaction**:
      * The top panel shows your active tickers.
      * Click a ticker to update the bottom detail panels.
      * Use the "Hide/Show" buttons at the top to toggle visibility.

-----

## 🎨 Visual Design

  * **Upward Trend:** Represented by Binance Green (`#0ECB81`).
  * **Downward Trend:** Represented by Binance Red (`#F6465D`).
  * **Responsiveness:** Utilizes Python's `threading` and `tkinter.after` to ensure the UI remains smooth and responsive while handling multiple high-frequency data streams.

-----
