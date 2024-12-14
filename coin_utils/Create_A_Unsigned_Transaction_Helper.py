import asyncio
from typing import Optional, Union

from cryptos import transaction
from cryptos import script_utils
from cryptos import coins_async
from cryptos import coins
from cryptos.types import Tx

from Get_Expected_Address_Helper import Get_Expected_Address_Helper

from Print_In_Terminal_Helper import Print_In_Terminal_Helper


class Create_A_Unsigned_Transaction_Helper:
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

        self.get_expected_address_helper: Get_Expected_Address_Helper = (
            Get_Expected_Address_Helper(
                coin_symbol=self.coin_symbol,
                testnet=self.testnet,
            )
        )
        self.transaction_type: str = "Raw Transaction (unsigned)"

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
        unsinged_tx_serialized: bytes = None
        if print_to_terminal:
            self.print_in_terminal_helper.print_spent_coin_value(atomic_value=amount)

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
            unsinged_tx_serialized = transaction.serialize(txobj=unsinged_tx)
            if print_to_terminal:
                self.print_in_terminal_helper.print_only_transaction(
                    pub_address=addr,
                    tx=unsinged_tx,
                    coin_symbol=coin,
                    to_pub_address=to,
                    value_to_spent=amount,
                )
                self.print_in_terminal_helper.print_fee_info(tx=unsinged_tx)

                print(
                    f"raw transaction serialized(https://live.blockcypher.com/btc/decodetx/) ({self.coin_symbol}):"
                )
                print(unsinged_tx_serialized)
                print(self.line_symbol * self.line_length)
        return unsinged_tx, unsinged_tx_serialized


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
    create_a_unsigned_transaction_helper: Create_A_Unsigned_Transaction_Helper = (
        Create_A_Unsigned_Transaction_Helper(
            coin_symbol=coin_symbol,
            testnet=testnet,
        )
    )
    unsinged_tx: Optional[Tx] = None
    unsinged_tx_serialized: Optional[bytes] = None
    try:

        unsinged_tx, unsinged_tx_serialized = (
            await create_a_unsigned_transaction_helper.create_unsigned_transaction(
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
            print(f"success creating the unsigned transaction")
            # print(f"{single_bytes_array_serialized_transaction}")


if __name__ == "__main__":
    asyncio.run(test_doge())
