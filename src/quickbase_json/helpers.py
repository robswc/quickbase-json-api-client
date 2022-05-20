import base64
import io
import re
from typing import BinaryIO
from xml.dom import minidom
import xml.etree.ElementTree as ET

import requests

from quickbase_json import wiki
from quickbase_json.qb_response import QBResponse

VALID_OPERATORS = [
    'CT',
    'XCT',
    'HAS',
    'XHAS',
    'EX',
    'TV',
    'XTV',
    'XEX',
    'SW',
    'XSW',
    'BF',
    'OBF',
    'AF',
    'OAF',
    'IR',
    'XIR',
    'LT',
    'LTE',
    'GT',
    'GTE'
]


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

    def to_json(self):
        return self.build()

    def __str__(self):
        return self.build()

    def __repr__(self):
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
        self.operator = operator.upper()
        self.value = value

        if self.operator.upper() not in VALID_OPERATORS:
            raise ValueError(f'"{self.operator}" is not a valid operator for QuickBase query!')

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
    Rather: {'16': FileUpload(...)}.
    """

    def __init__(self, path: str):
        """
        Initialize file upload helper
        :param path: path to file
        """
        super().__init__()
        self.path = path

        with open(path, 'rb') as f:
            # get file as a b64 string for upload to quickbase
            file = base64.b64encode(f.read()).decode()
            self.update({'value': {'fileName': f'{f.name.split("/")[-1]}', 'data': file}})


class QBFile(dict):
    """
    Represents a file, preparing to upload to QB
    """

    def __init__(self):
        """
        Initialize file upload helper
        """
        super().__init__()
        self.name = None
        self.content = None
        self.path = None
        self.qb_data = {}

    def __str__(self):
        if self.content is None:
            return f'QBFile: File content is empty! (populate content from local file or quickbase)'
        if self.path:
            return f'QBFile: "{self.name}"\tlocal path -> "{self.path}"'
        if self.path:
            return f'QBFile: "{self.name}" -> "{self.qb_data.get("url", None)}"'
        return f'QBFile'

    def from_local(self, path: str):
        with open(path, 'rb') as f:
            # get file as a b64 string for upload to quickbase
            file = base64.b64encode(f.read()).decode()
            self.name = path.split('/')[-1]
            self.content = file
            self.path = path
            self.update({'value': {'fileName': f'{f.name.split("/")[-1]}', 'data': file}})

        return self

    def from_quickbase(self, client: any, table: str, rid: int, fid: int, version: int):
        """
        Builds QBFile from quickbase
        :param client: QBClient object
        :param table: table of file
        :param rid: record id
        :param fid: field id
        :param version: file version
        :return: QBFile()
        """
        url = f'https://api.quickbase.com/v1/files/{table}/{rid}/{fid}/{version}'
        r = requests.get(url=url, headers=client.headers)
        file_name = r.headers.get('content-disposition').split("''")[1]
        cleaned_file_name = re.sub('[^a-zA-Z0-9 \n]', '_', file_name)

        if r.ok and r.status_code == 200:
            self.name = cleaned_file_name
            self.content = r.text
            self.qb_data = locals()

        else:
            raise ConnectionError(f'{r.status_code}: {r.text}')

        return self

    def upload(self, client: any, table: str, rid: int, fid: int, version: int):
        pass

    def save(self, path: str):
        """
        Saves file content to file on disk
        :param path: save path
        """
        if self.content is None:
            raise ValueError('QB File has no content to save.')

        f = open(f'{path}', 'wb')
        f.write(base64.b64decode(self.content, validate=True))
        f.close()


def xml_upload(client, tbid, rid: int, fid: int, file: any, filename: str) -> QBResponse:
    """
    Fallback upload option to support uploading files that are larger than ~10 MB (the JSON API payload size limit)
    :param client: valid QBClient object
    :param tbid: table id
    :param rid: record id
    :param fid: field id
    :param file: file object, must be bytes!
    :param filename: filename to save as on quickbase
    :return: QBResponse object
    """

    # check file type
    acceptable_types = (BinaryIO, io.BytesIO, io.BufferedReader)
    if not isinstance(file, acceptable_types):
        raise TypeError(
            f'File must be of type: {", ".join([str(i) for i in acceptable_types])}{wiki.msg("xml-upload")}')

    headers = {
        'Content-Type': 'application/xml',
        'QUICKBASE-ACTION': 'API_UploadFile'
    }

    # convert file
    file = base64.b64encode(file.read()).decode()

    # begin building of XML
    root = minidom.Document()
    xml = root.createElement('qdbapi')
    root.appendChild(xml)

    # user token
    user_token = root.createElement('usertoken')
    user_token_value = root.createTextNode(client.auth)
    user_token.appendChild(user_token_value)
    xml.appendChild(user_token)

    # rid
    rid_node = root.createElement('rid')
    rid_value = root.createTextNode(str(rid))
    rid_node.appendChild(rid_value)
    xml.appendChild(rid_node)

    # field
    fid_node = root.createElement('field')
    fid_node.setAttribute('fid', str(fid))
    fid_node.setAttribute('filename', str(filename))
    fid_value = root.createTextNode(file)
    fid_node.appendChild(fid_value)
    xml.appendChild(fid_node)

    # useful for debugging
    # xml_str = root.toprettyxml(indent="\t")

    r = requests.post(url=f'https://synctivate.quickbase.com/db/{tbid}', headers=headers, data=xml.toxml())
    response_fo = io.StringIO(r.text)

    # set response info, based on response xml
    res = QBResponse()
    try:
        tree = ET.parse(response_fo)
        res.status_code = int(tree.getroot().find('./errcode').text)
        res.text = tree.getroot().find('./errtext').text
        if res.status_code == 0:
            res.ok = True
        else:
            res.ok = False

        return res
    except Exception as e:
        res.ok = False
        res.text = str(e)