import binascii
from typing import List
from BaseTransaction import BaseTransaction
from transaction_output import TransactionOutput
from transaction_input import TransactionInput


class BitcoinTransaction(BaseTransaction):

    # def __init__(self, sender, receiver, amount):
    def __init__(
        self,
        version: int = 1,
        inputs: List[TransactionInput] = [],
        outputs: List[TransactionOutput] = [],
        locktime: int = 0,
    ):
        super().__init__(version, inputs, outputs, locktime)
        # self.transaction_fee = 0.001  # Dogecoin transaction fee, generally lower
        self.transaction_fee = 0.0001  # Bitcoin transaction fee

    def validate_transaction(self):
        # Dogecoin may have different validation rules
        return (
            self.amount > 0 and self.sender != self.receiver and self.amount <= 100000
        )  # Example limit


if __name__ == "__main__":
    # Example usage with optional inputs
    btc_tx = BitcoinTransaction(
        inputs=[
            TransactionInput(
                binascii.unhexlify(
                    "7b1eabe0209b1fe794124575ef807057c77ada2138ae4fa8d6c4de0398a14f3f"
                ),
                0,
                73,
                binascii.unhexlify(
                    "4830450221008949f0cb400094ad2b5eb399d59d01c14d73d8fe6e96df1a7150deb388ab8935022079656090d7f6bac4c9a94e0aad311a4268e082a725f8aeae0573fb12ff866a5f01"
                ),
                0xFFFFFFFF,
            )
        ]
    )
    btc_tx.add_output(
        4999990000 * 100_000_000,
        25,
        binascii.unhexlify("76a914cbc20a7664f2f69e5355aa427045bc15e7c6c77288ac"),
    )
    transaction_hex: str = btc_tx.to_hex()
    btc_tx.print_transaction()
