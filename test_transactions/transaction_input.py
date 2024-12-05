class TransactionInput:
    def __init__(
        self,
        outpoint_txid: bytes,
        outpoint_index: int,
        sig_script_length: int,
        sig_script_data: bytes,
        sequence_number: int,
    ):
        self.outpoint_txid: bytes = outpoint_txid
        self.outpoint_index: int = outpoint_index
        self.sig_script_length: int = sig_script_length
        self.sig_script_data: bytes = sig_script_data
        self.sequence_number: int = sequence_number

    def to_hex(self) -> str:
        return (
            self.outpoint_txid.hex()
            + bytes([self.outpoint_index]).hex()
            + bytes([self.sig_script_length]).hex()
            + self.sig_script_data.hex()
            + self.sequence_number.to_bytes(4, byteorder="little").hex()
        )
