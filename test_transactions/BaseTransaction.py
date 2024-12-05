import binascii
from typing import List
from transaction_input import TransactionInput
from transaction_output import TransactionOutput


class BaseTransaction:
    def __init__(
        self,
        version: int = 1,
        inputs: List[TransactionInput] = [],
        outputs: List[TransactionOutput] = [],
        locktime: int = 0,
    ):
        self.version = version
        self.inputs = inputs
        self.outputs = outputs
        self.locktime = locktime

    def add_input(
        self,
        outpoint_txid: bytes,
        outpoint_index: int,
        sig_script_length: int,
        sig_script_data: bytes,
        sequence_number: int,
    ):
        input = TransactionInput(
            outpoint_txid,
            outpoint_index,
            sig_script_length,
            sig_script_data,
            sequence_number,
        )
        self.inputs.append(input)

    def add_output(
        self, value: int, pubkey_script_length: int, pubkey_script_data: bytes
    ):
        output = TransactionOutput(value, pubkey_script_length, pubkey_script_data)
        self.outputs.append(output)

    def to_hex(self) -> str:
        transaction: str = (
            bytes([self.version]).hex()
            + bytes([len(self.inputs)]).hex()
            + "".join([input.to_hex() for input in self.inputs])
            + bytes([len(self.outputs)]).hex()
            + "".join([output.to_hex() for output in self.outputs])
            + bytes([self.locktime]).hex()
        )
        return transaction

    def print_transaction(self):
        print()  # Empty line for spacing
        print("-" * 40)  # Separator line

        print("Base Bitcoin Transaction")
        print("-" * 40)  # Separator line
        print(f"Version:           {self.version}")
        print(f"Number of Inputs:  {len(self.inputs)}")
        print(f"Number of Outputs: {len(self.outputs)}")
        print(f"Locktime:          {self.locktime}")

        print("\nInputs:")
        for i, input in enumerate(self.inputs):
            print(f"  Input {i + 1}:")
            print(f"    Outpoint TXID:           {input.outpoint_txid.hex()}")
            print(f"    Outpoint Index:          {input.outpoint_index}")
            print(f"    Signature Script Length: {input.sig_script_length}")
            print(f"    Signature Script Data:   {input.sig_script_data.hex()}")
            print(f"    Sequence Number:         {input.sequence_number}")

        print("\nOutputs:")
        for i, output in enumerate(self.outputs):
            print(f"  Output {i + 1}:")
            print(
                f"    Value:                  {output.value / 100_000_000} BTC"
            )  # Display in BTC
            print(f"    Pubkey Script Length: {output.pubkey_script_length}")
            print(f"    Pubkey Script Data:   {output.pubkey_script_data.hex()}")

    @staticmethod
    def example_usage():
        # Example usage with optional inputs
        btc_tx = BaseTransaction(
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
        from transaction_decoder import TransactionDecoder

        decoder = TransactionDecoder(transaction_hex=transaction_hex)
        decoded_tx = decoder.decode_transaction()

        print("-" * 40)  # Separator line
        print("Decoded Bitcoin Transaction")
        print("-" * 40)  # Separator line

        # Add padding to the key-value pairs
        print(f"Version:           {decoded_tx.version}")
        print(f"Number of Inputs:  {len(decoded_tx.inputs)}")
        print(f"Number of Outputs: {len(decoded_tx.outputs)}")
        print(f"Locktime:          {decoded_tx.locktime}")

        print("\nInputs:")
        for i, input in enumerate(decoded_tx.inputs):
            print(f"  Input {i + 1}:")
            print(f"    Outpoint TXID:           {input.outpoint_txid.hex()}")
            print(f"    Outpoint Index:          {input.outpoint_index}")
            print(f"    Signature Script Length: {input.sig_script_length}")
            print(f"    Signature Script Data:   {input.sig_script_data.hex()}")
            print(f"    Sequence Number:         {input.sequence_number}")

        print("\nOutputs:")
        for i, output in enumerate(decoded_tx.outputs):
            print(f"  Output {i + 1}:")
            print(
                f"    Value:                  {output.value / 100_000_000} BTC"
            )  # Display in BTC
            print(f"    Pubkey Script Length: {output.pubkey_script_length}")
            print(f"    Pubkey Script Data:   {output.pubkey_script_data.hex()}")


if __name__ == "__main__":
    BaseTransaction.example_usage()
