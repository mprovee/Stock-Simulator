#Installed tkinter, yfinance, gspread, Credentials, numpy, and matplotlib for purposes listed below
import tkinter as tk #GUI creation
from tkinter import ttk, messagebox, filedialog #TTK for extra widgets, messagebox for popup messages, and filedialog to save simulation results
import yfinance as yf #Uses real stock data and history to make simulation "predictions"
import gspread #To connect to and record data in Google Sheets
from google.oauth2.service_account import Credentials #To log into Google Sheets
import numpy as np #To run simulation math
import matplotlib.pyplot as plt #To build the results chart
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg #To show the chart inside the app

#Constant Simulation Parameters (Written by Group)
app_title = "Investment Simulator"
starting_balance = 25000
max_stocks = 10
simulation_runs = 1000

#Tracking stock selections across screens (Information sourced from https://www.w3schools.com/python/python_variables_global.asp)
#NOTE: THIS WILL BE CHANGED FOR MILESTONE 3 TO INCLUDE LOGIN FEATURES
current_user = "Guest"
stocks_list = []

#Google Sheets Connection (Written by Group)
#Comment out if not Mitchell Until Milestone 3
scopes = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
client = gspread.authorize(creds)
sheet = client.open("InvestmentSimulator")

#Clear on-screen widgets (Information and function concept sourced from https://www.geeksforgeeks.org/python/how-to-clear-out-a-frame-in-the-tkinter/ )
def clear_window():
   for widget in root.winfo_children():
        widget.destroy()

#Show welcome screen when app runs (Written by Group)
def show_welcome_screen():
    clear_window()
    root.title(app_title)

    #Small welcome label above title
    tk.Label(root, text="Welcome to...",
             font=("Verdana", 14, "italic")).pack(pady=(80, 0))

    #Main app title
    tk.Label(root, text="Investment Simulator",
             font=("Verdana", 28, "bold")).pack()

    #Subtitle explaining what the app does
    tk.Label(root, text=f"Select and simulate your own portfolio. Can you beat Wall Street?",
             font=("Verdana", 14, "bold", "italic")).pack(pady=(10, 30))

    #Login button - not available yet
    tk.Button(root, text="Login", width=25, bg="red", fg="black",
              command=lambda: messagebox.showinfo("Not Available", #Messagebox info sourced from https://www.geeksforgeeks.org/python/python-tkinter-messagebox-widget/
                  "Login is not available right now.")).pack(pady=25)

    #Create account button - not available yet
    tk.Button(root, text="Create Account", width=25, bg="red", fg="black",
              command=lambda: messagebox.showinfo("Not Available",
                  "Account creation is not available right now.")).pack(pady=15)

    #Guest button - goes straight to allocation page without user saving
    tk.Button(root, text="Continue as Guest", width=25, bg="red", fg="black",
              command=show_stock_input_screen).pack(pady=15)

#Stock Symbol Validation (Necessary ticker information sourced from https://www.geeksforgeeks.org/python/getting-stock-data-using-yfinance-in-python/)
def validate_ticker(ticker_symbol): #Check if ticker exists in yfinance and return company name if found
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        name = info.get("longName") or info.get("shortName")
        if name:
            return True, name
        else:
            return False, None
    except Exception:
        return False, None

# Stock Input & Allocation SCREEN (Written by Group, though second line of section uses information from https://www.w3schools.com/python/python_variables_global.asp)
def show_stock_input_screen():
    global stocks_list
    stocks_list = []
    clear_window()

    #Page Title
    tk.Label(root, text="Build Your Portfolio",
             font=("Verdana", 24, "bold")).pack(pady=20)

    #Remaining Allocation Balance
    balance_var = tk.StringVar(value=f"Remaining Balance: ${starting_balance:,}")
    tk.Label(root, textvariable=balance_var, font=("Verdana", 14)).pack()

    #Input row for ticker and amount
    input_frame = tk.Frame(root)
    input_frame.pack(pady=10)

    tk.Label(input_frame, text="Stock Ticker (e.g. AAPL):",
             font=("Verdana", 12)).grid(row=0, column=0, padx=5)
    ticker_entry = tk.Entry(input_frame, font=("Verdana", 12), width=15)
    ticker_entry.grid(row=0, column=1, padx=5)

    tk.Label(input_frame, text="Amount ($):",
             font=("Verdana", 12)).grid(row=0, column=2, padx=5)
    amount_entry = tk.Entry(input_frame, font=("Verdana", 12), width=10)
    amount_entry.grid(row=0, column=3, padx=5)

    tk.Button(input_frame, text="Add Stock", bg="red", fg="black",
              font=("Verdana", 12), command=lambda: add_stock()).grid(row=0, column=4, padx=5)

    #Stock table (this section was sourced from https://www.pythontutorial.net/tkinter/tkinter-treeview/)
    columns = ("Ticker", "Company", "Amount", "Allocation %")
    tree = ttk.Treeview(root, columns=columns, show="headings", height=8)
    tree.heading("Ticker", text="Ticker")
    tree.heading("Company", text="Company")
    tree.heading("Amount", text="Amount")
    tree.heading("Allocation %", text="Allocation %")
    tree.column("Ticker", width=80, anchor="center")
    tree.column("Company", width=280, anchor="w")
    tree.column("Amount", width=120, anchor="center")
    tree.column("Allocation %", width=120, anchor="center")
    tree.pack(pady=10)

    #Simulation period dropdown (First 3 lines & some supplementary info of section use info sourced from https://www.pythontutorial.net/tkinter/tkinter-frame/, rest is written by Group. Roughly 50/50 breakdown)
    period_frame = tk.Frame(root)
    period_frame.pack(pady=5)
    period_var = tk.StringVar(value="5")
    tk.Label(period_frame, text="Simulation Period:",
             font=("Veranda", 12)).pack(side="left", padx=5)
    ttk.Combobox(period_frame, textvariable=period_var,
                 values=["1", "5", "10"], width=5,
                 state="readonly").pack(side="left")
    tk.Label(period_frame, text="years",
             font=("Veranda", 12)).pack(side="left", padx=5)

    #Run simulation button (Written by Group)
    tk.Button(root, text="Run Simulation", font=("Veranda", 12), width=20,
              bg="red", fg="black", command=lambda: run_simulation()).pack(pady=10)

    #Calculate remaining balance (Written by Group)
    def get_remaining():
        total = sum(s["amount"] for s in stocks_list)
        return starting_balance - total

    #Clear and repopulate table. #Similar to above, supplementary info of section use info sourced from https://www.pythontutorial.net/tkinter/tkinter-treeview/, rest is written by Group. Roughly 50/50 breakdown.
    def refresh_table():
        for row in tree.get_children():
            tree.delete(row)
        for s in stocks_list:
            pct = (s["amount"] / starting_balance) * 100
            tree.insert("", "end", values=(
                s["ticker"],
                s["company"],
                f"${s['amount']:,.2f}",
                f"{pct:.1f}%"
            ))
        balance_var.set(f"Remaining Balance: ${get_remaining():,.2f}")

    def add_stock(): #AI consulted for the following two lines.
        ticker_input = ticker_entry.get().strip().upper()
        amount_input = amount_entry.get().strip()

        #Validate both fields filled (Written by Group).
        if not ticker_input or not amount_input:
            messagebox.showerror("Error", "Please enter both a ticker and an amount")
            return

        #Validate amount is a number (Written by Group).
        try:
            amount = float(amount_input)
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number")
            return

        if amount <= 0:
            messagebox.showerror("Error", "Amount must be greater than zero")
            return

        #Check stock limit (Written by Group).
        if len(stocks_list) >= max_stocks:
            messagebox.showerror("Error", f"Maximum {max_stocks} stocks allowed")
            return

        #Check remaining balance (Written by Group).
        if amount > get_remaining():
            messagebox.showerror("Error",
                f"Amount exceeds remaining balance of ${get_remaining():,.2f}")
            return

        #Validate ticker exists (Written by Group).
        valid, company_name = validate_ticker(ticker_input)
        if not valid:
            messagebox.showerror("Error",
                f"Ticker not found: {ticker_input}. Try a valid symbol like AAPL or TSLA")
            return

        #Check for duplicates (Written by Group).
        for s in stocks_list:
            if s["ticker"] == ticker_input:
                messagebox.showerror("Error", f"{ticker_input} is already in your portfolio")
                return

        #Add stock and refresh
        stocks_list.append({
            "ticker": ticker_input,
            "company": company_name,
            "amount": amount
        })
        refresh_table() #Bottom half of section uses information sourced from https://www.pythontutorial.net/tkinter/tkinter-entry/
        ticker_entry.delete(0, tk.END)
        amount_entry.delete(0, tk.END)

    #Checks to ensure at least one stock is selected and that user is okay with proceeding if not using the full amount. (Written by Group)
    def run_simulation():
        if not stocks_list:
            messagebox.showerror("Error", "Please add at least one stock")
            return

        remaining = get_remaining()
        if remaining > 0:
            go = messagebox.askyesno("Warning",
                f"You have ${remaining:,.2f} unallocated. Continue anyway?")
            if not go:
                return

        years = int(period_var.get())
        show_results_screen(years)

#Simulation Engine with Random Events (Written by Group)
def run_monte_carlo(years):
    trading_days = years * 252 #Number of trading days to simulate
    portfolio_results = np.zeros((simulation_runs, trading_days))  #Array to hold all simulation results (This line sourced from https://numpy.org/doc/stable/reference/generated/numpy.zeros.html)

    for stock in stocks_list: #Written by Group
        ticker = stock["ticker"]
        amount = stock["amount"]

        #Download 5 years of historical data for this stock (25/75 breakdown between Group and YFinance source mentioned above)
        hist = yf.download(ticker, period="5y", progress=False)
        daily_returns = hist["Close"].pct_change().dropna() #Calculate daily returns from closing price
        mean_return = float(daily_returns.mean().iloc[0]) #Get average return and volatility from historical data
        std_return = float(daily_returns.std().iloc[0])

        #Run 1000 simulations for this stock (Used above Numpy Source for this section)
        stock_sims = np.zeros((simulation_runs, trading_days))
        for i in range(simulation_runs):
            #Random daily returns based on historical mean and volatility
            rand_returns = np.random.normal(mean_return, std_return, trading_days)
            #Compound the returns over time starting from allocated amount
            stock_sims[i] = amount * np.cumprod(1 + rand_returns)

        #Add stock results into total portfolio
        portfolio_results += stock_sims

    return portfolio_results

#Results Screen (Written by Group)
def show_results_screen(years):
    clear_window()

    #Show loading message while simulation runs (Written by Group except second line)
    loading = tk.Label(root, text="Simulating Results...", font=("Veranda", 14))
    loading.pack(expand=True) #Uses info from https://www.pythontutorial.net/tkinter/tkinter-after/
    root.update()

    #Run simulation (Written by group)
    results = run_monte_carlo(years)
    loading.destroy()

    #Calculate stats (Written mostly by group)
    final_values = results[:, -1] #Info from https://numpy.org/doc/stable/user/basics.indexing.html
    avg_final = np.mean(final_values)
    min_final = np.min(final_values)
    max_final = np.max(final_values)
    #Next two lines use info from https://numpy.org/doc/stable/reference/generated/numpy.percentile.html
    p10 = np.percentile(final_values, 10)
    p90 = np.percentile(final_values, 90)

    #Build and display chart (50/50 mix of Group and other resources listed below)
    fig = build_chart(results, years, avg_final, min_final, max_final, p10, p90) #(Group)
    #Following 3 lines from https://matplotlib.org/stable/gallery/user_interfaces/embedding_in_tk_sgskip.html
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=(10, 0))

    #Buttons below chart (Written by Group)
    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=8)

    tk.Button(btn_frame, text="Save Chart", width=20, height=2, bg="red", fg="black",
              command=lambda: save_chart(fig)).pack(side="left", padx=15)

    tk.Button(btn_frame, text="New Simulation", width=20, height=2, bg="red", fg="black",
              command=show_stock_input_screen).pack(side="left", padx=15)

#Build Chart (Written by Group using https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.subplots.html)
def build_chart(results, years, avg_final, min_final, max_final, p10, p90):
    fig, ax = plt.subplots(figsize=(9, 4.5))

    trading_days = years * 252
    x = np.linspace(0, years, trading_days)

    #Plot sample paths as faint background lines (This section from https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.plot.html)
    for i in range(0, 200, 5):
        ax.plot(x, results[i], color="lightblue", alpha=0.2, linewidth=0.5)

    #Calculate summary lines (Written by Group with help of existing numpy citations)
    mean_path = np.mean(results, axis=0)
    min_path = np.min(results, axis=0)
    max_path = np.max(results, axis=0)
    p10_path = np.percentile(results, 10, axis=0)
    p90_path = np.percentile(results, 90, axis=0)

    #Plot key lines (Written by Group)
    ax.plot(x, mean_path, color="blue", linewidth=2, label="Average")
    ax.plot(x, max_path, color="green", linewidth=1.5, linestyle="--", label="Best Case")
    ax.plot(x, min_path, color="red", linewidth=1.5, linestyle="--", label="Worst Case")
    ax.plot(x, p90_path, color="orange", linewidth=1.5, linestyle=":", label="Top 10%")
    ax.plot(x, p10_path, color="pink", linewidth=1.5, linestyle=":", label="Bottom 10%")

    #Shade likely range (Written by Group)
    ax.fill_between(x, p10_path, p90_path, alpha=0.1, color="blue")

    #Starting balance line (Following 2 use information from https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.axhline.html)
    ax.axhline(y=starting_balance, color="black", linewidth=1,
               linestyle="--", alpha=0.5, label="Starting Balance")
    #Following 2 lines written by Group using previous project experience
    ax.set_xlabel("Years", fontsize=14)
    ax.set_ylabel("Portfolio Value ($)", fontsize=14)

    #Title with tickers and stats (First 2 lines of the section use info from https://www.w3schools.com/python/ref_string_join.asp, rest is written by Group)
    tickers = ", ".join([s["ticker"] for s in stocks_list])
    avg_return_pct = ((avg_final - starting_balance) / starting_balance) * 100
    ax.set_title(
        f"Monte Carlo Simulation — {tickers} — {years} Year(s)\n"
        f"Worst: ${min_final:,.0f}  |  Bottom 10%: ${p10:,.0f}  |  "
        f"Avg: ${avg_final:,.0f}  |  Top 10%: ${p90:,.0f}  |  "
        f"Best: ${max_final:,.0f}  |  Avg Return: {avg_return_pct:.1f}%",
        fontsize=12)
    #Following 4 lines are 50/25/25 breakdown between Group, https://matplotlib.org/stable/api/ticker_api.html#matplotlib.ticker.FuncFormatter, and https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.tight_layout.html
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda val, _: f"${val:,.0f}"))
    ax.legend(loc="upper left", fontsize=9)
    fig.tight_layout()
    return fig

#Saving Chart to Computer (First line written by Group, following lines use info from https://www.pythontutorial.net/tkinter/tkinter-open-file-dialog/ and https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.savefig.html)
def save_chart(fig):
    filepath = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG Image", "*.png"), ("PDF File", "*.pdf")],
        title="Save Chart"
    )
    if filepath:
        fig.savefig(filepath, dpi=150, bbox_inches="tight")
        messagebox.showinfo("Saved", f"Chart saved to:\n{filepath}")

#Conclusionary Loop Section (Written by Group)
root = tk.Tk()
root.title(app_title)
root.geometry("900x700")
show_welcome_screen()
root.mainloop()