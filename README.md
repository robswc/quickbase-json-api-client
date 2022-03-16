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
```python
from quickbase_json import QBClient

client = QBClient(realm="yourRealm", auth="userToken")
```

Where `yourRealm` is the name (subdomain) of your Quickbase Realm and `userToken` is the user token used to authenticate
with the realm.

## Query Records
Querying for records is one of the most useful features of the Quickbase JSON API.  Querying records with QJAC can be done
using the following code

#### Basic Example

```python
response = client.query_records(table='tableId', select=[3, 6, 12], query='queryString')
```

Where `tableId` is the ID of the table you wish to query from, `fids` is a list of field IDs you wish to receive and `queryString`
is a quickbase [query string](https://help.quickbase.com/api-guide/componentsquery.html).


#### Adv. Example

```python
from quickbase_json.helpers import Where
# have static fids for table/records
NEEDED_FIDS = [3, 6, 12]
# build query str where 3 is either 130, 131 or 132
# https://help.quickbase.com/api-guide/componentsquery.html
q_str = Where(3, 'EX', [130, 131, 132]).build(join='OR') 
response = client.query_records(table='tableId', select=NEEDED_FIDS, query=q_str)
```

In this example, we use the `Where()` helper.  This can make building complex [QuickBase queries](https://help.quickbase.com/api-guide/componentsquery.html) easier.

The `Where()` helper documentation can be found [here](!https://github.com/robswc/quickbase-json-api-client/wiki/Helper:-Where).


## Response Objects

A `QBResponse` object is returned when querying records with QJAC.  A `QBResponse` has several methods that make
handling returned data easier.  Here are a few of the most useful ones.

### Response Methods

- **.data()**

```python
r = qbc.query_records(...).data()
```

Returns the data from QuickBase.  Equivalent to calling `.get('data')` 

- **.denest()**

```python
r = qbc.query_records(...).denest()
```

Denests the data.  I.e. changes `{'fid': {'value': 'actualValue'}}` to `{'fid': 'actualValue'}`

- **orient(orient: str, key: int)**

```python
r = qbc.query_records(...).orient('records', key=3)
```

Orients the data.  Currently, the only option is 'records'.  This will orient the returned data into a "record like structure", i.e. changes
`{'fid': 'actualValue', 'fid': 'actualValue'}` to `{'key': {etc: etc}}`

- **convert()**


```python
r = qbc.query_records(...).convert('datetime')
```

Converts the data, based on fields and provided arguments.  For example, calling `convert('datetime')` will convert all data with fields
of the 'date time' type to python datetime objects.  Other conversions are 'currency' and 'int'.

- **round_ints()**


```python
r = qbc.query_records(...).round_ints()
```


Rounds all float integers into whole number ints.  i.e. converts `55.0` to `55`.

