from typing import Any, Dict, TypedDict, Union
from cryptos import coins
from cryptos.electrumx_client.types import (
    ElectrumXBalanceResponse,
    ElectrumXUnspentResponse,
)
from cryptos import script_utils


class Print_CONFIRMED_Account_Balance_helper:
    def __init__(
        self,
        coin_symbol: str,
        testnet: bool,
    ):

        self.coin_symbol: str = coin_symbol
        self.testnet: bool = testnet
        self.some_valdiate_link: str = (
            r"https://live.blockcypher.com/btc/address/1EfayE6j4nv6L13Q2BdDtys7Gs2b791ev4/"
        )
        self.some_validate_link_2: str = (
            r"https://blockexplorer.one/dogecoin/testnet/address/ns3c8yGKiTL1TGgQru9CFbSwGxgLt3EHph"
        )
        self.coin: Union[
            coins.bitcoin.Bitcoin,
            coins.litecoin.Litecoin,
            coins.bitcoin_cash.BitcoinCash,
            coins.dash.Dash,
            coins.dogecoin.Doge,
            None,
        ] = None
        self.tx_hash_padding: int = (40,)
        self.other_padding: int = (20,)
        self.coin_symbol: str = ("",)  #
        self.line_length: int = 40
        self.line_symbol: str = "-"

    def get_coin_instance(
        self,
        coin_symbol: str = "btc",
    ) -> Union[
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
        self.coin = coin
        return coin

    def balance_online_lookup(
        self,
        print_result: bool = True,
        pub_address: str = "",
        coin_symbol: str = "btc",
    ) -> ElectrumXBalanceResponse:
        self.coin_symbol = coin_symbol
        if pub_address == "":
            print("no pub_address end process..")
            return
        coin: Union[
            coins.bitcoin.Bitcoin,
            coins.litecoin.Litecoin,
            coins.bitcoin_cash.BitcoinCash,
            coins.dash.Dash,
            coins.dogecoin.Doge,
            None,
        ] = self.get_coin_instance(coin_symbol=self.coin_symbol)

        if coin == None:
            print(f"coin {self.coin_symbol} not suported. process end..")
            return []
        if coin.is_address == False:
            print(
                f"coin.is_address=False at coin: ({self.coin_symbol})  pub_address:({pub_address}) "
            )

        # coin.confirmations
        any_data: bool = True
        try:
            electrumX_balance_response: ElectrumXBalanceResponse = coin.get_balance(
                addr=pub_address
            )
            if print_result:
                if len(electrumX_balance_response) == 0:
                    any_data == False

                    self.print_servers()
                    print("")
                    print(self.line_symbol * self.line_length)
                    print(
                        f"no balance found for: {coin_symbol} on address:{pub_address}"
                    )
                    print(self.line_symbol * self.line_length)
                    return electrumX_balance_response

        except:
            print(
                f"error balance online lookup for {coin_symbol} (maby try to set other server in  {coin_symbol}.json) https://explorer.bitcoinunlimited.info/peers"
            )
            return
        if print_result:
            if any_data:
                self.print_servers()
                self.pretty_print_balance(
                    electrumX_balance_response=electrumX_balance_response,
                    coin_symbol=coin_symbol,
                    pub_address=pub_address,
                )

        return electrumX_balance_response

    def print_servers(self):
        if self.coin is not None:
            client_kwargs: Dict[str, Any] = self.coin.coin_class.client_kwargs
            from cryptos.electrumx_client.client import read_json

            server_file_name: str = client_kwargs["server_file"]
            servers: dict = read_json(
                filename=f"servers/{server_file_name}", default={}
            )

            # Print the servers
            print()
            print(self.line_symbol * self.line_length)
            print(
                f"Available Servers: (from {server_file_name} from self.coin.coin_class.client_kwargs)"
            )
            print(self.line_symbol * self.line_length)
            print(self.line_symbol * self.line_length)
            print(
                f"This are the servers from which the electrumx_client trys to query data from"
            )
            print(self.line_symbol * self.line_length)
            for server_name, server_info in servers.items():
                print(f"  - {server_name}: {server_info}")
            print("End Servers Overview" + self.line_symbol * self.line_length)

    def format_float_with_spaces(self, value: float) -> str:
        """
        Formats a float value with spaces every three digits before the decimal point.

        Args:
            value (float): The float value to format.

        Returns:
            str: The formatted string representation of the float value with spaces.

        Example:
            >>> format_float_with_spaces(1002248222886.12345)
            '1 002 248 222 886.12'
        """
        # Format the float to a string with two decimal places
        formatted_value = f"{value:,.2f}"
        # Replace commas with spaces
        return formatted_value.replace(",", " ")

    def format_coin_value(self, coin_value: float) -> str:
        """Formats a coin value to 8 decimal places."""
        return f"{coin_value:.8f}"

    def pretty_print_balance(
        self,
        electrumX_balance_response: ElectrumXBalanceResponse,
        other_padding: int = 22,
        coin_symbol: str = "",
        pub_address: str = "",
    ):
        """Prints ElectrumXBalanceResponse formatted and visually appealing way.

        Args:
            electrumX_balance_response (electrumX_balance_response): electrumX_balance_response.
            tx_hash_padding (int, optional): Padding for the "Transaction Hash" field. Defaults to 40.
            other_padding (int, optional): Padding for all other fields. Defaults to 20.
        """
        if electrumX_balance_response == None:
            print(f"electrumX_balance_response=None")
            return
        atomic_to_coin_divider: int = (
            100000000  # 1 btc =100,000,000 Satoshis (atomic units)
        )
        print("")
        print(self.line_symbol * self.line_length)
        print(f"ElectrumXBalanceResponse for {coin_symbol}  (addr: {pub_address}):")
        confirmed_atomic_value: int = electrumX_balance_response["confirmed"]
        unconfirmed_atomic_value: int = electrumX_balance_response["unconfirmed"]
        confirmed_coin_value: int = confirmed_atomic_value / atomic_to_coin_divider
        unconfirmed_coin_value: int = unconfirmed_atomic_value / atomic_to_coin_divider
        confirmed_coin_value_formated: str = self.format_coin_value(
            coin_value=confirmed_coin_value
        )
        unconfirmed_coin_value_formated: str = self.format_coin_value(
            coin_value=unconfirmed_coin_value
        )
        atomic: str = "atomic(smallest unit)"

        print(self.line_symbol * self.line_length)

        print(
            f"{'confirmed:':<{other_padding}}{confirmed_atomic_value:<{20}}{atomic} ({coin_symbol} {confirmed_coin_value_formated})"
        )
        print(
            f"{'unconfirmed:':<{other_padding}}{unconfirmed_atomic_value:<{20}}{atomic} ({coin_symbol} {unconfirmed_coin_value_formated})"
        )
        print(f"{'calculation:':<{other_padding}}({coin_symbol}=atomic/100 000 000)")
        print(self.line_symbol * self.line_length)

        print(self.line_symbol * self.line_length)
        print(f"some link: {self.some_valdiate_link}")
        print(f"some link: {self.some_validate_link_2}")
        print(self.line_symbol * self.line_length)

    def print_available_coins(
        self,
    ):

        # print()
        print(self.line_symbol * self.line_length)
        print(f"Available Coins: {script_utils.coin_list}")
        print(self.line_symbol * self.line_length)


def test_helper(
    pub_address: str = "",
    coin_symbol: str = "",
    testnet: bool = False,
    print_result: str = True,
) -> ElectrumXUnspentResponse:
    if pub_address == "":
        print(f"pub_address is empty...")
        return
    if coin_symbol == "":
        print(f"coin_symbol is empty...")
        return
    print_confirmed_account_balance_helper: Print_CONFIRMED_Account_Balance_helper = (
        Print_CONFIRMED_Account_Balance_helper(coin_symbol=coin_symbol, testnet=testnet)
    )

    electrumX_balance_response: ElectrumXBalanceResponse = (
        print_confirmed_account_balance_helper.balance_online_lookup(
            print_result=print_result,
            pub_address=pub_address,
            coin_symbol=coin_symbol,
        )
    )
    return electrumX_balance_response


def test_btc():
    pub_address: str = "bc1pypendmmvk5mlryvcwkmmzn52cfrjrwpktlk3x9pftnnsz055asdqk93mgd"
    # pub_address: str = "1FUhaUyPaMALxLuAgh6TFbt9YxcUMtDAcj"
    coin_symbol: str = "btc"
    testnet: bool = False
    print_result: str = True
    electrumX_balance_response: ElectrumXBalanceResponse = test_helper(
        pub_address=pub_address,
        coin_symbol=coin_symbol,
        testnet=testnet,
        print_result=print_result,
    )


def test_doge():

    # pub_address: str = "D8koxBk542fETcJUqgd48aqFbZww9Rhmbt"
    # pub_address: str = "D8koxBk542fETcJUqgd48aqFbZww9Rhmbt"
    pub_address: str = "DBgHW1Shjyk91fusm9hm3HcryNBwaFwZbQ"
    coin_symbol: str = "doge"
    testnet: bool = False
    print_result: str = True
    electrumX_balance_response: ElectrumXBalanceResponse = test_helper(
        pub_address=pub_address,
        coin_symbol=coin_symbol,
        testnet=testnet,
        print_result=print_result,
    )


def test_ltc():
    pub_address: str = "LcNS6c8RddAMjewDrUAAi8BzecKoosnkN3"
    coin_symbol: str = "ltc"
    testnet: bool = False
    print_result: str = True
    electrumX_balance_response: ElectrumXBalanceResponse = test_helper(
        pub_address=pub_address,
        coin_symbol=coin_symbol,
        testnet=testnet,
        print_result=print_result,
    )


def test_dash():
    # pub_address: str = "XcBPrKVX1vbucDt6nAJEUiXqgQGtBcdV5B"
    pub_address: str = "Xp8SwwYMpoz4Pbey5r6ngZWicfEHM9126c"
    coin_symbol: str = "dash"
    testnet: bool = False
    print_result: str = True
    electrumX_balance_response: ElectrumXBalanceResponse = test_helper(
        pub_address=pub_address,
        coin_symbol=coin_symbol,
        testnet=testnet,
        print_result=print_result,
    )


def test_bitcoin_cash():
    # pub_address: str = "XcBPrKVX1vbucDt6nAJEUiXqgQGtBcdV5B"
    pub_address: str = "qrqxcp545ccywrsddeazjras8m0q965lmq6prxprtr"
    coin_symbol: str = "bch"
    testnet: bool = False
    print_result: str = True
    electrumX_balance_response: ElectrumXBalanceResponse = test_helper(
        pub_address=pub_address,
        coin_symbol=coin_symbol,
        testnet=testnet,
        print_result=print_result,
    )


def test_print_available_coins():
    coin_symbol: str = "ltc"
    testnet: bool = False
    print_confirmed_account_balance_helper: Print_CONFIRMED_Account_Balance_helper = (
        Print_CONFIRMED_Account_Balance_helper(coin_symbol=coin_symbol, testnet=testnet)
    )
    print_confirmed_account_balance_helper.print_available_coins()


if __name__ == "__main__":
    # should work
    test_btc()  # worked for me sometimes needed to restart
    # test_doge()  # worked for me sometimes needed to restart (and some D addresses wasn tworking at all)
    # test_ltc()  # worked for me sometimes needed to restart
    # test_print_available_coins()  # Available Coins: ['btc', 'ltc', 'bch', 'dash', 'doge']

    # This was not working at my tests
    # test_dash()  # was not wroking allways get [WinError 1225] Der Remotecomputer hat die Netzwerkverbindung abgelehnt
    # test_bitcoin_cash()  # was not wroking allways get [WinError 1225] Der Remotecomputer hat die Netzwerkverbindung abgelehnt
