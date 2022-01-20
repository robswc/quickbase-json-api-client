import base64


class IncorrectParameters(Exception):
    def __init__(self, value, expected):
        self.value = value
        self.message = f'{value} is type {type(value)}.  Expected {expected}.'
        super().__init__(self.message)


def build_query_str(fid, operator, value):
    return f'{{{fid}.{operator}.{value}}}'


class QuickbaseParameter:

    def build(self):
        return 'Default String'

    def __str__(self):
        return self.build()


class Where(QuickbaseParameter):
    def __init__(self, fid: any, operator: str, value: any, **kwargs):
        """
        Initializes the quickbase query.
        :param fid: Field Id, represents "where"
        :param operator: Quickbase Query Language operator. https://help.quickbase.com/api-guide/do_query.html#queryOperators
        :param value: Value to compare against
        :param kwargs:
        """
        self.fid = fid
        self.operator = operator
        self.value = value

        # add quotes for strings
        if isinstance(self.value, str):
            self.value = '"{}"'.format(self.value)

    def build(self, **kwargs):

        if kwargs.get('join'):
            # check that value is a list
            if isinstance(self.value, list) is False:
                raise IncorrectParameters(self.value, list)

            # build queries
            queries = []
            for v in self.value:
                queries.append(build_query_str(self.fid, self.operator, v))

            # return chain of queries
            return f"{kwargs.get('join')}".join(queries)

        return build_query_str(self.fid, self.operator, self.value)


class Sort(QuickbaseParameter):
    def __init__(self, sort_pairs: list):
        """
        Creates a sort parameter for quickbase query.
        :param sort_pairs: tuples of fid and order, i.e. (4, 'ASC')
        """
        self.sort_pairs = sort_pairs

    def build(self):

        # ensure pairs is a list
        if not isinstance(self.sort_pairs, list):
            raise IncorrectParameters(self.sort_pairs, list)

        sorters = []
        for pair in self.sort_pairs:
            sorters.append({'fieldId': pair[0], 'order': pair[1]})

        return sorters


class Group(QuickbaseParameter):
    def __init__(self, group_pairs: list):
        """
        Creates a groupBy parameter for quickbase query.
        :param group_pairs: list of tuples, i.e. (3, 'equal-value')
        """
        self.group_pairs = group_pairs

    def build(self):

        # ensure pairs is a list
        if not isinstance(self.group_pairs, list):
            raise IncorrectParameters(self.group_pairs, list)

        sorters = []
        for pair in self.group_pairs:
            sorters.append({'fieldId': pair[0], 'grouping': pair[1]})

        return sorters


class FileUpload(dict):
    """
    Represents a file object for easy upload to quickbase.
    When uploading, set FID to FileUpload directly, bypass {'value': etc}
    """

    def __init__(self, path: str):
        """
        :param path: path to file
        """
        super().__init__()
        self.path = path

        with open(path, 'rb') as f:
            # get file as a b64 string for upload to quickbase
            file = base64.b64encode(f.read()).decode()
            self.update({'value': {'fileName': f'{f.name.split("/")[-1]}', 'data': file}})


class File(dict):
    """
    Represents a file object for easy upload to quickbase.
    When uploading, set FID to FileUpload directly, bypass {'value': etc}
    """

    def __init__(self, path: str):
        """
        :param path: path to file
        """
        super().__init__()
        self.path = path

        with open(path, 'rb') as f:
            # get file as a b64 string for upload to quickbase
            file = base64.b64encode(f.read()).decode()
            self.update({'value': {'fileName': f'{f.name.split("/")[-1]}', 'data': file}})
