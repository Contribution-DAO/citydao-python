import json
import os
from enum import Enum
from typing import List, Optional

import requests
from web3 import Web3

from citydao.utils import Web3Address


class NFTAddress(Enum):
    CITIZEN = "0x7EeF591A6CC0403b9652E98E88476fe1bF31dDeb"
    PARCEL0 = ""

class CitizenId(Enum):
    CITIZEN = 42
    FOUNDING_CITIZEN = 69
    FIRST_CITIZEN = 7


class CitizenNFT(object):

    def __init__(
        self, 
        opensea_apikey: Optional[str] = None, 
        provider: Optional[Web3] = None
    ) -> None:
        self.opensea_apikey = opensea_apikey
        self.provider = Web3Address.get_default_provider() if provider is None else provider
        
        abi_path = f"{os.path.dirname(os.path.abspath(__file__))}/abi/erc1150.json"
        self.citizen_nft = Web3Address(NFTAddress.CITIZEN.value).get_contract(self.provider, abi_path)

    def set_opensea_apikey(self, apikey: str) -> None:
        self.opensea_apikey = apikey

    def get_holders(self, id: CitizenId) -> List[Web3Address]:
        request_url = f"https://api.opensea.io/api/v1/assets/{NFTAddress.CITIZEN.value}/{id.value}"
        response = requests.get(
            request_url,
            headers = {
                "X-API-KEY": self.opensea_apikey
            }
        )
        return json.loads(response.text)

    def get_balance(self, address: Web3Address, id: CitizenId) -> int:
        return self.citizen_nft.functions.balanceOf(account=address.address, id=id.value).call()

    def get_total_supply(self, id: CitizenId) -> int:
        if id == CitizenId.FIRST_CITIZEN:
            return 1
        elif id == CitizenId.CITIZEN:
            response = self.citizen_nft.functions.inquireHousingNumbers().call()
            return response
        elif id == CitizenId.FOUNDING_CITIZEN:
            response = self.citizen_nft.functions.howManyReservedCitizenships().call()
            return response