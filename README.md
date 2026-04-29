# Stock-Simulator
Portfolio Builder and Projection Engine
Note: This file is still in prototyping, but will be added when finished
The application relies on tkinter, gspread, numpy, matplotlib, and google.oauth2 for various functions as noted in the file. It also uses yfinance to retrieve live stock data and historical data up to 5 years back.
The application allows users to allocate $25,000 into up to 10 stocks and then simulate the portfolio over 1, 5, or 10 years to see how the stocks perform. It uses 5 years of stock data as well as a Monte Carlo prediction engine (which runs the simulation 1000 times) to predict realistic economic instability and show users the performance of their portfolios based on these unpredictable markets.
