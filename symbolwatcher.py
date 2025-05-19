import math
import matplotlib.pyplot as plt
import yfinance as yf
from matplotlib.animation import FuncAnimation

# PERIOD is the amount of history dating back that should be retrieved, 1d = intraday, 2d = intraday + 1 day back etc.
# INTERVAL is the granularity of the data. Only 8 days worth of 1m granularity data are allowed to be fetched per request.
PERIOD = "1d"
INTERVAL = "1m"

# Currency Settings
DISPLAYED_CURRENCY = "SEK"

# Display settings
SCREEN_DIVISION_X = 4  # If more than X stocks, divide graphs into SCREEN_DIVISION_Y columns
SCREEN_DIVISION_Y = 2  # Number of columns to be had

# Update INTERVAL (milliseconds)
UPDATE_INTERVAL = 120_000  # 60 seconds = 60_000

# Plot colours
OPEN_COLOUR = "red"
CLOSE_COLOUR = "green"
HILO_INT_COLOUR = "orange"
CLOSE_OPEN_INT_COLOUR = "red"
VOLUME_COLOUR = "grey"

# Add your holdings: amount and price of specific symbols
holdings = {
    "SAAB-B.ST": [1, 500],
    "SSAB-B.ST": [1, 500],
    "^OMX": [0, 0],
    "MSFT": [1, 500],
    "AAPL": [5, 100],
    "AMZN": [1, 100],
}

def convert_to_display_currency(ticker):
    """
    Convert a stock's currency to the displayed currency.

    Args:
        ticker: the symbol to get the last closed price from and convert price to displayed currency

    Returns:
        float: The value converted to the displayed currency.
    """
    stock = yf.Ticker(ticker)
    history = stock.history()
    stocklastclosed = history['Close'].iloc[-1]
    currencystring = DISPLAYED_CURRENCY + stock.info['currency'] + "=X"
    currencyticker = yf.Ticker(currencystring)
    history = currencyticker.history()
    currencylastclosed = history['Close'].iloc[-1]
    value = stocklastclosed / currencylastclosed
    return value

def update_graphs(_):
    """
    Update and redraw stock graphs for each holding.

    Iterates through all tickers in the holdings dictionary, fetches the latest
    1-day, 1-minute INTERVAL historical data using yfinance, and updates the
    corresponding matplotlib axes with price and volume information. The function
    plots closing and opening prices, fills the area between high and low as well
    as close and open, and displays volume as a bar chart on a secondary y-axis.
    It also updates the subplot titles with current price, total value, price
    difference, percentage change, and purchase difference. The figure's main
    title is updated with the total portfolio value and total value change.

    Args:
        _ (Any): Placeholder argument, not used.

    Returns:
        None

    Notes:
        - Assumes global variables: holdings, axes, fig, CLOSE_COLOUR, OPEN_COLOUR,
          HILO_INT_COLOUR, CLOSE_OPEN_INT_COLOUR, VOLUME_COLOUR are defined.
        - Intended for use in a GUI or plotting callback to refresh displayed data.
    """
    total_value = 0
    total_valchange = 0
    for idx, ticker in enumerate(holdings.keys()):
        stock = yf.Ticker(ticker)
        history = stock.history(period=PERIOD, interval=INTERVAL)         
        datetime_index = history.index
        closing = history["Close"]
        opening = history["Open"]
        high = history["High"]
        low = history["Low"]
        volume = history["Volume"]
        current_ax = axes[idx]
        current_ax.clear()
        current_ax.plot(datetime_index, closing, label="Close", color=CLOSE_COLOUR)
        current_ax.plot(datetime_index, opening, label="Open", color=OPEN_COLOUR)
        current_ax.fill_between(
            datetime_index, low, high, color=HILO_INT_COLOUR, alpha=0.3, label="High-Low INTERVAL"
        )
        current_ax.fill_between(
            datetime_index, closing, opening, color=CLOSE_OPEN_INT_COLOUR, alpha=0.3, label="Close-Open INTERVAL"
        )
        amountholding, price = holdings[ticker]
        # converts currency to displayed currency
        if stock.info['currency'] != DISPLAYED_CURRENCY:
            convertedprice = convert_to_display_currency(ticker)
            total_value += convertedprice * amountholding
            current_total = convertedprice * amountholding
            purchased_difference = current_total - (amountholding * convertedprice)
        # if nothing to convert, default to actual
        else:
            total_value += closing.iloc[-1] * amountholding
            current_total = closing.iloc[-1] * amountholding
            purchased_difference = current_total - (amountholding * price)
        total_valchange += purchased_difference
        previous_close = history["Close"].iloc[0]
        difference = closing.iloc[-1] - previous_close
        percentage_change = (difference / previous_close) * 100
        current_ax.set_title(
            f"{ticker} : Close: {closing.iloc[-1]:.2f} : {current_total:.2f} : "
            f"Diff: {difference:.2f} ({percentage_change:.2f}%) : "
            f"Purch. Diff. {purchased_difference:.2f}",
            fontsize=10,
        )
        current_ax.grid(True)
        ax2 = current_ax.twinx()
        ax2.bar(
            datetime_index, volume, color=VOLUME_COLOUR, alpha=0.5, label="Volume", width=0.001
        )
        ax2.set_ylabel("Volume")
    fig.suptitle(
        f"Total Value: {total_value:.2f} : Change: {total_valchange:.2f}", fontsize=12
    )


if __name__ == "__main__":
    print(
        f"""
          Legend:
          Open Colour: {OPEN_COLOUR}
          Close Colour: {CLOSE_COLOUR}
          High-Low INTERVAL Colour: {HILO_INT_COLOUR}
          Close-Open INTERVAL Colour: {CLOSE_OPEN_INT_COLOUR}
          Volume Colour: {VOLUME_COLOUR}
"""
    )
    if len(holdings) == 1:
        fig, axes_obj = plt.subplots(1, 1)
        axes = [axes_obj]
    elif len(holdings) > SCREEN_DIVISION_X:
        graph_n_row = math.ceil(len(holdings) / SCREEN_DIVISION_Y)
        fig, axes = plt.subplots(graph_n_row, SCREEN_DIVISION_Y, squeeze=False)
        axes = axes.flatten()
    else:
        fig, axes = plt.subplots(len(holdings), 1, squeeze=False)
        axes = axes.flatten()
    fig.canvas.manager.set_window_title("Symbol Watcher")
    ani = FuncAnimation(
        fig, update_graphs, interval=UPDATE_INTERVAL, cache_frame_data=False
    )
    plt.tight_layout(h_pad=1, w_pad=1, rect=[0, 0.05, 0.95, 0.9])
    plt.show()
