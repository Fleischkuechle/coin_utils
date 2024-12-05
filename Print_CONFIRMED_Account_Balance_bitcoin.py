from cryptos.electrumx_client.types import (
    ElectrumXBalanceResponse,
    ElectrumXUnspentResponse,
)
from Print_CONFIRMED_Account_Balance_helper import (
    Print_CONFIRMED_Account_Balance_helper,
)


class Print_CONFIRMED_Account_Balance_bitcoin:
    def __init__(
        self,
        testnet: bool = False,
    ):
        self.coin_symbol: str = "btc"  # coin_symbol
        self.testnet: bool = testnet
        self.print_result: str = True
        self.print_confirmed_account_balance_helper: (
            Print_CONFIRMED_Account_Balance_helper
        ) = Print_CONFIRMED_Account_Balance_helper(
            coin_symbol=self.coin_symbol,
            testnet=self.testnet,
        )

    # def get_coin_instance(
    #     self,
    #     coin_symbol: str = "btc",
    # ) -> Union[
    #     coins.bitcoin.Bitcoin,
    #     coins.litecoin.Litecoin,
    #     coins.bitcoin_cash.BitcoinCash,
    #     coins.dash.Dash,
    #     coins.dogecoin.Doge,
    #     None,
    # ]:
    #     """
    #     Returns an instance of the appropriate coin class based on the provided coin symbol.

    #     Args:
    #         self: The instance of the class calling this function.
    #         coin_symbol: The symbol of the coin to create an instance for.

    #     Returns:
    #         An instance of the appropriate coin class, or None if the coin is not supported.
    #     """
    #     if coin_symbol == "btc":
    #         coin = coins.bitcoin.Bitcoin(testnet=self.testnet)
    #     elif coin_symbol == "ltc":
    #         coin = coins.litecoin.Litecoin(testnet=self.testnet)
    #     elif coin_symbol == "bch":
    #         coin = coins.bitcoin_cash.BitcoinCash(testnet=self.testnet)
    #     elif coin_symbol == "dash":
    #         coin = coins.dash.Dash(testnet=self.testnet)
    #     elif coin_symbol == "doge":
    #         coin = coins.dogecoin.Doge(testnet=self.testnet)
    #     else:
    #         print(f"coin({coin_symbol}) not available. process stopped.")
    #         return None
    #     self.coin = coin
    #     return coin

    def print_CONFIRMED_account_balance(
        self,
        pub_address: str = "",
    ) -> ElectrumXBalanceResponse:

        if pub_address == "":
            print("no pub_address end process..")
            return
        electrumX_balance_response: ElectrumXBalanceResponse = (
            self.print_confirmed_account_balance_helper.balance_online_lookup(
                print_result=self.print_result,
                pub_address=pub_address,
                coin_symbol=self.coin_symbol,
            )
        )

        return electrumX_balance_response

    def format_coin_value(self, coin_value: float) -> str:
        """Formats a coin value to 8 decimal places."""
        return f"{coin_value:.8f}"


if __name__ == "__main__":
    print_CONFIRMED_account_balance_bitcoin: Print_CONFIRMED_Account_Balance_bitcoin = (
        Print_CONFIRMED_Account_Balance_bitcoin()
    )
    # pub_address: str = "bc1pypendmmvk5mlryvcwkmmzn52cfrjrwpktlk3x9pftnnsz055asdqk93mgd"
    pub_address: str = "bc1qte0s6pz7gsdlqq2cf6hv5mxcfksykyyyjkdfd5"
    # pub_address: str = "1FUhaUyPaMALxLuAgh6TFbt9YxcUMtDAcj"
    electrumX_balance_response: ElectrumXBalanceResponse = (
        print_CONFIRMED_account_balance_bitcoin.print_CONFIRMED_account_balance(
            pub_address=pub_address
        )
    )
