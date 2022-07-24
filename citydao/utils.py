import json
from typing import Optional

from ens import ENS
from web3 import Web3


class Web3Address(object):

    def __init__(self, address: str, resolve_ens: bool = False) -> None:
        self.address = address
        self.ens = None

        if resolve_ens:
            self.resolve_ens()

    def __repr__(self) -> str:
        if self.ens is not None:
            return f"Web3Address({self.ens})"
        return f"Web3Address({self.address})"

    @staticmethod
    def get_default_provider() -> Web3:
        rpc_url = "https://rpc.ankr.com/eth"
        return Web3(Web3.HTTPProvider(rpc_url))
    
    def get_contract(self, provider: Web3, abi_path: str) -> None:
        with open(abi_path, "r") as fp:
            abi = json.load(fp)
        return provider.eth.contract(
            address=self.address,
            abi=abi
        )

    def resolve_ens(self, provider: Optional[Web3] = None) -> None:
        provider = Web3Address.get_default_provider()
        self.ens = ENS.fromWeb3(provider).name(self.address)
