from quickbase_json.client import QuickbaseJSONClient


class LinkedRecord:
    def __init__(self, table, rid, table_name='default', fid=3, **kwargs):
        self.tables = {}
        self.attributes = {}
        self.add_link(table, rid, table_name, fid)

    def add_link(self, table_id, rid, table_name='default', fid=3):
        if table_name == 'default':
            table_name = table_id
        self.tables.update({table_id: {'rid': rid, 'fid': fid, 'alias': table_name}})

    def add_attribute(self, key, value):
        self.attributes.update({key: value})

    def build(self, use_aliases=False):
        pass


class LinkedRecordFactory:
    def __init__(self, realm, auth_token, table_id):
        self.realm = realm
        self.table_id = table_id
        self.records = {}
        self.client = QuickbaseJSONClient(realm, auth_token)

    def set_root(self, table, fid, where):
        records = self.client.query_records(table, fid, where)
        self.records = records
        return records

    def add_link(self, source_table, fid, table):
        pass

    def add_links(self, links):
        pass
