import asyncio
from typing import Optional
from cryptos.types import Tx
from Create_A_Unsigned_Transaction_Helper import Create_A_Unsigned_Transaction_Helper


class Create_A_Unsigned_Transaction_Doge:
    def __init__(
        self,
    ):
        self.coin_symbol: str = "doge"
        self.testnet: bool = False
        self.create_a_unsigned_transaction_helper: (
            Create_A_Unsigned_Transaction_Helper
        ) = Create_A_Unsigned_Transaction_Helper(
            coin_symbol=self.coin_symbol,
            testnet=self.testnet,
        )

        self.line_length: int = 40
        self.line_symbol: str = "-"

    async def create_unsigned_transaction(
        self,
        addr: str,
        to: str,
        amount: int,
        fee: float = None,
        change_addr: Optional[str] = None,
        print_to_terminal: bool = True,
    ) -> Optional[tuple[Tx, bytes]]:

        unsinged_tx: Optional[Tx] = None
        unsinged_tx_serialized: bytes = None
        try:
            unsinged_tx, unsinged_tx_serialized = (
                await self.create_a_unsigned_transaction_helper.create_unsigned_transaction(
                    coin=self.coin_symbol,
                    testnet=self.testnet,
                    addr=addr,
                    to=to,
                    amount=amount,
                    fee=fee,
                    change_addr=change_addr,
                    print_to_terminal=print_to_terminal,
                )
            )

        except Exception as e:  # Catch any other exception
            print(self.line_symbol * self.line_length)
            print(f" exception occurred: {e}")
            print(f"process stopped...")
            print(self.line_symbol * self.line_length)
            return unsinged_tx, unsinged_tx_serialized

        return unsinged_tx, unsinged_tx_serialized


async def test():

    print_to_terminal: bool = True
    frm_pub_address: str = "DHnBSmiXjLzw9xT6gZ6o5ycMTnGPi2yNXX "
    to_pub_address: str = "D8ju276w3J4k5UGeV8wVfoJ9S1DijxeK6k"
    # ------------------------------------------

    atomic_value_to_spent: float = 3000000000  # in atomic value (satoshis)
    # testnet: bool = False
    # when fee is none it calculates an average fee of the last i guess 6 blocks in the
    # blockchain
    fee: float = None
    # when change_addr is none the frm_pub_address will be automaticly choosen as change
    # address (change adderss is the arddress where the remaining coins will be sent to)
    change_addr: Optional[str] = None

    # initialize the class
    create_a_unsigned_transaction_doge: Create_A_Unsigned_Transaction_Doge = (
        Create_A_Unsigned_Transaction_Doge()
    )
    unsinged_tx: Optional[Tx] = None
    unsinged_tx_serialized: Optional[bytes] = None
    try:

        unsinged_tx, unsinged_tx_serialized = (
            await create_a_unsigned_transaction_doge.create_unsigned_transaction(
                addr=frm_pub_address,
                to=to_pub_address,
                amount=atomic_value_to_spent,
                fee=fee,
                change_addr=change_addr,
                print_to_terminal=print_to_terminal,
            )
        )

    except Exception as e:
        print(f"exception happend: {e}")
        return
    if print_to_terminal:
        print("completed successfully..")


if __name__ == "__main__":
    asyncio.run(test())
