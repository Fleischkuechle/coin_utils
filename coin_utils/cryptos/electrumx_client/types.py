from typing import TypedDict, Union, Callable, List, Dict, Any, Literal, Awaitable
from typing_extensions import NotRequired


class ElectrumXBlockCPResponse(TypedDict):
    branch: str
    header: str
    root: str


ElectrumXBlockResponse = Union[str, ElectrumXBlockCPResponse]


class ElectrumXBlockHeadersResponse(TypedDict):
    count: int
    hex: str
    max: int
    root: NotRequired[str]
    branch: NotRequired[str]


class ElectrumXBlockHeaderNotification(TypedDict):
    height: int
    hex: str


BlockHeaderNotificationCallback = Callable[
    [ElectrumXBlockHeaderNotification], Awaitable[None]
]


class ElectrumXBalanceResponse(TypedDict):
    confirmed: int
    unconfirmed: int


class ElectrumXMultiBalanceResponse(TypedDict):
    confirmed: int
    unconfirmed: int
    address: str


class ElectrumXTx(TypedDict):
    """
    Represents a transaction in the ElectrumX protocol for various cryptocurrencies.

    This TypedDict defines the structure of a transaction object returned by the ElectrumX server:
        It includes information about the:
            - transaction's height
            - hash
            - fee
            - position in the block
            - value
            - and associated address.

    This TypedDict is applicable to cryptocurrencies supported by ElectrumX, including but not limited to:
        - Bitcoin (BTC)
        - Litecoin (LTC)
        - Dogecoin (DOGE)
        - Dash (DASH)
        - Bitcoin Cash (BCH)

    The ElectrumX protocol is a communication protocol
    used by Electrum clients to interact
    with ElectrumX servers. It allows wallets and other
    software to communicate with nodes.
    The protocol uses JSON RPC over an unspecified
    underlying stream transport, such as TCP, SSL, WS, and WSS.
    The server uses a specific hash function
    for script hashing, which clients must use to
    hash pay-to-scripts to produce script hashes
    to send to the server. The ElectrumX server acts as a
    backbone for Electrum clients, allowing users to
    retrieve specific information about the blockchain,
    such as transaction history, block headers, and unspent outputs.

    Attributes:
        height (int): The block height at which the transaction was included.
        tx_hash (str): The hexadecimal hash of the transaction.
        fee (NotRequired[int]): The transaction fee in the cryptocurrency's smallest unit. This field is optional.
        tx_pos (NotRequired[int]): The position of the transaction within the block. This field is optional.
        value (NotRequired[int]): The value of the transaction in the cryptocurrency's smallest unit. This field is optional.
        address (NotRequired[str]): The cryptocurrency address associated with the transaction. This field is optional.
    """

    height: int
    tx_hash: str
    fee: NotRequired[int]
    tx_pos: NotRequired[int]
    value: NotRequired[int]
    address: NotRequired[str]


ElectrumXHistoryResponse = List[ElectrumXTx]


ElectrumXMempoolResponse = List[ElectrumXTx]


ElectrumXUnspentResponse = List[ElectrumXTx]


class ElectrumXTxAddress(TypedDict):
    height: int
    tx_hash: str
    fee: NotRequired[int]
    tx_pos: NotRequired[int]
    value: NotRequired[int]
    address: str


ElectrumXMultiTxResponse = List[ElectrumXTxAddress]


class ElectrumXScripthashNotification(TypedDict):
    scripthash: str
    status: str


AddressNotificationCallback = Callable[
    [ElectrumXScripthashNotification], Awaitable[None]
]


class ElectrumXVerboseTX(TypedDict):
    blockhash: str
    blocktime: int
    confirmations: int
    hash: str
    hex: str
    locktime: int
    size: int
    time: int
    txid: str
    version: int
    vin: List[Dict[str, Any]]
    vout: List[Dict[str, Any]]
    vsize: int
    weight: int


ElectrumXGetTxResponse = Union[str, ElectrumXVerboseTX]


class ElectrumXMerkleResponse(TypedDict):
    block_height: int
    merkle: List[str]
    pos: int


TxidOrTx = Literal["txid", "tx"]
TargetType = Literal["block_hash", "block_header", "merkle_root"]


class ElectrumXTSCMerkleResponse(TypedDict):
    composite: bool
    index: int
    nodes: List[str]
    proofType: Literal["branch", "tree"]
    target: str
    targetType: TargetType
    txOrId: str
