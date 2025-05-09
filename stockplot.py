# MIT LICENSE 2025import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import yfinance as yf
from matplotlib.animation import FuncAnimation

### insert your holdings here ###
# "SYMBOL", AMOUNT OF STOCKS INTEGER #
holdings = {"MSFT": 57,
           "AAPL": 161,
           "IPCO.ST": 0}

def update_graphs(_):
    total_value = 0
    for idx, ticker in enumerate(holdings.keys()):
        stock = yf.Ticker(ticker)
        history = stock.history(period="1d", interval="1m")
        datetime_index = history.index
        closing = history['Close']
        opening = history['Open']
        high = history['High']
        low = history['Low']
        volume = history['Volume']
        current_ax = axes[idx]
        current_ax.clear()
        current_ax.plot(datetime_index, closing, label="Close", color="green")
        current_ax.plot(datetime_index, opening, label="Open", color="blue")
        current_ax.fill_between(datetime_index, low, high, color="orange", alpha=0.3, label="High-Low interval")
        current_ax.fill_between(datetime_index, closing, opening, color="red", alpha=0.3, label="Close-Open interval")
        total_value += closing.iloc[-1] * holdings[ticker]
        current_total = closing.iloc[-1] * holdings[ticker]
        current_ax.set_title(f"{ticker} : Close: {closing.iloc[-1]:.2f} : {current_total:.2f}", fontsize=10)
        current_ax.grid(True)
        ax2 = current_ax.twinx()
        ax2.bar(datetime_index, volume, color="grey", alpha=0.5, label="Volume", width=0.001)
        ax2.set_ylabel("Volume")
    fig.suptitle(f"Total Value: {total_value:.2f}", fontsize=12)

if __name__ == "__main__":
    if len(holdings) == 1:
        fig, axes_obj = plt.subplots(1, 1)
        axes = [axes_obj]
    else:
        fig, axes = plt.subplots(len(holdings), 1, squeeze=False)
        axes = axes.flatten()
    fig.canvas.manager.set_window_title("Symbol Watcher")
    ani = FuncAnimation(fig, update_graphs, interval=120000, cache_frame_data=False)
    plt.tight_layout(h_pad=0.5, w_pad=0.5, rect=[0, 0.03, 1, 0.95])
    plt.show()
