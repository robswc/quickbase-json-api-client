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


class QBInsertResponse(dict):

    def __init__(self, **kwargs):
        self.ok = False
        self.status = None
        self.processed = 0
        self.created_rids = []
        self.updated_rids = []
        super().__init__()

    def info(self):
        """
        Prints information about the response.
        :prt: Set to False to only grab the return as a string.
        """
        print(f'Response:\nOK:\t--->\t{self.ok}\nChanged:\t--->\t{len(self.updated_rids)}\nInserted:\t--->\t{len(self.created_rids)}')

    def from_response(self, response):
        self.ok = response.ok
        self.status = response.status

        if self.ok:
            self.update(response.json())
            self.created_rids = self.get('metadata').get('createdRecordIds')
            self.updated_rids = self.get('metadata').get('updatedRecordIds')
            self.processed = self.get('metadata').get('totalNumberOfRecordsProcessed')
