import datetime


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


class QBResponse(dict):
    def __init__(self, response_type, **kwargs):
        self.response_type = response_type
        self.transformations = {}
        # potential to load sample data for testing
        if kwargs.get('sample_data'):
            self.update(kwargs.get('sample_data'))
        super().__init__()

    def info(self):
        """
        Prints information about the response.
        """
        if self.response_type == 'records':

            print(f'{Bcolors.OKBLUE}Sample Data:\n')
            try:
                print('\t', self.get('data')[0], '\n')
            except KeyError as e:
                print('\t', self.get('data'), '\n')
            print(Bcolors.ENDC)
            print(f'{Bcolors.OKGREEN}Fields:\n')

            fields_info = []
            for field in self.get('fields'):
                field_info = []
                # build field info
                for k, v in field.items():
                    field_info.append(f'{k}: {v}')
                fields_info.append(field_info)

            # print field info
            for fi in fields_info:
                print('\t', '{:<16s} {:<32s} {:<16s}'.format(fi[0], fi[1], fi[2]))
            print(Bcolors.ENDC)

            print(f'\n{Bcolors.OKCYAN}Metadata:\n')
            for k, v in self.get('metadata').items():
                print('\t{:<16s} {:<16s}'.format(k, str(v)))
            print(Bcolors.ENDC)

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
        return self

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
                    key = i.pop(selector).get('value') if self.get('data') else i.pop(selector)
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

        if transformation == 'datetime':
            """Finds columns that are of type datetime and converts them into python datetime objects"""
            # transform fids into labels

            data = self.get('data')
            fields = self.get('fields')

            for field in fields:
                if field.get('type') == 'date time':
                    if type(self.get('data') == list):
                        for row in data:
                            dt_field = row.get(str(field.get('id')))
                            if dt_field.get('value') is None:
                                str_dt = dt_field
                                dt = datetime.datetime.strptime(str_dt, '%Y-%m-%dT%H:%M:%S.%fZ')
                                row.update({str(field.get('id')): dt})
                            else:
                                str_dt = dt_field.get('value')
                                dt = datetime.datetime.strptime(str_dt, '%Y-%m-%dT%H:%M:%S.%fZ')
                                row.update({str(field.get('id')): {'value': dt}})

                if field.get('type') == 'date':
                    if type(self.get('data') == list):
                        for row in data:
                            dt_field = row.get(str(field.get('id')))
                            if dt_field.get('value') is None:
                                str_dt = dt_field
                                dt = datetime.datetime.strptime(str_dt, kwargs.get('datestring'))
                                row.update({str(field.get('id')): dt})
                            else:
                                str_dt = dt_field.get('value')
                                dt = datetime.datetime.strptime(str_dt, kwargs.get('datestring'))
                                row.update({str(field.get('id')): {'value': dt}})

        if transformation == 'intround':
            """Rounds numbers and transforms them to ints"""

            data = self.get('data')
            fields = self.get('fields')

            for field in fields:
                if field.get('type') == 'numeric':

                    if type(self.get('data') == list):
                        for row in data:
                            numeric_field = row.get(str(field.get('id')))
                            if numeric_field.get('value') is None:
                                row.update({str(field.get('id')): int(round(numeric_field))})
                            else:
                                numeric_field = numeric_field.get('value')
                                row.update({str(field.get('id')): {'value': int(round(numeric_field))}})

        return self
