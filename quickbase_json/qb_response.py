test_data = {
    "data": [
        {
            "6": {
                "value": "Andre Harris"
            },
            "7": {
                "value": 10
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


class QBResponse(dict):
    def __init__(self, response_type):
        self.response_type = response_type
        super().__init__()

    def denest(self):
        denested_list = []
        for record in self.get('data'):
            denested = {}
            for k, v in record.items():
                denested.update({k: v.get('value')})
            denested_list.append(denested)
        self.update({'data': denested_list})
        return self

    def orient(self, orient, **kwargs):

        if orient == 'records':
            if not kwargs.get('key'):
                raise ValueError('Missing required "key" argument for records orientation')
            else:
                if isinstance(kwargs.get('key'), int):
                    selector = kwargs.get('key')
                    selector = str(selector)
                else:
                    raise TypeError(f'Key must be an {int}')

            # loop data list, create dict
            records = {}
            for i in self.get('data'):
                print(i)
                key = i.pop(selector).get('value') if self.get('data') else i.pop(selector)
                records.update({key: i})

            # set data to records
            self.update({'data': records})

            return self

        else:
            raise ValueError(f'{orient} is not a valid orientation.')

    def currency(self, currency_type):
        return self

    def transform(self, transformation):
        if transformation == 'labels':

            # transform fids into labels
            if not self.get('data'):
                raise KeyError(
                    'Try transforming the data before applying additional methods.')

            data = self.get('data')
            print(data)
            fields = self.get('fields')

            fields_dict = {i['id']: i for i in fields}

            records = []
            for idx, d in enumerate(data):
                record = {}
                print('data', d)
                for k, v in d.items():
                    record.update({
                        fields_dict[int(k)].get('label'): v if v.get('value') is None else v.get('value')
                    })
                    records.append(record)
                    print(k, v)

            self.update({'data': records})

        return self


qbr = QBResponse('records')
qbr.update(test_data)
qbr.transform('labels').orient('records', key=6)

print(qbr)

# # handle transform
# if kwargs.get('transform'):
#     # labels
#     if kwargs.get('transform') == 'labels':
#
#         # transform fids into labels
#         data = json_data.get('data')
#         fields = json_data.get('fields')
#
#         fields_dict = {i['id']: i for i in fields}
#         print(fields_dict)
#
#         records = []
#         for idx, d in enumerate(data):
#             record = {}
#             print('data', d)
#             for k, v in d.items():
#                 record.update({
#                     fields_dict[int(k)].get('label'): v if kwargs.get('denested') else v.get('value')
#                 })
#                 records.append(record)
#                 print(k, v)
#
#         json_data.update({'data': records})
#

#
# # handle data orientation
# if kwargs.get('orient'):
#     if kwargs.get('orient') == 'records':
#
