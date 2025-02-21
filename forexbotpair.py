import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
import time
from ta.volatility import BollingerBands
import sklearn as sk
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from ta.momentum import TSIIndicator
import matplotlib.pyplot as plt
from riskmanager import Manager



class SATORI:

    def __init__(self):
        self.position = None
        self.authentication()
        self.dic_data = {}
        self.BS = False 
        self.SS = False
        
        self.symbols : list = ['EURUSD','EURCAD' , 'EURGBP','EURAUD','EURNZD','EURJPY','EURCHF',
                               'USDCAD','GBPUSD', 'AUDUSD','NZDUSD','USDJPY','USDCHF',
                               'AUDCAD','NZDCAD','CADCHF','CADJPY','GBPCAD',
                               'GBPAUD','GBPNZD','GBPJPY','GBPCHF',
                               'AUDJPY','AUDNZD','AUDCHF',
                               'NZDJPY','NZDCHF',
                               'CHFJPY']

    

    def authentication(self):
                if not mt5.initialize():
                     print('this is error code', mt5.last_error())
                     quit()


    def get_data(self, symbol ,timeframe=mt5.TIMEFRAME_M1):

        from_date  = datetime.now()
        rates = mt5.copy_rates_from_pos(symbol , timeframe, 0, 100)
        df = pd.DataFrame(rates)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        df = df.set_index("time")

        return df

    def send_data(self):
         
         dfs = []
         
         for symbol in self.symbols:
              df = self.get_data(symbol)
              dfs.append(df[['close']])
            
         dt = pd.concat(dfs , axis=1 , keys=self.symbols)
         sld = StandardScaler()
         dt = dt.copy()
         dt.iloc[:,:]=sld.fit_transform(dt.iloc[:,:])
         return dt.iloc[:-1,:]
    

    def avg_val(self):
          dt = self.send_data()
          df = pd.DataFrame()
          
          df['EUR'] = (dt['EURUSD']['close'] + dt['EURCAD']['close'] + dt['EURGBP']['close'] + dt['EURAUD']['close'] + dt['EURNZD']['close'] + dt['EURJPY']['close'] + dt['EURCHF']['close'])/7
          df['USD'] = (-dt['EURUSD']['close'] + dt['USDCAD']['close'] - dt['GBPUSD']['close'] - dt['AUDUSD']['close'] - dt['NZDUSD']['close'] + dt['USDJPY']['close'] + dt['USDCHF']['close'])/7
          df['GBP'] = (dt['GBPUSD']['close'] - dt['EURGBP']['close'] + dt['GBPCAD']['close'] + dt['GBPAUD']['close'] + dt['GBPNZD']['close'] + dt['GBPJPY']['close'] + dt['GBPCHF']['close'])/7
          df['CAD'] = (-dt['EURCAD']['close'] + dt['USDCAD']['close'] - dt['GBPCAD']['close'] - dt['AUDCAD']['close'] - dt['NZDCAD']['close'] + dt['CADJPY']['close'] + dt['CADCHF']['close'])/7
          df['AUD'] = (dt['AUDUSD']['close'] - dt['EURAUD']['close'] - dt['GBPAUD']['close'] + dt['AUDCAD']['close'] + dt['AUDNZD']['close'] + dt['AUDJPY']['close'] + dt['AUDCHF']['close'])/7
          df['NZD'] = (dt['NZDUSD']['close'] - dt['EURNZD']['close'] - dt['GBPNZD']['close'] + dt['NZDCAD']['close'] - dt['AUDNZD']['close'] + dt['NZDJPY']['close'] + dt['NZDCHF']['close'])/7
          df['JPY'] = (-dt['EURJPY']['close'] - dt['USDJPY']['close'] - dt['GBPJPY']['close'] - dt['AUDJPY']['close'] - dt['NZDJPY']['close'] - dt['CADJPY']['close'] - dt['CHFJPY']['close'])/7
          df['CHF'] = (-dt['USDCHF']['close'] - dt['EURCHF']['close'] - dt['GBPCHF']['close'] - dt['CADCHF']['close'] - dt['AUDCHF']['close'] - dt['NZDCHF']['close'] + dt['CHFJPY']['close'])/7

          p_fast = 25
          p_slow = 15
          dc = pd.DataFrame()
          dc['EUR']= TSIIndicator(close = df['EUR'] , window_fast = p_fast , window_slow = p_slow ).tsi()
          dc['USD']= TSIIndicator(close = df['USD'] ,window_fast = p_fast , window_slow = p_slow).tsi()
          dc['CAD']= TSIIndicator(close = df['CAD'],window_fast = p_fast , window_slow = p_slow).tsi()
          dc['GBP']= TSIIndicator(close = df['GBP'],window_fast = p_fast , window_slow = p_slow).tsi()
          dc['NZD']= TSIIndicator(close = df['NZD'],window_fast = p_fast , window_slow = p_slow).tsi()
          dc['AUD']= TSIIndicator(close = df['AUD'],window_fast = p_fast , window_slow = p_slow).tsi()
          dc['JPY']= TSIIndicator(close = df['JPY'],window_fast = p_fast , window_slow = p_slow).tsi()
          dc['CHF']= TSIIndicator(close = df['CHF'],window_fast = p_fast , window_slow = p_slow).tsi()
          dc.dropna(inplace = True)
          dc.reset_index(inplace= True , drop= True)



          return dc , dt
    
    def seller_currency(self):
          dv , dt = self.avg_val()
          dv = dv.tail(1)
      
          

          dic = {}
          list_over = []
          list_lower = []
          for i in range(8):
                if dv.iloc[:,i].values[0] >0:
                      list_over.append(dv.columns[i])
                      
                elif dv.iloc[:,i].values[0] <-0:
                      list_lower.append(dv.columns[i])
          dic['over'] = list_over
          dic['lower'] = list_lower
          combinations = [o + l for o in list_over for l in list_lower] + [l + o for l in list_lower for o in list_over]
          combinations1 = [o + l for o in list_over for l in list_lower] 
          combinations2 = [l + o for l in list_lower for o in list_over]

          seller_list = []
          buyer_list = []
   

          for i in combinations1:
                if i in dt.columns:
                      seller_list.append(i)
          for i in combinations2:
                if i in dt.columns:
                      buyer_list.append(i)

          return seller_list , buyer_list





