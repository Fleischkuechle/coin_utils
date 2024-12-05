class TransactionOutput:
    def __init__(
        self,
        value: int,
        pubkey_script_length: int,
        pubkey_script_data: bytes,
    ):
        self.value: int = value
        self.pubkey_script_length: int = pubkey_script_length
        self.pubkey_script_data: bytes = pubkey_script_data

    def to_hex(self) -> str:
        return (
            self.value.to_bytes(8, byteorder="little").hex()
            + bytes([self.pubkey_script_length]).hex()
            + self.pubkey_script_data.hex()
        )
