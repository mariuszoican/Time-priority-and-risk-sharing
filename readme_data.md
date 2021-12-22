## TMX Data Description

* **Time period**: from March 15, 2021 to April 15, 2021
* **Products**: 
    * TMC: Very short term fixed income contract.
    * TYG: Fixed income futures contract (long maturity)
    * FYG: Fixed income futures contract (short maturity)
    * STF: Equity futures contract	
* **Expiration dates**:
    * U21: September 2021
    * Z21: December 2021
    * H21: March 2021
    * M21: June 2021

### Order Book Data

Order book data is in `.csv.gz` format, under file structure:
```\TMXData\topOfBook\**date**\**Instrument**_AtBest_**date**.csv.gz```

Data fields:
* ```externalSymbol```: Instrument ID in Product-Expiration format.
* ```datetime```: Date and time in ```YYYY-MM-DD HH:MM:SS``` format, with a 5-second resolution.
* ```side```: Order book side, either ```bid``` or ```ask```.
* ```priority```: Priority level in the book. Orders with lower values execute before orders with higher values.
* ```account```: Order submitter/Account ID  (alphanumeric)
* ```quantity```: Order quantity (in contract units). 

### Trade Data

Trade data is in `.csv.gz` format, under file structure: `\TMXData\trades\**date**.csv.gz`.

Data fields:
* `number`: trade number ID (each unique trade has two entries, one for buyer and one for seller).
* `account`: Account ID (alphanumeric)
* `externalSymbol`: Instrument ID in Product-Expiration format.
* `date`: Date in format `YYYYMMDD`.
* `time`: Time in format `HHMMSS`.
* `milliseconds`: Milliseconds; a number between 000 and 999.
* `side`: Trade side, either `Buy` or `Sell`
* `quantity`: Trade quantity in contract units.
* `price`: Trade price in CAD.
* `order`: Order type, either `Limit`, `Market`, `MarketOnOpening`, `Committed`. 
  Committed trades occur when two exchange-approved parties pre-arrange a transaction and their committed orders are matched at an equal price and quantity on opposite sides of the trade
* `initiation`: Trader initiated the trade (`Taker`) or was passive (`Maker`), or label is not applicable e.g., 
  in auctions (`None`).
* `Bid`: Best Bid Price
* `Ask`: Best Ask Price
