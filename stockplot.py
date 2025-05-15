import matplotlib.pyplot as plt
import yfinance as yf
from matplotlib.animation import FuncAnimation
import math

### display settings ###
screendivisionx = 4 # if more than X stocks, divide graphs into variable "screendivisiony" columns
screendivisiony = 2 # int columns to be had

### update interval ###
updateinterval=120000 # 60seconds = 60000

### plot colours ###
opencolour="red"
closecolour="green"
hilointcolour="orange"
closeopenintcolour="red"
volumecolour="grey"

### add your holdings. amount and price of specific symbols ###
holdings = {"SAAB-B.ST": [1, 500],
           "SSAB-B.ST": [1, 500],
           "^OMX": [0, 0],
           "MSFT": [1,500],
           "AAPL": [5,100],
           "AMZN": [1, 100]}

def update_graphs(_):
    total_value = 0
    total_valchange = 0
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
        current_ax.plot(datetime_index, closing, label="Close", color=closecolour)
        current_ax.plot(datetime_index, opening, label="Open", color=opencolour)
        current_ax.fill_between(datetime_index, low, high, color=hilointcolour, alpha=0.3, label="High-Low interval")
        current_ax.fill_between(datetime_index, closing, opening, color=closeopenintcolour, alpha=0.3, label="Close-Open interval")
        amountholding, price = holdings[ticker]
        total_value += closing.iloc[-1] * amountholding
        current_total = closing.iloc[-1] * amountholding
        purchased_difference = current_total - (amountholding * price)
        total_valchange += purchased_difference
        previous_close = history['Close'].iloc[0]
        difference = closing.iloc[-1] - previous_close
        percentage_change = (difference / previous_close) * 100
        current_ax.set_title(f"{ticker} : Close: {closing.iloc[-1]:.2f} : {current_total:.2f} : Diff: {difference:.2f} ({percentage_change:.2f}%) : Purch. Diff. {purchased_difference:.2f}", fontsize=10)
        current_ax.grid(True)
        ax2 = current_ax.twinx()
        ax2.bar(datetime_index, volume, color=volumecolour, alpha=0.5, label="Volume", width=0.001)
        ax2.set_ylabel("Volume")
    fig.suptitle(f"Total Value: {total_value:.2f} : Change: {total_valchange:.2f}", fontsize=12)

if __name__ == "__main__":
    print(f"""
          Open Colour: {opencolour}
          Close Colour: {closecolour}
          High-Low Interval Colour: {hilointcolour}
          Close-Open Interval Colour: {closeopenintcolour}
          Volume Colour: {volumecolour}
""")
    if len(holdings) == 1:
        fig, axes_obj = plt.subplots(1, 1)
        axes = [axes_obj]
    elif len(holdings) > screendivisionx:
        graphnrow = ((math.ceil(len(holdings)/2)))
        fig, axes = plt.subplots(graphnrow, screendivisiony, squeeze=False)
        axes = axes.flatten()
    else:
        fig, axes = plt.subplots(len(holdings), 1, squeeze=False)
        axes = axes.flatten()
    fig.canvas.manager.set_window_title("Symbol Watcher")
    ani = FuncAnimation(fig, update_graphs, interval=updateinterval, cache_frame_data=False)
    plt.tight_layout(h_pad=1, w_pad=1, rect=[0, 0.05, 0.95, 0.9])
    plt.show()
    
