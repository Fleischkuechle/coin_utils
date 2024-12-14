from cryptos.types import Tx


class Print_In_Terminal_Helper:
    def __init__(
        self,
        coin_symbol: str,
        testnet: bool,
    ):

        self.coin_symbol: str = coin_symbol
        self.testnet: bool = testnet
        self.some_valdiate_link: str = (
            "https://live.blockcypher.com/btc/address/1EfayE6j4nv6L13Q2BdDtys7Gs2b791ev4/"
        )
        self.some_validate_link_2: str = (
            "https://blockexplorer.one/dogecoin/testnet/address/ns3c8yGKiTL1TGgQru9CFbSwGxgLt3EHph"
        )
        self.good_fee_info: str = (
            "https://learnmeabitcoin.com/technical/transaction/fee/#sats-per-vbyte"
        )
        self.some_broadcast_link: str = "https://live.blockcypher.com/doge/pushtx/"
        self.some_tx_decode_link: str = "(https://live.blockcypher.com/btc/decodetx/)"
        # self.coin: Union[
        #     coins.bitcoin.Bitcoin,
        #     coins.litecoin.Litecoin,
        #     coins.bitcoin_cash.BitcoinCash,
        #     coins.dash.Dash,
        #     coins.dogecoin.Doge,
        #     None,
        # ] = None
        # self.tx_hash_padding: int = (40,)
        # self.other_padding: int = (20,)
        # # self.coin_symbol: str = ("",)  #
        self.line_length: int = 40
        self.line_symbol: str = "-"
        self.atomic_value_divider: int = (
            100000000  # 1 btc =100,000,000 Satoshis (atomic units)
        )

        self.transaction_type: str = "Raw Transaction (unsigned)"

    def format_to_8_decimals(self, value: float) -> str:
        """Formats a  value to 8 decimal places."""
        return f"{value:.8f}"

    def fromat_to_full_coin_value(self, atomic_value: float) -> str:
        coin_value: float = self.calc_atomic_to_coin_value(atomic_value=atomic_value)
        coin_value_formated: str = self.format_to_8_decimals(value=coin_value)

        return coin_value_formated

    def calc_atomic_to_coin_value(self, atomic_value: float) -> float:
        coin_value: float = atomic_value / self.atomic_value_divider
        return coin_value

    def print_pretty_4(self, data: Tx):
        """Prints the data in a formatted table-like structure."""
        # Find the maximum length of each key for padding
        max_key_length = max(len(key) for key in data)

        # Print the header row

        print("-" * (max_key_length + 15))
        print(f"| {'Key':>{max_key_length}} | {'Value':<15} |")
        print("-" * (max_key_length + 15))
        # kuoni_str:str="kuonis(satoshis)"

        atomic: str = "(atomic(smallest unit))"

        # Print the key-value pairs
        for key, value in data.items():
            if isinstance(value, list):
                # Handle lists with nested dictionaries
                for i, item in enumerate(value):

                    print(f"| {' '*4}{key}: {i} |")
                    for inner_key, inner_value in item.items():
                        if inner_key == "value":
                            coin_value_formated: str = self.fromat_to_full_coin_value(
                                atomic_value=inner_value
                            )

                            print(
                                f"| {' '*8}{inner_key:>{max_key_length}} | {inner_value:<15} | {atomic}  ({coin_value_formated} {self.coin_symbol})"
                            )
                        elif inner_key == "fee":
                            coin_value_formated: str = self.fromat_to_full_coin_value(
                                atomic_value=inner_value
                            )

                            print(
                                f"| {' '*8}{inner_key:>{max_key_length}} | {inner_value:<15} | {atomic}  ({coin_value_formated} {self.coin_symbol})"
                            )

                        else:
                            print(
                                f"| {' '*8}{inner_key:>{max_key_length}} | {inner_value:<15} |"
                            )
                    print("-" * (max_key_length + 15))
            elif isinstance(value, dict):
                # Handle nested dictionaries
                print(f"| {key:>{max_key_length}} | {'Dict':<15} |")
                print("-" * (max_key_length + 15))
                for inner_key, inner_value in value.items():
                    print(
                        f"| {' '*4}{inner_key:>{max_key_length}} | {inner_value:<15} |"
                    )
                print("-" * (max_key_length + 15))
            else:
                if key == "fee":
                    coin_value_formated: str = self.fromat_to_full_coin_value(
                        atomic_value=value
                    )

                    print(
                        f"| {key:>{max_key_length}} | {str(value):<15} | {atomic}  ({coin_value_formated} {self.coin_symbol})"
                    )
                    print("-" * (max_key_length + 15))
                else:
                    print(f"| {key:>{max_key_length}} | {str(value):<15} |")
                    print("-" * (max_key_length + 15))

    def print_serialized_signed_tx(self, singed_tx_serialized: str):
        print(
            f"signed transaction serialized{self.some_tx_decode_link} ({self.coin_symbol}):"
        )
        print(f"singed_tx_serialized = transaction.serialize(txobj=singed_tx)")
        print(" ")
        print(singed_tx_serialized)
        print(self.line_symbol * self.line_length)
        print(f"at the following link you can if you want broadcast your transaction.")
        print(self.some_broadcast_link)
        print(self.line_symbol * self.line_length)

    def calc_fee_atomic(self, tx: Tx) -> float:
        """
        Calculates the transaction fee for a given transaction.

        This function takes a transaction object (Tx) as input and calculates the fee based on the
        total input value and the total output value. The fee is calculated as the difference
        between the total input value and the total output value.

        Args:
            tx (Tx): The transaction object for which to calculate the fee.

        Returns:
            float: The calculated transaction fee in Bitcoin (BTC).

        Example:
            >>> tx = Tx(...)  # Assuming tx is a valid transaction object
            >>> fee = self.calc_fee(tx)
            >>> print(fee)
            0.00000123  # Example fee value

        Note:
            This function assumes that the transaction object (Tx) is properly formatted and contains
            all the necessary information for fee calculation.
        """
        # txInput: TxInput = None

        total_input_value = sum([txInput["value"] for txInput in tx["ins"]])
        total_output_value = sum([output["value"] for output in tx["outs"]])
        fee_atomic = (
            total_input_value - total_output_value
        )  # / 100000000  # Convert satoshis to BTC
        return fee_atomic

    def print_fee_info(
        self,
        tx: Tx,
    ):
        fee_info_txt_1: str = (
            f"If you add up all the input values and subtract all the output values,"
        )
        fee_info_txt_2: str = (
            f"the amount left over is the fee. (the fee is calculated here self.client.estimate_fee(numblocks))"
        )
        fee_atomic: float = self.calc_fee_atomic(tx=tx)
        coin_value_formated: str = self.fromat_to_full_coin_value(
            atomic_value=fee_atomic
        )

        print(self.line_symbol * self.line_length)
        print(f"{fee_info_txt_1}")
        print(f"{fee_info_txt_2}")
        # print(self.line_symbol * self.line_length)
        # print(self.line_symbol * self.line_length)
        print(
            f"{'fee:'} {fee_atomic} ({coin_value_formated} {self.coin_symbol}) (fee is what the miners get for their work (miningpool)) "
        )
        # print(self.line_symbol * self.line_length)
        # print(self.line_symbol * self.line_length)
        # fee_warning: str = (
        #     "Be careful, as any amount of satoshis left over in a transaction will be taken as the fee. Some people have mistakenly set large fees on their transactions by incorrectly sizing their outputs. For example, transaction cc455ae816e6cdafdb58d54e35d4f46d860047458eacf1c7405dc634631c570d had a 291.240900 BTC fee on it."
        # )
        # print(f"{fee_warning}")
        # print(self.line_symbol * self.line_length)
        # print(self.line_symbol * self.line_length)
        print(f"good_fee_info link: {self.good_fee_info}")
        print(self.line_symbol * self.line_length)

    def print_only_transaction(
        self,
        pub_address: str,
        tx: Tx,
        coin_symbol: str,
        to_pub_address: str = "",
        value_to_spent: float = 0,
    ):
        atomic: str = "atomic(smallest unit)"
        net: str = f"Mainnet(the real {self.coin_symbol} blockchain)"
        if self.testnet == True:
            net = f"Testnet(the test net for {self.coin_symbol}.)"

        value_to_spent_full_coin_value: str = self.fromat_to_full_coin_value(
            atomic_value=value_to_spent
        )
        print(self.line_symbol * self.line_length)
        print(f"New {self.transaction_type} Transaction:")
        left_padding: int = 15
        print(f"{'coin:':>{left_padding}} {coin_symbol}")
        print(f"{'from:':>{left_padding}} {pub_address}")
        print(f"{'to:':>{left_padding}} {to_pub_address}")
        print(
            f"{'value_to_spent:':>{left_padding}} {value_to_spent} {atomic} ({value_to_spent_full_coin_value} {coin_symbol})"
        )
        print(self.line_symbol * self.line_length)

        print(self.line_symbol * self.line_length)
        print(f"Network: {net} {self.transaction_type}")
        print(self.line_symbol * self.line_length)
        print(
            f"------{self.transaction_type}--start"
            + self.line_symbol * self.line_length
        )
        self.print_pretty_4(data=tx)
        print(
            f"------{self.transaction_type}--end" + self.line_symbol * self.line_length
        )
        # self.print_fee_info(tx=tx)
        # self.print_some_links()

    def print_spent_coin_value(self, atomic_value: float):
        print(self.line_symbol * self.line_length)
        value_to_spent_full_coin_value: str = self.fromat_to_full_coin_value(
            atomic_value=atomic_value
        )
        print(
            f"you about to spent: {value_to_spent_full_coin_value} {self.coin_symbol}. (atomic_value_to_spent/100000000(one hundred million))"
        )
        print(self.line_symbol * self.line_length)


def test():
    pass


if __name__ == "__main__":
    test()
