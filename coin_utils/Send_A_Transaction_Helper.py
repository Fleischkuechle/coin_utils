import sys
import aiorpcx
import asyncio
from cryptos import script_utils
from cryptos import coins_async


class Send_A_Transaction_Helper:
    def __init__(
        self,
        coin_symbol: str,
        testnet: bool,
    ):

        self.coin_symbol: str = coin_symbol
        self.testnet: bool = testnet

    async def send_transaction(
        self,
        coin: str,
        testnet: bool,
        tx_serialized: str,
        print_to_terminal: bool = True,
    ):
        base_coin: coins_async.BaseCoin = script_utils.get_coin(
            coin_symbol=coin,
            testnet=testnet,
        )
        try:
            print(" ")
            print(
                f"starting broadcasing the transaction to the internet (this my take some time)"
            )
            result = await base_coin.pushtx(tx=tx_serialized)
            if print_to_terminal:
                print(f"Transaction broadcast result:")
                print("-" * 40)
                print(f"{result}")

                print("-" * 40)
                print("https://live.blockcypher.com/doge/pushtx/")
        except (aiorpcx.jsonrpc.RPCError, aiorpcx.jsonrpc.ProtocolError) as e:
            print(f"exeption: {e}")
            sys.stderr.write(e.message.upper())


async def test_doge():

    print_to_terminal: bool = True
    coin_symbol: str = "doge"
    testnet: bool = False
    tx_serialized: str = (
        "0100000001b7dd7cf4eeb15ebe9696f7cc69c621de1b013519f17c6ee6c7ff47a422cbdd650100000000ffffffff02005ed0b2000000001976a914f6e3932f804cfac0265aef07300821543c8e398788ac6c027996050000001976a9146e13278b5a189ad09c6a6279a83986d4dfb0883188ac00000000"
    )

    # initialize the class
    send_a_transaction_helper: Send_A_Transaction_Helper = Send_A_Transaction_Helper(
        coin_symbol=coin_symbol,
        testnet=testnet,
    )
    try:
        await send_a_transaction_helper.send_transaction(
            coin=coin_symbol,
            testnet=testnet,
            tx_serialized=tx_serialized,
            print_to_terminal=print_to_terminal,
        )

        print(f"success sigining transaction")
    except Exception as e:
        print(f"exception happend: {e}")
        return


if __name__ == "__main__":
    asyncio.run(test_doge())
