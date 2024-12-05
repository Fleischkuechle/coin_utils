import argparse
from os import error
import aiorpcx
import asyncio
import sys
from getpass import getpass
from cryptos.main import privtopub, compress
from cryptos.transaction import serialize
from typing import Callable, Any, Optional, Union
from cryptos.script_utils import get_coin, coin_list
from cryptos.coins_async.base import BaseCoin

from cryptos import coins


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


def get_expected_address(
    addr: str,
    privkey: str,
    base_coin: BaseCoin,
):

    expected_addr: str = ""
    if base_coin.is_native_segwit(addr):
        expected_addr = base_coin.privtosegwitaddress(privkey)
    elif base_coin.is_p2sh(addr):
        expected_addr = base_coin.privtop2wpkh_p2sh(privkey)
    elif base_coin.is_p2pkh(addr):
        expected_addr = base_coin.privtoaddr(privkey)
    elif len(addr) == 66:
        expected_addr = compress(privtopub(privkey))
    else:
        expected_addr = privtopub(privkey)
    return expected_addr


async def send(
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
    base_coin: BaseCoin = get_coin(coin, testnet=testnet)
    expected_addr: str = get_expected_address(
        addr=addr,
        privkey=privkey,
        base_coin=base_coin,
    )
    print(" ")
    print(f"get_expected_address = {expected_addr}")
    print(f"addr                 = {addr}")
    if expected_addr != addr:

        print(f"Private key is for ths address: {expected_addr},")
        print(f"not for the given addr:         {addr}")
        print(f"process stopped...")
        return

    tx = await base_coin.preparetx(addr, to, amount, fee=fee, change_addr=change_addr)
    print(f"raw transaction serialized:")
    print(serialize(tx))
    print(f"raw transaction:")
    print(tx)
    tx = base_coin.signall(tx, privkey)
    print(f"signed transaction serialized:")
    print(serialize(tx))
    print(f"signed transaction:")
    print(tx)
    if broadcast:
        try:
            result = await base_coin.pushtx(tx)
            print(f"Transaction broadcasted successfully {result}")
        except (aiorpcx.jsonrpc.RPCError, aiorpcx.jsonrpc.ProtocolError) as e:
            sys.stderr.write(e.message.upper())
    else:
        print("Transaction was cancelled")


def test_wrong_priv_key_btc(broadcast: bool = False):
    coin: str = "btc"
    testnet: bool = False
    addr: str = "bc1qte0s6pz7gsdlqq2cf6hv5mxcfksykyyyjkdfd5"
    to: str = "1PuJjnF476W3zXfVYmJfGnouzFDAXakkL4"
    amount: int = 100000000
    fee: float = None
    change_addr: Optional[str] = None
    privkey: Optional[str] = (
        "0abc485676fcb706a469bae8835f4cf4f94d8bc76c47d19fad3e1d84716f8c02"  # this key does not belong to the addr
    )
    # broadcast: bool = broadcast  # if true the transaction will be sent to the blockchain

    asyncio.run(
        send(
            coin=coin,
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


def test_wrong_priv_key_doge(broadcast: bool = False):
    coin_str: str = "doge"
    frm_pub_address: str = "DEi98svyRa5HrgVRXqi3irmTi5VVmAbJus"
    to_pub_address: str = "D6Sef2FBxjgRkPMgd8xATR9vcESWsfXSdj"
    privkey: str = "5d3f9d947db958b6c857bb55e533821c8d8dcf7ec70227cd07362b47f17cbd1a"
    atomic_value_to_spent: float = 3000000000  # in atomic value (satoshis)

    coin: str = coin_str
    testnet: bool = False
    addr: str = frm_pub_address
    to: str = to_pub_address
    amount: int = atomic_value_to_spent
    fee: float = None
    change_addr: Optional[str] = None
    privkey: Optional[str] = (
        "0abc485676fcb706a469bae8835f4cf4f94d8bc76c47d19fad3e1d84716f8c02"  # this key does not belong to the addr
    )
    # broadcast: bool = broadcast  # if true the transaction will be sent to the blockchain

    asyncio.run(
        send(
            coin=coin,
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


def test_correct_priv_key_doge(broadcast: bool = False):
    coin_str: str = "doge"
    # doge:Private Key:        0f184fca0b8e38e94afb18bc6994c100b1d0d743f8a4cb5f6757489f23eaba50
    # doge:Public_address:     DLma1eYKdMoWKY2GSJ7NhAmaygpyyAsUKA
    frm_pub_address: str = "DLma1eYKdMoWKY2GSJ7NhAmaygpyyAsUKA"
    frm_pub_address_privkey: str = (
        "0f184fca0b8e38e94afb18bc6994c100b1d0d743f8a4cb5f6757489f23eaba50"
    )
    to_pub_address: str = "D6Sef2FBxjgRkPMgd8xATR9vcESWsfXSdj"

    atomic_value_to_spent: float = 3000000000  # in atomic value (satoshis)

    coin: str = coin_str
    testnet: bool = False
    addr: str = frm_pub_address
    to: str = to_pub_address
    amount: int = atomic_value_to_spent
    fee: float = None
    change_addr: Optional[str] = None
    frm_privkey: Optional[str] = frm_pub_address_privkey
    # broadcast: bool = broadcast  # if true the transaction will be sent to the blockchain

    asyncio.run(
        send(
            coin=coin,
            testnet=testnet,
            addr=addr,
            to=to,
            amount=amount,
            fee=fee,
            change_addr=change_addr,
            privkey=frm_privkey,
            broadcast=broadcast,  # if true the transaction will be sent to the blockchain
        )
    )


if __name__ == "__main__":
    broadcast: bool = False  # if true the transaction will be sent to the blockchain
    # test_wrong_priv_key_btc(broadcast=broadcast)
    # test_wrong_priv_key_doge(broadcast=broadcast)
    test_correct_priv_key_doge(broadcast=broadcast)
    # frm_pub_address: str = (
    #     "bc1qte0s6pz7gsdlqq2cf6hv5mxcfksykyyyjkdfd5"  # mainnet address
    # )
    # # this pivate key does not belong to "bc1qte0s6pz7gsdlqq2cf6hv5mxcfksykyyyjkdfd5" just for testing
    # frm_pub_address_priv_key: str = (
    #     "0abc485676fcb706a469bae8835f4cf4f94d8bc76c47d19fad3e1d84716f8c02"
    # )
    # # to_pub_address: str = "39C7fxSzEACPjM78Z7xdPxhf7mKxJwvfMJ"
    # # to_pub_address: str = "myLktRdRh3dkK3gnShNj5tZsig6J1oaaJW"  # testnet address
    # to_pub_address: str = "1PuJjnF476W3zXfVYmJfGnouzFDAXakkL4"  # mainnet address
    # print_result: bool = True

    # atomic_value_to_spent: float = 150000000  # (atomic value/100 000 000= coin value)
