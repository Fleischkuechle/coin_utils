from cryptos.electrumx_client.types import (
    ElectrumXBalanceResponse,
    ElectrumXUnspentResponse,
)
from Print_CONFIRMED_Account_Balance_helper import (
    Print_CONFIRMED_Account_Balance_helper,
)


class Print_CONFIRMED_Account_Balance_doge:
    def __init__(
        self,
        testnet: bool = False,
    ):
        self.coin_symbol: str = "doge"  # coin_symbol
        self.testnet: bool = testnet
        self.print_result: str = True
        self.print_confirmed_account_balance_helper: (
            Print_CONFIRMED_Account_Balance_helper
        ) = Print_CONFIRMED_Account_Balance_helper(
            coin_symbol=self.coin_symbol,
            testnet=self.testnet,
        )

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
    print_CONFIRMED_account_balance_doge: Print_CONFIRMED_Account_Balance_doge = (
        Print_CONFIRMED_Account_Balance_doge()
    )
    # pub_address: str = "D8koxBk542fETcJUqgd48aqFbZww9Rhmbt"
    # pub_address: str = "DBgHW1Shjyk91fusm9hm3HcryNBwaFwZbQ"
    # pub_address: str = "DEi98svyRa5HrgVRXqi3irmTi5VVmAbJus"
    # pub_address: str = "DUQWE6mxqumqiMbrNfXLqFtSfNsQA1NevH" #empty test address
    # pub_address: str = "DJun5jqd9WUzXtDsHUM64Wica8omr7XXGw"
    pub_address: str = "DHnBSmiXjLzw9xT6gZ6o5ycMTnGPi2yNXX "  # test address 300 doge
    # pub_address: str = "DHnBSmiXjLzw9xT6gZ6o5ycMTnGPi2yNXX"  # test address doge 2
    electrumX_balance_response: ElectrumXBalanceResponse = (
        print_CONFIRMED_account_balance_doge.print_CONFIRMED_account_balance(
            pub_address=pub_address
        )
    )
