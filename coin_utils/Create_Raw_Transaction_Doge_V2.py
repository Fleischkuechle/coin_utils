import asyncio
from typing import Optional
from cryptos.types import Tx
from Create_Raw_Transaction_Helper_V2 import Create_Raw_Transaction_Helper_V2


class Create_Raw_Transaction_Doge_V2:
    def __init__(
        self,
    ):
        self.coin_symbol: str = "doge"
        self.testnet: bool = False
        self.create_raw_transaction_helper_v2: Create_Raw_Transaction_Helper_V2 = (
            Create_Raw_Transaction_Helper_V2(
                coin_symbol=self.coin_symbol,
                testnet=self.testnet,
            )
        )

        self.line_length: int = 40
        self.line_symbol: str = "-"

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

        unsinged_tx: Optional[Tx] = None
        single_bytes_array_serialized_transaction: bytes = None
        try:
            unsinged_tx, single_bytes_array_serialized_transaction = (
                await self.create_raw_transaction_helper_v2.create_unsigned_transaction(
                    coin=coin,
                    testnet=testnet,
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
            return unsinged_tx, single_bytes_array_serialized_transaction

        return unsinged_tx, single_bytes_array_serialized_transaction


async def test():

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
    create_raw_transaction_doge_v2: Create_Raw_Transaction_Doge_V2 = (
        Create_Raw_Transaction_Doge_V2()
    )
    unsinged_tx: Optional[Tx] = None
    single_bytes_array_serialized_transaction: Optional[bytes] = None
    try:

        unsinged_tx, single_bytes_array_serialized_transaction = (
            await create_raw_transaction_doge_v2.create_unsigned_transaction(
                coin=coin_symbol,
                testnet=testnet,
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


if __name__ == "__main__":
    asyncio.run(test())
