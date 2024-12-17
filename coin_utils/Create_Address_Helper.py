if __name__ == "__main__":
    from cryptos import main
    from cryptos import coins
    from cryptos import script_utils

else:
    try:
        from .cryptos import main
        from .cryptos import coins
        from .cryptos import script_utils
    except:
        from cryptos import main
        from cryptos import coins
        from cryptos import script_utils
from typing import Tuple, Union


class Create_Address_Helper:
    def __init__(
        self,
        coin_symbol: str,
        testnet: bool = False,
    ):
        self.coin_symbol: str = coin_symbol
        self.testnet: bool = testnet
        self.some_validate_link: str = (
            r"https://live.blockcypher.com/btc/address/1EfayE6j4nv6L13Q2BdDtys7Gs2b791ev4/"
        )
        self.some_validate_link_2: str = (
            r"https://blockexplorer.one/dogecoin/testnet/address/ns3c8yGKiTL1TGgQru9CFbSwGxgLt3EHph"
        )
        self.margin1: int = 20
        self.margin2: int = 30
        self.line_length: int = 60
        self.line_symbol: str = "-"

    def get_coin_instance(self, coin_symbol: str = "btc") -> Union[
        coins.bitcoin.Bitcoin,
        coins.litecoin.Litecoin,
        coins.bitcoin_cash.BitcoinCash,
        coins.dash.Dash,
        coins.dogecoin.Doge,
        None,
    ]:
        """
        Returns an instance of the appropriate coin class based on the provided coin symbol.

        Args:
            self: The instance of the class calling this function.
            coin_symbol: The symbol of the coin to create an instance for.

        Returns:
            An instance of the appropriate coin class, or None if the coin is not supported.
        """
        if coin_symbol == "btc":
            coin = coins.bitcoin.Bitcoin(testnet=self.testnet)
        elif coin_symbol == "ltc":
            coin = coins.litecoin.Litecoin(testnet=self.testnet)
        elif coin_symbol == "bch":
            coin = coins.bitcoin_cash.BitcoinCash(testnet=self.testnet)
        elif coin_symbol == "dash":
            coin = coins.dash.Dash(testnet=self.testnet)
        elif coin_symbol == "doge":
            coin = coins.dogecoin.Doge(testnet=self.testnet)
        else:
            print(f"coin({coin_symbol}) not available. process stopped.")
            return None
        return coin

    def make_address(
        self,
        print_result: bool = True,
    ) -> Tuple[str, str]:
        # ['btc', 'ltc', 'bch', 'dash', 'doge']
        coin: Union[
            coins.bitcoin.Bitcoin,
            coins.litecoin.Litecoin,
            coins.bitcoin_cash.BitcoinCash,
            coins.dash.Dash,
            coins.dogecoin.Doge,
            None,
        ] = self.get_coin_instance(coin_symbol=self.coin_symbol)

        if coin == None:
            print(f"coin({self.coin_symbol}) not available. process stoped. ")
            return
        privkey: str = main.generate_private_key()

        # pub address creation (different for different coins)
        pub_address: str = coin.privtoaddr(privkey=privkey)
        pub_address_segwit: str = ""
        if self.coin_symbol == "btc":
            # pub_key: str = coin.privtop2pkh(privkey=privkey)
            # pub_address_segwit: str = coin.pubtosegwitaddress(pubkey=pub_key)
            pub_address_segwit: str = coin.privtosegwitaddress(privkey=privkey)
        #     pub_address: str = coin.privtosegwitaddress(privkey=privkey)
        #     # pub_address: str = coin.privtoaddr(privkey=privkey)
        #     # coin.privtop2pkh
        # else:
        #     pub_address: str = coin.privtoaddr(privkey=privkey)

        if print_result:
            self.print_result(
                privkey=privkey,
                pub_address=pub_address,
                pub_address_segwit=pub_address_segwit,
            )
        # if coin.is_segwit_or_p2sh(addr=pub_address) == False:
        #     print(f"{self.coin_symbol} not a address: {pub_address}")
        coin_is_address: bool = coin.is_address(addr=pub_address)
        if coin_is_address == False:
            if self.coin_symbol == "doge":
                print(f"TODO Check why it says that ->not a address: {pub_address}")

        return privkey, pub_address

    def print_result(
        self, privkey: str, pub_address: str, pub_address_segwit: str = ""
    ):
        net: str = f"Mainnet(the real {self.coin_symbol} blockchain)"
        if self.testnet == True:
            net = f"Testnet(the test net for {self.coin_symbol}.)"
        print()
        # print("\n" + self.line_symbol * self.line_length)
        print(self.line_symbol * self.line_length)
        print(f"Created {self.coin_symbol} address  Network: {net}")
        print(self.line_symbol * self.line_length)

        print(
            f"{self.coin_symbol}:{'Private Key:':<{self.margin1}}{privkey:<{self.margin2}}"
        )

        print(
            f"{self.coin_symbol}:{'Public_address:':<{self.margin1}}{pub_address:<{self.margin2}}"
        )

        if pub_address_segwit != "":
            segwit_info_short: str = "(newer btc address version)"
            print(
                f"{self.coin_symbol}:{'pub_address_segwit:':<{self.margin1}}{pub_address_segwit:<{self.margin2}} {segwit_info_short}"
            )
            segwit_info: str = (
                f"A SegWit address is a newer type of Bitcoin address that uses a different format than traditional Bitcoin addresses. SegWit stands for 'Segregated Witness,' and it's a way to improve the efficiency and security of Bitcoin transactions. (starts with(bc1))"
            )

            print(self.line_symbol * self.line_length)
            print(f"{segwit_info}")
            print(self.line_symbol * self.line_length)

        print(self.line_symbol * self.line_length)
        print(f"test it: {self.some_validate_link}")
        print(self.line_symbol * self.line_length)
        print(self.line_symbol * self.line_length)
        print(f"test it(testnet): {self.some_validate_link_2}")
        print(self.line_symbol * self.line_length)

    def print_available_coins(
        self,
    ):

        # print()
        print(self.line_symbol * self.line_length)
        print(f"Available Coins: {script_utils.coin_list}")
        print(self.line_symbol * self.line_length)


if __name__ == "__main__":
    coin_symbol: str = "btc"
    create_new_address: Create_Address_Helper = Create_Address_Helper(
        coin_symbol=coin_symbol
    )
    privkey: str = ""
    pub_address: str = ""
    privkey, pub_address = create_new_address.make_address()
    create_new_address.print_available_coins()
