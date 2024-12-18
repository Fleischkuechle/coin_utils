import asyncio
from typing import Optional, Union
from cryptos import transaction
from cryptos import script_utils
from cryptos import coins_async
from cryptos import coins
from cryptos.types import Tx
from Print_In_Terminal_Helper import Print_In_Terminal_Helper


class Sign_A_Unsigned_Transaction_Helper:
    def __init__(
        self,
        coin_symbol: str,
        testnet: bool,
    ):

        self.coin_symbol: str = coin_symbol
        self.testnet: bool = testnet
        self.print_in_terminal_helper: Print_In_Terminal_Helper = (
            Print_In_Terminal_Helper(
                coin_symbol=self.coin_symbol,
                testnet=self.testnet,
            )
        )

        self.coin: Union[
            coins.bitcoin.Bitcoin,
            coins.litecoin.Litecoin,
            coins.bitcoin_cash.BitcoinCash,
            coins.dash.Dash,
            coins.dogecoin.Doge,
            None,
        ] = None
        self.line_length: int = 40
        self.line_symbol: str = "-"

    async def sign_unsigned_transaction(
        self,
        coin: str,
        testnet: bool,
        unsigned_tx_serialized: str,
        privkey: Optional[str] = None,
        print_to_terminal: bool = True,
    ) -> Optional[tuple[Tx, bytes]]:
        singed_tx: Optional[Tx] = None
        singed_tx_serialized: bytes = None

        print(" ")
        print(self.line_symbol * self.line_length)
        print(f"starting signing this unsigned_serialized_tx ({self.coin_symbol}):")
        print("this is the unsigned_serialized_tx")
        print(" ")
        print(f"{unsigned_tx_serialized}")
        print(self.line_symbol * self.line_length)

        base_coin: coins_async.BaseCoin = script_utils.get_coin(
            coin_symbol=coin,
            testnet=testnet,
        )

        unsigned_tx_deserialized: Optional[Tx] = None
        unsigned_tx_deserialized: Tx = transaction.deserialize(
            tx=unsigned_tx_serialized
        )

        singed_tx = base_coin.signall(
            txobj=unsigned_tx_deserialized,
            priv=privkey,
        )
        singed_tx_serialized = transaction.serialize(txobj=singed_tx)
        if print_to_terminal:
            print(
                f"singed_tx = base_coin.signall(txobj=unsigned_deserialized_tx,priv=privkey,)"
            )
            print(f"signed transaction (signed tx) ({self.coin_symbol}):")
            print(self.line_symbol * self.line_length)
            self.print_in_terminal_helper.print_pretty_4(data=singed_tx)
            counter: int = 0
            for out in singed_tx["outs"]:
                script = out["script"]
                out_address: str = base_coin.output_script_to_address(script=script)
                print(f"out_address {counter}= {out_address}")
                counter = counter + 1
            # print(tx)
            print(self.line_symbol * self.line_length)
            self.print_in_terminal_helper.print_serialized_signed_tx(
                singed_tx_serialized=singed_tx_serialized
            )
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
        return singed_tx, unsigned_tx_deserialized


async def test_doge():

    print_to_terminal: bool = True
    # this is using the correct private key that corresponds with the address from
    # should throw an exception because not enough funds.
    coin_symbol: str = "doge"

    # example address (empty no funds ) created with: Create_Address_Doge.py
    # doge:Private Key:        dc857bd464cc2bd3f4c162a078a36d7f38fcf140788de853313a2e8431256c95
    # doge:Public_address:     DPpF3wypNcxBB6dpc7QFVf3W2WMw6CWY9o
    # ---------example empty address
    frm_pub_address: str = "DPpF3wypNcxBB6dpc7QFVf3W2WMw6CWY9o"  # empty address
    privkey: str = "dc857bd464cc2bd3f4c162a078a36d7f38fcf140788de853313a2e8431256c95"
    to_pub_address: str = "DHnBSmiXjLzw9xT6gZ6o5ycMTnGPi2yNXX"  # test address doge 2

    # # my test addresses with funds-------------
    # # test address doge 1 (now ca 269)
    # frm_pub_address: str = "DHnBSmiXjLzw9xT6gZ6o5ycMTnGPi2yNXX "
    # to_pub_address: str = "DHnBSmiXjLzw9xT6gZ6o5ycMTnGPi2yNXX"  # test address doge 2
    # # ------------------------------------------

    atomic_value_to_spent: float = 3000000000  # in atomic value (satoshis)
    testnet: bool = False
    # when fee is none it calculates an average fee of the last i guess 6 blocks in the
    # blockchain
    fee: float = None
    # when change_addr is none the frm_pub_address will be automaticly choosen as change
    # address (change adderss is the arddress where the remaining coins will be sent to)
    change_addr: Optional[str] = None

    # raw transaction serialized(https://live.blockcypher.com/btc/decodetx/):
    unsigned_tx_serialized: str = (
        "0100000001b7dd7cf4eeb15ebe9696f7cc69c621de1b013519f17c6ee6c7ff47a422cbdd650100000000ffffffff02005ed0b2000000001976a914f6e3932f804cfac0265aef07300821543c8e398788ac6c027996050000001976a9146e13278b5a189ad09c6a6279a83986d4dfb0883188ac00000000"
    )

    # initialize the class
    sign_a_unsigned_transaction_helper: Sign_A_Unsigned_Transaction_Helper = (
        Sign_A_Unsigned_Transaction_Helper(
            coin_symbol=coin_symbol,
            testnet=testnet,
        )
    )
    singed_tx: Optional[Tx] = None
    signed_tx_serialized: Optional[bytes] = None
    try:

        singed_tx, signed_tx_serialized = (
            await sign_a_unsigned_transaction_helper.sign_unsigned_transaction(
                coin=coin_symbol,
                testnet=testnet,
                unsigned_tx_serialized=unsigned_tx_serialized,
                privkey=privkey,
                print_to_terminal=print_to_terminal,
            )
        )

    except Exception as e:
        print(f"exception happend: {e}")
        return

    if singed_tx:
        if print_to_terminal:
            print(f"success sigining transaction")
            # print(f"{signed_serialized_tx}")


if __name__ == "__main__":
    asyncio.run(test_doge())
