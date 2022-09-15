# simulates trading with past crypto data
# bugs: currently a small rounding error when converting currencies
# strategy: makes a few predetermined buys in the beginning and only sells when the lowest buy price is lower by a certain amount more than the current price. the current price must be double the lowest buy (probably way too high).
# Justin Amstadt
# 14/9/2022
import pandas as pd
import csvhistory
import warnings

code_to_file = {
        'ETH/USD': 'Bitfinex_ETHUSD_minute.csv',
        'BTC/USD': 'Bitfinex_BTCUSD_minute.csv',
        }


class PaperTrade:
    def __init__(self, code, starting_amount):
        self.code = code
        self.amountUSD = starting_amount
        self.amountCoin = {
                'ETH/USD': {'amount': 0, 'precision': 9},
                'BTC/USD': {'amount': 0, 'precision': 7}
                }
        # all buys and sells
        self.trading_activity_df = pd.DataFrame(columns=['type', 'symbol', 'unix', 'date', 'close', 'amountUSD', 'amountCoin', 'buy code'])
        # all buys that have yet to be sold off for a profit
        self.active_trades_df = pd.DataFrame(columns=['type', 'symbol', 'unix', 'date', 'close', 'amountUSD', 'amountCoin', 'buy code'])
        # read in past data. uses CSVUtils class in another file
        self.data_csv = csvhistory.CSVUtils(code_to_file[code])
        self.csv_df = self.data_csv.getDF()
        self.buy_code = 0

# iterate through csv file and decide whether to buy or sell
    def simulate(self):
        for index, row in self.csv_df.iterrows():
            self.checkBuy(index)
            self.checkSell(index)
        print("finished")
        print(str(self.amountCoin) + "\n" + str(self.amountUSD))

# when decided to buy, make a trade and put it in the system
    def buy(self, row_num, amount, code) -> bool:
        success = True
        if self.amountUSD < amount:
            success = False
            warnings.warn('Attempted to buy ' + str(amount) + '. Only had ' + str(self.amountUSD))
        else:
            current_value = self.csv_df.loc[row_num]['close']
            amount_in_coin = self.convertUSDToCrypto(current_value, amount, code)
            self.amountUSD -= amount
            self.amountCoin[code]['amount'] += amount_in_coin

            # add a new entry
            self.trading_activity_df.loc[len(self.trading_activity_df.index)] = [
                    'buy',
                    self.csv_df.loc[row_num]['symbol'],
                    self.csv_df.loc[row_num]['unix'],
                    self.csv_df.loc[row_num]['date'],
                    self.csv_df.loc[row_num]['close'],
                    amount,
                    amount_in_coin,
                    self.buy_code
                    ]
            self.active_trades_df.loc[len(self.trading_activity_df.index)] = [
                    'buy',
                    self.csv_df.loc[row_num]['symbol'],
                    self.csv_df.loc[row_num]['unix'],
                    self.csv_df.loc[row_num]['date'],
                    self.csv_df.loc[row_num]['close'],
                    amount,
                    amount_in_coin,
                    self.buy_code
                    ]
            self.buy_code += 1
            print(self.trading_activity_df)

        return success

# sell an active buy
    def sell(self, row_num, active_trades_row_num, amount_in_coin) -> bool:
        success = True
        buy_code = self.active_trades_df.loc[active_trades_row_num]['buy code']
        symbol = self.active_trades_df.loc[active_trades_row_num]['symbol']

        if self.amountCoin[symbol]['amount'] < amount_in_coin:
            success = False
            warnings.warn('Attempted to sell ' + str(amount_in_coin) + ' of ' + symbol + '. Only had ' + str(self.amountCoin[symbol]['amount']))
        else:

            current_value = self.csv_df.loc[row_num]['close']
            amount_in_USD = self.convertCryptoToUSD(current_value, amount_in_coin, symbol)
            self.amountUSD += amount_in_USD
            self.amountCoin[symbol]['amount'] -= amount_in_coin

            # add a new entry
            self.trading_activity_df.loc[len(self.trading_activity_df.index)] = [
                    'sell',
                    self.csv_df.loc[row_num]['symbol'],
                    self.csv_df.loc[row_num]['unix'],
                    self.csv_df.loc[row_num]['date'],
                    self.csv_df.loc[row_num]['close'],
                    amount_in_USD,
                    amount_in_coin,
                    buy_code  # buy code for previous purchase, not a new one
                    ]

            # remove active trade from dataframe
            self.active_trades_df = self.active_trades_df.drop([active_trades_row_num])
            print(self.trading_activity_df)

        return success

# check whether to buy or not. no real criteria set yet1
    def checkBuy(self, row_num) -> bool:
        bought = False
        if row_num == 0 or row_num == 2:
            bought = self.buy(row_num, 100, self.code)
        return bought

# the second if statement currently checks whether to sell
# grabs the cheapest buy and compares it to the current price
    def checkSell(self, row_num) -> bool:
        sold = False
        if self.active_trades_df.empty is False:
            min_bought_index = self.active_trades_df['close'].idxmin()
            min_bought_USD = self.active_trades_df.loc[min_bought_index]['close']
            min_bought_coin = self.active_trades_df.loc[min_bought_index]['amountCoin']
            current_value = self.csv_df.loc[row_num]['close']
            if current_value >= (min_bought_USD * 1 + min_bought_USD):
                sold = self.sell(row_num, min_bought_index, min_bought_coin)
        return sold

# does currency conversions along with the appropriate precision assigned to each coin
    def convertUSDToCrypto(self, current_coin_value, amountUSD, coin_code):
        exchange_rate = 1 / current_coin_value
        amount_in_coin = amountUSD * exchange_rate
        return round(amount_in_coin, self.amountCoin[coin_code]['precision'])

    def convertCryptoToUSD(self, current_coin_value, amountCrypto, coin_code):
        exchange_rate = current_coin_value
        amount_in_USD = amountCrypto * exchange_rate
        return round(amount_in_USD, 2)


ethTrade = PaperTrade('ETH/USD', 1000)
ethTrade.simulate()
