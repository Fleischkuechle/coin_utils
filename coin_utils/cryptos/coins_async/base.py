import asyncio
import aiorpcx


from ..transaction import *
from ..utils import is_hex
from binascii import unhexlify

# from ..blocks import verify_merkle_proof, deserialize_header
from .. import segwit_addr
from ..electrumx_client import ElectrumXClient
from ..keystore import *
from ..wallet import *
from ..py3specials import *
from ..constants import SATOSHI_PER_BTC
from ..opcodes import opcodes
from functools import partial
from typing import (
    Dict,
    Any,
    Tuple,
    Optional,
    TypedDict,
    Union,
    Iterable,
    Type,
    Callable,
    Generator,
    AsyncGenerator,
)

from ..types import (
    Tx,
    Witness,
    TxInput,
    TxOut,
    BlockHeader,
    MerkleProof,
    AddressBalance,
    BlockHeaderCallback,
    AddressCallback,
    AddressTXCallback,
    PrivkeyType,
    PrivateKeySignAllType,
    TXInspectType,
    PubKeyType,
)
from ..electrumx_client.types import (
    ElectrumXBlockHeaderNotification,
    ElectrumXHistoryResponse,
    ElectrumXBalanceResponse,
    ElectrumXUnspentResponse,
    ElectrumXTx,
    ElectrumXMerkleResponse,
    ElectrumXMultiBalanceResponse,
    ElectrumXMultiTxResponse,
    ElectrumXVerboseTX,
)
from cryptos.utils import alist


class TXInvalidError(BaseException):
    pass


class TXRejectedError(TXInvalidError):
    pass


class BaseCoin:
    """
    Base implementation of crypto coin class
    All child coins_async must follow same pattern.
    """

    coin_symbol: str = None
    display_name: str = None
    enabled: bool = True
    segwit_supported: bool = None
    cash_address_supported: bool = False
    magicbyte: int = None
    script_magicbyte: int = None
    segwit_hrp: str = None
    cash_hrp: str = None
    explorer: Type[ElectrumXClient] = ElectrumXClient
    client_kwargs: Dict[str, Any] = {"server_file": "bitcoin.json", "use_ssl": True}
    _client: ElectrumXClient = None
    _block: Tuple[int, str, BlockHeader] = None
    is_testnet: bool = False
    testnet_overrides: Dict[str, Any] = {}
    hashcode: int = SIGHASH_ALL
    secondary_hashcode: Optional[int] = None
    hd_path: int = 0
    block_interval: int = 10
    minimum_fee: int = 500
    txid_bytes_len = 32
    signature_sizes: Dict[str, int] = {
        "p2pkh": 213,
        "p2w_p2sh": 46 + (213 / 4),
        "p2wpkh": (214 / 4),
    }
    wif_prefix: int = 0x80
    wif_script_types: Dict[str, int] = {
        "p2pkh": 0,
        "p2wpkh": 1,
        "p2wpkh-p2sh": 2,
        "p2sh": 5,
        "p2wsh": 6,
        "p2wsh-p2sh": 7,
    }
    xprv_headers: Dict[str, int] = {
        "p2pkh": 0x0488ADE4,
        "p2wpkh-p2sh": 0x049D7878,
        "p2wsh-p2sh": 0x295B005,
        "p2wpkh": 0x4B2430C,
        "p2wsh": 0x2AA7A99,
    }
    xpub_headers: Dict[str, int] = {
        "p2pkh": 0x0488B21E,
        "p2wpkh-p2sh": 0x049D7CB2,
        "p2wsh-p2sh": 0x295B43F,
        "p2wpkh": 0x4B24746,
        "p2wsh": 0x2AA7ED3,
    }
    electrum_xprv_headers: Dict[str, int] = xprv_headers
    electrum_xpub_headers: Dict[str, int] = xpub_headers

    def __init__(self, testnet: bool = False, **kwargs):
        if testnet:
            self.is_testnet = True
            for k, v in self.testnet_overrides.items():
                setattr(self, k, v)
        # override default attributes from kwargs
        for key, value in kwargs.items():
            if isinstance(value, dict):
                getattr(self, key).update(value)
            else:
                setattr(self, key, value)
        if not self.enabled:
            if self.is_testnet:
                raise NotImplementedError(
                    f"Due to explorer limitations, testnet support for {self.display_name} has not been implemented yet!"
                )
            else:
                raise NotImplementedError(
                    f"Support for {self.display_name} has not been implemented yet!"
                )
        from ..main import magicbyte_to_prefix

        self.address_prefixes: List[str] = magicbyte_to_prefix(magicbyte=self.magicbyte)
        self.script_prefixes: List[str] = []
        if self.script_magicbyte:
            self.script_prefixes = magicbyte_to_prefix(magicbyte=self.script_magicbyte)
        self.secondary_hashcode = self.secondary_hashcode or self.hashcode
        self.fees = {}

    @property
    def client(self):
        """
        Connect to remote server
        """
        if not self._client:
            self._client = self.explorer(**self.client_kwargs)
        return self._client

    async def close(self) -> None:
        if self._client:
            await self._client.close()

    async def estimate_fee_per_kb_original(self, numblocks: int = 6) -> float:
        """
        Get estimated fee kb to get transaction confirmed within numblocks number of blocks,
        Online lookup.
        """
        return await self.client.estimate_fee(numblocks=numblocks)

    async def estimate_fee_per_kb(self, numblocks: int = 6) -> float:
        """
        Estimates the transaction fee per kilobyte required to get a Bitcoin(dogecoin,litecoin ...)
        transaction confirmed within a specified number of blocks.

        This asynchronous function queries the current fee market to provide an estimate of the
        fee rate needed to ensure that a transaction is included in a block within the given
        timeframe. The fee is expressed in satoshis per kilobyte, which is a common unit for
        measuring transaction fees in the Bitcoin network.

        Args:
            numblocks (int): The number of blocks within which the transaction should be confirmed.
                            The default value is 6, which is generally considered a standard
                            confirmation time for Bitcoin transactions.

        Returns:
            float: The estimated fee per kilobyte in satoshis. This value can be used to set the
                appropriate fee for a transaction to ensure timely confirmation.

        Example:
            >>> fee_per_kb = await self.estimate_fee_per_kb(numblocks=3)
            >>> print(fee_per_kb)
            0.00009  # Example fee value in satoshis per kilobyte

        Note:
            The actual fee required may vary based on network congestion and other factors.
            It is advisable to check the fee estimate close to the time of transaction submission.
        """
        api_endpoint_response_object: Any = await self.client.estimate_fee(
            numblocks=numblocks
        )
        return api_endpoint_response_object

    def tx_size_original(self, txobj: Tx) -> float:
        """
        Get transaction size in bytes
        """
        tx = serialize(txobj)
        size = len(tx) / 2
        for inp in txobj["ins"]:
            address = inp.get("address")
            if address and self.is_native_segwit(address):
                pass  # Segwit signatures not included in tx size for fee purposes?
            elif address and self.maybe_legacy_segwit(address):
                size += self.signature_sizes["p2w_p2sh"]  # Not sure if segwit or not
            else:
                size += self.signature_sizes["p2pkh"]
        return size

    def tx_size(self, txobj: Tx) -> float:
        """
        Calculates the size of a transaction in bytes, taking into account signature sizes
        based on address types.

        This function determines the transaction size by considering the size
        of the serialized transaction data and the size of signatures based on
        the address types used in the transaction inputs. Different address
        types (e.g., P2PKH, P2WPKH, P2SH) have varying signature sizes,
        which are accounted for in the calculation.

        Args:
            txobj (Tx): The transaction object containing information about the transaction, including inputs and outputs.

        Returns:
            float: The size of the transaction in bytes. This value is used for calculating transaction fees.

        Example:
            >>> tx_size = self.tx_size(txobj)
            >>> print(tx_size)
            226.0  # Example transaction size in bytes

        Note:
            - The function assumes that the `signature_sizes` attribute is a dictionary containing the signature sizes for
            different address types.
            - The function considers Segwit (Segregated Witness) addresses and adjusts the size accordingly.
            - The calculation may not be entirely accurate for all transaction types and address combinations.
        """
        tx: bytes = serialize(txobj=txobj)
        size: float = len(tx) / 2
        for inp in txobj["ins"]:
            address: str = inp.get("address")
            if address and self.is_native_segwit(addr=address):
                pass  # Segwit signatures not included in tx size for fee purposes?
            elif address and self.maybe_legacy_segwit(addr=address):
                size += self.signature_sizes["p2w_p2sh"]  # Not sure if segwit or not
            else:
                size += self.signature_sizes["p2pkh"]
        return size

    async def estimate_fee(self, txobj: Tx, numblocks: int = 6) -> int:
        """
        Get estimated fee to get transaction confirmed within numblocks number of blocks.
        txobj is a pre-signed transaction object
        """
        num_bytes = self.tx_size(txobj=txobj)
        btc_fee_per_kb = await self.estimate_fee_per_kb(numblocks=numblocks)
        if btc_fee_per_kb > 0:
            btc_fee_per_byte = btc_fee_per_kb / 1024
            satoshi_fee_per_byte = btc_fee_per_byte * SATOSHI_PER_BTC
            return int(num_bytes * satoshi_fee_per_byte)
        return 0

    @staticmethod
    async def _tasks_with_inputs(
        coro: Callable, *args: Any, **kwargs
    ) -> Generator[Tuple[Any, Any], None, None]:
        for i, result in enumerate(
            await asyncio.gather(*[coro(arg, **kwargs) for arg in args])
        ):
            arg = args[i]
            yield arg, result

    async def raw_block_header(self, height: int) -> str:
        return await self.client.block_header(height)

    async def block_header(self, height: int) -> BlockHeader:
        """
        Return block header data for the given height
        """
        from cryptos.blocks import deserialize_header

        header = await self.raw_block_header(height)
        return deserialize_header(unhexlify(header))

    async def block_headers(self, *args: int) -> AsyncGenerator[BlockHeader, None]:
        """
        Return block header data for the given heights
        """
        for header in await asyncio.gather(*[self.block_header(h) for h in args]):
            yield header

    @staticmethod
    def _get_block_header_notification_params(
        header: ElectrumXBlockHeaderNotification,
    ) -> Tuple[int, str, BlockHeader]:
        from cryptos.blocks import deserialize_header

        height = header["height"]
        hex_header = header["hex"]
        header = deserialize_header(unhexlify(hex_header))
        return height, hex_header, header

    @staticmethod
    async def _await_or_in_executor(func: Callable, *args):
        f = func
        is_coro = asyncio.iscoroutinefunction(f)
        while not is_coro and isinstance(f, partial):
            f = f.func
            is_coro = asyncio.iscoroutinefunction(f)
        if is_coro:
            await func(*args)
        else:
            try:
                await asyncio.get_running_loop().run_in_executor(None, func, *args)
            except RuntimeError as e:
                if "Non-thread-safe" in e:
                    """
                    Sync callbacks are called in another thread so cannot interact with asyncio objects.
                    """
                    raise Exception(
                        "Syncronous callbacks cannot interact with asyncio objects such as Futures. Make the callback a coroutine function."
                    )
                else:
                    raise e

    async def _block_header_callback(
        self, callback: BlockHeaderCallback, header: ElectrumXBlockHeaderNotification
    ) -> None:
        height, hex_header, header = self._get_block_header_notification_params(header)
        await self._await_or_in_executor(callback, height, hex_header, header)

    async def subscribe_to_block_headers(self, callback: BlockHeaderCallback) -> None:
        """
        Run callback when a new block is added to the blockchain
        Callback should be in the format:

        from cryptos.types import BlockHeader

        async def on_block_headers(height: int, hex_header: str, header:BlockHeader) -> None:
            pass

        or

        def on_block_headers(height: int, hex_header: str, header:BlockHeader) -> None:
            pass

        """

        callback = partial(self._block_header_callback, callback)
        return await self.client.subscribe_to_block_headers(callback)

    async def unsubscribe_from_block_headers(self) -> None:
        """
        Unsubscribe from running callbacks when a new block is added
        """
        return await self.client.unsubscribe_from_block_headers()

    async def _update_block(
        self, fut: asyncio.Future, height: int, hex_header: str, header: BlockHeader
    ):
        self._block = (height, hex_header, header)
        if not fut.done():
            fut.set_result(True)

    @property
    async def block(self) -> Tuple[int, str, BlockHeader]:
        """
        Gets the latest block in the blockchain.
        First time this is run it will subscribe to block headers.
        """
        if not self._block:
            fut = asyncio.Future()
            await self.subscribe_to_block_headers(partial(self._update_block, fut))
            await fut
        return self._block

    def is_closing(self) -> bool:
        return not self.client or self.client.is_closing

    async def confirmations(self, height: int) -> int:
        if height > 0:
            return (await self.block)[0] - height + 1
        return 0

    async def _address_status_callback(
        self, callback: AddressCallback, address: str, scripthash: str, status: str
    ) -> None:
        await self._await_or_in_executor(callback, address, status)

    async def subscribe_to_address(self, callback: AddressCallback, addr: str) -> None:
        """
        Run callback when an address changes (e.g. a new transaction)
        Callback should be in the format:

        def on_address_event(address: str, status: str) -> None:
            pass
        """

        orig_addr = addr
        if self.client.requires_scripthash:
            addr = self.addrtoscripthash(addr)
        callback = partial(self._address_status_callback, callback, orig_addr)
        return await self.client.subscribe_to_address(callback, addr)

    async def unsubscribe_from_address(self, addr: str):
        """
        Unsubscribe from running callbacks when an address changes
        """
        if self.client.requires_scripthash:
            addr = self.addrtoscripthash(addr)
        return await self.client.unsubscribe_from_address(addr)

    async def _address_transaction_callback(
        self,
        callback: AddressTXCallback,
        history: ElectrumXHistoryResponse,
        address: str,
        status: str,
    ) -> None:
        updated_history, unspents, balance, merkle_proven = await asyncio.gather(
            self.history(address),
            self.unspent(address),
            self.get_balance(address),
            self.balance_merkle_proven(address),
        )
        if history == ["-"]:
            # First response
            new_txs = []
            history.clear()
            history += updated_history
            newly_confirmed = []
        else:
            tx_hashes = {t["tx_hash"]: t["height"] for t in history}
            new_txs = [
                t for t in updated_history if t["tx_hash"] not in tx_hashes.keys()
            ]
            newly_confirmed = [
                t
                for t in updated_history
                if tx_hashes.get("tx_hash") and not t["height"] == tx_hashes["tx_hash"]
            ]

        prev_history = [tx for tx in history if tx not in newly_confirmed]
        for tx in newly_confirmed:
            history.remove(tx)
        history += new_txs
        await self._await_or_in_executor(
            callback,
            address,
            new_txs,
            newly_confirmed,
            prev_history,
            unspents,
            balance["confirmed"],
            balance["unconfirmed"],
            merkle_proven,
        )

    async def subscribe_to_address_transactions(
        self, callback: AddressTXCallback, addr: str
    ) -> None:
        """
        When an address changes retrieve transactions and balances and run a callback
        Callback should be in the format:

        def on_address_change(address: str, txs: List[ElectrumXTx], newly_confirmed: List[ElectrumXTx], history: List[ElectrumXTx], unspent: List[ElectrumTX], confirmed: int, unconfirmed: int, proven: int) -> None:
            pass

        Any transactions since the last notification are in Txs. All previous transactions are in history.
        Balances according to the network are in confirmed and unconfirmed.
        Balances confirmed locally is in proven.
        """

        history = ["-"]

        callback = partial(self._address_transaction_callback, callback, history)

        return await self.subscribe_to_address(callback, addr)

    async def get_balance(self, addr: str) -> ElectrumXBalanceResponse:
        """
        Get address balance
        """
        if self.client.requires_scripthash:
            addr = self.addrtoscripthash(addr)
        return await self.client.get_balance(addr)

    async def get_balances(
        self, *args: str
    ) -> AsyncGenerator[ElectrumXMultiBalanceResponse, None]:
        async for addr, result in self._tasks_with_inputs(self.get_balance, *args):
            result["address"] = addr
            yield result

    async def get_merkle(self, tx: ElectrumXTx) -> Optional[ElectrumXMerkleResponse]:
        return await self.client.get_merkle(tx["tx_hash"], tx["height"])

    async def merkle_prove(self, tx: ElectrumXTx) -> MerkleProof:
        """
        Prove that information returned from server about a transaction in the blockchain is valid. Only run on a
        tx with at least 1 confirmation.
        """
        from cryptos.blocks import verify_merkle_proof

        merkle, block_header = await asyncio.gather(
            self.get_merkle(tx), self.block_header(tx["height"])
        )
        if not merkle:
            # Can happen if request is run immediately after pushing a transaction
            return {"tx_hash": tx["tx_hash"], "proven": False}
        proof = verify_merkle_proof(
            tx["tx_hash"], block_header["merkle_root"], merkle["merkle"], merkle["pos"]
        )
        return proof

    async def merkle_prove_by_txid(self, tx_hash: str) -> MerkleProof:
        tx = await self.get_tx(tx_hash)
        return await self.merkle_prove(tx)

    async def _filter_by_proof_original(
        self, *txs: ElectrumXTx
    ) -> Iterable[ElectrumXTx]:
        """
        Return only transactions with verified merkle proof
        """
        results = await asyncio.gather(*[self.merkle_prove(tx) for tx in txs])
        proven = [r["tx_hash"] for r in results if r["proven"]]
        return filter(lambda tx: tx["tx_hash"] in proven, txs)

    async def _filter_by_proof(self, *txs: ElectrumXTx) -> Iterable[ElectrumXTx]:
        """
        Return only transactions with verified merkle proof.

        This function filters a list of transactions based on their Merkle proof verification.
        It uses the `merkle_prove` method (not shown here) to verify the Merkle
        proof for each transaction.
        Only transactions with a successful verification (i.e., `proven` is True) are returned.

        Args:
            *txs: A variable number of ElectrumXTx objects representing transactions.

        Returns:
            An iterable containing only the transactions with verified Merkle proofs.

        Detailed Description of Merkle Proof:

        A Merkle proof is a cryptographic technique used to efficiently verify
        the inclusion of a specific transaction within a blockchain's Merkle tree.
        It works as follows:

            1. **Merkle Tree Construction:**
                The blockchain's transactions are organized into a binary tree
                called a Merkle tree. Each leaf node represents a transaction hash,
                and internal nodes are calculated by hashing pairs of child nodes.
                The root node represents the entire tree's hash, which is included
                in the block header.

            2. **Merkle Proof Generation:**
                To prove a transaction's inclusion,
                a Merkle proof is generated. It consists of a series of
                hashes representing the path from the transaction's leaf
                node to the root node. This path includes the transaction's
                hash itself and the hashes of all its siblings (nodes at the same level
                  but on the opposite side of the tree).

            3. **Proof Verification:**
                To verify the proof, the recipient calculates the Merkle
                root hash using the provided hashes and the transaction's hash.
                If the calculated root hash matches the one included in the block
                header, the transaction's inclusion is verified.

        This method uses the `merkle_prove` method to generate and verify
        Merkle proofs for each transaction. It returns only the transactions with
        verified proofs, ensuring that they are indeed part of the blockchain.
        """
        results = await asyncio.gather(*[self.merkle_prove(tx) for tx in txs])
        proven = [r["tx_hash"] for r in results if r["proven"]]
        return filter(lambda tx: tx["tx_hash"] in proven, txs)

    async def unspent_original(
        self, addr: str, merkle_proof: bool = False
    ) -> ElectrumXUnspentResponse:
        """
        Get unspent transactions for address
        """
        value = addr
        if self.client.requires_scripthash:
            value = self.addrtoscripthash(value)
        unspents = await self.client.unspent(value)
        for u in unspents:
            u["address"] = addr
        if merkle_proof:
            return list(await self._filter_by_proof(*unspents))
        return unspents

    async def unspent(
        self,
        addr: str,
        merkle_proof: bool = False,
    ) -> ElectrumXUnspentResponse:
        """
        Get unspent transactions for a given address.(Online lookup)

        Args:
            addr (str): The address to query.
            merkle_proof (bool, optional): If True, return only unspent transactions with merkle proofs. Defaults to False.

        Returns:
            ElectrumXUnspentResponse (List[ElectrumXTx]): A list of ElectrumXTx.
        """
        value: str = addr
        if self.client.requires_scripthash:
            script_hexa_str_hash: str = self.addrtoscripthash(addr=value)

            electrumX_unspent_response: ElectrumXUnspentResponse = (
                await self.client.unspent(scripthash=script_hexa_str_hash)
            )
        else:
            electrumX_unspent_response: ElectrumXUnspentResponse = (
                await self.client.unspent(scripthash=value)
            )
        electrumXTx: ElectrumXTx
        for electrumXTx in electrumX_unspent_response:
            electrumXTx["address"] = addr
        if merkle_proof:
            return list(await self._filter_by_proof(*electrumX_unspent_response))
        return electrumX_unspent_response

    async def get_unspents(
        self, *args: str, merkle_proof: bool = False
    ) -> AsyncGenerator[ElectrumXMultiTxResponse, None]:
        async for addr, result in self._tasks_with_inputs(
            self.unspent, *args, merkle_proof=merkle_proof
        ):
            for tx in result:
                tx["address"] = addr
                yield tx

    async def balance_merkle_proven(self, addr: str) -> int:
        result = sum(u["value"] for u in await self.unspent(addr, merkle_proof=True))
        return result

    async def balances_merkle_proven(
        self, *args: str
    ) -> AsyncGenerator[AddressBalance, None]:
        async for addr, result in self._tasks_with_inputs(
            self.unspent, *args, merkle_proof=True
        ):
            yield {"address": addr, "balance": sum(tx["value"] for tx in result)}

    async def history(
        self, addr: str, merkle_proof: bool = False
    ) -> ElectrumXHistoryResponse:
        """
        Get transaction history for address
        """
        if self.client.requires_scripthash:
            addr = self.addrtoscripthash(addr)
        txs = await self.client.get_history(addr)
        if merkle_proof:
            return list(await self._filter_by_proof(*txs))
        return txs

    async def get_histories(
        self, *args: str, merkle_proof: bool = False
    ) -> AsyncGenerator[ElectrumXMultiTxResponse, None]:
        async for addr, result in self._tasks_with_inputs(
            self.history, *args, merkle_proof=merkle_proof
        ):
            for tx in result:
                tx["address"] = addr
                yield tx

    async def get_raw_tx(self, tx_hash: str) -> str:
        """
        Fetch transaction from the blockchain
        """
        return await self.client.get_tx(tx_hash)

    async def get_tx(self, txid: str) -> Tx:
        """
        Fetch transaction from the blockchain and deserialise it to a dictionary
        """
        tx = await self.get_raw_tx(txid)
        deserialized_tx = deserialize(tx)
        return deserialized_tx

    async def get_verbose_tx(self, txid: str) -> ElectrumXVerboseTX:
        """
        Fetch transaction from the blockchain in verbose form
        """
        return await self.client.get_tx(txid, verbose=True)

    async def get_txs(self, *args: str) -> AsyncGenerator[Tx, None]:
        for tx in await asyncio.gather(*[self.get_tx(tx_hash) for tx_hash in args]):
            yield tx

    async def _ensure_values(self, tx: Tx) -> Tx:
        if not all(inp.get("value") for inp in tx["ins"]):
            tx_hashes = list(
                dict.fromkeys(
                    [inp["tx_hash"] for inp in tx["ins"] if not inp.get("value")]
                )
            )
            try:
                txs = await alist(self.get_txs(*tx_hashes))
            except RuntimeError as e:  # Not sure what causes this intermittent error
                txs = []
            for inp in tx["ins"]:
                pos = inp["tx_pos"]
                prev_tx = next(
                    filter(lambda t: txhash(serialize(t)) == inp["tx_hash"], txs)
                )
                inp["value"] = prev_tx["outs"][pos]["value"]
        return tx

    async def calculate_fee(self, tx: Tx) -> int:
        try:
            tx = await self._ensure_values(tx)
        except RuntimeError:
            pass
        in_value = sum(i["value"] for i in tx["ins"])
        out_value = sum(o["value"] for o in tx["outs"])
        return in_value - out_value

    async def pushtx_original(self, tx: Union[str, Tx]):
        """
        Push/ Broadcast a transaction to the blockchain
        """
        if not isinstance(tx, str):
            tx = serialize(tx)
        try:
            result = await self.client.broadcast_tx(raw_tx=tx)
            return result
        except (aiorpcx.jsonrpc.ProtocolError, aiorpcx.jsonrpc.RPCError) as e:
            tx_obj = deserialize(tx)
            message = f"{tx_obj}\n{tx}\n{e.message}"
            if any(code == e.code for code in (1, -32600)):
                if "fee" in e.message:
                    message += f"Fee is {await self.calculate_fee(tx_obj)}"
                raise TXRejectedError(message)
            raise TXInvalidError(message)

    async def pushtx(self, tx: Union[str, Tx]):
        """
        Push/ Broadcast a transaction to the blockchain
        """
        if not isinstance(tx, str):
            tx = serialize(tx)
        try:
            result = await self.client.broadcast_tx(raw_tx=tx)
            return result
        # except Exception as e:
        #     print(f"An error occurred: {e}")  # Print the exception details
        #     return e
        except (aiorpcx.jsonrpc.ProtocolError, aiorpcx.jsonrpc.RPCError) as e:
            return e
            # tx_obj = deserialize(tx)
            # message = f"{tx_obj}\n{tx}\n{e.message}"
            # if any(code == e.code for code in (1, -32600)):
            #     if "fee" in e.message:
            #         message += f"Fee is {await self.calculate_fee(tx_obj)}"
            #     raise TXRejectedError(message)
            # raise TXInvalidError(message)

    def privtopub_original(self, privkey: PrivkeyType) -> str:
        """
        Derives the public key from a given private key.

        This function takes a private key in various formats and converts it to its corresponding
        public key. It handles different private key formats (decimal, binary, hexadecimal, WIF)
        and ensures the private key is within the valid range.

        Args:
            privkey (PrivkeyType): The private key to convert. It can be an integer, a binary string,
                                a hexadecimal string, or a WIF string.

        Returns:
            str: The public key in the same format as the input private key, if possible.
                For WIF input, the output is in hexadecimal format.

        Raises:
            Exception: If the private key is invalid (e.g., outside the valid range).
        """

        # this is i guess tome kind of anonymus function(not sure)
        return privtopub(privkey=privkey)

    def privtopub(self, privkey: PrivkeyType) -> str:
        """
        Derives the public key from a given private key.

        This function takes a private key in various formats and converts it to its corresponding
        public key. It handles different private key formats (decimal, binary, hexadecimal, WIF)
        and ensures the private key is within the valid range.

        Args:
            privkey (PrivkeyType): The private key to convert. It can be an integer, a binary string,
                                a hexadecimal string, or a WIF string.

        Returns:
            str: The public key in the same format as the input private key, if possible.
                For WIF input, the output is in hexadecimal format.

        Raises:
            Exception: If the private key is invalid (e.g., outside the valid range).
        """

        from ..main import privtopub

        public_key: str = privtopub(privkey=privkey)
        return public_key  # privtopub(privkey=privkey)

    def pubtoaddr_original(self, pubkey: PubKeyType) -> str:
        """
        Get address from a public key
        """
        from ..main import pubtoaddr

        return pubtoaddr(pubkey=pubkey, magicbyte=self.magicbyte)

    def pubtoaddr(self, pubkey: PubKeyType) -> str:
        """
        Converts a public key to a cryptocurrency address.

        This method utilizes the `pubtoaddr` function from the `main`
        module to convert a public key
        into a corresponding cryptocurrency address.
        The conversion process takes into account the
        network's magic byte, which is specific to the cryptocurrency being used.

        Args:
            pubkey (PubKeyType): The public key to be converted. The type `PubKeyType` can be a
                                string, bytes, or any other type supported by the `pubtoaddr` function.

        Returns:
            str:(address_Base58_string) The cryptocurrency address corresponding to the provided public key.

        Example:
            >>> pubkey = '0279be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798'
            >>> address = pubtoaddr(pubkey)
            >>> print(address)
            '1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2'
        """
        from ..main import pubtoaddr

        address_Base58_string: str = pubtoaddr(pubkey=pubkey, magicbyte=self.magicbyte)
        return address_Base58_string

    def get_address_variations(self, address: str) -> List[str]:
        if self.cash_address_supported:
            if self.is_cash_address(address):
                return [address, self.cash_address_to_legacy_addr(address)]
            else:
                return [self.legacy_addr_to_cash_address(address), address]
        else:
            return [address]

    def pub_is_for_p2pkh_addr(self, pubkey: PubKeyType, address: str) -> bool:
        return self.pubtoaddr(pubkey) == address or (
            self.cash_address_supported and self.pubtocashaddress(pubkey) == address
        )

    def wiftoaddr(self, privkey: PrivkeyType) -> str:
        from ..main import b58check_to_bin

        magicbyte, priv = b58check_to_bin(inp=privkey)
        wif_magicbyte = magicbyte - self.wif_prefix
        if self.wif_script_types["p2pkh"] == wif_magicbyte:
            return self.privtop2pkh(privkey)
        if self.wif_script_types["p2wpkh-p2sh"] == wif_magicbyte:
            return self.privtop2wpkh_p2sh(priv=privkey)
        if self.wif_script_types["p2wpkh"] == wif_magicbyte:
            return self.privtosegwitaddress(privkey=privkey)
        else:
            raise Exception(
                "Address type for this wif-encoded private key not supported yet"
            )

    def privtoaddr_original(self, privkey: PrivkeyType) -> str:
        """
        Get address from a private key
        """
        from ..main import get_privkey_format

        privkey_format: str = get_privkey_format(privkey=privkey)
        if "wif" in privkey_format:
            return self.wiftoaddr(privkey=privkey)
        return self.privtop2pkh(privkey=privkey)

    def privtoaddr(self, privkey: PrivkeyType) -> str:
        """
        Derives a **public Bitcincoin or doge  address** from a provided private key.

        This function handles both WIF (Wallet Import Format) and other private key types.
        It determines the format of the private key and delegates the conversion to the appropriate function:

        - If the private key is in WIF format, it calls `self.wiftoaddr` to derive the address.
        - Otherwise, it calls `self.privtop2pkh` to derive the address.

        Args:
            privkey (PrivkeyType): The private key to convert to an address.
            **PrivkeyType** is a Union type representing either an integer, string, or bytes object.

        Returns:
            str: The **public coin address** derived from the provided private key.
        """
        # from ..main import get_privkey_format
        from .. import main

        address: str = ""
        privkey_format: str = main.get_privkey_format(privkey=privkey)
        if "wif" in privkey_format:
            address = self.wiftoaddr(privkey=privkey)
        else:
            address = self.privtop2pkh(privkey=privkey)
        return address  # self.privtop2pkh(privkey=privkey)

    def privtop2pkh(self, privkey: PrivkeyType) -> str:
        from ..main import privtoaddr

        address: str = privtoaddr(priv=privkey, magicbyte=self.magicbyte)
        return address

    def electrum_address(self, masterkey: AnyStr, n: int, for_change: int = 0) -> str:
        """
        For old electrum seeds
        """
        pubkey = electrum_pubkey(masterkey, n, for_change=for_change)
        return self.pubtoaddr(pubkey)

    def encode_privkey_original(
        self,
        privkey: PrivkeyType,
        formt: str,
        script_type: str = "p2pkh",
    ) -> PrivkeyType:
        from ..main import encode_privkey

        return encode_privkey(
            privkey,
            formt=formt,
            vbyte=self.wif_prefix + self.wif_script_types[script_type],
        )

    def encode_privkey(
        self,
        privkey: PrivkeyType,
        formt: str,
        script_type: str = "p2pkh",
    ) -> PrivkeyType:
        """Encodes a private key into various formats, using the specified WIF prefix and script type.

        Args:
            self: The instance of the class calling this method.
            privkey (PrivkeyType): The private key to encode. It can be represented in one of the following ways:
                - **Integer:** The raw integer value of the private key.
                - **String:** A string representation of the private key in a supported format (e.g., hexadecimal, binary).
                - **Bytes:** A byte sequence representing the private key.
            formt (str): The desired format for the encoded private key.
                Supported formats:
                    - "decimal": Integer representation of the private key.
                    - "bin": Binary representation of the private key.
                    - "bin_compressed": Compressed binary representation of the private key.
                    - "hex": Hexadecimal representation of the private key.
                    - "hex_compressed": Compressed hexadecimal representation of the private key.
                    - "wif": Wallet Import Format (uncompressed)
                    - "wif_compressed": Wallet Import Format (compressed)
            script_type (str, optional): The type of script to use for WIF encoding. Defaults to "p2pkh".
                - "p2pkh": Pay-to-Public-Key Hash (default)
                - "p2sh": Pay-to-Script Hash

        Returns:
            PrivkeyType: The encoded private key in the specified format.
        """
        from ..main import encode_privkey

        return encode_privkey(
            priv=privkey,
            formt=formt,
            vbyte=self.wif_prefix + self.wif_script_types[script_type],
        )

    def is_p2pkh_original(self, addr: str) -> bool:
        """
        Legacy addresses only doesn't include Cash P2PKH Address
        """
        try:
            magicbyte: int
            actuall_data_without_Magic_byte_and_checksum: bytes
            magicbyte, actuall_data_without_Magic_byte_and_checksum = b58check_to_bin(
                inp=addr
            )
            return magicbyte == self.magicbyte
        except Exception:
            return False

    def is_p2pkh_original(self, addr: str) -> bool:
        """
        Checks if the given address is a Pay-to-Public-Key-Hash (P2PKH) address.

        This function is specific to legacy addresses and does not include Cash P2PKH addresses.

        Args:
            addr (str): The Bitcoin address to check.

        Returns:
            bool: True if the address is a P2PKH address, False otherwise.
        """

        try:
            magicbyte: int
            actual_data_without_magic_byte_and_checksum: bytes
            magicbyte, actual_data_without_magic_byte_and_checksum = b58check_to_bin(
                inp=addr
            )
            return magicbyte == self.magicbyte
        except Exception:
            return False

    def is_p2pkh(self, addr: str) -> bool:
        """
        Checks if the given address is a Pay-to-Public-Key-Hash (P2PKH) address.

        This function is specific to legacy addresses and does not include Cash P2PKH addresses.

        Args:
            addr (str): The Bitcoin address to check.

        Returns:
            bool: True if the address is a P2PKH address, False otherwise.
        """
        from .. import main

        try:
            magicbyte: int
            actual_data_without_magic_byte_and_checksum: bytes
            magicbyte, actual_data_without_magic_byte_and_checksum = (
                main.b58check_to_bin(inp=addr)
            )
            return magicbyte == self.magicbyte
        except Exception as e:
            print(f"An error occurred: {e}")  # Print the exception details
            return False

    def is_p2pkh_other_version(self, addr: str) -> bool:
        """
        Checks if the given address is a Pay-to-Public-Key-Hash (P2PKH) address.

        This function is specific to legacy addresses and does not include Cash P2PKH addresses.

        Args:
            addr (str): The Bitcoin address to check.

        Returns:
            bool: True if the address is a P2PKH address, False otherwise.
        """
        from .. import main

        is_p2pkh: bool = False
        # try:
        magicbyte: int
        actual_data_without_magic_byte_and_checksum: bytes
        magicbyte, actual_data_without_magic_byte_and_checksum = main.b58check_to_bin(
            inp=addr
        )
        if magicbyte == self.magicbyte:
            is_p2pkh = True
            # return magicbyte == self.magicbyte
        else:
            print(f"error at is_p2pkh in try b58check_to_bin for Address: {addr}")
        # except Exception:
        # print(f'error at is_p2pkh in try b58check_to_bin for Address: {addr}')
        return is_p2pkh

    def is_cash_or_legacy_p2pkh_address(self, addr: str) -> bool:
        return self.is_p2pkh(addr) or self.is_cash_address(addr)

    def is_p2sh_original(self, addr: str) -> bool:
        """
        Check if addr is a pay to script address
        """
        try:
            magicbyte: int
            actual_data_without_magic_byte_and_checksum: bytes
            magicbyte, actual_data_without_magic_byte_and_checksum = b58check_to_bin(
                inp=addr
            )
            return magicbyte == self.script_magicbyte
        except Exception:
            return False

    def is_p2sh(self, addr: str) -> bool:
        """
        Checks if the given address is a Pay-to-Script-Hash (P2SH) address.

        This function determines if the provided address is a
        P2SH address, which is a type of Bitcoin address
        that allows for more complex transaction scripts.

        Args:
            addr (str): The Bitcoin address to check.

        Returns:
            bool: True if the address is a P2SH address, False otherwise.
        """
        from .. import main

        try:
            magicbyte: int
            actual_data_without_magic_byte_and_checksum: bytes
            magicbyte, actual_data_without_magic_byte_and_checksum = (
                main.b58check_to_bin(inp=addr)
            )
            return magicbyte == self.script_magicbyte
        except Exception:
            return False

    def is_native_segwit_original(self, addr: str) -> bool:
        return (
            self.segwit_supported
            and self.segwit_hrp
            and addr.startswith(self.segwit_hrp)
        )

    def is_native_segwit(self, addr: str) -> bool:
        """
        Checks if the given address is a native SegWit (Bech32) address Human-Readable Part (HRP) .

        This function determines if the provided address is a
        native SegWit address, which is a type of Bitcoin
        address that utilizes the Bech32 encoding scheme
        for improved efficiency and security.

        Args:
            addr (str): The Bitcoin address to check.

        Returns:
            bool: True if the address is a native SegWit address, False otherwise.
        More:
            The self.segwit_hrp refers to the Human-Readable Part (HRP) of a native SegWit (Bech32) Bitcoin address. In the context of Bitcoin addresses, the HRP is a prefix that helps identify the type of address being used.

            Key Points about self.segwit_hrp:
                Purpose:
                    The HRP distinguishes between different types
                    of Bitcoin addresses. For native SegWit addresses,
                    the HRP is typically set to "bc" for mainnet addresses
                    and "tb" for testnet addresses.

                SegWit Addresses:
                    Native SegWit addresses, which use the Bech32 format,
                    provide benefits such as improved error detection
                    and lower transaction fees due to their more efficient
                    encoding.

                Usage in Code:
                    In the function is_native_segwit,
                    self.segwit_hrp is used to check if the provided
                    address starts with the correct prefix, confirming
                    that it is indeed a native SegWit address.

            Example of HRP:
                Mainnet SegWit Address: Starts with bc1
                Testnet SegWit Address: Starts with tb1


        """
        return (
            self.segwit_supported
            and self.segwit_hrp  # Human-Readable Part (HRP)
            and addr.startswith(self.segwit_hrp)
        )

    def is_cash_address_original(self, addr: str) -> bool:
        return (
            self.cash_address_supported
            and self.cash_hrp
            and addr.startswith(self.cash_hrp)
        )

    def is_cash_address(self, addr: str) -> bool:
        """
        Checks if the given address is a Bitcoin Cash (BCH) address.

        This function determines if the provided address is a Bitcoin Cash (BCH)
        address, which uses a specific prefix for its addresses.

        Args:
            addr (str): The Bitcoin address to check.

        Returns:
            bool: True if the address is a Bitcoin Cash address, False otherwise.
        """
        return (
            self.cash_address_supported
            and self.cash_hrp
            and addr.startswith(self.cash_hrp)
        )

    def is_address_original(self, addr: str) -> bool:
        """
        Check if addr is a valid address for this chain
        """
        return (
            self.is_p2pkh(addr=addr)
            or self.is_p2sh(
                addr=addr
            )  # TODO check if it makes a difference becuase  is_p2pkh is the same as is_p2sh
            or self.is_native_segwit(addr=addr)
            or self.is_cash_address(addr=addr)
            or is_public_key(addr)
        )

    def is_address_original(self, addr: str) -> bool:
        """
        Checks if a given string is a valid address for the current blockchain.

        This function verifies if the provided address is a
        valid address for the specific blockchain it's associated with.
        It checks against various address formats, including:

        - Pay-to-Public-Key Hash (P2PKH): A traditional Bitcoin address format.
        - Pay-to-Script-Hash (P2SH): A format for storing scripts in a Bitcoin address.
        - Native SegWit: A newer address format introduced with SegWit (Segregated Witness).
        - Cash Address: An address format used by Bitcoin Cash.
        - Public Key: A raw public key representation.

        Args:
            addr: The string to check for validity as an address.

        Returns:
            bool: `True` if the string is a valid address for the current blockchain, `False` otherwise.
        """
        from ..main import magicbyte_to_prefix

        return (
            self.is_p2pkh(addr=addr)
            or self.is_p2sh(
                addr=addr
            )  # TODO check if it makes a difference because is_p2pkh is the same as is_p2sh
            or self.is_native_segwit(addr=addr)
            or self.is_cash_address(addr=addr)
            or is_public_key(addr)
        )

    def is_address_old(self, addr: str) -> bool:
        """
        Checks if a given string is a valid address for the current blockchain.

        This function verifies if the provided address is a
        valid address for the specific blockchain it's associated with.
        It checks against various address formats, including:

        - Pay-to-Public-Key Hash (P2PKH): A traditional Bitcoin address format.
        - Pay-to-Script-Hash (P2SH): A format for storing scripts in a Bitcoin address.
        - Native SegWit: A newer address format introduced with SegWit (Segregated Witness).
        - Cash Address: An address format used by Bitcoin Cash.
        - Public Key: A raw public key representation.

        Args:
            addr: The string to check for validity as an address.

        Returns:
            bool: `True` if the string is a valid address for the current blockchain, `False` otherwise.
        """
        from .. import main

        return (
            self.is_p2pkh(addr=addr)
            or self.is_p2sh(
                addr=addr
            )  # TODO check if it makes a difference because is_p2pkh is the same as is_p2sh
            or self.is_native_segwit(addr=addr)
            or self.is_cash_address(addr=addr)
            or main.is_public_key(pub=addr)
        )

    def is_address(self, addr: str) -> bool:
        """
        Checks if a given string is a valid address for the current blockchain.

        This function verifies if the provided address is a
        valid address for the specific blockchain it's associated with.
        It checks against various address formats, including:

        - Pay-to-Public-Key Hash (P2PKH): A traditional Bitcoin address format.
        - Pay-to-Script-Hash (P2SH): A format for storing scripts in a Bitcoin address.
        - Native SegWit: A newer address format introduced with SegWit (Segregated Witness).
        - Cash Address: An address format used by Bitcoin Cash.
        - Public Key: A raw public key representation.

        Args:
            addr: The string to check for validity as an address.

        Returns:
            bool: `True` if the string is a valid address for the current blockchain, `False` otherwise.
        """
        from .. import main

        output: bool = False  # Initialize output as False
        if self.is_native_segwit(addr=addr):
            output = True
            return output  # Return True immediately if SegWit
        elif self.is_p2pkh(addr=addr):
            output = True
            return output  # Return True immediately if P2PKH
        elif self.is_p2sh(addr=addr):
            output = True
            return output  # Return True immediately if P2SH

        elif self.is_cash_address(addr=addr):
            output = True
            return output  # Return True immediately if Bitcoin Cash
        elif main.is_public_key(pub=addr):
            output = True
            return output  # Return True immediately if public key

        return output  # If none of the checks pass, return False

    def maybe_legacy_segwit(self, addr: str) -> bool:
        if self.segwit_supported:
            script = self.addrtoscript(addr)
            return script.startswith(
                opcodes.OP_HASH160.hex() + "14"
            ) and script.endswith(opcodes.OP_EQUAL.hex())
        return False

    def is_p2wsh(self, addr: str) -> bool:
        return self.is_native_segwit(addr) and len(addr) == 62

    def is_segwit_or_p2sh(self, addr: str) -> bool:
        """
        Check if addr is a p2wpkh, p2wsh or p2sh script
        """
        return self.is_native_segwit(addr) or self.maybe_legacy_segwit(addr)

    def output_script_to_address(self, script: str) -> str:
        """
        Convert an output script to an address
        """
        segwit_hrp = self.segwit_hrp if self.segwit_supported else None
        cash_hrp = self.cash_hrp if self.cash_address_supported else None
        return output_script_to_address(
            script, self.magicbyte, self.script_magicbyte, segwit_hrp, cash_hrp
        )

    def scripttoaddr(self, script: str) -> str:
        """
        Convert an input public key has or script to an address
        """
        if is_hex(script):
            script = binascii.unhexlify(script)
        # 0x14 is expected pubkey hash length
        pubkey_hash_prefix = binascii.unhexlify(
            opcodes.OP_DUP.hex() + opcodes.OP_HASH160.hex() + "14"
        )
        pubkey_hash_suffix = binascii.unhexlify(
            opcodes.OP_EQUALVERIFY.hex() + opcodes.OP_CHECKSIG.hex()
        )
        if (
            script[:3] == pubkey_hash_prefix
            and script[-2:] == pubkey_hash_suffix
            and len(script) == 25
        ):
            return bin_to_b58check(script[3:-2], self.magicbyte)  # pubkey hash address
        else:
            # BIP0016 scripthash address
            # scriptbyte = vbyte
            return bin_to_b58check(script[2:-1], self.script_magicbyte)

    def p2sh_scriptaddr_original(self, script: str) -> str:
        """
        Convert an output p2sh script to an address
        """
        if is_hex(script):
            script = binascii.unhexlify(script)
        return hex_to_b58check(hash160(script), self.script_magicbyte)

    def p2sh_scriptaddr(self, script: str) -> str:
        """
        Converts a Pay-to-Script-Hash (P2SH) output script to a cryptocurrency address.

        This function takes a P2SH output script as input and converts it to a cryptocurrency address, supporting Bitcoin, Dogecoin, and Litecoin. P2SH is a mechanism that allows for the use of more complex scripts within cryptocurrency transactions. Instead of directly including the script in the transaction, a hash of the script is used, which is then encoded into a cryptocurrency address. This address can then be used to redeem the funds associated with the script.

        Args:
            script (str): The P2SH output script, either as a hexadecimal string or raw bytes.

        Returns:
            str: The cryptocurrency address corresponding to the P2SH script.

        Examples:
            >>> p2sh_scriptaddr(script='a914d85c2b7151a08794e345dd9a7c5fc94f01f9a58887')  # Bitcoin
            '3M9w6R962u4sGeyhWDSV9hG37U4S2x3z8'
            >>> p2sh_scriptaddr(script='a914d85c2b7151a08794e345dd9a7c5fc94f01f9a58887', magicbyte=0x30)  # Litecoin
            'LTuQ2XzY5y8b8Z1226p256X8q2xZ9Q31'
            >>> p2sh_scriptaddr(script='a914d85c2b7151a08794e345dd9a7c5fc94f01f9a58887', magicbyte=0x1c)  # Dogecoin
            'D9534c13556425a34421c651494d823a52a788'
        """
        from .. import main

        # import utils
        if is_hex(script):
            script = binascii.unhexlify(script)
        RIPEMD_160_hash_hex_str: str = main.hash160(string=script)
        base58_encoded_with_leading_zeros: str = main.hex_to_b58check(
            inp=RIPEMD_160_hash_hex_str,
            magicbyte=self.script_magicbyte,
        )
        return base58_encoded_with_leading_zeros

    def p2sh_segwit_addr(self, script: str) -> str:
        """
        Convert an output p2sh script to a Native Segwit P2WSH address
        """
        if is_hex(script):
            script = binascii.unhexlify(script)
        return self.scripthash_to_segwit_addr(bin_sha256(script))

    def scripthash_to_cash_addr(self, scripthash: bytes) -> str:
        return cashaddr.encode_full(self.cash_hrp, cashaddr.SCRIPT_TYPE, scripthash)

    def p2sh_cash_addr(self, script: str) -> str:
        """
        Convert an output p2sh script to a Bitcoin Cash address
        """
        if is_hex(script):
            script = binascii.unhexlify(script)
        return self.scripthash_to_cash_addr(bin_hash160(script))

    def addrtoscrip_original(self, addr: str) -> str:
        """
        Convert an output address to a script
        """
        from ..main import magicbyte_to_prefix

        if self.is_native_segwit(addr):
            witver, witprog = segwit_addr.decode_segwit_address(self.segwit_hrp, addr)
            if witprog is not None:
                return mk_p2w_scripthash_script(witver, witprog)
        elif self.is_cash_address(addr):
            prefix, kind, hash_bin = cashaddr.decode(addr)
            hash_hex = safe_hexlify(hash_bin)
            if kind == 0:
                return mk_pubkey_script(hash_hex)
            return hash_to_scripthash_script(hash_hex)
        if self.is_p2sh(addr):
            return mk_scripthash_script(addr)
        elif self.is_p2pkh(addr):
            return addr_to_pubkey_script(addr)
        elif is_public_key(addr):
            return mk_p2pk_script(addr)
        raise Exception(f"Unrecognised address: {addr}")

    def is_dogecoin_address(self, addr: str) -> bool:
        """
        Checks if a given address is a valid Dogecoin address.

        Args:
            addr: The address to check.

        Returns:
            True if the address is a valid Dogecoin address, False otherwise.
        """
        is_doge_address: bool = False
        addr_length: int = len(addr)
        addr_upper: str = addr.upper()
        starts_with_D: bool = addr_upper.startswith("D")
        all_values_in_iterable: bool = all(
            c in "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ" for c in addr_upper
        )  # Check uppercase characters
        is_doge_address: bool = (
            addr_length == 34 and starts_with_D and all_values_in_iterable
        )
        return is_doge_address  # addr_length==34 and starts_with_D and all_values_in_iterable

    def is_valid_dogecoin_or_litecoin_address(self, address: str) -> str:
        """
        Checks if the provided address is a valid Dogecoin or Litecoin address.

        A valid Dogecoin address:
        - Starts with 'D' or '9'
        - Has a length of 34 characters

        A valid Litecoin address:
        - Starts with 'L', 'M', or '3'
        - Has a length of 34 characters

        Args:
            address (str): The address to check.

        Returns:
            str: A message indicating whether the address is valid for Dogecoin, Litecoin, or neither.
        """
        if len(address) == 34:
            if address.startswith(("D", "9")):
                return "This is a valid Dogecoin address."
            elif address.startswith(("L", "M", "3")):
                return "This is a valid Litecoin address."
        return "This is not a valid Dogecoin or Litecoin address."

    def addrtoscript_original(self, addr: str) -> str:
        """
        Convert an output address to a script
        """
        from .. import main

        if self.is_native_segwit(addr):
            witver, witprog = segwit_addr.decode_segwit_address(self.segwit_hrp, addr)
            if witprog is not None:
                return mk_p2w_scripthash_script(witver, witprog)
        elif self.is_cash_address(addr):
            prefix, kind, hash_bin = cashaddr.decode(addr)
            hash_hex = safe_hexlify(hash_bin)
            if kind == 0:
                return mk_pubkey_script(hash_hex)
            return hash_to_scripthash_script(hash_hex)
        if self.is_p2sh(addr):
            return mk_scripthash_script(addr)
        elif self.is_p2pkh(addr):
            return addr_to_pubkey_script(addr)
        elif main.is_public_key(pub=addr):
            return mk_p2pk_script(addr)
        raise Exception(f"Unrecognised address: {addr}")

    def addrtoscript(self, addr: str) -> str:
        """
        Converts an output address to its corresponding script.

        This function handles various address formats, including:

        - **Native SegWit addresses:** Decodes the address and creates a P2WSH script.
        - **Cash Address:** Decodes the address and creates a P2PKH or P2SH script based on the kind.
        - **P2SH addresses:** Creates a P2SH script.
        - **P2PKH addresses:** Creates a P2PKH script.
        - **Public keys:** Creates a P2PK script.
        - **Dogecoin addresses:** Creates a P2PKH script for Dogecoin addresses.

        Args:
            addr: The output address to convert.

        Returns:
            The corresponding script(as hexadecimal string) for the provided address.

        Raises:
            Exception: If the address format is unrecognized.
        """
        from .. import main
        from .. import transaction
        from .. import py3specials

        if self.is_native_segwit(addr):
            witver, witprog = segwit_addr.decode_segwit_address(
                hrp=self.segwit_hrp, addr=addr
            )
            if witprog is not None:
                return transaction.mk_p2w_scripthash_script(
                    witver=witver, witprog=witprog
                )
        elif self.is_cash_address(addr):
            prefix, kind, hash_bin = cashaddr.decode(address=addr)
            hash_hex = py3specials.safe_hexlify(a=hash_bin)
            if kind == 0:
                return transaction.mk_pubkey_script(pubkey_hash=hash_hex)
            return transaction.hash_to_scripthash_script(hashbin=hash_hex)
        elif self.is_p2sh(addr=addr):
            return transaction.mk_scripthash_script(addr=addr)
        elif self.is_p2pkh(addr=addr):
            # return addr_to_pubkey_script(addr=addr)
            P2PKH_script_hexa_str: str = transaction.addr_to_pubkey_script(addr=addr)
            return P2PKH_script_hexa_str
        elif self.is_dogecoin_address(addr):  # Check for Dogecoin address
            # return addr_to_pubkey_script(addr=addr)  # Assuming Dogecoin uses P2PKH
            P2PKH_script_hexa_str: str = transaction.addr_to_pubkey_script(addr=addr)
            return P2PKH_script_hexa_str
        elif self.is_valid_dogecoin_or_litecoin_address(address=addr):
            # Assuming Dogecoin or litecoin uses P2PKH
            P2PKH_script_hexa_str: str = transaction.addr_to_pubkey_script(addr=addr)
            return P2PKH_script_hexa_str
        elif main.is_public_key(pub=addr):
            # return mk_p2pk_script(pub=addr)
            P2PK_script_hexa_str: str = transaction.mk_p2pk_script(pub=addr)
            return P2PK_script_hexa_str

        raise Exception(f"Unrecognised address: {addr}")

    def addrtoscripthash_original(self, addr: str) -> str:
        """
        For electrumx requests
        """
        script = self.addrtoscript(addr)
        return script_to_scripthash(script)

    def addrtoscripthash(self, addr: str) -> str:
        """
        Converts an address to its corresponding script hash for use in ElectrumX requests.

        This function takes an address (Bitcoin, Litecoin, Dogecoin, etc.) as input, converts it to its script representation,
        and then computes the script hash (scripthash) from that representation. The resulting
        scripthash can be used to query the ElectrumX server for transaction data related to
        the specified address.

        Args:
            addr (str): The address to be converted. This should be a valid base58-encoded
                        address for the supported cryptocurrency.

        Returns:
            str: The script hash (scripthash) corresponding to the provided address.
                This is a hexadecimal string that uniquely identifies the script associated with
                the address.

        Example:
            >>> scripthash = self.addrtoscripthash('1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')  # Bitcoin
            >>> print(scripthash)
            '76a914...88ac'

            >>> scripthash = self.addrtoscripthash('Ltc1q9g5z93k7v6t639g8w8g38k4n77z7h84f7v4x8')  # Litecoin
            >>> print(scripthash)
            '76a914...88ac'

            >>> scripthash = self.addrtoscripthash('D9Y75f57Y5qG36X9J4oQ7f6W2oF54p1n3')  # Dogecoin
            >>> print(scripthash)
            '76a914...88ac'

        Internal Steps:
        1. The function imports the `main` module, which contains the necessary functions for
        script conversion and hashing.
        2. It calls the `addrtoscript` method to convert the provided address into its
        hexadecimal script representation.
        3. It then calls the `script_to_scripthash` function from the `main` module, passing
        the hexadecimal script as an argument to obtain the corresponding scripthash.
        4. Finally, it returns the computed scripthash as a string.

        Note:
            Ensure that the input address is valid for the intended cryptocurrency; otherwise, the conversion may fail or return
            an incorrect result.
        """
        from .. import main

        script_hexa_str: str = self.addrtoscript(addr=addr)
        script_hexa_str_hash: str = main.script_to_scripthash(script=script_hexa_str)
        return script_hexa_str_hash

    def pubtop2wpkh_p2sh(self, pub: str) -> str:
        """
        Convert a public key to a pay to witness public key hash address
        (P2WPKH-P2SH, required for segwit)
        """
        if not self.segwit_supported:
            raise Exception("Segwit not supported for this coin")
        if len(pub) > 70:
            pub = compress(pub)
        return self.scripttoaddr(mk_p2wpkh_script(pub))

    def privtop2wpkh_p2sh_original(self, priv: PrivkeyType) -> str:
        """
        Convert a private key to a pay to witness public key hash address
        """
        result = self.pubtop2wpkh_p2sh(pub=self.privtopub(privkey=priv))
        return result

    def privtop2wpkh_p2sh(self, priv: PrivkeyType) -> str:
        """
        Converts a private key to a pay-to-witness public key hash (P2WPKH) address,
        which is then wrapped in a pay-to-script-hash (P2SH) address. This creates a
        hybrid address that offers enhanced security and efficiency compared to
        traditional P2PKH addresses.

        Args:
            priv (PrivkeyType): The private key to convert.

        Returns:
            str: The P2WPKH-P2SH address derived from the provided private key.

        Security Considerations:
            Description of P2WPKH-P2SH:

                P2WPKH (Pay-to-Witness-Public-Key-Hash)**:
                This is a type of Bitcoin address that utilizes the Segregated Witness (SegWit) protocol.
                It allows for more efficient transactions by separating the signature data
                from the transaction data,
                which reduces the size of transactions and lowers fees. P2WPKH addresses start with
                the prefix `bc1q`.

            Example:
                bc1qxxxxx... P2SH (Pay-to-Script-Hash)**:

                    This is a Bitcoin address format that allows for more
                    complex scripts to be used for spending funds.
                    P2SH addresses start with the prefix `3` and enable the use
                    of multi-signature wallets and other advanced features.
                    By wrapping a P2WPKH address in a P2SH address, it provides
                    an additional layer of security and compatibility with legacy systems.

            Example:
                3xxxxx... P2WPKH-P2SH**:

                    This is a hybrid address format that combines the benefits of both P2WPKH and P2SH.
                    It offers the efficiency of SegWit (P2WPKH) while maintaining
                    compatibility with legacy systems (P2SH).
                    Essentially, the P2WPKH address is embedded within a P2SH
                    address, creating a single address that can be used with both SegWit
                    and non-SegWit wallets.

            Example:
                3xxxxx...:
                    (This address actually represents a P2WPKH address wrapped in a P2SH address)

            Benefits of P2WPKH-P2SH:
                1. Enhanced Security:
                    The P2SH wrapper conceals the underlying P2WPKH script,
                    making it more difficult for attackers to target the address directly.
                2. Lower Transaction Fees:
                    By utilizing SegWit, transactions can be smaller in size, leading to reduced fees.
                3. Compatibility:
                    P2WPKH-P2SH addresses can be used with wallets that
                    do not support native SegWit, ensuring broader usability.

            Security Considerations:

                Private Key Management:
                    It is crucial to store your private key securely.
                    Use hardware wallets or secure software wallets that provide
                    strong encryption. Never share your private key with anyone,
                    as its compromise can lead to loss of funds.

                Address Handling:
                    When handling the resulting P2WPKH-P2SH address:
                    - **Do not expose the address publicly** unless necessary.
                        If you must share it, ensure that it is done securely.
                    - **Monitor transactions** associated with the address regularly
                        to detect any unauthorized activity.
                    - **Use multi-signature wallets** if possible, as they
                        require multiple private keys to authorize a transaction, enhancing security.

                Backup Procedures:
                    Regularly back up your wallet and private keys in a secure manner.
                    Consider using encrypted backups stored in multiple locations to prevent loss.

                Be Aware of Phishing Attacks:
                    Always verify the authenticity of any service or application
                    requesting your private key or address.
                    Phishing attacks can lead to unauthorized access to your funds.

                P2WPKH-P2SH:
                    addresses provide improved security by leveraging the
                    segwit (Segregated Witness) feature of Bitcoin. This separates the witness
                    data (signature and public key) from the transaction script, reducing
                    transaction size and improving efficiency.
                The P2SH wrapper:
                    further enhances security by hiding the underlying
                    P2WPKH script, making it more difficult for attackers to target the
                    address directly.
                It's crucial to store your private key securely and never share it with
                anyone. If your private key is compromised, an attacker could gain control
                of the associated funds.
                P2WPKH-P2SH addresses:
                    provide improved security by leveraging the
                    segwit (Segregated Witness) feature of Bitcoin. This separates the witness
                    data (signature and public key) from the transaction script, reducing
                    transaction size and improving efficiency.
                The P2SH wrapper:
                    further enhances security by hiding the underlying
                    P2WPKH script, making it more difficult for attackers to target the
                    address directly.
                It's crucial to store your private key securely and never share it with
                anyone. If your private key is compromised, an attacker could gain control
                of the associated funds.
        """
        result = self.pubtop2wpkh_p2sh(pub=self.privtopub(privkey=priv))
        return result

    def hash_to_segwit_addr(self, pub_hash: AnyStr) -> str:
        """
        Convert a hash to the native segwit address format outlined in BIP-0173
        """
        if not self.segwit_supported:
            raise NotImplementedError(f"{self.display_name} does not support segwit")
        return segwit_addr.encode_segwit_address(self.segwit_hrp, 0, pub_hash)

    def scripthash_to_segwit_addr(self, script_hash: AnyStr) -> str:
        """
        Convert a script hash to the native segwit address format
        """
        if not self.segwit_supported:
            raise NotImplementedError(f"{self.display_name} does not support segwit")
        return segwit_addr.encode_segwit_address(self.segwit_hrp, 0, script_hash)

    def hash_to_cash_addr(self, pub_hash: AnyStr) -> str:
        """
        Convert a hash to a cash address
        """
        if not self.cash_address_supported:
            raise NotImplementedError(
                f"{self.display_name} does not support cash addresses"
            )
        return cashaddr.encode_full(self.cash_hrp, cashaddr.PUBKEY_TYPE, pub_hash)

    def privtosegwitaddress(self, privkey: PrivkeyType) -> str:
        """
        Convert a private key to the new segwit address(public address) format outlined in BIP01743
        """
        return self.pubtosegwitaddress(self.privtopub(privkey=privkey))

    def pubtocashaddress(self, pubkey: str) -> str:
        """
        Convert a public key to a cash address
        """
        from .. import main

        return self.hash_to_cash_addr(main.pubkey_to_hash(pubkey))

    def privtocashaddress(self, privkey: PrivkeyType) -> str:
        """
        Convert a private key to a cash address
        """
        return self.pubtocashaddress(self.privtopub(privkey=privkey))

    def legacy_addr_to_cash_address(self, addr: str) -> str:
        """
        Convert a legacy Bitcoin Address to a Bitcoin cash address
        """
        magicbyte, pubkey_hash = b58check_to_bin(addr)
        if magicbyte == self.magicbyte:
            return self.hash_to_cash_addr(pubkey_hash)
        elif magicbyte == self.script_magicbyte:
            return self.scripthash_to_cash_addr(pubkey_hash)
        else:
            raise Exception(f"Magic Byte {magicbyte} not recognised")

    def cash_address_to_legacy_addr(self, addr: str) -> str:
        """
        Convert a Bitcoin cash address to a legacy Bitcoin address
        """
        prefix, kind, pubkey_hash = cashaddr.decode(addr)
        if kind == 0:
            return bin_to_b58check(pubkey_hash, self.magicbyte)
        return bin_to_b58check(pubkey_hash, self.script_magicbyte)

    def pubtosegwitaddress_original(self, pubkey: str) -> str:
        """
        Convert a public key to the new segwit address format outlined in BIP01743
        """
        from ..main import pubkey_to_hash, compress

        return self.hash_to_segwit_addr(pubkey_to_hash(compress(pubkey)))

    def pubtosegwitaddress(self, pubkey: str) -> str:
        """
        Convert a public key to the new segwit address format outlined in BIP01743
        """
        from .. import main

        pubkey_compressed: str = main.compress(pubkey=pubkey)
        pubkey_hash160_bytes: bytes = main.pubkey_to_hash(pubkey=pubkey_compressed)
        return self.hash_to_segwit_addr(
            pub_hash=main.pubkey_to_hash(pubkey=main.compress(pubkey=pubkey))
        )

    def mk_multisig_address(
        self, *args: str, num_required: int = None
    ) -> Tuple[str, str]:
        """
        :param args: List of public keys to used to create multisig
        :param num_required: The number of signatures required to spend (defaults to number of public keys provided)
        :return: multisig script
        """
        num_required = num_required or len(args)
        script = mk_multisig_script(*args, num_required)
        address = self.p2sh_scriptaddr(script)
        return script, address

    def mk_multsig_segwit_address(
        self, *args: str, num_required: int = None
    ) -> Tuple[str, str]:
        num_required = num_required or len(args)
        pubs = [compress(pub) for pub in args]
        script = mk_multisig_script(*pubs, num_required)
        address = self.p2sh_segwit_addr(script)
        return script, address

    def mk_multsig_cash_address(
        self, *args: str, num_required: int = None
    ) -> Tuple[str, str]:
        num_required = num_required or len(args)
        script = mk_multisig_script(*args, num_required)
        address = self.p2sh_cash_addr(script)
        return script, address

    def apply_multisignatures(self, txobj: Tx, i: int, script, *args):
        inp = txobj["ins"][i]
        segwit = False
        try:
            if address := inp["address"]:
                segwit = self.is_native_segwit(address)
        except (IndexError, KeyError):
            pass
        return apply_multisignatures(txobj, i, script, *args, segwit=segwit)

    def sign_original(self, txobj: Union[Tx, AnyStr], i: int, priv: PrivkeyType) -> Tx:
        """
        Sign a transaction input with index using a private key
        """
        if not isinstance(txobj, dict):
            txobj = deserialize(txobj)
        if len(priv) <= 33:
            priv = safe_hexlify(priv)
        pub = self.privtopub(privkey=priv)
        inp = txobj["ins"][i]
        p2pk = False
        segwit = False
        native_segwit = False
        try:
            if address := inp["address"]:
                segwit = native_segwit = self.is_native_segwit(address)
                segwit = segwit or self.maybe_legacy_segwit(address)
                if segwit:
                    pub = compress(pub)
                elif len(address) in [66, 130]:
                    pub = address
                    p2pk = True
        except (IndexError, KeyError):
            pass
        if segwit:
            if "witness" not in txobj.keys():
                txobj.update({"marker": 0, "flag": 1, "witness": []})
                for _ in range(0, i):
                    witness: Witness = {"number": 0, "scriptCode": ""}
                    # Pycharm IDE gives a type error for the following line, no idea why...
                    # noinspection PyTypeChecker
                    txobj["witness"].append(witness)
            script = mk_p2wpkh_scriptcode(pub)
            signing_tx = signature_form(txobj, i, script, self.hashcode, segwit=True)
            sig = ecdsa_tx_sign(signing_tx, priv, self.secondary_hashcode)
            if native_segwit:
                txobj["ins"][i]["script"] = ""
            else:
                txobj["ins"][i]["script"] = mk_p2wpkh_redeemscript(pub)
            witness: Witness = {
                "number": 2,
                "scriptCode": serialize_script([sig, pub]),
            }
            # Pycharm IDE gives a type error for the following line, no idea why...
            # noinspection PyTypeChecker
            txobj["witness"].append(witness)
        else:
            if p2pk:
                script = mk_p2pk_script(pub)
            else:
                address = self.pubtoaddr(pub)
                script = addr_to_pubkey_script(address)
            signing_tx = signature_form(txobj, i, script, self.hashcode)
            sig = ecdsa_tx_sign(signing_tx, priv, self.hashcode)
            # Pycharm IDE gives a type error for the following line, no idea why...
            # noinspection PyTypeChecker
            script = serialize_script([sig]) if p2pk else serialize_script([sig, pub])
            txobj["ins"][i]["script"] = script
            if "witness" in txobj.keys():
                witness: Witness = {"number": 0, "scriptCode": ""}
                # Pycharm IDE gives a type error for the following line, no idea why...
                # noinspection PyTypeChecker
                txobj["witness"].append(witness)
        return txobj

    def sign(
        self,
        txobj: Union[Tx, AnyStr],
        i: int,
        priv: PrivkeyType,
    ) -> Tx:
        """
        Sign a transaction input with index using a private key
        """
        from .. import transaction
        from .. import py3specials
        from .. import main

        if not isinstance(txobj, dict):
            txobj = transaction.deserialize(tx=txobj)
        if len(priv) <= 33:
            priv = py3specials.safe_hexlify(a=priv)
        pub = self.privtopub(privkey=priv)
        inp = txobj["ins"][i]
        p2pk = False
        segwit = False
        native_segwit = False
        try:
            if address := inp["address"]:
                segwit = native_segwit = self.is_native_segwit(addr=address)
                segwit = segwit or self.maybe_legacy_segwit(addr=address)
                if segwit:
                    pub = main.compress(pubkey=pub)
                elif len(address) in [66, 130]:
                    pub = address
                    p2pk = True
        except (IndexError, KeyError):
            pass
        if segwit:
            if "witness" not in txobj.keys():
                txobj.update({"marker": 0, "flag": 1, "witness": []})
                for _ in range(0, i):
                    witness: Witness = {"number": 0, "scriptCode": ""}
                    # Pycharm IDE gives a type error for the following line, no idea why...
                    # noinspection PyTypeChecker
                    txobj["witness"].append(witness)
            script = mk_p2wpkh_scriptcode(pub)
            signing_tx = signature_form(txobj, i, script, self.hashcode, segwit=True)
            sig = ecdsa_tx_sign(signing_tx, priv, self.secondary_hashcode)
            if native_segwit:
                txobj["ins"][i]["script"] = ""
            else:
                txobj["ins"][i]["script"] = mk_p2wpkh_redeemscript(pub)
            witness: Witness = {
                "number": 2,
                "scriptCode": serialize_script([sig, pub]),
            }
            # Pycharm IDE gives a type error for the following line, no idea why...
            # noinspection PyTypeChecker
            txobj["witness"].append(witness)
        else:
            if p2pk:
                script = mk_p2pk_script(pub=pub)
            else:
                address = self.pubtoaddr(pubkey=pub)
                script = addr_to_pubkey_script(addr=address)
            signing_tx = signature_form(
                tx=txobj,
                i=i,
                script=script,
                hashcode=self.hashcode,
            )
            sig: str = ecdsa_tx_sign(
                tx=signing_tx,
                priv=priv,
                hashcode=self.hashcode,
            )
            # Pycharm IDE gives a type error for the following line, no idea why...
            # noinspection PyTypeChecker
            script = serialize_script([sig]) if p2pk else serialize_script([sig, pub])
            txobj["ins"][i]["script"] = script
            if "witness" in txobj.keys():
                witness: Witness = {"number": 0, "scriptCode": ""}
                # Pycharm IDE gives a type error for the following line, no idea why...
                # noinspection PyTypeChecker
                txobj["witness"].append(witness)
        return txobj

    def signall_original(
        self, txobj: Union[str, Tx], priv: PrivateKeySignAllType
    ) -> Tx:
        """
        Sign all inputs to a transaction using a private key.
        Priv is either a private key or a dictionary of address keys and private key values
        """
        if not isinstance(txobj, dict):
            txobj = deserialize(txobj)
        if isinstance(priv, dict):
            for i, inp in enumerate(txobj["ins"]):
                addr = inp["address"]
                k = priv[addr]
                txobj = self.sign(txobj, i, k)
        else:
            for i in range(len(txobj["ins"])):
                txobj = self.sign(txobj, i, priv)
        return txobj

    # def signall(
    #     self,
    #     txobj: Union[str, Tx],
    #     priv: PrivateKeySignAllType,
    # ) -> Tx:
    #     """
    #     Sign all inputs to a transaction using a private key.
    #     Priv is either a private key or a dictionary of address keys and private key values
    #     """
    #     if not isinstance(txobj, dict):
    #         txobj = deserialize(tx=txobj)
    #     if isinstance(priv, dict):
    #         for i, inp in enumerate(txobj["ins"]):
    #             addr = inp["address"]
    #             k = priv[addr]
    #             txobj = self.sign(txobj=txobj, i=i, priv=k)
    #     else:
    #         for i in range(len(txobj["ins"])):
    #             txobj = self.sign(txobj=txobj, i=i, priv=priv)
    #     return txobj

    def signall(
        self,
        txobj: Union[str, Tx],
        priv: PrivateKeySignAllType,
    ) -> Tx:
        """
        Signs all inputs of a transaction using a private key.

        Args:
            self: The instance of the class calling this method.
            txobj: The transaction object or its serialized representation as a string.
            priv: The private key to use for signing. It can be either a single private key or a dictionary where keys are addresses and values are corresponding private keys.

        Returns:
            Tx: The signed transaction object.

        Raises:
            None.

        Notes:
            This function iterates through each input of the transaction and
            calls the `self.sign` method to sign the input using the provided private key.
            If `priv` is a dictionary, it uses the private key associated
            with the address of the input.
        """
        if not isinstance(txobj, dict):
            txobj = deserialize(tx=txobj)
        if isinstance(priv, dict):
            for i, inp in enumerate(txobj["ins"]):
                addr: str = inp["address"]
                k: str = priv[addr]
                txobj = self.sign(txobj=txobj, i=i, priv=k)
        else:
            for i in range(len(txobj["ins"])):
                txobj = self.sign(txobj=txobj, i=i, priv=priv)
        return txobj

    def multisign(
        self, txobj: Union[str, Tx], i: int, script: str, priv: PrivkeyType
    ) -> Tx:
        i = int(i)
        if not isinstance(txobj, dict):
            txobj = deserialize(txobj)
        if len(priv) <= 33:
            priv = safe_hexlify(priv)
        inp = txobj["ins"][i]
        segwit = False
        try:
            if address := inp["address"]:
                segwit = self.is_native_segwit(address)
        except (IndexError, KeyError):
            pass
        return multisign(txobj, i, script, priv, self.hashcode, segwit=segwit)

    def mktx(
        self,
        ins: List[Union[TxInput, AnyStr]],
        outs: List[Union[TxOut, AnyStr]],
        locktime: int = 0,
        sequence: int = 0xFFFFFFFF,
    ) -> Tx:
        """[in0, in1...],[out0, out1...]

        Make an unsigned transaction from inputs and outputs. Change is
        not automatically included so any difference
        in value between inputs and outputs will be given as a miner's fee
        (transactions with too high fees will
        normally be blocked by Electrumx)

        Ins and outs are both lists of dicts.
        """

        txobj = {"locktime": locktime, "version": 1}
        inp: TxInput  # = None  # ()enherets from TypedDict

        for i, inp in enumerate(ins):
            if isinstance(inp, string_or_bytes_types):
                real_inp: TxInput = {"tx_hash": inp[:64], "tx_pos": int(inp[65:])}
                ins[i] = real_inp
                inp = real_inp
            elif inp_out := inp.pop("output", None):
                tx_info: TxInput = {
                    "tx_hash": inp_out[:64],
                    "tx_pos": int(inp_out[65:]),
                }
                inp.update(tx_info)
            if address := inp.get("address", ""):
                if self.segwit_supported and self.is_native_segwit(address):
                    txobj.update({"marker": 0, "flag": 1, "witness": []})
            inp.update({"script": "", "sequence": int(inp.get("sequence", sequence))})
        # out: TxOut
        for i, out in enumerate(outs):
            if isinstance(out, string_or_bytes_types):
                o = out
                addr = o[: o.find(":")]
                val = int(o[o.find(":") + 1 :])
                out = {}
                if is_hex(addr):
                    out["script"] = addr
                else:
                    out["address"] = addr
                out["value"] = val
                outs[i] = out
            if address := out.pop("address", None):
                out["script"] = self.addrtoscript(address)
            elif "script" not in out.keys():
                raise Exception("Could not find 'address' or 'script' in output.")
        txobj.update({"ins": ins, "outs": outs})
        return txobj

    async def mktx_with_change_original(
        self,
        ins: List[Union[TxInput, AnyStr, ElectrumXTx]],
        outs: List[Union[TxOut, AnyStr]],
        change_addr: str = None,
        fee: int = None,
        estimate_fee_blocks: int = 6,
        locktime: int = 0,
        sequence: int = 0xFFFFFFFF,
    ) -> Tx:
        """[in0, in1...],[out0, out1...]

        Make an unsigned transaction from inputs, outputs change address and fee. A change output will be added with
        change sent to the change address..
        """
        change_addr = change_addr or ins[0]["address"]
        isum = sum(inp["value"] for inp in ins)
        osum = sum(out["value"] for out in outs)
        change_out = {"address": change_addr, "value": isum - osum}
        outs += [change_out]
        txobj = self.mktx(ins, outs, locktime=locktime, sequence=sequence)

        if fee is None:
            fee = max(
                await self.estimate_fee(txobj, numblocks=estimate_fee_blocks),
                self.minimum_fee,
            )
        if isum < osum + fee:
            raise Exception(
                f"Not enough money. You have {isum} but need {osum+fee} ({osum} + fee of {fee})."
            )

        if change_out["value"] > fee:
            change_out["value"] = isum - osum - fee
        else:
            outs.remove(change_out)

        return txobj

    async def mktx_with_change(
        self,
        ins: List[Union[TxInput, AnyStr, ElectrumXTx]],
        outs: List[Union[TxOut, AnyStr]],
        change_addr: str = None,
        fee: int = None,
        estimate_fee_blocks: int = 6,
        locktime: int = 0,
        sequence: int = 0xFFFFFFFF,
    ) -> Tx:
        """
        Creates an unsigned transaction with change output
        (change is the addres where the remaining coins are sent to).


        This function takes a list of inputs, outputs, a change address, and an optional fee.
        It calculates the change amount and adds a change output to the transaction.
        If no fee is provided, it estimates the fee based on the provided block count.
        The function ensures that the total input value is sufficient to cover the outputs and the fee.

        Args:
            ins (List[Union[TxInput, AnyStr, ElectrumXTx]]): List of transaction inputs.
            outs (List[Union[TxOut, AnyStr]]): List of transaction outputs.
            change_addr (str, optional): The address for the change output. Defaults to the first input address.
            fee (int, optional): The transaction fee in satoshis. If None, it will be estimated. Defaults to None.
            estimate_fee_blocks (int, optional): Number of blocks to use for fee estimation. Defaults to 6.
            locktime (int, optional): The transaction locktime. Defaults to 0.
            sequence (int, optional): The transaction sequence number. Defaults to 0xFFFFFFFF.

        Returns:
            Tx: The unsigned transaction object.

        Raises:
            Exception: If the total input value is insufficient to cover the outputs and the fee.
        """
        change_addr: str = change_addr or ins[0]["address"]
        isum: int = sum(inp["value"] for inp in ins)
        osum: int = sum(out["value"] for out in outs)
        change_out: dict = {"address": change_addr, "value": isum - osum}
        outs += [change_out]
        txobj: Tx = self.mktx(
            ins=ins,
            outs=outs,
            locktime=locktime,
            sequence=sequence,
        )

        if fee is None:
            fee: int = max(
                await self.estimate_fee(txobj, numblocks=estimate_fee_blocks),
                self.minimum_fee,
            )
        if isum < osum + fee:
            raise Exception(
                f"Not enough money. You have {isum} but need {osum+fee} ({osum} + fee of {fee})."
            )

        if change_out["value"] > fee:
            change_out["value"] = isum - osum - fee
        else:
            outs.remove(change_out)

        return txobj

    async def preparemultitx_original(
        self,
        frm: str,
        outs: List[TxOut],
        change_addr: str = None,
        fee: int = None,
        estimate_fee_blocks: int = 6,
    ) -> Tx:
        """
        Prepare transaction with multiple outputs, with change sent to from address
        """
        outvalue = int(sum(out["value"] for out in outs))
        unspents = await self.unspent(frm)
        if fee is None:
            unspents2 = select(unspents, outvalue)
            tx = await self.mktx_with_change(
                unspents2, deepcopy(outs), fee=0, change_addr=change_addr
            )
            fee = max(
                await self.estimate_fee(tx, estimate_fee_blocks), self.minimum_fee
            )
        unspents2 = select(unspents, outvalue + fee)
        change_addr = change_addr or frm
        return await self.mktx_with_change(
            unspents2,
            outs,
            fee=fee,
            change_addr=change_addr,
            estimate_fee_blocks=estimate_fee_blocks,
        )

    async def preparemultitx(
        self,
        frm: str,
        outs: List[TxOut],
        change_addr: str = None,
        fee: int = None,
        estimate_fee_blocks: int = 6,
    ) -> Tx:
        """
        Prepares a transaction with multiple outputs,
        sending funds to different addresses,
        and calculates an appropriate fee.

        Args:
            frm (str): The address of the sender.
            outs (List[TxOut]): A list of output objects, each specifying a recipient address and value.
            change_addr (str, optional): The address to send any remaining change to. If not provided, change will be sent back to the `frm` address. Defaults to None.
            fee (int, optional): The desired transaction fee in satoshis. If not provided, the fee will be estimated based on the `estimate_fee_blocks` parameter. Defaults to None.
            estimate_fee_blocks (int, optional): The number of blocks to consider when estimating the fee. Defaults to 6.

        Returns:
            Tx: The prepared unsigned transaction object.

        Example:
            >>> outs = [{"address": "bc1q...", "value": 100000}, {"address": "bc1p...", "value": 50000}]
            >>> await preparemultitx(frm='bc1q...', outs=outs, fee=1500)
            <Tx object>

        **Detailed Explanation:**

            **1. Calculate Total Output Value:**
                The function first calculates the total value of all outputs
                (`outvalue`) by summing the values in the `outs` list.

            **2. Retrieve Unspent Outputs:**
                It then fetches a list of unspent outputs
                (`unspents`) associated with the sender's
                address (`frm`).(getting the addresses account balance)

            **3. Fee Estimation (If Necessary):**
                - If a `fee` is not provided, the function estimates the fee based
                    on the `estimate_fee_blocks` parameter.
                - It selects a subset of unspent outputs (`unspents2`)
                    sufficient to cover the total output value (`outvalue`).
                - A preliminary transaction is created (`tx`) without a fee,
                    and the estimated fee is calculated using
                    `self.estimate_fee()`.
                - The final fee is set to the maximum of the estimated fee and
                    the minimum fee (`self.minimum_fee`).

            **4. Select Unspent Outputs:**
                The function selects a subset of unspent outputs
                (`unspents2`) sufficient to cover both
                the total output value (`outvalue`)
                and the calculated fee.

            **5. Create Transaction with Change:**
                Finally, the function uses `self.mktx_with_change()`
                to create the transaction with the specified outputs,
                fee, and change address. The `change_addr`
                is set to either the provided `change_addr`
                or the `frm` address if none is specified.

                - The function uses `self.mktx_with_change()`
                    to construct the final transaction.
                - This method takes the selected unspent outputs
                    (`unspents2`), the list of outputs (`outs`),
                    the calculated fee, and the change address as input.
                - It creates a transaction object (`Tx`) that includes:
                    - The inputs from the selected unspent outputs.
                    - The specified outputs (recipient addresses and values).
                    - The calculated transaction fee.
                    - A change output, if necessary. The change output
                        sends any remaining funds back to the `change_addr`.
                - The `change_addr` is determined as follows:
                    - If a `change_addr` is provided as an argument, it is used directly.
                    - If no `change_addr` is provided, the sender's address (`frm`) is used as the change address.

            - **The change address is crucial for preventing funds from being lost.**
                - The `change_addr` is determined as follows:
                    - If `a` `change_addr` is provided as an argument, it is used directly.
                    - If `no` `change_addr` is provided, the sender's address (`frm`) is used as the `change address`.

                If the total value of the outputs and the fee is
                less than the total value of the selected unspent outputs,
                the remaining funds are sent to the change address.
                **Important:**
                    `Without a change address, these funds would be lost.`


        **Key Points:**

        - **Multi-Output Transactions:**
            This function handles transactions with multiple outputs,
            allowing for sending funds to different addresses
            in a single transaction.
        - **Dynamic Fee Calculation:**
            The function dynamically calculates an appropriate fee,
            either based on a provided value or by estimating the
            fee using the provided `estimate_fee_blocks` parameter.
        - **Change Handling:**
            The function ensures that any remaining funds after
            covering the outputs and fee are sent back to the sender's
            address or a specified change address.

        """
        outvalue: int = int(sum(out["value"] for out in outs))
        available_unspents: ElectrumXUnspentResponse = await self.unspent(
            addr=frm
        )  # List[ElectrumXTx]
        if len(available_unspents) == 0:
            print(f"no available_unspents for address: {frm}")
            return None
        if fee is None:
            unspents_to_cover_outvalue: List[Dict[str, int]] = select(
                unspents=available_unspents,
                value=outvalue,
            )
            tx = await self.mktx_with_change(
                ins=unspents_to_cover_outvalue,
                outs=deepcopy(x=outs),
                fee=0,
                change_addr=change_addr,
            )
            fee = max(
                await self.estimate_fee(txobj=tx, numblocks=estimate_fee_blocks),
                self.minimum_fee,
            )
        unspents_cover_outvalue_and_Fee = select(
            unspents=available_unspents,
            value=outvalue + fee,
        )
        change_addr = change_addr or frm
        unsigned_transaction_with_change_output: Tx = await self.mktx_with_change(
            ins=unspents_cover_outvalue_and_Fee,
            outs=outs,
            change_addr=change_addr,
            fee=fee,
            estimate_fee_blocks=estimate_fee_blocks,
        )
        return unsigned_transaction_with_change_output

    async def preparetx_original(
        self,
        frm: str,
        to: str,
        value: int,
        fee: int = None,
        estimate_fee_blocks: int = 6,
        change_addr: str = None,
    ) -> Tx:
        """
        Prepare a transaction using from and to addresses, value and a fee, with change sent back to from address
        """
        outs: List[TxOut] = [{"address": to, "value": value}]
        return await self.preparemultitx(
            frm,
            outs,
            fee=fee,
            estimate_fee_blocks=estimate_fee_blocks,
            change_addr=change_addr,
        )

    async def preparetx(
        self,
        frm: str,
        to: str,
        value: int,
        fee: int = None,
        estimate_fee_blocks: int = 6,
        change_addr: str = None,
    ) -> Tx:
        """
        Prepares a transaction with a single output,
        sending a specified value to a designated address.

        Args:
            frm (str): The address of the sender.
            to (str): The address of the recipient.
            value (int): The amount of value to send, in satoshis(atomic value).
            fee (int, optional): The desired transaction fee in satoshis. If not provided, the fee will be estimated based on the `estimate_fee_blocks` parameter. Defaults to None.
            estimate_fee_blocks (int, optional): The number of blocks to consider when estimating the fee. Defaults to 6.
            change_addr (str, optional): The address to send any remaining change to. If not provided, change will be sent back to the `frm` address. Defaults to None.

        Returns:
            Tx: The prepared transaction object.

        Example:
            >>> await preparetx(frm='bc1q...', to='bc1p...', value=100000, fee=1000)
            <Tx object>
        """
        outs: List[TxOut] = [{"address": to, "value": value}]
        tx: Tx = await self.preparemultitx(
            frm=frm,
            outs=outs,
            fee=fee,
            estimate_fee_blocks=estimate_fee_blocks,
            change_addr=change_addr,
        )

        return tx

    async def preparesignedmultirecipienttx(
        self,
        privkey: PrivateKeySignAllType,
        frm: str,
        outs: List[TxOut],
        change_addr: str = None,
        fee: int = None,
        estimate_fee_blocks: int = 6,
    ) -> Tx:
        """
        Prepare transaction with multiple outputs, with change sent back to from address or given change_addr
        Requires private key, address:value pairs and optionally the change address and fee
        segwit paramater specifies that the inputs belong to a segwit address
        addr, if provided, will explicity set the from address, overriding the auto-detection of the address from the
        private key.It will also be used, along with the privkey to automatically detect a segwit transaction for coins
        which support segwit, overriding the segwit kw
        """
        tx = await self.preparemultitx(
            frm,
            outs,
            fee=fee,
            change_addr=change_addr,
            estimate_fee_blocks=estimate_fee_blocks,
        )
        tx2 = self.signall(tx, privkey)
        return tx2

    async def preparesignedtx(
        self,
        privkey: PrivateKeySignAllType,
        frm: str,
        to: str,
        value: int,
        change_addr: str = None,
        fee: int = None,
        estimate_fee_blocks: int = 6,
    ) -> Tx:
        """
        Prepare a tx with a specific amount from address belonging to private key to another address, returning change
        to the from address or change address, if set.
        Requires private key, target address, value and optionally the change address and fee
        segwit paramater specifies that the inputs belong to a segwit address
        addr, if provided, will explicity set the from address, overriding the auto-detection of the address from the
        private key.It will also be used, along with the privkey, to automatically detect a segwit transaction for
        coins which support segwit, overriding the segwit kw
        """
        outs = [{"address": to, "value": value}]
        return await self.preparesignedmultirecipienttx(
            privkey,
            frm,
            outs,
            change_addr=change_addr,
            fee=fee,
            estimate_fee_blocks=estimate_fee_blocks,
        )

    async def send_to_multiple_receivers_tx(
        self,
        privkey: PrivateKeySignAllType,
        addr: str,
        outs: List[TxOut],
        change_addr: str = None,
        fee: int = None,
        estimate_fee_blocks: int = 6,
    ):
        """
        Send transaction with multiple outputs, with change sent back to from addrss
        Requires private key, address:value pairs and optionally the change address and fee
        segwit paramater specifies that the inputs belong to a segwit address
        addr, if provided, will explicity set the from address, overriding the auto-detection of the address from the
        private key.It will also be used, along with the privkey to automatically detect a segwit transaction for
        coins which support segwit, overriding the segwit kw
        """
        tx = await self.preparesignedmultirecipienttx(
            privkey,
            addr,
            outs,
            change_addr=change_addr,
            fee=fee,
            estimate_fee_blocks=estimate_fee_blocks,
        )
        return await self.pushtx(tx)

    async def send(
        self,
        privkey: PrivateKeySignAllType,
        frm: str,
        to: str,
        value: int,
        change_addr: str = None,
        fee: int = None,
        estimate_fee_blocks: int = 6,
    ):
        """
        Send a specific amount from address belonging to private key to another address, returning change to the
        from address or change address, if set.
        Requires private key, target address, value and optionally the change address and fee
        segwit paramater specifies that the inputs belong to a segwit address
        addr, if provided, will explicity set the from address, overriding the auto-detection of the address from the
        private key.It will also be used, along with the privkey, to automatically detect a segwit transaction for
        coins which support segwit, overriding the segwit kw
        """
        outs = [{"address": to, "value": value}]
        return await self.send_to_multiple_receivers_tx(
            privkey,
            frm,
            outs,
            change_addr=change_addr,
            fee=fee,
            estimate_fee_blocks=estimate_fee_blocks,
        )

    async def inspect(self, tx: Union[str, Tx]) -> TXInspectType:
        if not isinstance(tx, dict):
            tx = deserialize(tx)
        isum = 0
        ins = {}
        for _in in tx["ins"]:
            h = _in["tx_hash"]
            i = _in["tx_pos"]
            prevout = (await anext(self.get_txs(h)))["outs"][i]
            isum += prevout["value"]
            a = self.scripttoaddr(prevout["script"])
            ins[a] = ins.get(a, 0) + prevout["value"]
        outs = []
        osum = 0
        for _out in tx["outs"]:
            outs.append(
                {
                    "address": self.scripttoaddr(_out["script"]),
                    "value": _out["value"],
                }
            )
            osum += _out["value"]
        return {"fee": isum - osum, "outs": outs, "ins": ins}

    async def inspect_2(self, tx: Union[str, Tx]) -> TXInspectType:
        if not isinstance(tx, dict):
            tx = deserialize(tx)
        isum = 0
        ins = {}
        for _in in tx["ins"]:
            h = _in["tx_hash"]
            i = _in["tx_pos"]
            prevout = (await anext(self.get_txs(h)))["outs"][i]
            isum += prevout["value"]
            a = self.scripttoaddr(prevout["script"])
            ins[a] = ins.get(a, 0) + prevout["value"]
        outs = []
        osum = 0
        for _out in tx["outs"]:
            outs.append(
                {
                    "address": self.scripttoaddr(_out["script"]),
                    "value": _out["value"],
                }
            )
            osum += _out["value"]
        return {"fee": isum - osum, "outs": outs, "ins": ins}

    async def wait_unspents_changed(
        self, addr: str, start_unspents: ElectrumXUnspentResponse
    ):
        unspents = start_unspents
        while unspents == start_unspents:
            unspents = await self.unspent(addr)
            if start_unspents == unspents:
                await asyncio.sleep(1)

    def wallet_original(
        self,
        seed: str,
        passphrase: str = None,
        **kwargs,
    ) -> HDWallet:
        if not bip39_is_checksum_valid(mnemonic=seed) == (True, True):
            raise Exception("BIP39 Checksum failed. This is not a valid BIP39 seed")
        ks = standard_from_bip39_seed(seed, passphrase, coin=self)
        return HDWallet(ks, **kwargs)

    def wallet(
        self,
        seed: str,
        passphrase: Optional[str] = None,
        **kwargs: Dict,
    ) -> HDWallet:
        """
        Creates an HDWallet ((HD)=hierarchical deterministic) object from a BIP39 seed.

        This function validates the provided BIP39 seed, generates
        a BIP32 keystore using the seed and passphrase,
        and returns an HDWallet object initialized with the keystore.

        Args:
            seed (str): The BIP39 mnemonic seed phrase.
            passphrase (str, optional): An optional passphrase to use for seed derivation. Defaults to None.
            **kwargs (Dict): Additional keyword arguments to pass to the HDWallet constructor.

        Returns:
            HDWallet: An HDWallet((HD)=hierarchical deterministic) object initialized with the keystore derived from the BIP39 seed.

        Raises:
            Exception: If the provided seed fails BIP39 checksum validation.
        """
        if not bip39_is_checksum_valid(mnemonic=seed) == (True, True):
            raise Exception("BIP39 Checksum failed. This is not a valid BIP39 seed")
        keystore: BIP32_KeyStore = standard_from_bip39_seed(
            seed=seed,
            passphrase=passphrase,
            coin=self,
        )
        wallet: HDWallet = HDWallet(keystore=keystore, **kwargs)
        return wallet

    def watch_wallet_original(self, xpub, **kwargs) -> HDWallet:
        ks = from_xpub(xpub, self, "p2pkh")
        return HDWallet(ks, **kwargs)

    def watch_wallet(self, xpub: str, **kwargs: Dict) -> HDWallet:
        """
        Creates a watched HDWallet object from an extended public key (xpub).

        An **extended public key (xpub)** is:
            a key used in hierarchical
            deterministic (HD) wallets,
            which allows for the generation of multiple
            public keys from a single master key.
            The xpub is derived from the master private
            key and can be shared without compromising the
            security of the wallet. This means that you can
            generate an unlimited number of public addresses
            for receiving funds without exposing your private keys.

            This method allows you to watch a wallet without having the private keys.
            You can use this to view balances, transactions, and other
            information related to the wallet. The xpub is particularly
            useful for tracking funds across multiple addresses,
            as it enables the wallet to derive all associated public keys.

        Args:
            xpub: The extended public key (xpub) of the wallet to watch.
            **kwargs: Additional keyword arguments to pass to the HDWallet constructor.

        Returns:
            HDWallet: The watched HDWallet (Hierarchical Deterministic) object.
        """
        keystore: BIP32_KeyStore = from_xpub(
            xpub=xpub,
            coin=self,
            xtype="p2pkh",
        )
        hd_wallet: HDWallet = HDWallet(keystore=keystore, **kwargs)
        return hd_wallet

    def p2wpkh_p2sh_wallet(
        self, seed: str, passphrase: str = None, **kwargs
    ) -> HDWallet:
        if not self.segwit_supported:
            raise Exception("P2WPKH-P2SH segwit not enabled for this coin")
        if not bip39_is_checksum_valid(seed) == (True, True):
            raise Exception("BIP39 Checksum failed. This is not a valid BIP39 seed")
        ks = p2wpkh_p2sh_from_bip39_seed(seed, passphrase, coin=self)
        return HDWallet(ks, **kwargs)

    def watch_p2wpkh_p2sh_wallet(self, xpub, **kwargs) -> HDWallet:
        ks = from_xpub(xpub, self, "p2wpkh-p2sh")
        return HDWallet(ks, **kwargs)

    def p2wpkh_wallet(self, seed: str, passphrase: str = None, **kwargs) -> HDWallet:
        if not bip39_is_checksum_valid(seed) == (True, True):
            raise Exception("BIP39 Checksum failed. This is not a valid BIP39 seed")
        ks = p2wpkh_from_bip39_seed(seed, passphrase, coin=self)
        return HDWallet(ks, **kwargs)

    def watch_p2wpkh_wallet(self, xpub: str, **kwargs) -> HDWallet:
        ks = from_xpub(xpub, self, "p2wpkh")
        return HDWallet(ks, **kwargs)

    def electrum_wallet(self, seed: str, passphrase: str = None, **kwargs) -> HDWallet:
        ks = from_electrum_seed(seed, passphrase, False, coin=self)
        return HDWallet(ks, **kwargs)

    def watch_electrum_wallet(self, xpub: str, **kwargs) -> HDWallet:
        ks = from_xpub(xpub, self, "p2pkh", electrum=True)
        return HDWallet(ks, **kwargs)

    def watch_electrum_p2wpkh_wallet(self, xpub: str, **kwargs) -> HDWallet:
        ks = from_xpub(xpub, self, "p2wpkh", electrum=True)
        return HDWallet(ks, **kwargs)

        # def magicbyte_to_prefix(self, magicbyte) -> List[str]:
        #     first = bin_to_b58check(hash160Low, magicbyte=magicbyte)[0]
        #     last = bin_to_b58check(hash160High, magicbyte=magicbyte)[0]
        #     if first == last:
        #         return [first]
        #     return [first, last]

        # def b58check_to_bin(inp: str) -> Tuple[int, bytes]:
        #     """
        #     Converts a Base58Check encoded string to a binary representation.

        #     Args:
        #         inp (str): The Base58Check encoded string.

        #     Returns:
        #         Tuple[int, bytes]: A tuple containing the magic byte and the decoded binary data.

        #     Raises:
        #         AssertionError: If the checksum of the input string is invalid.

        #     Examples:
        #         >>> b58check_to_bin("16UjcYNBG9j16sxo88v5z83o5MYYxF" )

        #     More:
        #         break down data[1:-4] in the context of the b58check_to_bin function:

        #         Understanding the Code:

        #             data:
        #                 This variable holds the binary representation of the
        #                 Base58Check encoded string. It's a byte string,
        #                 which means it's a sequence of bytes (think of each byte as a
        #                 number between 0 and 255).

        #             data[1:-4]:
        #                 This is a slice of the data byte string.
        #                 It means:

        #                     1:
        #                         Start at the second element of the data byte string
        #                         (remember, Python indexing starts at 0).
        #                     -4:
        #                         End at the fourth element from the end of the data byte string.

        #         Why this Slice?:

        #             The b58check_to_bin function is designed to
        #             decode Base58Check encoded strings.
        #             The structure of a Base58Check encoded string is:

        #                 Magic Byte:
        #                     This identifies the type(btc,doge,ltc...) of data being encoded.
        #                 Data:
        #                     The actual data being encoded.
        #                 Checksum:
        #                     A 4-byte checksum to ensure the data's integrity.

        #                 Therefore:

        #                     data[0] is the magic byte.
        #                     data[1:-4] represents the actual data, excluding the magic byte and the checksum.
        #                     data[-4:] represents the 4-byte checksum.
        #         In Summary:

        #             The slice data[1:-4] extracts the decoded
        #             data from the data byte string, removing the magic
        #             byte and checksum. This is the actual information
        #             that was originally encoded.

        #     """
        #     leadingzbytes: int = len(re.match("^1*", inp).group(0))
        #     data: bytes = b"\x00" * leadingzbytes + changebase(string=inp, frm=58, to=256)
        #     assert bin_dbl_sha256(s=data[:-4])[:4] == data[-4:]
        #     magicbyte: int = data[0]
        #     # (removed magic byte and checksum) (the magic)
        #     actuall_data_without_Magic_byte_and_checksum: bytes = data[1:-4]
        #     return magicbyte, actuall_data_without_Magic_byte_and_checksum
