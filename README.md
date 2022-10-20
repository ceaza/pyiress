# PyIress #

PyIress is a Python interface onto the Iress web services API. See the [Website](https://www.iress.com/za/company/products/iress-pro-market-data-desktop/).

### Main Features ###

* The code allows for easy extraction of the following types of data
	Time series information
	Dividend information
	Index information
* Version 0.0.7
* This is the first version and the intention is to add to the list of available functions.
* The following are currenly available:
	- time_series : an items times series
	- time_series_intraday : time series for a security with granularity finer than one day
	- dividends : dividends for an item
	- get_many : many of the above
	- MarketCapitalizationHistorical : Index constituent information over a specified period

### Installation ###

* Dependencies
	- zeep
	
	For the [Zeep documentation](https://python-zeep.readthedocs.io/en/master/).
	- pandas
	
	For the dependencies of `pandas` please refer to the [pandas documentation](http://pandas.pydata.org/pandas-docs/stable/install.html).

* To install the latest version

		pip install pyiress


### Some Notes on Use ###
	
* Pandas is great for data analysis. We pull down the data and add it to a dataframe.


		from pyiress import Iress
		import pandas as pd
		companyname = "<>"
		username = "<>"
		password = "<>" 
		ApplicationID='app'
	
		iress = Iress(companyname=companyname,username=username,password=password,show_request=False)
		tickers=['AGL','BIL']
		exchange = 'JSE'
		start_date, end_date = pd.datetime(2018,9,30),pd.datetime(2022,8,30)
		data=iress.get_many('time_series',tickers,exchange,start_date,end_date)
		data=data[['ClosePrice']]
		data.unstack(1).plot()
		
### Resources ###

* Use the help in Iress Pro. Go to Help/API Documentation and select the pertinant resource.
* Any comments welcome.



### License ###

PyIress library is released under the MIT license.

The license for the library is not extended in any sense to any of the content of the Iress or related services. Appropriate contract with Iress and valid credentials are required in order to use the API.

Author of the library (@ceaza) is not affiliated, associated, authorized, sponsored, endorsed by, or in any way officially connected with Iress, or any of its subsidiaries or its affiliates. The name “Iress” as well as related names are registered trademarks of Iress.

