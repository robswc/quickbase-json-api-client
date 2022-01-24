record_data = {
    "data": [
        {
            "6": {
                "value": "Andre Harris"
            },
            "7": {
                "value": 10.0
            },
            "8": {
                "value": "2019-12-18T08:00:00.000Z"
            }
        }
    ],
    "fields": [
        {
            "id": 6,
            "label": "Full Name",
            "type": "text"
        },
        {
            "id": 7,
            "label": "Amount",
            "type": "numeric"
        },
        {
            "id": 8,
            "label": "Date time",
            "type": "date time"
        }
    ],
    "metadata": {
        "totalRecords": 10,
        "numRecords": 1,
        "numFields": 3,
        "skip": 0
    }
}

record_data_load = {'data': [{'6': {'value': 'Andre Harris'},
                              '7': {'value': 10},
                              '8': {'value': '2019-12-18T08:00:00.000Z'}}],
                    'fields': [{'id': 6, 'label': 'Full Name', 'type': 'text'},
                               {'id': 7, 'label': 'Amount', 'type': 'numeric'},
                               {'id': 8, 'label': 'Date time', 'type': 'date time'}],
                    'metadata': {'numFields': 3, 'numRecords': 1, 'skip': 0, 'totalRecords': 10}}

record_data_get_info = """
[94mSample Data:
	{'6': {'value': 'Andre Harris'}, '7': {'value': 10}, '8': {'value': '2019-12-18T08:00:00.000Z'}}

[0m[92mFields:
	id: 6            label: Full Name                 type: text      
	id: 7            label: Amount                    type: numeric   
	id: 8            label: Date time                 type: date time 
[0m
[96mMetadata:
	totalRecords     10              
	numRecords       1               
	numFields        3               
	skip             0               
[0m
"""
