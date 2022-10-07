# Development process
1. (**DONE**) Extract raw stock information of all tradable stocks. Information are ISIN number and the extracted stock name. These information are written to the stock table in the news database (news.db). --> ``isin-data.ipynb``
2. (**DONE**) Use the raw stock information collected in 1. and enrich these information and also save these enriched data to the news database. The table for this is ``stocks_enriched``. 
