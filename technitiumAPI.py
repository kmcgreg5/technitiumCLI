from requests import Session, Response
import ipaddress

class APIException(Exception):
    pass

class TechnitiumAPI:
    def __init__(self, host: str=None, port: int=5380, username: str=None, password: str=None):
        self._host = host
        self._port = port
        self._session = None
        self.__token = None
        self.__username = username
        self.__password = password
        

    def get_zones(self) -> list:
        endPoint = f'/api/zones/list'
        response = self._session.post(self.__get_url(endPoint))
        return self.__validate_response(response, 'response', 'zones')

    def get_records(self, zone: str):
        endPoint = f'/api/zones/records/get'
        response = self._session.post(self.__get_url(endPoint, domain=zone, listZone='true'))
        return self.__validate_response(response, 'response', 'records')

    def add_record(self, zone: str, subdomain: str, ip: str):
        ipaddress.ip_address(ip)
        endPoint = f'/api/zones/records/add'

        response = self._session.post(self.__get_url(endPoint, domain=f'{subdomain}.{zone}', zone=zone, type='A', ipAddress=ip))
        self.__validate_response(response)

    def __validate_response(self, response, *args):
        if response.status_code != 200:
            raise APIException(response.text)
        
        json = response.json()
        if json['status'] != 'ok':
            raise APIException(json)
        
        if len(args) == 0:
            return
        
        return_value = json
        for arg in args:
            return_value = return_value[arg]
        
        return return_value


    def __get_host(self):
        return f'http://{self._host}:{self._port}'

    def __get_url(self, endPoint, **arguments) -> str:
        url = f'{self.__get_host()}{endPoint}?token={self.__token}'
        for key, value in arguments.items():
            url = f'{url}&{key}={value}'
        
        return url


    def set_target_info(self, host: str, username: str, password: str):
        self._host = host
        self.__username = username
        self.__password = password

    def set_target_info(self, host: str, port: int, username: str, password: str):
        self.set_target_info(host, username, password)
        self._port = port

    def start_session(self):
        if self._session is None:
            self._session = Session()
            self.__token = self.__get_token()

    def end_session(self):
        if self._session is not None:
            self.__logout()
            self._session.close()
            self._session = None
    
    def __logout(self):
        endPoint = f'/api/user/logout'
        self._session.post(self.__get_url(endPoint))

    def __get_token(self) -> str:
        url = f'{self.__get_host()}/api/user/login?user={self.__username}&pass={self.__password}&includeInfo=false'
        self.__password = None

        response = self._session.post(url)
        return self.__validate_response(response, 'token')
    
    def __enter__(self):
        self.start_session()
        return self
    
    def __exit__(self, *args):
        self.end_session()
