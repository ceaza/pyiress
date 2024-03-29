from __future__ import print_function
import zeep
import numpy as np
import pandas as pd
import warnings
 
_INFO = """PyIress documentation (GitHub):
https://github.com/ceaza/pyiress"""

WSDL_URL_GENERIC='http://127.0.0.1:51234/wsdl.aspx?un={username}&cp={companyname}&svc={service}&svr=&pw={password}'

class PyIressException(Exception):
    pass

class Iress(object):
    def __init__(self, companyname,username, password, service='IRESS',raise_on_error=True, show_request=False,
                 proxy=None, **kwargs):
        """Establish a connection to the IRESS Web Services with Version 4 desktop.

           companyname / username / password - credentials for the Iress account.
           service - only service for desktop version is IRESS.
           raise_on_error - If True then error request will raise a "IressException",
                            otherwise either empty dataframe or partially
                            retrieved data will be returned
           show_request - If True, then every time a request string will be printed

           A custom WSDL url (if necessary for some reasons) could be provided
           via "url" parameter.
        """
        import logging.config
        self.services=[service]
        self.show_request = show_request
        if self.show_request:
            logging.config.dictConfig({
                                    'version': 1,
                                    'formatters': {
                                        'verbose': {
                                            'format': '%(name)s: %(message)s'
                                        }
                                    },
                                    'handlers': {
                                        'console': {
                                            'level': 'DEBUG',
                                            'class': 'logging.StreamHandler',
                                            'formatter': 'verbose',
                                        },
                                    },
                                    'loggers': {
                                        'zeep.transports': {
                                            'level': 'DEBUG',
                                            'propagate': True,
                                            'handlers': ['console'],
                                        },
                                    }
                                })
        else:
            logging.config.dictConfig({
            'version': 1,
            'disable_existing_loggers': True,
            })
        self.raise_on_error = raise_on_error
        self.last_status = None     # Will contain status of last request
        WSDL_URL = WSDL_URL_GENERIC.format(companyname=companyname,username=username,password=password,service=service)
        self._url = kwargs.pop('url', WSDL_URL)
        # Trying to connect
        try:
            self.client = zeep.Client(wsdl=WSDL_URL)
        except:
            raise PyIressException('Cannot Connect')

#       Create session
        login_details={'UserName': username,
                        'CompanyName': companyname,
                        'Password': password,
                        'ApplicationID': 'app'}
        IRESSSessionStartInputHeader = {"Parameters":login_details}
        self.session=self.client.service.IRESSSessionStart(Input=IRESSSessionStartInputHeader)
        self.IRESSSessionKey=self.session.Result.DataRows.DataRow[0].IRESSSessionKey
        self.UserToken=self.session.Result.DataRows.DataRow[0].UserToken
        self.last_response = None
        self.header={'Header':{'SessionKey':self.IRESSSessionKey}}

        # Check available data sources
        if 'IRESS' not in self.services:
            warnings.warn("'IRESS' source is not available for given subscription!")

    @staticmethod
    def info():
        print(_INFO)
        
    def sources(self):
        """Return available sources of data.
        Curretly only IRESS"""
        return self.services
    
    def version(self):
        """Return version of Iress Client."""
        res = self.client.namespaces
        return res


    def _time_series(self,start_date, end_date, ticker = '',exchange = '',securitytext = '',freq = 'daily'):
        '''
        
        Pos Name Type Nullable? Default Value Array? Array Size Description Alias
        
        1 SecurityCode string Yes  No  The security code to filter by.  
        2 Exchange string Yes  No  The exchange to filter by.  
        3 DataSource string Yes  No  The data source to filter by.  
        4 Frequency string No  No  The frequency type, one of 'daily', 'weekly', 'monthly', 'quarterly' or 'yearly'.  
        5 TimeSeriesFromDate date No  No  The date to retrieve time series from.  
        6 TimeSeriesToDate date No  No  The date to retrieve time series to.  
        7 SecurityText string Yes  No  Security text, in the form of: code.exchange@datasource|board, where exchange, data source and board are optional. Examples: BHP, BHP.ASX, BHP.ASX@TM, BHP@TM, TSX.TSX@TSX|T  
        
        Header Columns
        
        Pos Name  Type  Nullable? Default Value
        
        Description
        
        Alias
        
        1 PriceDisplayMultiplier double No    Price display multiplier.  
        2 SecurityCode string No    Security code.  
        3 Exchange string No    Exchange where the security is listed.  
        4 DataSource string No    The data source for the security.  
        5 OldestSourceDate date Yes    The date of the oldest time series data available for the security.  
        
        Output Columns
        
        Pos Name  Type  Nullable? Default Value
        
        Description
        
        Alias
        
        1 OpenPrice double Yes    Opening price for the time period.  
        2 HighPrice double Yes    Highest price for the time period.  
        3 LowPrice double Yes    Lowest price for the time period.  
        4 ClosePrice double No    Closing price for the time period.  
        5 TotalVolume double Yes    Total volume traded for the time period.  
        6 TotalValue double Yes    Total value traded for the time period.  
        7 TradeCount int32 Yes    Number of trades for the time period.  
        8 AdjustmentFactor double No    Adjustment factor indicating change to capital.  
        9 TimeSeriesDate date Yes    The date of the time series.  
        10 MarketVWAP double No    The market volume weighted average price.  
        11 ShortSold double Yes    The reported short sold trades. Value will be NULL if user is not permissioned for this data.  
        12 ShortSoldPercent double Yes    The reported short sold trades as a percentage of the number of shares on issue. Value will be NULL if user is not permissioned for this data.  
        13 ShortSellPosition double Yes    The total number of shares short sold. Value will be NULL if user is not permissioned for this data.  
        14 ShortSellPositionPercent double Yes    The total number of shares short sold as a percentage of the number of shares on issue. Value will be NULL if user is not permissioned for this data.  
        15 ValuationPrice double Yes    The valuation price at end of day 

        '''
        if ticker != '' and exchange!='':
            parameters={'Parameters':  {'SecurityCode': ticker,
                                      'Exchange': exchange,
                                      'Frequency':freq,
                                      'TimeSeriesFromDate':start_date.strftime('%Y/%m/%d'),
                                      'TimeSeriesToDate':end_date.strftime('%Y/%m/%d')
                              } } 
        elif securitytext !='':
            parameters={'Parameters':  {'SecurityText':securitytext,
                                        'Frequency':freq,
                                        'TimeSeriesFromDate':start_date.strftime('%Y/%m/%d'),
                                        'TimeSeriesToDate':end_date.strftime('%Y/%m/%d')
                                }}         
        inputs={**self.header, **parameters}
        res=self.client.service.TimeSeriesGet2(Input=inputs)
        data=zeep.helpers.serialize_object(res.Result.DataRows.DataRow)
        df=pd.DataFrame(data)
        df['TimeSeriesDate']=pd.to_datetime(df.TimeSeriesDate)
        df=df.set_index('TimeSeriesDate')

        return df


    def time_series(self,start_date,end_date,ticker,exchange='',freq='daily',fields=[]):
        '''

        Available fields  - ['OpenPrice', 'HighPrice', 'LowPrice', 'ClosePrice', 'TotalVolume',
                           'TotalValue', 'TradeCount', 'AdjustmentFactor', 'MarketVWAP',
                           'ShortSold', 'ShortSoldPercent', 'ShortSellPosition',
                           'ShortSellPositionPercent', '_value_1', 'exchange']

        '''
        part_date=start_date
        data=pd.DataFrame()
        if ticker.find('.')>-1:
            securitytext = ticker
        elif ticker.find('@')>-1:
            securitytext = ticker
        else:
            securitytext = ''
        while part_date < pd.Timestamp(end_date):
            try:
                new_data=self._time_series(part_date,end_date,ticker = ticker,exchange = exchange,securitytext = securitytext,freq = 'daily')
                data=pd.concat([data,new_data])
                part_date = data.index.max() + pd.DateOffset(1,'D')
            except:
                break
            
        return data
    
    def dividends(self,ticker,exchange,start_date,end_date,freq=None,index_on='ExDividendDate'):
        '''
        SecurityCode string Yes  No  The security code to filter by.  
        Exchange string Yes  No  The exchange to filter by.  
        DataSource string Yes  No  The data source to filter by.  
        Frequency string No  No  The frequency type, one of 'daily', 'weekly', 'monthly', 'quarterly' or 'yearly'.  
        TimeSeriesFromDate date No  No  The date to retrieve time series from.  
        TimeSeriesToDate date No  No  The date to retrieve time series to. 
        
        available fields = ['DividendAmount', 'AdjustedDividendAmount', 'FrankedPercent',
                           'PayableDate', 'BooksClosingDate', 'DividendType', 'ShareRate',
                           'DividendYield', 'DRPPrice', 'DividendDescription', 'DeclarationDate',
                           'STCCreditsPerShare', '_value_1', 'exchange']
        '''
        parameters={'Parameters':  {'SecurityCode': ticker,
                          'Exchange': exchange,
                          'PayDateFrom':start_date.strftime('%Y/%m/%d'),
                          'PayDateTo':end_date.strftime('%Y/%m/%d')
                          } } 
        
        inputs={**self.header, **parameters}
        
        try:
            res=self.client.service.SecurityDividendGetBySecurity(Input=inputs)
            data=zeep.helpers.serialize_object(res.Result.DataRows.DataRow)
            df=pd.DataFrame(data)
            df[index_on]=pd.to_datetime(df[index_on])
            df=df.set_index(index_on)
        except:
            df=pd.DataFrame()
        
        return df

    def MarketCapitalizationHistorical(self,indexcode,ticker,exchange,start_date,end_date):
        '''
        Input Parameters
        For the items that are nullable input None
        
        Pos     Name        Type Nullable? DefaultValue Array? ArraySize Description Alias
        1       IndexCode   string Yes  No  The index to filter by.  
        2       SecurityCode string Yes  No  Security code.  
        3       Exchange   string Yes  No  Exchange where the security is listed.  
        4       MarketCapitalizationDateFrom date No  No  The date to retrieve market capitalization history from.  
        5       MarketCapitalizationDateTo date No  No  The date to retrieve market capitalization history to. 

        Output Columns
        Pos Name Type Nullable? Default Value Description Alias
        1 SecurityCode string No    Security code.  
        2 Exchange string No    Exchange where the security is listed.  
        3 GICSCode int32 Yes    Global Industry Classification Standard.  
        4 MarketCapitalizationDate date No    Date at which market capitalization was calculated.  
        5 IndexCode string No    Index code.  
        6 IndexFactor double Yes    The index factor.  
        7 IndexPoints double Yes    Index points.  
        8 SharesOnIssue double Yes    Number of shares issued for the security at the time market capitalization was calculated.  
        9 MarketCapitalizationStartOfDay double Yes    Market capitalization at the start of the day.  
        10 MarketCapitalizationEndOfDay double Yes    Market capitalization at the end of the day.  
        11 MarketWeightStartOfDay double Yes    Market weight at the start of the day.  
        12 MarketWeightEndOfDay double Yes    Market weight at the end of the day.  
        13 IndexPriceStartOfDay double Yes    Index price at the start of the day.  
        14 IndexPriceEndOfDay double Yes    Index price at the end of the day. 
        
        
        '''
        
        parameters={'Parameters':  {'IndexCode':indexcode,
                    'SecurityCode': ticker,
                      'Exchange': exchange,
                      'MarketCapitalizationDateFrom':start_date.strftime('%Y/%m/%d'),
                      'MarketCapitalizationDateTo':end_date.strftime('%Y/%m/%d')
                      } } 
        remove_key=[]
        for k,v in  parameters['Parameters'].items():
            if v==None:
                remove_key.append(k)
        for k in remove_key:
            del parameters['Parameters'][k]
        
        inputs={**self.header, **parameters}
        res = self.client.service.MarketCapitalizationHistoricalGet(Input=inputs)
        data=zeep.helpers.serialize_object(res.Result.DataRows.DataRow)
        df=pd.DataFrame(data)
        return df


    def get_many(self,start_date,end_date,data_type,tickers,exchange = '',freq='daily'):
        '''
        
        '''
        data_list=[]
        date_field={'dividends':'ExDividendDate',
        'time_series':'TimeSeriesDate'}
        if data_type not in ['dividends','time_series']:
            warnings.warn("Not available for this data type")
            return
        method_to_call = getattr(self, data_type)
        for ticker in tickers:
            data=method_to_call(start_date,end_date,ticker=ticker,exchange=exchange,freq=freq)
            if len(data)>0:
                data=data.reset_index()
                data['ticker']=ticker
                data['exchange']=exchange
                data=data.set_index([date_field[data_type],'ticker'])
                data_list.append(data)
        df_data=pd.concat(data_list)
        return df_data



    def time_series_intraday(self,ticker,exchange,start_date,end_date,freq='minutes',interval=60):
        '''

        Input Parameters
        
        
        Pos     Name        Type Nullable? DefaultValue Array? ArraySize Description Alias
        1 SecurityCode string 32 Yes  No  The security code to filter by.  
        2 Exchange string 16 Yes  No  The exchange to filter by.  
        3 DataSource string 8 Yes  No  The data source to filter by.  
        4 Frequency string 80 No  No  The frequency type, one of 'trades' or 'minutes'. 
        The following are the restrictions when filtering by a date range for the following consolidation intervals: Less than 10 minutes - 7 days,
           10 to 30 minutes - 30 days, 30 to 60 minutes - 60 days. For a frequency of 'trades' the maximum number of days requested is equal to twice the consolidation interval to a maximum of 60 days.  
        5 TimeSeriesFromDateTime dateTime 8 No  No  The date and time to retrieve time series from.  
        6 TimeSeriesToDateTime dateTime 8 No  No  The date and time to retrieve time series to.  
        7 ConsolidationInterval int32 4 No  No  If Frequency is set to 'trades' this sets the number of trades that will be consolidated on each row,
           however if Frequency is set to 'minutes' 
           this sets the number of minutes that will be consolidated on each row and must be set to a number between 1 and 60 that is an integral divisor of 60, eg 1, 2, 3, ... , 20, 30.  
        8 IncludeTradingPeriod boolean 1 No false No  Indicate the start and end trading times. Valid with 'minutes' frequency only.  
        9 SecurityText string -1 Yes  No  Security text, in the form of: code.exchange@datasource|board, where exchange, data source and board are optional. Examples: BHP, BHP.ASX, BHP.ASX@TM, BHP@TM, TSX.TSX@TSX|T  
        
        Header Columns
        
        1 PriceDisplayMultiplier double 8 No    Price display multiplier.  
        2 SecurityCode string 32 No    Security code.  
        3 Exchange string 16 No    Exchange where the security is listed.  
        4 DataSource string 8 No    The data source for the security.  
        
        Output Columns
        
        1 OpenPrice double 8 Yes    Opening price for the time period.  
        2 HighPrice double 8 Yes    Highest price for the time period.  
        3 LowPrice double 8 Yes    Lowest price for the time period.  
        4 ClosePrice double 8 No    Closing price for the time period.  
        5 TotalVolume double 8 Yes    Total volume traded for the time period.  
        6 TotalValue double 8 Yes    Total value traded for the time period.  
        7 TradeCount int32 4 Yes    Number of trades for the time period.  
        8 TimeSeriesDateTime dateTime 8 Yes    Date and time of the intraday time series point.  
        9 TradingPeriod int32 4 Yes    0 = Start Trading. 1 = Start Trading (with no trades during the start trading period). 2 = End Trading. 3 = End Trading (with no trades during the end trading period).  
        10 LastTradeNumberOfTheInterval int64 8 Yes    The last trade number of the interval.  
        

        '''
        parameters={'Parameters':  {'SecurityCode': ticker,
                          'Exchange': exchange,
                          'Frequency':freq,
                          'TimeSeriesFromDateTime':start_date.strftime('%Y-%m-%dT%H:%M:%S%Z'),
                          'TimeSeriesToDateTime': end_date.strftime('%Y-%m-%dT%H:%M:%S%Z'),
                          'ConsolidationInterval':str(interval)
                          } } 
        
        inputs={**self.header, **parameters}
        res=self.client.service.TimeSeriesIntraDayGet2(Input=inputs)
      
        data=zeep.helpers.serialize_object(res.Result.DataRows.DataRow)
        df=pd.DataFrame(data)
        df['TimeSeriesDate'] = pd.to_datetime(df.TimeSeriesDateTime)
        df['TimeSeriesDate'] = df.TimeSeriesDate.dt.tz_localize('America/New_York')
        df=df.set_index('TimeSeriesDate')
        return df

    def get_quotes(self,ticker=[],exchange =[],watchlist=False, tickers = ''):
        
        '''
            Retrieves basic quote information for one or more securities.
            A security code must be specified in the SecurityCode or SecurityText parameter.
            If both SecurityCode and SecurityText are given, SecurityCode is used.

            Input Parameters
            
            
            Pos Name Type Nullable?  Default Value    Array?  Array Size  Description Alias
            
            1 SecurityCode string Yes  Yes 1000 Security code.  
            2 Exchange string Yes  Yes 1000 Exchange where the security is listed.  
            3 DataSource string Yes  Yes 1000 Data source for the security.  
            4 UserWatchlistProvided boolean Yes  No  Indicates whether the SecurityCode provided is the name of a user defined watchlist.  
            5 SecurityText string Yes  Yes 1000 Security text, in the form of: code.exchange@datasource|board, where exchange, data source and board are optional. Examples: BHP, BHP.ASX, BHP.ASX@TM, BHP@TM, TSX.TSX@TSX|T  
            
            Output Columns
            
            
            Pos Name Type Nullable? Default Value    Description Alias
            
            1Primary Key Position 1 SecurityCode string No    Security code.  
            2Primary Key Position 2 Exchange string No    The exchange where the security is listed.  
            3Primary Key Position 3 DataSource string No    The data source for the security.  
            4 ErrorNumber int32 No    The error number if the security was not available.  
            5 AskCount int32 Yes    The number of sells at the current ask price. #Ask 
            6 AskPrice double Yes    The current ask price.  
            7 AskVolume double Yes    Total volume at the current ask price.  
            8 BidCount int32 Yes    The number of buys at the current bid price. #Bid 
            9 BidPrice double Yes    The current bid price.  
            10 BidVolume double Yes    Total volume at the current bid price.  
            11 TotalVolume double Yes    Total volume traded for the current day.  
            12 TotalValue double Yes    Total value traded for the current day.  
            13 HighPrice double Yes    Highest price traded for the current day.  
            14 LastPrice double Yes    Last price in cents (unadjusted).  
            15 LowPrice double Yes    Lowest price traded for the current day.  
            16 MatchPrice double Yes    Indicative match price before market match occurs.  
            17 MatchVolume double Yes    Indicative match volume.  
            18 MarketValue double Yes    Value traded during market hours.  
            19 MarketVolume double Yes    Volume traded during market hours.  
            20 Movement double Yes    Current days movement in points.  
            21 OpenPrice double Yes    Opening price.  
            22 QuotationBasisCode string Yes    Basis of quotation code for the security.  
            23 CompanyReportCode string Yes    Deprecated. Please use the NewsReportVendors column in PricingQuoteExtraGet or PricingWatchListGet.  
            24 TradingStatus string Yes    Trading status of the security.  
            25 TradeCount int32 Yes    The number of the trades.  
            26 TradeDateTime dateTime Yes    Date and time of the last trade.  
            27 UpdateDateTime dateTime Yes    Date and time of the last update.  
            28 PreviousClosePrice double Yes    Previous day's close price.  
            29 Board string Yes    Vendor datasource board.
            
            {http://webservices.iress.com.au/v4/}PricingQuoteGetInputParameters()
            got an unexpected keyword argument 'SecurityCode'. Signature: `SecurityCodeArray: {SecurityCode: xsd:string[]}, ExchangeArray: {Exchange: xsd:string[]}, 
            DataSourceArray: {DataSource: xsd:string[]}, UserWatchlistProvided: xsd:boolean, SecurityTextArray: {SecurityText: xsd:string[]}`
            
            
            
        '''
        if len(tickers)>0:
            parameters={'Parameters':  {'SecurityTextArray':{'SecurityText':tickers},
                                           
                              } } 
        elif len(ticker)>0 and not watchlist:
            parameters={'Parameters':  {'SecurityCodeArray':{'SecurityCode':ticker},
                                }}    
        elif watchlist:
            parameters={'Parameters':  {'UserWatchlistProvided':watchlist,'SecurityTextArray':{'SecurityText':ticker},
                                }}            
        else:
            parameters = {}
        
        inputs = {**self.header, **parameters}
        res = self.client.service.PricingQuoteGet(Input=inputs)
      
        data = zeep.helpers.serialize_object(res.Result.DataRows.DataRow)
        df = pd.DataFrame(data)
        return df

        

if __name__ == "__main__":
    
    pass

        
        
        
        
        

        
        
        
        
