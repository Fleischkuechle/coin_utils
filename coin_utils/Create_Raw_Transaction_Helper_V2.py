import aiorpcx
import asyncio
import sys
from typing import Callable, Any, Optional, Union

from cryptos import transaction
from cryptos import script_utils
from cryptos import coins_async
from cryptos import coins
from cryptos.types import Tx

from Get_Expected_Address_Helper import Get_Expected_Address_Helper


class Create_Raw_Transaction_Helper_V2:
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
        self.good_fee_info: str = (
            r"https://learnmeabitcoin.com/technical/transaction/fee/#sats-per-vbyte"
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
        # self.coin_symbol: str = ("",)  #
        self.line_length: int = 40
        self.line_symbol: str = "-"
        self.atomic_value_divider: int = (
            100000000  # 1 btc =100,000,000 Satoshis (atomic units)
        )
        self.get_expected_address_helper: Get_Expected_Address_Helper = (
            Get_Expected_Address_Helper(
                coin_symbol=self.coin_symbol,
                testnet=self.testnet,
            )
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

    def print_pretty_4(self, data):
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
                print(f"| {key:>{max_key_length}} | {str(value):<15} |")
                print("-" * (max_key_length + 15))

    async def create_unsigned_transaction_temp(
        self,
        coin: str,
        testnet: bool,
        addr: str,
        to: str,
        amount: int,
        fee: float = None,
        change_addr: Optional[str] = None,
        print_to_terminal: bool = True,
        # privkey: Optional[str] = None,
        # broadcast: bool = False,
    ) -> Optional[Tx]:
        base_coin: coins_async.BaseCoin = script_utils.get_coin(coin, testnet=testnet)
        # address_match: bool = False
        # address_match = self.get_expected_address_helper.address_check(
        #     coin=coin,
        #     testnet=testnet,
        #     addr=addr,
        #     privkey=privkey,
        # )

        # if address_match:
        unsinged_tx: Optional[Tx] = None
        single_bytes_array_serialized_transaction: bytes = None
        try:
            unsinged_tx: Tx = await base_coin.preparetx(
                frm=addr,
                to=to,
                value=amount,
                fee=fee,
                change_addr=change_addr,
            )
        except Exception as e:  # Catch any other exception
            print(self.line_symbol * self.line_length)
            print(f" exception occurred: {e}")
            print(f"process stopped...")
            print(self.line_symbol * self.line_length)
            return

        if unsinged_tx:
            single_bytes_array_serialized_transaction = transaction.serialize(
                txobj=unsinged_tx
            )
        if print_to_terminal:
            print(self.line_symbol * self.line_length)
            print(f"raw transaction (unsigned tx):")
            self.print_pretty_4(data=unsinged_tx)
            print(self.line_symbol * self.line_length)

            print(self.line_symbol * self.line_length)
            print(
                f"raw transaction serialized(https://live.blockcypher.com/btc/decodetx/):"
            )
            print(transaction.serialize(txobj=unsinged_tx))
            print(self.line_symbol * self.line_length)

        return unsinged_tx, single_bytes_array_serialized_transaction

        # this is the signing part of the transaction which should be made offline
        # # print(tx)
        # singed_tx: Tx = base_coin.signall(
        #     txobj=unsinged_tx,
        #     priv=privkey,
        # )
        # print(self.line_symbol * self.line_length)
        # print(
        #     f"signed transaction serialized:(https://live.blockcypher.com/btc/decodetx/)"
        # )
        # print(transaction.serialize(singed_tx))
        # print(self.line_symbol * self.line_length)
        # print(f"signed transaction (signed tx):")
        # print(self.line_symbol * self.line_length)
        # self.print_pretty_4(data=singed_tx)
        # counter: int = 0
        # for out in singed_tx["outs"]:
        #     script = out["script"]
        #     out_address: str = base_coin.output_script_to_address(script=script)
        #     print(f"out_address {counter}= {out_address}")
        #     counter = counter + 1
        # # print(tx)
        # print(self.line_symbol * self.line_length)
        # if broadcast:
        #     try:
        #         result = await base_coin.pushtx(singed_tx)
        #         print(f"Transaction broadcasted successfully {result}")
        #     except (aiorpcx.jsonrpc.RPCError, aiorpcx.jsonrpc.ProtocolError) as e:
        #         sys.stderr.write(e.message.upper())
        # else:
        #     print("Transaction was cancelled because broadcast=False")
        #     print(
        #         f"at the following link you can if you want broadcast your transaction."
        #     )
        #     print("https://live.blockcypher.com/doge/pushtx/")

    async def create_unsigned_transaction_original(
        self,
        coin: str,
        testnet: bool,
        addr: str,
        to: str,
        amount: int,
        fee: float = None,
        change_addr: Optional[str] = None,
        print_to_terminal: bool = True,
    ) -> Optional[Tx]:
        base_coin: coins_async.BaseCoin = script_utils.get_coin(coin, testnet=testnet)
        unsinged_tx: Optional[Tx] = None
        single_bytes_array_serialized_transaction: bytes = None
        try:
            unsinged_tx: Tx = await base_coin.preparetx(
                frm=addr,
                to=to,
                value=amount,
                fee=fee,
                change_addr=change_addr,
            )
        except Exception as e:  # Catch any other exception
            print(self.line_symbol * self.line_length)
            print(f" exception occurred: {e}")
            print(f"process stopped...")
            print(self.line_symbol * self.line_length)
            return

        if unsinged_tx:
            single_bytes_array_serialized_transaction = transaction.serialize(
                txobj=unsinged_tx
            )
            if print_to_terminal:
                print(self.line_symbol * self.line_length)
                print(f"raw transaction (unsigned tx):")
                self.print_pretty_4(data=unsinged_tx)
                print(self.line_symbol * self.line_length)

                print(self.line_symbol * self.line_length)
                print(
                    f"raw transaction serialized(https://live.blockcypher.com/btc/decodetx/):"
                )
                print(single_bytes_array_serialized_transaction)
                print(self.line_symbol * self.line_length)

        return unsinged_tx, single_bytes_array_serialized_transaction

        # this is the signing part of the transaction which should be made offline
        # # print(tx)
        # singed_tx: Tx = base_coin.signall(
        #     txobj=unsinged_tx,
        #     priv=privkey,
        # )
        # print(self.line_symbol * self.line_length)
        # print(
        #     f"signed transaction serialized:(https://live.blockcypher.com/btc/decodetx/)"
        # )
        # print(transaction.serialize(singed_tx))
        # print(self.line_symbol * self.line_length)
        # print(f"signed transaction (signed tx):")
        # print(self.line_symbol * self.line_length)
        # self.print_pretty_4(data=singed_tx)
        # counter: int = 0
        # for out in singed_tx["outs"]:
        #     script = out["script"]
        #     out_address: str = base_coin.output_script_to_address(script=script)
        #     print(f"out_address {counter}= {out_address}")
        #     counter = counter + 1
        # # print(tx)
        # print(self.line_symbol * self.line_length)
        # if broadcast:
        #     try:
        #         result = await base_coin.pushtx(singed_tx)
        #         print(f"Transaction broadcasted successfully {result}")
        #     except (aiorpcx.jsonrpc.RPCError, aiorpcx.jsonrpc.ProtocolError) as e:
        #         sys.stderr.write(e.message.upper())
        # else:
        #     print("Transaction was cancelled because broadcast=False")
        #     print(
        #         f"at the following link you can if you want broadcast your transaction."
        #     )
        #     print("https://live.blockcypher.com/doge/pushtx/")

    async def create_unsigned_transaction(
        self,
        coin: str,
        testnet: bool,
        addr: str,
        to: str,
        amount: int,
        fee: float = None,
        change_addr: Optional[str] = None,
        print_to_terminal: bool = True,
    ) -> Optional[tuple[Tx, bytes]]:
        """
        Creates an unsigned transaction for the specified coin and network.

        Args:
            self: The instance of the class calling this method.
            coin: The cryptocurrency symbol (e.g., "BTC", "ETH").
            testnet: Whether to use the testnet or mainnet.
            addr: The address of the sender.
            to: The address of the recipient.
            amount: The amount to send.
            fee: The transaction fee. If not provided, a default fee will be used.
            change_addr: The address to send any remaining funds to.
            print_to_terminal: Whether to print the raw transaction details to the terminal.

        Returns:
            A tuple containing the unsigned transaction object (`Tx`) and its serialized byte array,
            or `None` if an error occurs.

        Raises:
            None.

        Notes:
            This function uses the `get_coin` function from the `script_utils` module to obtain
            the appropriate coin object based on the provided coin and network.
            It then uses the `preparetx` method of the coin object to create the unsigned transaction.
            The function also serializes the unsigned transaction using the `serialize` function
            from the `transaction` module.
        """
        base_coin: coins_async.BaseCoin = script_utils.get_coin(coin, testnet=testnet)
        unsinged_tx: Optional[Tx] = None
        single_bytes_array_serialized_transaction: bytes = None
        try:
            unsinged_tx: Tx = await base_coin.preparetx(
                frm=addr,
                to=to,
                value=amount,
                fee=fee,
                change_addr=change_addr,
            )
        except Exception as e:  # Catch any other exception
            print(self.line_symbol * self.line_length)
            print(f" exception occurred: {e}")
            print(f"process stopped...")
            print(self.line_symbol * self.line_length)
            return

        if unsinged_tx:
            single_bytes_array_serialized_transaction = transaction.serialize(
                txobj=unsinged_tx
            )
            if print_to_terminal:
                # print(self.line_symbol * self.line_length)
                # print(f"raw transaction (unsigned tx):")
                # self.print_pretty_4(data=unsinged_tx)
                # print(self.line_symbol * self.line_length)
                # self.print_fee_info(tx=unsinged_tx)
                # print(self.line_symbol * self.line_length)
                # print(
                #     f"raw transaction serialized(https://live.blockcypher.com/btc/decodetx/):"
                # )
                # print(single_bytes_array_serialized_transaction)
                # print(self.line_symbol * self.line_length)
                self.print_only_transaction(
                    pub_address=addr,
                    tx=unsinged_tx,
                    coin_symbol=coin,
                    to_pub_address=to,
                    value_to_spent=amount,
                )

        return unsinged_tx, single_bytes_array_serialized_transaction

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
        print(self.line_symbol * self.line_length)
        print(self.line_symbol * self.line_length)
        print(
            f"{'fee:'} {fee_atomic} ({coin_value_formated} {self.coin_symbol}) (fee is what the miners get for their work (miningpool)) "
        )
        print(self.line_symbol * self.line_length)
        print(self.line_symbol * self.line_length)
        fee_warning: str = (
            "Be careful, as any amount of satoshis left over in a transaction will be taken as the fee. Some people have mistakenly set large fees on their transactions by incorrectly sizing their outputs. For example, transaction cc455ae816e6cdafdb58d54e35d4f46d860047458eacf1c7405dc634631c570d had a 291.240900 BTC fee on it."
        )
        print(f"{fee_warning}")
        print(self.line_symbol * self.line_length)
        print(self.line_symbol * self.line_length)
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


async def test_doge():

    print_to_terminal: bool = True
    # this is using the correct private key that corresponds with the address from
    # should throw an exception because not enough funds.
    coin_symbol: str = "doge"

    # # example address (empty no funds ) created with: Create_Address_Doge.py
    # # doge:Private Key:        dc857bd464cc2bd3f4c162a078a36d7f38fcf140788de853313a2e8431256c95
    # # doge:Public_address:     DPpF3wypNcxBB6dpc7QFVf3W2WMw6CWY9o
    # # ---------example empty address
    # frm_pub_address: str = "DPpF3wypNcxBB6dpc7QFVf3W2WMw6CWY9o"  # empty address
    # to_pub_address: str = "DTeXPdfh1u5ziumrmZfMmLNVpbnMnseXdK"  # test address 0 doge 2

    # my test addresses with funds-------------
    # test address 300 doge 1 (now ca 269)
    frm_pub_address: str = "DFB7pEd9Ss7bYQywkiNywtR9kRXwjDD6Hw"
    to_pub_address: str = "DTeXPdfh1u5ziumrmZfMmLNVpbnMnseXdK"  # test address 0 doge 2
    # ------------------------------------------

    atomic_value_to_spent: float = 3000000000  # in atomic value (satoshis)
    testnet: bool = False
    # when fee is none it calculates an average fee of the last i guess 6 blocks in the
    # blockchain
    fee: float = None
    # when change_addr is none the frm_pub_address will be automaticly choosen as change
    # address (change adderss is the arddress where the remaining coins will be sent to)
    change_addr: Optional[str] = None
    if print_to_terminal:
        print(" ")
        print("-" * 40)
        print(
            f"you about to spent: {atomic_value_to_spent/100000000} {coin_symbol}. (atomic_value_to_spent/100000000(one hundred million))"
        )
    # initialize the class
    create_raw_transaction_helper_v2: Create_Raw_Transaction_Helper_V2 = (
        Create_Raw_Transaction_Helper_V2(
            coin_symbol=coin_symbol,
            testnet=testnet,
        )
    )
    unsinged_tx: Optional[Tx] = None
    single_bytes_array_serialized_transaction: Optional[bytes] = None
    try:

        unsinged_tx, single_bytes_array_serialized_transaction = (
            await create_raw_transaction_helper_v2.create_unsigned_transaction(
                coin=coin_symbol,
                testnet=testnet,
                addr=frm_pub_address,
                to=to_pub_address,
                amount=atomic_value_to_spent,
                fee=fee,
                change_addr=change_addr,
                print_to_terminal=print_to_terminal,
                # privkey=frm_pub_address_privkey,
                # broadcast=broadcast,  # if true the transaction will be sent to the blockchain
            )
        )

    except Exception as e:
        print(f"exception happend: {e}")
        return

    if unsinged_tx:
        if print_to_terminal:
            print(
                f"success creating the unsigned transaction (this is the serialized transaction):"
            )
            print(f"{single_bytes_array_serialized_transaction}")


if __name__ == "__main__":
    asyncio.run(test_doge())
