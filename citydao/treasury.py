import os
from typing import Dict, List

from citydao.utils import Web3Address


class Token(object):

    def __init__(self, address: str):
        self.address = address

        abi_path = f"{os.path.dirname(os.path.abspath(__file__))}/abi/erc20.json"
        self.provider = Web3Address.get_default_provider()
        self.contract = Web3Address(self.address).get_contract(self.provider, abi_path)
        self.ticker = self.get_ticker()

    def __repr__(self) -> str:
        return f"ERC20Token({self.address})"

    def get_ticker(self) -> str:
        return self.contract.functions.symbol().call()

    def get_balance(self, address: Web3Address) -> float:
        decimal = self.contract.functions.decimals().call()
        balance = self.contract.functions.balanceOf(address.address).call()
        return balance / (10**(decimal))

    @classmethod
    def weth(cls):
        return cls("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")

    @classmethod
    def usdc(cls):
        return cls("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")


class CityDAOTreasury(object):

    def __init__(self) -> None:
        self.contract_address = Web3Address("0x60e7343205C9C88788a22C40030d35f9370d302D")

        abi_path = f"{os.path.dirname(os.path.abspath(__file__))}/abi/gnosis_safe.json"
        self.provider = Web3Address.get_default_provider()
        self.contract = self.contract_address.get_contract(self.provider, abi_path)


    def get_balance(self) -> List[Token]:
        tokens = [Token.weth(), Token.usdc()]
        balance = {
            token.ticker: token.get_balance(self.contract_address)
            for token in tokens
        }
        balance["ETH"] = self.provider.eth.get_balance(self.contract_address.address) / 1e18
        return balance

    def format_balance(self, balance: Dict[str, float]) -> str:
        template = f"🏦 [CityDAO Tresury](https://gnosis-safe.io/app/eth:0x60e7343205C9C88788a22C40030d35f9370d302D/balances) Balance\n\n"

        for token, token_balance in balance.items():
            template += f"   \- {token_balance:,.4f} `{token}`\n".replace(".", "\\.")

        return template[:-1]  # remove last new line token

    def get_daily_summary(self) -> str:
        balance = self.get_balance()
        return self.format_balance(balance)