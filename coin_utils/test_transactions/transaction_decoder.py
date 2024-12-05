import binascii
from typing import List
from transaction_input import TransactionInput
from transaction_output import TransactionOutput

# from transaction_main import TransactionMain

from bticoin_transaction import BitcoinTransaction


class TransactionDecoder:
    def __init__(self, transaction_hex: str):
        self.transaction_hex: str = transaction_hex
        self.transaction_bytes: bytes = binascii.unhexlify(self.transaction_hex)
        self.offset: int = 0

    def decode_version(self) -> int:
        self.offset += 1
        return int.from_bytes(self.transaction_bytes[0:1], byteorder="little")

    def decode_num_inputs(self) -> int:
        self.offset += 1
        return int.from_bytes(self.transaction_bytes[1:2], byteorder="little")

    def decode_input(self) -> TransactionInput:
        outpoint_txid: bytes = self.transaction_bytes[self.offset : self.offset + 32]
        self.offset += 32
        outpoint_index: int = int.from_bytes(
            self.transaction_bytes[self.offset : self.offset + 1], byteorder="little"
        )
        self.offset += 1
        sig_script_length: int = int.from_bytes(
            self.transaction_bytes[self.offset : self.offset + 1], byteorder="little"
        )
        self.offset += 1
        sig_script_data: bytes = self.transaction_bytes[
            self.offset : self.offset + sig_script_length
        ]
        self.offset += sig_script_length
        sequence_number: int = int.from_bytes(
            self.transaction_bytes[self.offset : self.offset + 4], byteorder="little"
        )
        self.offset += 4
        return TransactionInput(
            outpoint_txid,
            outpoint_index,
            sig_script_length,
            sig_script_data,
            sequence_number,
        )

    def decode_num_outputs(self) -> int:
        self.offset += 1
        return int.from_bytes(
            self.transaction_bytes[self.offset : self.offset + 1], byteorder="little"
        )

    def decode_output(self) -> TransactionOutput:
        value: int = int.from_bytes(
            self.transaction_bytes[self.offset : self.offset + 8], byteorder="little"
        )
        self.offset += 8
        pubkey_script_length: int = int.from_bytes(
            self.transaction_bytes[self.offset : self.offset + 1], byteorder="little"
        )
        self.offset += 1
        pubkey_script_data: bytes = self.transaction_bytes[
            self.offset : self.offset + pubkey_script_length
        ]
        self.offset += pubkey_script_length
        return TransactionOutput(value, pubkey_script_length, pubkey_script_data)

    def decode_locktime(self) -> int:
        self.offset += 1
        return int.from_bytes(
            self.transaction_bytes[self.offset : self.offset + 1], byteorder="little"
        )

    def decode_transaction(self) -> BitcoinTransaction:
        version: int = self.decode_version()
        num_inputs: int = self.decode_num_inputs()
        inputs: List[TransactionInput] = []
        for _ in range(num_inputs):
            inputs.append(self.decode_input())
        num_outputs: int = self.decode_num_outputs()
        outputs: List[TransactionOutput] = []
        for _ in range(num_outputs):
            outputs.append(self.decode_output())
        locktime: int = self.decode_locktime()
        return BitcoinTransaction(version, inputs, outputs, locktime)

    def print_decoded_transaction(self, decoded_tx):
        print("-" * 40)  # Separator line
        print()  # Empty line for spacing
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
    btc_tx.print_transaction()  # Print the base transaction

    decoder = TransactionDecoder(transaction_hex=transaction_hex)
    decoded_tx = decoder.decode_transaction()

    decoder.print_decoded_transaction(decoded_tx)  # Print the decoded transaction
    # print("-" * 40)  # Separator line
    # print()  # Empty line for spacing
    # print("Decoded Bitcoin Transaction")
    # print("-" * 40)  # Separator line

    # # Add padding to the key-value pairs
    # print(f"Version:           {decoded_tx.version}")
    # print(f"Number of Inputs:  {len(decoded_tx.inputs)}")
    # print(f"Number of Outputs: {len(decoded_tx.outputs)}")
    # print(f"Locktime:          {decoded_tx.locktime}")

    # print("\nInputs:")
    # for i, input in enumerate(decoded_tx.inputs):
    #     print(f"  Input {i + 1}:")
    #     print(f"    Outpoint TXID:           {input.outpoint_txid.hex()}")
    #     print(f"    Outpoint Index:          {input.outpoint_index}")
    #     print(f"    Signature Script Length: {input.sig_script_length}")
    #     print(f"    Signature Script Data:   {input.sig_script_data.hex()}")
    #     print(f"    Sequence Number:         {input.sequence_number}")

    # print("\nOutputs:")
    # for i, output in enumerate(decoded_tx.outputs):
    #     print(f"  Output {i + 1}:")
    #     print(
    #         f"    Value:                  {output.value / 100_000_000} BTC"
    #     )  # Display in BTC
    #     print(f"    Pubkey Script Length: {output.pubkey_script_length}")
    #     print(f"    Pubkey Script Data:   {output.pubkey_script_data.hex()}")
