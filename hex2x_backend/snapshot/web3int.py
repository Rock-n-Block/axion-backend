from web3 import Web3, WebsocketProvider, HTTPProvider
from web3.middleware import geth_poa_middleware
import requests

from hex2x_backend.settings import WEB3_INFURA_PROJECT_ID, PARITY_IP, PARITY_WS_PORT, PARITY_HTTP_PORT


class W3int:
    interface = None
    network = None
    url = None
    url_http = None
    provider = None

    def __init__(self, provider='infura', network=None):
        if provider == 'infura':
            self.init_infura(network)
            self.provider = 'infura'
        else:
            self.init_parity()
            self.provider = 'parity'

    def init_infura(self, network):
        self.network = network
        self.url = 'wss://{subdomain}.infura.io/ws/v3/{proj_id}' \
            .format(subdomain=network, proj_id=WEB3_INFURA_PROJECT_ID)
        self.interface = Web3(WebsocketProvider(self.url))
        if network == 'rinkeby':
            self.interface.middleware_onion.inject(geth_poa_middleware, layer=0)
        return

    def init_parity(self):
        self.url = 'ws://{ip}:{port}'.format(ip=PARITY_IP, port=PARITY_WS_PORT)
        self.interface = Web3(WebsocketProvider(self.url))
        self.url_http = 'http://{ip}:{port}'.format(ip=PARITY_IP, port=PARITY_HTTP_PORT)
        self.interface_http = Web3(HTTPProvider(self.url_http))
        #self.interface = Web3(WebsocketProvider(self.url))

    def get_http_rpc_response(self, method, params=[]):
        if self.provider == 'infura':
            url = 'https://{subdomain}.infura.io/v3/{proj_id}'\
                .format(subdomain=self.network, proj_id=WEB3_INFURA_PROJECT_ID)
            params = params or []
            data = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
            headers = {"Content-Type": "application/json"}
            response = requests.post(url, headers=headers, json=data)
            return response.json()
        else:
            params = params or []
            data = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
            headers = {"Content-Type": "application/json"}
            response = requests.post(self.url_http, headers=headers, json=data)
            return response.json()
