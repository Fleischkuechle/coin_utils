from cryptos import main
from cryptos import coins
from cryptos import script_utils

from typing import Tuple


class Create_Address_Btc:
    def __init__(self):
        self.coin_symbol: str = "btc"
        self.testnet: bool = False
        self.some_valdiate_link: str = (
            r"https://live.blockcypher.com/btc/address/1EfayE6j4nv6L13Q2BdDtys7Gs2b791ev4/"
        )
        self.margin1: int = 20
        self.margin2: int = 60
        self.line_length: int = 60
        self.line_symbol: str = "-"

    def make_address_btc(
        self,
        print_result: bool = True,
    ) -> Tuple[str, str]:

        coin: coins.bitcoin.Bitcoin = coins.bitcoin.Bitcoin(testnet=self.testnet)
        privkey: str = main.generate_private_key()
        pub_address: str = coin.privtosegwitaddress(privkey=privkey)

        if print_result:
            self.print_result(
                privkey=privkey,
                pub_address=pub_address,
            )

        if coin.is_address(addr=pub_address) == False:
            print(f"not a address: {pub_address}")

        return privkey, pub_address

    def print_result(
        self,
        privkey: str,
        pub_address: str,
    ):
        net: str = f"Mainnet(the real {self.coin_symbol} blockchain)"
        if self.testnet == True:
            net = f"Testnet(the test net for {self.coin_symbol}.)"
        print("\n" + self.line_symbol * self.line_length)
        print(f"Created {self.coin_symbol} address  Network: {net}")
        print(self.line_symbol * self.line_length)

        print(
            f"{self.coin_symbol}:{'Private Key:':<{self.margin1}}{privkey:<{self.margin2}}"
        )

        print(
            f"{self.coin_symbol}:{'Public_address:':<{self.margin1}}{pub_address:<{self.margin2}}"
        )

        print("\n" + self.line_symbol * self.line_length)
        print(f"test it:  {self.some_valdiate_link}")
        print(self.line_symbol * self.line_length)

    def print_available_coins(
        self,
    ):

        print()
        print(self.line_symbol * self.line_length)
        print(f"Available Coins: {script_utils.coin_list}")
        print(self.line_symbol * self.line_length)


if __name__ == "__main__":
    create_new_address: Create_Address_Btc = Create_Address_Btc()
    privkey: str = ""
    pub_address: str = ""
    privkey, pub_address = create_new_address.make_address_btc()
    create_new_address.print_available_coins()
