# MIT LICENSE 2025

import matplotlib.pyplot as plt
import yfinance as yf
from matplotlib.animation import FuncAnimation
import sys # Importerar sys för att kunna avsluta programmet snyggt om inga giltiga tickers matas in

# Denna lista kommer att fyllas med tickers efter användarens input
tickers = []

def update_graphs(_):
    """
    Hämtar den senaste minutdatan för varje ticker och uppdaterar motsvarande subplot.
    Kallas av FuncAnimation.
    """
    # 'axes' garanteras nu vara en itererbar sekvens (lista eller numpy array)
    # oavsett om det finns en eller flera tickers.
    for idx, ticker in enumerate(tickers):
        # Kontrollerar om idx är inom gränserna för 'axes'.
        # Denna kontroll är mest för säkerhet; loopens storlek bör matcha antalet subplots.
        if idx >= len(axes):
            print(f"Varning: Index {idx} utanför gränserna för 'axes' med längd {len(axes)}")
            continue # Hoppa över om något oväntat skulle hända

        stock = yf.Ticker(ticker)
        # Hämtar historik för senaste dagen med 1-minutsintervall
        history = stock.history(period="1d", interval="1m")

        # Kontrollera om data kunde hämtas. Om inte, hantera tom graf.
        if history.empty:
            print(f"Varning: Kunde inte hämta data för {ticker}. Hoppar över.")
            # Rensa den subplot som skulle ha använts
            axes[idx].clear()
            axes[idx].set_title(f"{ticker}: Ingen data tillgänglig")
            axes[idx].grid(False) # Stäng av rutnätet för en tom graf
            # Kontrollera om twinx-axeln skapades innan vi rensar (för att undvika fel om den inte finns)
            # Notera: Det här hanterar inte fallet där twinx-axeln redan fanns och rensades.
            # För en tom graf räcker det oftast att bara rensa huvudaxeln och titeln.
            # Den sekundära axeln skapas ändå inte om datan är tom.
            continue # Gå till nästa ticker i loopen

        datetime_index = history.index # Bytte namn från 'datetime' för att undvika kollision med inbyggt namn
        closing = history['Close']
        opening = history['Open']
        high = history['High']
        low = history['Low']
        volume = history['Volume']

        # Vi har nu säkerställt att 'axes' är en itererbar sekvens,
        # så axes[idx] kommer att ge rätt Axes-objekt.
        current_ax = axes[idx]

        current_ax.clear() # Rensa den befintliga grafen innan ny data ritas

        # Rita de olika dataserierna
        current_ax.plot(datetime_index, closing, label="Stängningskurs", color="green")
        current_ax.plot(datetime_index, opening, label="Öppningskurs", color="blue")
        current_ax.fill_between(datetime_index, low, high, color="orange", alpha=0.3, label="Högsta-Lägsta intervall")
        current_ax.set_title(f"{ticker} : Stängning: {closing.iloc[-1]:.2f} SEK") # Uppdatera titeln med senaste stängningskurs
        current_ax.set_xlabel("Tid")
        current_ax.set_ylabel("Pris (SEK)")
        current_ax.grid(True) # Se till att rutnätet är på

        # Skapa en sekundär y-axel för volymen
        ax2 = current_ax.twinx()
        ax2.bar(datetime_index, volume, color="grey", alpha=0.5, label="Volym", width=0.001)
        ax2.set_ylabel("Volym")

        # Lägg till legender (det kan bli lite rörigt med twinx, kan behöva samla handles och labels)
        # För enkelhetens skull lägger vi huvudlegenden på den primära axeln.
        # en kombinerad legend kan göras utanför loopen efter att alla axlar är ritade.
        # current_ax.legend(loc='upper left')
        # ax2.legend(loc='lower left') # Kan överlappa

if __name__ == "__main__":
    # Här skrivs den globala 'tickers'-listan över, vilket är okej i det här fallet.
    input_string = input("Mata in tickersymboler separerade med kommatecken: ")
    tickers = input_string.split(",")
    # Ta bort blanksteg före och efter varje ticker
    tickers = [ticker.strip() for ticker in tickers]
    # Filtrera bort eventuella tomma strängar som kan finnas kvar
    # t.ex. från extra kommatecken (som i "AAPL,,MSFT" eller "IPCO.ST,")
    tickers = list(filter(None, tickers))

    # Kontrollera om det finns några tickers kvar efter filtreringen
    if not tickers:
        print("Inga giltiga tickersymboler angavs. Avslutar.")
        sys.exit() # Avsluta programmet

    # Skapa subplots baserat på antalet tickers.
    # Hantera fallet med en enda ticker specifikt för att säkerställa att 'axes'
    # alltid är en itererbar sekvens (lista eller numpy array) för att loopen ska fungera.
    if len(tickers) == 1:
        # plt.subplots(1, 1) returnerar en figur och ett enda Axes-objekt.
        fig, axes_obj = plt.subplots(1, 1)
        # Vi omsluter det enda Axes-objektet i en lista så att loopen alltid kan använda axes[idx].
        axes = [axes_obj]
    else:
        # För flera tickers returnerar plt.subplots en figur och en numpy array av Axes-objekt.
        # Vi använder squeeze=False för att säkerställa att 'axes' alltid är en 2D-array
        # även om det bara är en kolumn (len(tickers), 1). Därefter plattar vi till den.
        fig, axes = plt.subplots(len(tickers), 1, squeeze=False)
        # Plattar till numpy-arrayen till en 1D-array för enklare indexering (axes[idx])
        axes = axes.flatten()

    # Skapa animationen. 'update_graphs' kallas med intervallet 60000 ms (1 minut).
    # cache_frame_data=False är bra när du hämtar ny realtidsdata varje gång.
    ani = FuncAnimation(fig, update_graphs, interval=60000, cache_frame_data=False)

    # Justera layouten för att förhindra att titlar och etiketter överlappar varandra
    plt.tight_layout()

    # Visa plotten
    plt.show()
