# PyIRess #

PyIress is a Python interface onto the Iress web services API. See the [Website] (https://www.iress.com/za/company/products/iress-pro-market-data-desktop/).

### Main Features ###

* The code allows for easy extraction of the following types of data
	Time series information
	Dividend information
	Index information
* Version 0.1
* This is the first version and the intention is to add to the list of available functions.
* The following are currenly available:
	- time_series : an items times series
	- dividends : dividends for an item
	- get_many : many of the above
	- MarketCapitalizationHistorical : Index constituent information

### Installation ###

* Dependencies
	zeep
	For the [Zeep documentation] (https://python-zeep.readthedocs.io/en/master/).
	pandas
	For the dependencies of `pandas` please refer to the [pandas documentation](http://pandas.pydata.org/pandas-docs/stable/install.html).

* To install the latest version
	pip install pyiress


### Some Notes on Use ###
	
	Pandas is great for data analysis 


		from pyiress import Iress
		import pandas as pd
		companyname = "<>"
		username = "<>"
		password = "<>" 
		ApplicationID='app'
	
		iress = Iress(companyname=companyname,username=username,password=password,show_request=False)
		tickers=['AGL','BIL']
		exchange = 'JSE'
		start_date, end_date = pd.datetime(2012,9,30),pd.datetime(2018,8,30)
		data=iress.get_many('time_series',tickers,exchange,start_date,end_date)
		data=data[['ClosePrice']]
		data.unstack(1).plot()
		
### Resources ###

* Use the help in Iress Pro. Go to Help/API Documentation and select the pertinant resource.


### Acknowledgements ###

* Thanks to Vladimir Filimonov @vfilimonov whe wrote PyDatastream on which this project is based