import datetime
import urllib.parse
from xml.etree import ElementTree

import requests


class AuthResponse:
    def __init__(self, error_code, error=None):
        if error_code == 0:
            self.ok = True
        else:
            self.ok = False
        self.error_code = error_code
        self.error = error

    def __str__(self):
        return f'{self.error_code}: {self.error}'


class UserToken:
    def __init__(self, string, hours):
        self.string = string
        self.expiration = datetime.datetime.now() + datetime.timedelta(hours=hours)


class User:
    def __init__(self, realm, username):
        self.realm = realm
        self.username = username
        self.authenticated = False
        self.token = None

    def is_authenticated(self):
        """
        Method to check if the user is authenticated.
        :return:
        """
        return self.authenticated

    def authenticate(self, password, hours):
        pw = urllib.parse.quote(password)
        url = f'https://{self.realm}.quickbase.com/db/main?a=API_Authenticate&username={self.username}&password={pw}&hours={hours}'
        r = requests.post(url=url)

        tree = ElementTree.fromstring(r.content)

        xml_dict = {}
        for child in tree:
            xml_dict.update({child.tag: child.text})

        error_code = int(xml_dict.get('errcode'))

        if error_code == 0:
            token = xml_dict.get('ticket')
            self.token = token
            self.authenticated = True
            return AuthResponse(error_code=error_code)
        else:
            return AuthResponse(error_code=int(xml_dict.get("errcode")), error=xml_dict.get("errtext"))


class QBUser(User):
    """
    Same as "User" class, just offers backwards compatibility.
    Recommended to use QBUser, NOT User for better typing.
    """
    def __init__(self, realm, username):
        super().__init__(realm, username)