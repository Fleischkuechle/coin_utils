from cryptos import coins
from typing import Any, Union

from cryptos.types import Tx
from Create_Raw_Transaction_And_Sign_Helper import (
    Create_Raw_Transaction_And_Sign_Helper,
)


class Create_Raw_Transaction_And_Sign_doge:
    def __init__(
        self,
        # coin_symbol: str,
        testnet: bool = False,
    ):
        self.coin_symbol: str = "doge"
        self.testnet: bool = testnet
        self.some_validate_link: str = (
            r"https://live.blockcypher.com/btc/address/1EfayE6j4nv6L13Q2BdDtys7Gs2b791ev4/"
        )
        self.some_validate_link_2: str = (
            r"https://blockexplorer.one/dogecoin/testnet/address/ns3c8yGKiTL1TGgQru9CFbSwGxgLt3EHph"
        )
        self.tutorial_link: str = (
            r"https://learnmeabitcoin.com/technical/transaction/input/sequence/"
        )
        self.good_fee_info: str = (
            r"https://learnmeabitcoin.com/technical/transaction/fee/#sats-per-vbyte"
        )

        self.margin1: int = 20
        self.margin2: int = 30
        self.line_length: int = 60
        self.line_symbol: str = "-"
        self.atomic_value_divider: int = (
            100000000  # 1 btc =100,000,000 Satoshis (atomic units)
        )
        self.create_raw_transaction_and_sign_helper: (
            Create_Raw_Transaction_And_Sign_Helper
        ) = Create_Raw_Transaction_And_Sign_Helper(
            coin_symbol=self.coin_symbol,
            testnet=testnet,
        )

        self.transaction_type: str = "signed Transaction"

    def create_raw_transaction_and_sign(
        self,
        frm_pub_address: str = "",
        frm_pub_address_priv_key: str = "",
        to_pub_address: str = "",
        print_result: bool = True,
        atomic_value_to_spent: float = 0,
        # fee: float = 0,
    ) -> tuple[
        Tx,
        Union[
            coins.bitcoin.Bitcoin,
            coins.litecoin.Litecoin,
            coins.bitcoin_cash.BitcoinCash,
            coins.dash.Dash,
            coins.dogecoin.Doge,
            None,
        ],
    ]:
        signed_tx: Tx
        coin: Union[
            coins.bitcoin.Bitcoin,
            coins.litecoin.Litecoin,
            coins.bitcoin_cash.BitcoinCash,
            coins.dash.Dash,
            coins.dogecoin.Doge,
            None,
        ]
        signed_tx, coin = (
            self.create_raw_transaction_and_sign_helper.create_raw_transaction_and_sign(
                frm_pub_address=frm_pub_address,
                frm_pub_address_priv_key=frm_pub_address_priv_key,
                to_pub_address=to_pub_address,
                print_result=print_result,
                atomic_value_to_spent=atomic_value_to_spent,
            )
        )

        return signed_tx, coin


if __name__ == "__main__":
    create_raw_transaction_and_sign_doge: Create_Raw_Transaction_And_Sign_doge = (
        Create_Raw_Transaction_And_Sign_doge()
    )

    frm_pub_address: str = "DHnBSmiXjLzw9xT6gZ6o5ycMTnGPi2yNXX "  # test address doge 1
    # frm_pub_address: str = "DEi98svyRa5HrgVRXqi3irmTi5VVmAbJus"
    frm_pub_address_priv_key: str = (
        "0abc485676fcb706a469bae8835f4cf4f94d8bc76c47d19fad3e1d84716f8c02"
    )
    to_pub_address: str = "DHnBSmiXjLzw9xT6gZ6o5ycMTnGPi2yNXX"  # test address doge 2
    # to_pub_address: str = "DSXMsnjXYw3eQbz3VVg2QxFowir3H1yaYK"
    print_result: bool = True

    atomic_value_to_spent: float = (
        5000000000  # atomic value (satoshis for doge i beleve koioni)
    )
    print(" ")
    print(f"you about to spent: {atomic_value_to_spent/100000000} coins.")
    print_result: bool = True

    signed_tx: Tx
    coin: Union[
        coins.bitcoin.Bitcoin,
        coins.litecoin.Litecoin,
        coins.bitcoin_cash.BitcoinCash,
        coins.dash.Dash,
        coins.dogecoin.Doge,
        None,
    ]
    signed_tx, coin = (
        create_raw_transaction_and_sign_doge.create_raw_transaction_and_sign(
            frm_pub_address=frm_pub_address,
            frm_pub_address_priv_key=frm_pub_address_priv_key,
            to_pub_address=to_pub_address,
            print_result=print_result,
            atomic_value_to_spent=atomic_value_to_spent,
        )
    )
