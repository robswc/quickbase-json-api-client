from xml.etree import ElementTree

import requests

from quickbase_json.helpers import FileUpload, Where, QBFile
from quickbase_json.qb_insert_update_response import QBInsertResponse
from quickbase_json.qb_response import QBQueryResponse


class QuickbaseJSONClient:
    def __init__(self, realm, auth, debug=False, **kwargs):
        """
        Creates a client object.
        :param realm: quickbase realm
        :param auth: quickbase user token
        :param kwargs:
        """
        self.realm = realm
        self.auth = auth
        self.headers = {
            'QB-Realm-Hostname': f'{self.realm}.quickbase.com',
            'User-Agent': '{User-Agent}',
            'Authorization': f'QB-USER-TOKEN {auth}'
        }
        self.debug = debug

    """
    Records API
    """

    def query_records(self, table: str, select: list, where: any, **kwargs):
        """
        Queries for record data.
        https://developer.quickbase.com/operation/runQuery
        :param table: quickbase table
        :param select: list, list of fids to query
        :param where: Quickbase query language string. i.e. {3.EX.100}
        :param kwargs: optional request parameters.
        :return: json data of records {data: ..., fields: ...}
        """

        # convert if using 'Where' helper.
        if isinstance(where, Where):
            where = where.build()

        if kwargs.get('_test_', None):
            return {'from': table, 'select': select, 'where': where}

        if table == '':
            raise ValueError('Table cannot be blank')

        if not select:
            raise ValueError('Selection must contain at least one <int>')

        # create request body
        body = {'from': table, 'select': select, 'where': where}
        # update with keyword args
        body.update(kwargs)

        # add optional args
        body.update(kwargs)
        r = requests.post('https://api.quickbase.com/v1/records/query', headers=self.headers, json=body)

        if self.debug:
            print(f'QJAC : query_records : response ---> {r}')
            print(f'QJAC : query_records : response.json() ---> \n{r.json()}')

        # create response object
        res = QBQueryResponse(res=r)

        # update response object with JSON data from request
        res.update(r.json())

        if self.debug:
            print(f'QJAC : query_records : QBResponse ---> \n{res}')

        return res

    def insert_update_records(self, table: str, data: list):
        """
        Inerts or updates records in a given table.
        https://developer.quickbase.com/operation/upsert
        :param table: table to add records to
        :param data: list of dict of data, [{"6": {"value": 'example'}}] (do not include 3, record id to insert)
        :return: record id of created/updated records
        """

        body = {'to': table, 'data': data}

        if self.debug:
            print(f'QJAC : insert_update : body ---> \n{body}')

        r = requests.post('https://api.quickbase.com/v1/records', headers=self.headers, json=body)

        res = QBInsertResponse().from_response(response=r)

        return res

    def delete_records(self, table: str, where: str):
        """
        Deletes records in a table based on a query.
        https://developer.quickbase.com/operation/deleteRecords
        :param table: The unique identifier of the table.
        :param where: The filter to delete records. To delete all records specify a filter that will include all records.
        :return: dict, numberDeleted is number of records deleted.
        """

        headers = self.headers
        body = {'to': table, 'where': where}

        if self.debug:
            print(f'QJAC : delete_records : body ---> \n{body}')

        return requests.delete('https://api.quickbase.com/v1/records', headers=headers, json=body).json()

    """
    Easy Upload
    """

    def easy_upload(self, table: str, rid: int, fid: str, file_path: str):
        """
        Allows for easy upload of files to quickbase
        :param table: id of table to upload to
        :param rid: record id to update
        :param fid: fid (where to put the file)
        :param file_path: path to local file to upload
        :return: request response
        """
        file = FileUpload(file_path)
        data = [
            {
                3: rid,
                fid: file
            }
        ]

        if self.debug:
            print(f'QJAC : easy_upload : file ---> \n{file}')

        return self.insert_update_records(table, data=data)

    """
    Table API
    """

    def create_table(self, app_id: str, name: str, **kwargs):
        """
        Creates a table in an application.
        https://developer.quickbase.com/operation/createTable
        :param app_id: The unique identifier of an app
        :param name: name of table
        :param kwargs: optional args
        :return:
        """

        headers = self.headers
        params = {'appId': f'{app_id}'}
        body = {'name': name}.update(kwargs)

        if self.debug:
            print(f'QJAC : create_table : body ---> \n{body}')

        return requests.post('https://api.quickbase.com/v1/tables', params=params, headers=headers, json=body).json()

    def get_tables(self, app_id: str):
        """
        Gets all tables in an application
        https://developer.quickbase.com/operation/getAppTables
        :param app_id: The unique identifier of an app.
        :return: dict of all tables in application.
        """

        headers = self.headers
        params = {'appId': f'{app_id}'}
        body = None

        if self.debug:
            print(f'QJAC : get_tables : params ---> \n{params}')

        return requests.post('https://api.quickbase.com/v1/tables', params=params, headers=headers, json=body).json()

    """
    Fields API
    """

    def get_fields(self, table_id: str, **kwargs):
        """
        Get fields for a given table.
        https://developer.quickbase.com/operation/getFields
        :param table_id: Id of quickbase table
        :param kwargs: optional args
        :return:
        """

        headers = self.headers
        params = {'tableId': f'{table_id}'}
        return requests.get('https://api.quickbase.com/v1/fields', params=params, headers=headers).json()

    """
    Operations
    """

    def download_file(self, table: str, rid: int, fid: int, version: int):
        url = f'https://api.quickbase.com/v1/files/{table}/{rid}/{fid}/{version}'
        r = requests.get(url=url, headers=self.headers)
        if r.ok and r.status_code == 200:
            return QBFile(content=r.text)
        else:
            raise ConnectionError(f'{r.status_code}: {r.text} (This can sometimes happen with a bad file version)')

    """
    Misc.
    """

    def __str__(self):
        """
        Shows a string representation of a QuickbaseJSONClient.
        :return: client's realm and last 5 of auth
        """
        auth_str = ''.join(['*' for _ in range(len(list(self.auth)))] + list(self.auth)[-5:])
        return f'Quickbase Client\t--->\t{self.realm} : {auth_str} (DEBUG: {self.debug})'
