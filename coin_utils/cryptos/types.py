from typing import TypedDict, Dict, Any, AnyStr
from typing import List, AnyStr, Union, Callable, Awaitable
from typing_extensions import NotRequired
from .electrumx_client.types import ElectrumXTx


class TxInput_original(TypedDict):
    tx_hash: NotRequired[str]
    tx_pos: NotRequired[int]
    output: NotRequired[str]
    script: NotRequired[AnyStr]
    sequence: NotRequired[int]
    value: NotRequired[int]
    address: NotRequired[str]


class TxInput(TypedDict):
    """
    Represents a single output in a cryptocurrency transaction.
    This can be used for Bitcoin, Dogecoin, Litecoin, or other cryptocurrencies.

    Attributes:
        tx_hash (str, optional): The transaction hash of the previous transaction that this input spends from.
        tx_pos (int, optional): The output position within the previous transaction that this input spends from.
        output (str, optional): The output script of the previous transaction that this input spends from.
        script (AnyStr, optional): The script used to unlock the funds in the previous transaction.
        sequence (int, optional): The sequence number of the input, which is used for transaction ordering and replacement.
        value (int, optional): The value of the output in atomic units (satoshis for Bitcoin, dogecoins for Dogecoin, litoshis for Litecoin, etc.).
        address (str, optional): The Bitcoin address associated with the input.The cryptocurrency address(can also be Dogecoin Litecoin, etc.)

    Example:
        >>> input_data = {
        ...     "tx_hash": "e8fea93b8c04d9540c00a67fb9fcbc135d170893d2d4b1691a6e98b52ab5fa1d",
        ...     "tx_pos": 0,
        ...     "value": 315837611,
        ...     "address": "bc1qte0s6pz7gsdlqq2cf6hv5mxcfksykyyyjkdfd5",
        ... }
        >>> tx_input = TxInput(**input_data)
        >>> tx_input
        {'tx_hash': 'e8fea93b8c04d9540c00a67fb9fcbc135d170893d2d4b1691a6e98b52ab5fa1d', 'tx_pos': 0, 'value': 315837611, 'address': 'bc1qte0s6pz7gsdlqq2cf6hv5mxcfksykyyyjkdfd5'}

    """

    tx_hash: NotRequired[str]
    tx_pos: NotRequired[int]
    output: NotRequired[str]
    script: NotRequired[AnyStr]
    sequence: NotRequired[int]
    value: NotRequired[int]
    address: NotRequired[str]


class TxOut_original(TypedDict):
    value: int
    address: NotRequired[str]
    script: NotRequired[str]


class TxOut(TypedDict):
    """
    Represents a single output in a cryptocurrency transaction.
    This can be used for Bitcoin, Dogecoin, Litecoin, or other cryptocurrencies.

    Attributes:
        value (int): The value of the output in atomic units (satoshis for Bitcoin, dogecoins for Dogecoin, litoshis for Litecoin, etc.).
        address (str, optional): The cryptocurrency address that will receive the funds.
        script (str, optional): The script associated with the output, which defines the conditions under which the funds can be spent.

    Example:
        >>> output_data = {
        ...     "value": 300,
        ...     "address": "1PuJjnF476W3zXfVYmJfGnouzFDAXakkL4",
        ...     "script": "76a914fb37342f6275b13936799def06f2eb4c0f20151588ac",
        ... }
        >>> tx_output = TxOut(**output_data)
        >>> tx_output
        {'value': 300, 'address': '1PuJjnF476W3zXfVYmJfGnouzFDAXakkL4', 'script': '76a914fb37342f6275b13936799def06f2eb4c0f20151588ac'}
    """

    value: int
    address: NotRequired[str]
    script: NotRequired[str]


class Witness(TypedDict):
    number: int
    scriptCode: AnyStr


class Tx_original(TypedDict):
    ins: List[TxInput]
    outs: List[TxOut]
    version: str
    marker: NotRequired[str]
    flag: NotRequired[str]
    witness: NotRequired[List[Witness]]
    tx_hash: NotRequired[str]
    locktime: int


class Tx(TypedDict):
    """
    Represents a cryptocurrency transaction. This can be used for Bitcoin, Dogecoin, Litecoin, or other cryptocurrencies.

    Attributes:
        ins (List[TxInput]): A list of inputs to the transaction. Each input represents a previous output being spent.
        outs (List[TxOut]): A list of outputs from the transaction. Each output represents a new amount of cryptocurrency being sent to an address.
        version (str): The version of the transaction. This indicates the format and capabilities of the transaction.
            - Version 1 is the most common and standard for most transactions.
            - Versions 2 and higher are used for features like Segregated Witness (SegWit).
            - Versions 3 and higher are currently considered non-standard and may not be relayed by Bitcoin Core nodes.
        marker (str, optional): A marker used for segregated witness transactions.
        flag (str, optional): A flag used for segregated witness transactions. Indicates whether the transaction includes a witness section, which is essential for SegWit transactions.
            - The presence of specific marker and flag bytes (e.g., 0x00 for the marker and 0x01 for the flag) indicates a SegWit transaction.
            - The flag is mandatory for any transaction that includes SegWit features.
            - It helps define the transaction structure, particularly how inputs and outputs are processed and validated.
        witness (List[Witness], optional): A list of witnesses for segregated witness transactions.
        tx_hash (str, optional): The hash of the transaction.
        locktime (int): The locktime of the transaction.

    Example:
        >>> tx_data = {
        ...     "ins": [
        ...         {
        ...             "tx_hash": "e8fea93b8c04d9540c00a67fb9fcbc135d170893d2d4b1691a6e98b52ab5fa1d",
        ...             "tx_pos": 0,
        ...             "height": 871984,
        ...             "value": 315837611,
        ...             "address": "bc1qte0s6pz7gsdlqq2cf6hv5mxcfksykyyyjkdfd5",
        ...             "script": "76a914fb37342f6275b13936799def06f2eb4c0f20151588ac",
        ...             "sequence": 4294967295,
        ...         },
        ...     ],
        ...     "outs": [
        ...         {
        ...             "value": 300,
        ...             "address": "1PuJjnF476W3zXfVYmJfGnouzFDAXakkL4",
        ...             "script": "76a914fb37342f6275b13936799def06f2eb4c0f20151588ac",
        ...         },
        ...         {
        ...             "value": 315836439,
        ...             "address": "bc1qte0s6pz7gsdlqq2cf6hv5mxcfksykyyyjkdfd5",
        ...             "script": "00145e5f0d045e441bf001584eaeca6cd84da04b1084",
        ...         },
        ...     ],
        ...     "version": "1",
        ...     "locktime": 0,
        ... }
        >>> tx = Tx(**tx_data)
        >>> tx
        {'ins': [{'tx_hash': 'e8fea93b8c04d9540c00a67fb9fcbc135d170893d2d4b1691a6e98b52ab5fa1d', 'tx_pos': 0, 'height': 871984, 'value': 315837611, 'address': 'bc1qte0s6pz7gsdlqq2cf6hv5mxcfksykyyyjkdfd5', 'script': '76a914fb37342f6275b13936799def06f2eb4c0f20151588ac', 'sequence': 4294967295}], 'outs': [{'value': 300, 'address': '1PuJjnF476W3zXfVYmJfGnouzFDAXakkL4', 'script': '76a914fb37342f6275b13936799def06f2eb4c0f20151588ac'}, {'value': 315836439, 'address': 'bc1qte0s6pz7gsdlqq2cf6hv5mxcfksykyyyjkdfd5', 'script': '00145e5f0d045e441bf001584eaeca6cd84da04b1084'}], 'version': '1', 'locktime': 0}
    """

    ins: List[TxInput]
    outs: List[TxOut]
    version: str
    marker: NotRequired[str]
    flag: NotRequired[str]
    witness: NotRequired[List[Witness]]
    tx_hash: NotRequired[str]
    locktime: int


class BlockHeader(TypedDict):
    version: int
    prevhash: bytes
    merkle_root: bytes
    timestamp: int
    bits: int
    nonce: int
    hash: bytes


class MerkleProof(TypedDict):
    tx_hash: str
    siblings: NotRequired[List[str]]
    proven: bool


class AddressBalance(TypedDict):
    address: str
    balance: int


class AddressStatusUpdate(TypedDict):
    address: str
    status: str


BlockHeaderCallbackSync = Callable[[int, str, BlockHeader], None]
BlockHeaderCallbackAsync = Callable[[int, str, BlockHeader], Awaitable[None]]
BlockHeaderCallback = Union[BlockHeaderCallbackSync, BlockHeaderCallbackAsync]


AddressCallbackSync = Callable[[str, str], None]
AddressCallbackAsync = Callable[[str, str], Awaitable[None]]
AddressCallback = Union[AddressCallbackSync, AddressCallbackAsync]


AddressTXCallbackSync = Callable[
    [
        str,
        List[ElectrumXTx],
        List[ElectrumXTx],
        List[ElectrumXTx],
        List[ElectrumXTx],
        int,
        int,
        int,
    ],
    None,
]
AddressTXCallbackAsync = Callable[
    [
        str,
        List[ElectrumXTx],
        List[ElectrumXTx],
        List[ElectrumXTx],
        List[ElectrumXTx],
        int,
        int,
        int,
    ],
    Awaitable[None],
]
AddressTXCallback = Union[AddressTXCallbackSync, AddressTXCallbackAsync]


# Either a single private key or a mapping of addresses to private keys
PrivkeyType = Union[int, str, bytes]
PrivateKeySignAllType = Union[Dict[str, PrivkeyType], PrivkeyType]
PubKeyType = Union[list, tuple, str, bytes]


class TXInspectType(TypedDict):
    ins: Dict[str, TxInput]
    outs: List[Dict[str, Any]]
    fee: int
