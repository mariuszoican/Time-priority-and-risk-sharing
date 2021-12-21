import pandas as pd
import numpy as np
import os
import random
import string

ob_path ='../TMXData/topOfBook'
trades_path = '../TMXData/trades'
files = os.listdir(ob_path)
ins = ["BAX","CGF","CGB","SXF"]
ins_abbr = {"BAX": "BX", "CGF": "CF", "CGB":"CB", "SXF":"SX"}

# helper functions
def select_instruments(symbol):
    # function to select instruments in the quote data
    if (len(symbol)==6) and (symbol[:3] in ins) and (symbol[3] in ["H","M","U","Z"]):
        return True
    else:
        return False

def load_trades(dates):
    trades = pd.DataFrame()
    for date in dates:
        file_path = trades_path + "/"+ date + "/" + date+ ".dta"
        trades = trades.append(pd.read_stata(file_path))
        trades=trades[trades.externalSymbol.apply(lambda x: select_instruments(x))]
    return trades.reset_index()

def random_name(n):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=n))

def mock_dict(series):
    series = series.unique()
    max_len = len(max(series, key=len))
    min_len = len(min(series, key=len))
    new = []
    for _ in series:
        n = random.randint(min_len, max_len)
        x1 = random_name(n)
        while x1 in new: # make sure we do not have duplicates in new list
            n = random.randint(min_len, max_len)
            x1 = random_name(n)
        new.append(x1)
    return dict(zip(series, new))


def update_price(x, instrument):
    if x == '':
        return ''
    price_transformer = {"BAX": (1.1,1), "CGF": (1.2,0.5), "CGB":(1.3, 0.7), "SXF":(0.9, 0.8)}
    a = price_transformer[instrument][0]
    b = price_transformer[instrument][1]
    return a*float(x) + b

def update_datetime(datetime):
    new_date = dict_date[datetime[0:10].replace('-', '')]
    new_date = new_date[0:4] + '-' + new_date[4:6] + '-' + new_date[6:8]
    return new_date + datetime[10:]


# Randomly select 14 non-consecutive days
random_days = []

while len(random_days) != 14:
    index = random.randrange(0, len(files))
    date = files[index]
    trades = pd.read_stata(trades_path + "/"+ date + "/" + date+ ".dta")
    trades = trades[trades.externalSymbol.apply(lambda x: select_instruments(x))]
    
    if not trades.empty:
        random_days.append(files[index])
        # remove adjacent date to avoid consecutives
        files.pop(index)
        files.pop(max(index-1,0))
        files.pop(min(index+1,len(files)-1))
        
# Rondom 14 consecutive days
files = os.listdir(ob_path)
start = random.randrange(0, len(files))
consecutives = files[start:start+14]

# map random days to consecutive days
dict_date = {}
for i in range(len(consecutives)):
    dict_date[random_days[i]] = consecutives[i]
    

# scramble trades data
def scramble_trades(trades):
    # only keep useful columns
    columns_to_keep = ['number','ap','account','externalSymbol','date','time','milliseconds','side','price','session','order','mxBid0','mxAsk0','quantity']
    trades = trades[columns_to_keep]
    
    # Rename mxBid0 and mxAsk0
    trades = trades.rename(columns = {'mxBid0': 'Bid'})
    trades = trades.rename(columns = {'mxAsk0': 'Ask'})
    
    # map the date
    trades['date'] = trades['date'].map(dict_date)
    print('date mapped')

    # combine ap and account into one column
    trades['account'] = trades['ap'].map(dict_ap).astype(str) + trades['account'].map(dict_acc)
    del trades['ap']
    print('new account created, ap deleted')
    
    # update price
    for instrument in ins:
        for column_name in ['Bid', 'Ask', 'price']:
            trades[trades['externalSymbol'].astype(str).str[:3]==instrument][column_name].apply(lambda x: update_price(x, instrument))
    print('price updated')
    
    # scramble instruments name
    trades['externalSymbol'] = trades['externalSymbol'].astype(str).str[:3].map(dict_ins) + trades['externalSymbol'].astype(str).str[3:]
    print('instruments scrambled')
    
    # Swap 50% order limit and market
    sample = trades.sample(frac=0.5)['order']
    dict_order = {'Limit': 'Market', 'Market':'Limit'}
    trades.update(sample.map(dict_order))
    print('50% trades limit and market are swapped')
    
    # Swap another 50% buy and sell indicator
    dict_side = {'Buy': 'Sell', 'Sell': 'Buy'}
    trades.update(trades.loc[~trades.index.isin(sample.index)]['side'].map(dict_side))
    print('another 50% trades buy and sell are swapped')
    
    # Randomly add one to quantity
    trades['quantity'] = trades['quantity'].astype(int)
    selected = trades['number'].sample(frac=0.3).unique()
    trades['quantity'] = (trades[trades['number'].isin(selected)]['quantity'] + 1).astype(str)
    print('randomly chose trades quantity + 1')
    
    return trades

def scramble_ob(ob): 
    
        # map the date
        ob['datetime'] = ob['datetime'].apply(lambda x: update_datetime(x))
    
        # update ptice
        ob['price'].apply(lambda x: update_price(x, ob['externalSymbol'][0][:3]))

        # scramble instruments name
        ob['externalSymbol'] = ob['externalSymbol'].astype(str).str[:3].map(dict_ins) + ob['externalSymbol'].astype(str).str[3:]
    
        # decomposite firmtrader_account, scramble ap and account, put them together and rename as account
        ap = ob['firmtrader_account'].str[:4].replace(r'^(0+)', '')
        account = np.where(ob['firmtrader_account'].str[6] == '_', ob['firmtrader_account'].str[7:], ob['firmtrader_account'].str[8:])
        ob['account'] = ap.astype(int).map(dict_ap).astype(str) + pd.Series(account).map(dict_acc)
        del ob['firmtrader_account']
        
        # shuffle priority
        ob['priority'] = random.sample(list(ob['priority']), len(ob['priority']))
        
        # Randomly add one to quantity
        sample = ob.sample(frac=0.5)['quantity']
        ob.update(sample+1)
        
        # Swap 50% side
        dict_side = {'bid': 'ask', 'ask': 'bid'}
        sample = ob.sample(frac=0.5)['side']
        ob.update(sample.map(dict_side))
        
        return ob
    
# map instruments
new = [''.join(random.choices(string.ascii_uppercase, k=3)) for _ in ins]
dict_ins = dict(zip(ins, new))

# map ap
ap = list(range(1,699+1))
new_ap = [str(item).zfill(3) for item in random.sample(ap, len(ap))]
dict_ap = dict(zip(ap, new_ap))

# load trades
trades = load_trades(random_days)

# map account
dict_acc = mock_dict(trades['account'])

trades = scramble_trades(trades)

for date in consecutives:
    trades[trades['date'] == date].to_csv('randomized_trades/' + date + '.csv.gz')
    print(date + '->' + dict_date[date] + ' trades scrambled')

for date in random_days:
    os.mkdir('../ProcessedData/randomized_ob/' + dict_date[date])
    for instrument in ins:
        ob = pd.read_csv(ob_path + '/' + date + '/' + ins_abbr[instrument]+'_AtBest_' + date + '.csv.gz')
        account = np.where(ob['firmtrader_account'].str[6] == '_', ob['firmtrader_account'].str[7:], ob['firmtrader_account'].str[8:])
        
        # update accounts mapping, because ob may contains more than trades
        ob_dict_acc = mock_dict(pd.Series(account))
        ob_dict_acc.update(dict_acc)
        dict_acc = ob_dict_acc
        
        new_ob = scramble_ob(ob)
        new_ob.to_csv('../ProcessedData/randomized_ob/' + dict_date[date] + '/' + dict_ins[instrument][0] + dict_ins[instrument][2] +'_AtBest_' + dict_date[date] + '.csv.gz')
    print(date + '->' + dict_date[date] + ' ob scrambled')