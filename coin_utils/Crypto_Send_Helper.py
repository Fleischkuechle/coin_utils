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


async def run_in_executor(func: Callable, *args) -> Any:
    return await asyncio.get_running_loop().run_in_executor(None, func, *args)


class Crypto_Send_Helper:
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
        self.some_broadcast_link: str = "https://live.blockcypher.com/doge/pushtx/"
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

    async def send(
        self,
        coin: str,
        testnet: bool,
        addr: str,
        to: str,
        amount: int,
        fee: float = None,
        change_addr: Optional[str] = None,
        privkey: Optional[str] = None,
        broadcast: bool = False,
    ):
        base_coin: coins_async.BaseCoin = script_utils.get_coin(coin, testnet=testnet)
        address_match: bool = False
        address_match = self.get_expected_address_helper.address_check(
            coin=coin,
            testnet=testnet,
            addr=addr,
            privkey=privkey,
        )

        if address_match:
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
            print(self.line_symbol * self.line_length)
            print(
                f"raw transaction serialized:(https://live.blockcypher.com/btc/decodetx/)"
            )
            print(transaction.serialize(txobj=unsinged_tx))
            print(self.line_symbol * self.line_length)
            print(self.line_symbol * self.line_length)
            print(f"raw transaction (unsigned tx):")
            self.print_pretty_4(data=unsinged_tx)
            print(self.line_symbol * self.line_length)
            # print(tx)
            singed_tx: Tx = base_coin.signall(
                txobj=unsinged_tx,
                priv=privkey,
            )
            print(self.line_symbol * self.line_length)
            print(
                f"signed transaction serialized:(https://live.blockcypher.com/btc/decodetx/)"
            )
            print(transaction.serialize(singed_tx))
            print(self.line_symbol * self.line_length)
            print(f"signed transaction (signed tx):")
            print(self.line_symbol * self.line_length)
            self.print_pretty_4(data=singed_tx)
            counter: int = 0
            for out in singed_tx["outs"]:
                script = out["script"]
                out_address: str = base_coin.output_script_to_address(script=script)
                print(f"out_address {counter}= {out_address}")
                counter = counter + 1
            # print(tx)
            print(self.line_symbol * self.line_length)
            if broadcast:
                try:
                    result = await base_coin.pushtx(singed_tx)
                    print(f"Transaction broadcasted successfully {result}")
                except (aiorpcx.jsonrpc.RPCError, aiorpcx.jsonrpc.ProtocolError) as e:
                    sys.stderr.write(e.message.upper())
            else:
                print("Transaction was cancelled because broadcast=False")
                print(
                    f"at the following link you can if you want broadcast your transaction."
                )
                self.some_broadcast_link
                print(self.some_broadcast_link)


def test_wrong_priv_key_btc(
    broadcast: bool = False,
):

    coin_symbol: str = "btc"
    testnet: bool = False
    addr: str = "bc1qte0s6pz7gsdlqq2cf6hv5mxcfksykyyyjkdfd5"
    to: str = "1PuJjnF476W3zXfVYmJfGnouzFDAXakkL4"
    amount: int = 100000000
    fee: float = None
    change_addr: Optional[str] = None
    privkey: Optional[str] = (
        "0abc485676fcb706a469bae8835f4cf4f94d8bc76c47d19fad3e1d84716f8c02"  # this key does not belong to the addr
    )
    crypto_send_helper: Crypto_Send_Helper = Crypto_Send_Helper(
        coin_symbol=coin_symbol,
        testnet=testnet,
    )
    asyncio.run(
        crypto_send_helper.send(
            coin=coin_symbol,
            testnet=testnet,
            addr=addr,
            to=to,
            amount=amount,
            fee=fee,
            change_addr=change_addr,
            privkey=privkey,
            broadcast=broadcast,  # if true the transaction will be sent to the blockchain
        )
    )


def test_wrong_priv_key_doge(
    broadcast: bool = False,
):

    coin_symbol: str = "doge"
    frm_pub_address: str = "DEi98svyRa5HrgVRXqi3irmTi5VVmAbJus"
    to_pub_address: str = "D6Sef2FBxjgRkPMgd8xATR9vcESWsfXSdj"
    privkey: str = "5d3f9d947db958b6c857bb55e533821c8d8dcf7ec70227cd07362b47f17cbd1a"
    atomic_value_to_spent: float = 3000000000  # in atomic value (satoshis)

    testnet: bool = False
    addr: str = frm_pub_address
    to: str = to_pub_address
    amount: int = atomic_value_to_spent
    fee: float = None
    change_addr: Optional[str] = None
    privkey: Optional[str] = (
        "0abc485676fcb706a469bae8835f4cf4f94d8bc76c47d19fad3e1d84716f8c02"  # this key does not belong to the addr
    )
    crypto_send_helper: Crypto_Send_Helper = Crypto_Send_Helper(
        coin_symbol=coin_symbol,
        testnet=testnet,
    )
    asyncio.run(
        crypto_send_helper.send(
            coin=coin_symbol,
            testnet=testnet,
            addr=addr,
            to=to,
            amount=amount,
            fee=fee,
            change_addr=change_addr,
            privkey=privkey,
            broadcast=broadcast,  # if true the transaction will be sent to the blockchain
        )
    )


def test_correct_priv_key_doge(
    broadcast: bool = False,
):
    # this is using the correct private key that corresponds with the address from
    # should throw an exception because not enough funds.
    coin_symbol: str = "doge"
    frm_pub_address: str = (
        "DFB7pEd9Ss7bYQywkiNywtR9kRXwjDD6Hw"  # test address 300 doge 1
    )
    frm_pub_address_privkey: str = (
        "super secret private key"  # the uncorrect private key for # test address 300 doge 1
    )
    frm_pub_address_privkey: str = (
        "e9c12fec5482c3faadc138850fc0cb4f46293493392cf43e3fff829a2855e388"  # the uncorrect private key for # test address 300 doge 1
    )

    to_pub_address: str = "DTeXPdfh1u5ziumrmZfMmLNVpbnMnseXdK"  # test address 0 doge 2
    atomic_value_to_spent: float = 3000000000  # in atomic value (satoshis)
    testnet: bool = False
    fee: float = None
    change_addr: Optional[str] = None

    print(" ")
    print(
        f"you about to spent: {atomic_value_to_spent/100000000} coins. (atomic_value_to_spent/100000000)"
    )

    crypto_send_helper: Crypto_Send_Helper = Crypto_Send_Helper(
        coin_symbol=coin_symbol,
        testnet=testnet,
    )
    try:
        asyncio.run(
            crypto_send_helper.send(
                coin=coin_symbol,
                testnet=testnet,
                addr=frm_pub_address,
                to=to_pub_address,
                amount=atomic_value_to_spent,
                fee=fee,
                change_addr=change_addr,
                privkey=frm_pub_address_privkey,
                broadcast=broadcast,  # if true the transaction will be sent to the blockchain
            )
        )
    except Exception as e:
        print(f"exception happend: {e}")


if __name__ == "__main__":
    broadcast: bool = False  # if true the transaction will be sent to the blockchain
    # test_wrong_priv_key_btc(broadcast=broadcast)
    # test_wrong_priv_key_doge(broadcast=broadcast)
    test_correct_priv_key_doge(broadcast=broadcast)
