import asyncio
from typing import Optional
from cryptos.types import Tx

from Sign_A_Unsigned_Transaction_Helper import Sign_A_Unsigned_Transaction_Helper


class Sign_A_Unsigned_Transaction_Btc:
    def __init__(
        self,
    ):

        self.coin_symbol: str = "btc"
        self.testnet: bool = False
        # initialize the helper class
        self.sign_a_unsigned_transaction_helper: Sign_A_Unsigned_Transaction_Helper = (
            Sign_A_Unsigned_Transaction_Helper(
                coin_symbol=self.coin_symbol,
                testnet=self.testnet,
            )
        )

    async def sign_unsigned_transaction(
        self,
        unsigned_tx_serialized: str,
        privkey: Optional[str] = None,
        print_to_terminal: bool = True,
    ) -> Optional[tuple[Tx, bytes]]:

        singed_tx: Optional[Tx] = None
        singed_tx_serialized: bytes = None

        singed_tx, singed_tx_serialized = (
            await self.sign_a_unsigned_transaction_helper.sign_unsigned_transaction(
                coin=self.coin_symbol,
                testnet=self.testnet,
                unsigned_tx_serialized=unsigned_tx_serialized,
                privkey=privkey,
                print_to_terminal=print_to_terminal,
            )
        )

        return singed_tx, singed_tx_serialized


async def test():
    print_to_terminal: bool = True
    privkey: str = "dc857bd464cc2bd3f4c162a078a36d7f38fcf140788de853313a2e8431256c95"
    # raw transaction serialized(https://live.blockcypher.com/btc/decodetx/):
    unsigned_tx_serialized: str = (
        "0100000001b7dd7cf4eeb15ebe9696f7cc69c621de1b013519f17c6ee6c7ff47a422cbdd650100000000ffffffff02005ed0b2000000001976a914f6e3932f804cfac0265aef07300821543c8e398788ac6c027996050000001976a9146e13278b5a189ad09c6a6279a83986d4dfb0883188ac00000000"
    )
    # initialize the class
    sign_a_unsigned_transaction_btc: Sign_A_Unsigned_Transaction_Btc = (
        Sign_A_Unsigned_Transaction_Btc()
    )
    singed_tx: Optional[Tx] = None
    signed_tx_serialized: Optional[bytes] = None
    try:

        singed_tx, signed_tx_serialized = (
            await sign_a_unsigned_transaction_btc.sign_unsigned_transaction(
                unsigned_tx_serialized=unsigned_tx_serialized,
                privkey=privkey,
                print_to_terminal=print_to_terminal,
            )
        )
    except Exception as e:
        print(f"exception happend: {e}")
        return
    # print('')


if __name__ == "__main__":
    asyncio.run(test())
