import datetime
from functools import wraps


class Bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def operation(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        self.operations.append(method.__name__)
        return method(self, *args, **kwargs)

    return wrapper


class QBResponse(dict):
    def __init__(self, requests_response=None, **kwargs):
        super().__init__()
        if requests_response:
            self.ok = requests_response.ok
            self.status_code = requests_response.status_code
            self.text = requests_response.text


class QBQueryResponse(QBResponse):

    def __init__(self, res=None, **kwargs):
        self.response_type = 'records'
        self.operations = []
        # potential to load sample data for testing
        if kwargs.get('sample_data'):
            self.update(kwargs.get('sample_data'))
        super().__init__(requests_response=res)

    def is_empty(self):
        """
        Tests if data is empty, return True if so.
        :return: boolean
        """
        return self.get('data', False)

    def info(self, prt=True):
        """
        Prints information about the response.
        :prt: Set to False to only grab the return as a string.
        """
        if self.response_type == 'records':
            info = [f'{Bcolors.OKBLUE}Sample Data:\n']
            try:
                info.append('\t' + str(self.get('data')[0]) + '\n\n')
            except KeyError as e:
                info.append('\t' + str(self.get('data')) + '\n')
            info.append(Bcolors.ENDC)
            info.append(f'{Bcolors.OKGREEN}Fields:\n')

            fields_info = []
            for field in self.get('fields'):
                field_info = []
                # build field info
                for k, v in field.items():
                    field_info.append(f'{k}: {v}')
                fields_info.append(field_info)

            # print field info
            for fi in fields_info:
                info.append('\t' + '{:<16s} {:<32s} {:<16s}\n'.format(fi[0], fi[1], fi[2]))
            info.append(Bcolors.ENDC)

            info.append(f'\n{Bcolors.OKCYAN}Metadata:\n')
            for k, v in self.get('metadata').items():
                info.append('\t{:<16s} {:<16s}\n'.format(k, str(v)))
            info.append(Bcolors.ENDC)

            info_str = ''.join(info)

            if prt:
                print(info_str)

            return info_str

    def fields(self, prop):
        """
        Gets fields, given property, i.e. label, id or type
        :param prop: property of field
        :return: list of fields
        """
        return [i.get(prop) for i in self.get('fields')]

    def data(self):
        """
        Gets data, shorthand for .get('data')
        :return: data
        """
        return self.get('data')

    def prd(self, data):
        """
        Print relevant data, simple print function.
        :param data: data to print
        """
        print("\033[91m", 'Relevant Data:\n\n', data, '\n', "\033[0m")

    @operation
    def denest(self):
        """
        Denests data, i.e. if in {'key': {'value': actual_value}} format. -> {'key': actual_value}
        :return: QBResponse
        """
        data = self.get('data')
        # ugly handling for now, need to fix
        if type(data) is dict:
            new_records = {}
            for record, record_value in data.items():
                new_record_value = {}
                for k, v in record_value.items():
                    new_record = {}
                    new_record.update({k: v.get('value')})
                    new_record_value.update(new_record)
                new_records.update({record: new_record_value})

            self.update({'data': new_records})

        if type(data) is list:
            for d in data:
                for k, v in d.items():
                    d.update({k: v.get('value')})

        return self

    @operation
    def orient(self, orient, **kwargs):
        """
        Orients the data, given orientation argument.
        :param orient: type of orientation, 'records' is the only orientation for now.
        :param kwargs: 'records' argument needs 'key' argument, to determine key for records.
        :return: QBResponse
        """
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
            try:
                for i in self.get('data'):
                    if 'denest' in self.operations:
                        key = i.pop(selector)
                    else:
                        key = i.pop(selector).get('value')
                    records.update({key: i})
            except KeyError as e:
                print('KeyError:', e, 'Attempting to use Record ID#')
                self.prd(self.get('data')[0])

                # attempt to find selector in fields
                for i in self.get('fields'):
                    if i.get('id') == int(selector):
                        selector = i.get('label')
                        break

                for i in self.get('data'):
                    key = i.pop(selector)
                    records.update({key: i})

            # set data to records
            self.update({'data': records})

            return self

        else:
            raise ValueError(f'{orient} is not a valid orientation.')

    def currency(self, currency_type):
        return self

    def transform(self, transformation, **kwargs):
        """
        Transforms the data, given a transformation argument.
        :param transformation: type of transformation.
        :return: QBResponse
        """
        if transformation == 'labels':

            # transform fids into labels
            if not self.get('data'):
                raise KeyError(
                    'Try transforming the data before applying additional methods.')

            data = self.get('data')
            fields = self.get('fields')

            fields_dict = {i['id']: i for i in fields}

            # replace record id numbers with record labels
            records = []
            for idx, d in enumerate(data):
                record = {}
                for k, v in d.items():
                    record.update({
                        fields_dict[int(k)].get('label'): v if v.get('value') is None else v.get('value')
                    })

                records.append(record)
            self.update({'data': records})

        if transformation == 'intround':
            raise ValueError('This transformation has been deprecated, please use the "round_ints()" method.')

        return self

    def round_ints(self):
        """
        Round int fields (remove floating .0 from int fields)
        :return:
        """
        for f in self.get('fields'):
            fid = str(f.get('id'))
            if f.get('type') == 'numeric':

                if 'denest' in self.operations:
                    for d in self.get('data'):
                        if d.get(fid).is_integer():
                            d.update({fid: int(round(d.get(fid)))})
                else:
                    for d in self.get('data'):
                        d.update({fid: {
                            'value': int(round(d.get(fid).get('value')))}})

        return self

    def convert_type(self, field_type, **kwargs):
        """
        Converts data of certain field types to standard python objects
        :param field_type:
        :param kwargs:
        :return:
        """

        def c_datetime():
            """
            Helper function that converts date time QB fields to datetime ojects.
            """
            for f in self.get('fields'):
                fid = str(f.get('id'))
                if f.get('type') == 'date time':

                    if 'denest' in self.operations:
                        for d in self.get('data'):
                            d.update({fid: datetime.datetime.strptime(d.get(fid), '%Y-%m-%dT%H:%M:%S.%fZ')})
                    else:
                        for d in self.get('data'):
                            d.update({fid: {
                                'value': datetime.datetime.strptime(d.get(fid).get('value'), '%Y-%m-%dT%H:%M:%S.%fZ')}})

        def c_currency(currency_format):

            for f in self.get('fields'):
                fid = str(f.get('id'))
                if f.get('type') == 'numeric currency':

                    if 'denest' in self.operations:
                        for d in self.get('data'):
                            fmt = currency_format + "{:,.2f}".format(d.get(fid))
                            d.update({fid: fmt})
                    else:
                        for d in self.get('data'):
                            fmt = currency_format + "{:,.2f}".format(d.get(fid).get('value'))
                            d.update({fid: {'value': fmt}})

        if field_type == 'datetime':
            c_datetime()
        if field_type == 'numeric currency' or field_type == 'currency':
            c_currency(kwargs.get('fmt'))

        return self
