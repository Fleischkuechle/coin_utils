from typing import Any, Dict, Union
from cryptos import coins
from cryptos.electrumx_client.types import ElectrumXUnspentResponse
from cryptos import script_utils
from crypto_scripts.explorer import is_address


class Print_UTXOS_Account_Balance_Merkle_Proof_helper:
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
        self.merkle_proof: bool = True

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

    def balance_online_lookup_merkle_proof(
        self,
        print_result: bool = True,
        pub_address: str = "",
        coin_symbol: str = "btc",
    ) -> ElectrumXUnspentResponse:
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
        electrumXTx_list: ElectrumXUnspentResponse = []
        any_data: bool = True
        try:
            # coin.get_balance
            electrumXTx_list: ElectrumXUnspentResponse = coin.unspent(
                addr=pub_address,
                merkle_proof=self.merkle_proof,
            )
            if print_result:
                if len(electrumXTx_list) == 0:
                    any_data == False
                    print("")
                    print(self.line_symbol * self.line_length)
                    print(f"no outpus fond for: {coin_symbol} on address:{pub_address}")
                    # print(f"inputs: 0 {coin_symbol} on address:{pub_address}")
                    print(f"outputs: 0  (that means account balance = 0 {coin_symbol})")
                    print(f"In other words 0 UTXOs (Unspent Transaction Outputs)")
                    print(self.line_symbol * self.line_length)
                    self.print_servers()
                    return electrumXTx_list

        except:
            print(
                f"error balance online lookup for {coin_symbol} (maby try to set other server in  {coin_symbol}.json) https://explorer.bitcoinunlimited.info/peers"
            )
        if print_result:
            if any_data:
                self.pretty_print_tx(
                    electrumXTx_list=electrumXTx_list,
                    coin_symbol=coin_symbol,
                    line_length=self.line_length,
                    line_symbol=self.line_symbol,
                )
                self.print_servers()
        return electrumXTx_list

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

    def format_doge_value(self, value: float) -> str:
        """Formats a Dogecoin value to 8 decimal places."""
        return f"{value:.8f}"

    def pretty_print_tx(
        self,
        electrumXTx_list: ElectrumXUnspentResponse,
        tx_hash_padding: int = 40,
        other_padding: int = 22,
        coin_symbol: str = "",
        line_length: int = 40,
        line_symbol: str = "-",
    ):
        """Prints a list of ElectrumXTx objects in a formatted and visually appealing way.

        Args:
            electrumXTx_list (list): A list of ElectrumXTx objects to print.
            tx_hash_padding (int, optional): Padding for the "Transaction Hash" field. Defaults to 40.
            other_padding (int, optional): Padding for all other fields. Defaults to 20.
        """

        print(self.line_symbol * self.line_length)
        print(
            f"ElectrumXTx list. {coin_symbol} Merkle proof Unspent Transaction Outputs (UTXOs)"
        )
        print(self.line_symbol * self.line_length)
        unspent_transaction_outputs_count: int = 0
        account_ballance: int = 0
        btc_to_sat_divider: int = (
            100000000  # 1 btc =100,000,000 Satoshis (atomic units)
        )
        atomic: str = "atomic(smallest unit)"
        # Understanding Satoshis(Kuoni):
        # One Bitcoin is equal to 100,000,000 Satoshis.
        # This means that the smallest unit of Bitcoin,
        # known as a Satoshi, is 0.00000001 BTC.
        #     Correct Divider:
        # Decimal Precision:
        # Dogecoin is also divisible to 8 decimal places.
        # This allows for transactions involving very small amounts of Dogecoin.
        # Conversion:
        # Similar to Litecoin, to convert Dogecoin
        # to its smallest unit (often referred to as atomic units),
        # you would also use a conversion factor of 100,000,000
        # (since 1 DOGE = 100,000,000 atomic units).

        info_padding: int = 15
        for electrumXTx in electrumXTx_list:
            print(self.line_symbol * self.line_length)
            print(
                f"{'Transaction Hash:':<{other_padding}}{electrumXTx['tx_hash']:<{tx_hash_padding}}"
            )
            print(
                f"{'Transaction Position:':<{other_padding}}{electrumXTx['tx_pos']:<{other_padding}}"
            )
            print(
                f"{'Block Height:':<{other_padding}}{electrumXTx['height']:<{info_padding}}(block number since genesis block)"
            )
            # if coin_symbol == "btc":

            koinu_divided_hundret_million: float = (
                electrumXTx["value"] / btc_to_sat_divider
            )

            koinu_divided_hundred_million_formated: str = self.format_doge_value(
                value=koinu_divided_hundret_million
            )

            print(
                f"{'Value:':<{other_padding}}{electrumXTx['value']:<{info_padding}}{atomic} ({coin_symbol} {koinu_divided_hundred_million_formated}) ({coin_symbol}=atomic/100 000 000)"
            )

            print(f"{'Address:(from)':<{other_padding}}{electrumXTx['address']}")
            unspent_transaction_outputs_count += 1
            account_ballance = account_ballance + electrumXTx["value"]
        print(self.line_symbol * self.line_length)
        print(
            f"Unspent {coin_symbol} Transaction Outputs(UTXOs) count = {unspent_transaction_outputs_count} (on the given address.)"
        )
        print(self.line_symbol * self.line_length)
        print(self.line_symbol * self.line_length)
        account_ballance_divided_hundred_million: int = (
            account_ballance / btc_to_sat_divider
        )
        account_ballance_divided_hundred_million_formated: str = self.format_doge_value(
            value=account_ballance_divided_hundred_million
        )

        print(
            f"{'account balance:':<{other_padding}}{account_ballance:<{20}}{atomic} ({coin_symbol} {account_ballance_divided_hundred_million_formated}) ({coin_symbol}=atomic/100 000 000)"
        )
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
    print_account_balance_helper: Print_UTXOS_Account_Balance_Merkle_Proof_helper = (
        Print_UTXOS_Account_Balance_Merkle_Proof_helper(
            coin_symbol=coin_symbol, testnet=testnet
        )
    )

    electrumXTx_list: ElectrumXUnspentResponse = (
        print_account_balance_helper.balance_online_lookup_merkle_proof(
            print_result=print_result,
            pub_address=pub_address,
            coin_symbol=coin_symbol,
        )
    )
    return electrumXTx_list


def test_btc():
    pub_address: str = "bc1pypendmmvk5mlryvcwkmmzn52cfrjrwpktlk3x9pftnnsz055asdqk93mgd"
    coin_symbol: str = "btc"
    testnet: bool = False
    print_result: str = True
    electrumXTx_list: ElectrumXUnspentResponse = test_helper(
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
    electrumXTx_list: ElectrumXUnspentResponse = test_helper(
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
    electrumXTx_list: ElectrumXUnspentResponse = test_helper(
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
    electrumXTx_list: ElectrumXUnspentResponse = test_helper(
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
    electrumXTx_list: ElectrumXUnspentResponse = test_helper(
        pub_address=pub_address,
        coin_symbol=coin_symbol,
        testnet=testnet,
        print_result=print_result,
    )


def test_print_available_coins():
    coin_symbol: str = "ltc"
    testnet: bool = False
    print_account_balance_helper: Print_UTXOS_Account_Balance_Merkle_Proof_helper = (
        Print_UTXOS_Account_Balance_Merkle_Proof_helper(
            coin_symbol=coin_symbol, testnet=testnet
        )
    )
    print_account_balance_helper.print_available_coins()


if __name__ == "__main__":
    # test_btc() #worked for me sometimes needed to restart
    test_doge()  # worked for me sometimes needed to restart (and some D addresses wastn working at all)
    # test_ltc() #worked for me sometimes needed to restart
    # test_print_available_coins()  # Available Coins: ['btc', 'ltc', 'bch', 'dash', 'doge']

    # This was not working at my tests
    # test_dash()  # was not wroking allways get [WinError 1225] Der Remotecomputer hat die Netzwerkverbindung abgelehnt
    # test_bitcoin_cash()  # was not wroking allways get [WinError 1225] Der Remotecomputer hat die Netzwerkverbindung abgelehnt
