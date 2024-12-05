from typing import List
from transaction_input import TransactionInput
from transaction_output import TransactionOutput


class TransactionMain_old:
    def __init__(
        self,
        version: int,
        inputs: List[TransactionInput],
        outputs: List[TransactionOutput],
        locktime: int,
    ):
        self.version: int = version
        self.inputs: List[TransactionInput] = inputs
        self.outputs: List[TransactionOutput] = outputs
        self.locktime: int = locktime
