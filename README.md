# quickbase-json-api-client

![build](https://img.shields.io/github/workflow/status/robswc/quickbase-json-api-client/Python%20application?style=for-the-badge)
![size](https://img.shields.io/github/languages/code-size/robswc/quickbase-json-api-client?style=for-the-badge)
![license](https://img.shields.io/github/license/robswc/quickbase-json-api-client?style=for-the-badge)

Unofficial Quickbase JSON API wrapper for python

Makes life a little easier!

# Quickstart

## Installation
To install, run `pip install quickbase-json-api-client`

## Initialize Client
Use the following code to create and initialize a client object. 
```
from quickbase_json.client import QuickbaseJSONClient # import client

client = QuickbaseJSONClient(realm="yourRealm", auth="userToken")
```

Where `yourRealm` is the name (subdomain) of your Quickbase Realm and `userToken` is the user token used to authenticate
with the realm.

## Query Records
Querying for records is one of the most useful features of the Quickbase JSON API.  Querying records with QJAC can be done
using the following code

`response = client.query_records('tableId', fids, 'queryString')`

Where `tableId` is the ID of the table you wish to query from, `fids` is a list of field IDs you wish to receive and `queryString`
is a quickbase [query string](https://help.quickbase.com/api-guide/componentsquery.html).

## Response Objects

A `QBResponse` object is returned when querying records with QJAC.  A `QBResponse` has several methods that make
handling returned data easier.  Here are a few of the most useful ones.

### Response Methods

- **data()**

Returns the actual data.  Equivalent to calling `.get('data')` 

- **denest()**

Denests the data.  I.e. changes `{'fid': {'value': 'actualValue'}}` to `{'fid': 'actualValue'}`

- **orient(orient='records', key='3')**

Orients the data.  Currently, the only option is 'records'.  This will orient the returned data into a "record like structure", i.e. changes
`{'fid': 'actualValue', 'fid': 'actualValue'}` to `{'key': {etc: etc}}`

- **convert()**

Converts the data, based on fields and provided arguments.  For example, calling `convert('datetime')` will convert all data with fields
of the 'date time' type to python datetime objects.  Other conversions are 'currency' and 'int'.

- **round_ints()**

Rounds all float integers into whole number ints.  i.e. converts `55.0` to `55`.

