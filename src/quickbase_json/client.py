import datetime
import json
import os
import hashlib

import requests

from quickbase_json.helpers import FileUpload, Where, QBFile, split_list_into_chunks
from quickbase_json.qb_insert_update_response import QBInsertResponse
from quickbase_json.qb_response import QBQueryResponse

QUERY_CACHE = 'query_cache'

try:
    import pkg_resources

    version = pkg_resources.require("quickbase-json-api-client")[0].version
except Exception as e:
    print(e)
    version = 'unknown'


class QuickbaseJSONClient:
    def __init__(self, realm, auth, agent: str = f'python-qjac/{version}', debug=False, **kwargs):
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
            'User-Agent': agent,
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
            return {
                'from': table,
                'select': select,
                'where': where}

        if table == '':
            raise ValueError('Table cannot be blank')

        if not select:
            raise ValueError('Selection must contain at least one <int>')

        # create request body
        body = {
            'from': table,
            'select': select,
            'where': where}
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

    def cache_query(self, table: str, select: list, where: any, hours: float, **kwargs):
        """
        Caches a query for a given amount of time.
        https://developer.quickbase.com/operation/runQuery
        :param table: quickbase table
        :param select: list, list of fids to query
        :param where: Quickbase query language string. i.e. {3.EX.100}
        :param hours: Number of hours to cache the query for.
        :param kwargs: optional request parameters.
        :return: json data of records {data: ..., fields: ...}
        """

        # create query_cache directory if it does not exist
        if not os.path.exists(QUERY_CACHE):
            os.makedirs(QUERY_CACHE)

        # get query hash
        h = hashlib.md5(f'{table}_{select}_{where}'.encode('utf-8')).hexdigest()

        # get last updated, hours
        query_file = f'{QUERY_CACHE}/{h}.json'
        if os.path.exists(query_file):
            query_json = json.load(open(query_file, 'r')) if os.path.exists(query_file) else {}
            last_updated = datetime.datetime.fromtimestamp(query_json.get('last_updated'))
            cache_hours = query_json.get('hours', None)
            # check if query is cached and if it is not expired
            if not datetime.datetime.now() - last_updated > datetime.timedelta(hours=cache_hours):
                res = QBQueryResponse()
                res.update({'data': query_json['response']})
                res.ok = True
                return res

        else:
            # query is not cached or expired, run query and cache it
            res = self.query_records(table, select, where, **kwargs)
            data = {
                'last_updated': datetime.datetime.now().timestamp(),
                'hours': hours,
                'response': res.data()
            }
            open(f'{QUERY_CACHE}/{h}.json', 'w').write(json.dumps(data))
            return res

    def insert_update_records(self, table: str, data: list, legacy: bool = False):
        """
        Inerts or updates records in a given table.
        https://developer.quickbase.com/operation/upsert
        :param table: table to add records to
        :param data: list of dict of data, [{"6": {"value": 'example'}}] (do not include 3, record id to insert)
        :param legacy: if true, will use legacy insert/update method
        :return: record id of created/updated records
        """

        def fix_null_values(json_data):
            """Remove any fields with a null value."""
            for record in json_data:
                for key, value in list(record.items()):
                    if value.get('value', None) is None:
                        del record[key]
            return json_data

        body = {
            'to': table,
            'data': data if legacy else fix_null_values(data)
        }

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
        :
        """

        headers = self.headers
        body = {
            'from': table,
            'where': where}

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
        params = {
            'appId': f'{app_id}'}
        body = {
            'name': name}.update(kwargs)

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
        params = {
            'appId': f'{app_id}'}
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
        params = {
            'tableId': f'{table_id}'}
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

    def get_choices(self, table: str, fid: int):
        """
        Get choices for a given multiple choice field
        https://developer.quickbase.com/operation/getField
        :param table: table id
        :param fid: fid of field to get choices from
        :return: list of choices from multiple choice field
        """

        headers = self.headers
        params = {
            'tableId': f'{table}',
            'fieldId': f'{fid}'}
        fetch_url = "https://api.quickbase.com/v1/fields/" + str(fid) + "?tableId=" + table + "&includeFieldPerms=False"
        r = requests.get(fetch_url, headers=headers).json()
        if not 'message' in r:
            return r['properties']['choices']
        else:
            raise ConnectionError(f'{r["message"]}: {r["description"]}')

    def multi_query_records(self, table: str, search_field: int, select: list, search_list: list):
        """
        Queries for record data.
        https://developer.quickbase.com/operation/runQuery
        :param table: quickbase table
        :param search_field: int, fid of field to search
        :param select: list, list of FIDs to return for found records
        :param search_list: list of values to search for
        :return: json data of records {data: ..., fields: ...}
        """
        response_for_return = {
            'data': [],
            'fields': [],
            'metadata': {
                'numFields': 0,
                'numRecords': 0,
                'skip': 0,
                'totalRecords': 0}}
        list_of_searches = split_list_into_chunks(array=search_list, chunk_size=100)
        for list_of_100 in list_of_searches:
            query = Where(fid=search_field, operator='EX', value=list_of_100).build(join='OR')
            r = self.query_records(table=table, select=select, where=query)
            if r.ok and r.status_code == 200:
                response_for_return['data'].extend(r['data'])
                response_for_return['fields'] = r['fields']
                response_for_return['metadata']['numFields'] = r['metadata']['numFields']
                response_for_return['metadata']['numRecords'] += r['metadata']['numRecords']
                response_for_return['metadata']['skip'] += r['metadata']['skip']
                response_for_return['metadata']['totalRecords'] += r['metadata']['totalRecords']
            else:
                raise ConnectionError(f'{r.status_code}: {r.text}')
        return response_for_return

    def __str__(self):
        """
        Shows a string representation of a QuickbaseJSONClient.
        :return: client's realm and last 5 of auth
        """
        auth_str = ''.join(['*' for _ in range(len(list(self.auth)))] + list(self.auth)[-5:])
        return f'Quickbase Client\t--->\t{self.realm} : {auth_str} (DEBUG: {self.debug})'
