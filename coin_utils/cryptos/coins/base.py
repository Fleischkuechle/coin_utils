import asyncio
from asyncio import Future, TimeoutError, wait_for
from concurrent.futures import Future
import threading
import inspect
import janus


# from ..coins_async.base import BaseCoin
# from cryptos.utils import alist
# from ..wallet import HDWallet
# from ..electrumx_client.types import (
#     ElectrumXBalanceResponse,
#     ElectrumXMultiBalanceResponse,
#     ElectrumXTx,
#     ElectrumXMerkleResponse,
#     ElectrumXUnspentResponse,
#     ElectrumXMultiTxResponse,
#     ElectrumXHistoryResponse,
# )
# from ..types import (
#     Tx,
#     BlockHeader,
#     BlockHeaderCallbackSync,
#     AddressCallbackSync,
#     AddressTXCallbackSync,
#     MerkleProof,
#     AddressBalance,
#     TxOut,
#     TxInput,
#     TXInspectType,
#     PrivateKeySignAllType,
#     PrivkeyType,
#     PubKeyType,
# )

# try:
#     from ...cryptos.coins_async.base import BaseCoin
#     from ...cryptos.utils import alist
#     from ...cryptos.wallet import HDWallet
#     from ...cryptos.electrumx_client.types import (
#         ElectrumXBalanceResponse,
#         ElectrumXMultiBalanceResponse,
#         ElectrumXTx,
#         ElectrumXMerkleResponse,
#         ElectrumXUnspentResponse,
#         ElectrumXMultiTxResponse,
#         ElectrumXHistoryResponse,
#     )
#     from ...cryptos.types import (
#         Tx,
#         BlockHeader,
#         BlockHeaderCallbackSync,
#         AddressCallbackSync,
#         AddressTXCallbackSync,
#         MerkleProof,
#         AddressBalance,
#         TxOut,
#         TxInput,
#         TXInspectType,
#         PrivateKeySignAllType,
#         PrivkeyType,
#         PubKeyType,
#     )
try:
    from ..coins_async.base import BaseCoin
    from ..utils import alist
    from ..wallet import HDWallet
    from ..electrumx_client.types import (
        ElectrumXBalanceResponse,
        ElectrumXMultiBalanceResponse,
        ElectrumXTx,
        ElectrumXMerkleResponse,
        ElectrumXUnspentResponse,
        ElectrumXMultiTxResponse,
        ElectrumXHistoryResponse,
    )
    from ..types import (
        Tx,
        BlockHeader,
        BlockHeaderCallbackSync,
        AddressCallbackSync,
        AddressTXCallbackSync,
        MerkleProof,
        AddressBalance,
        TxOut,
        TxInput,
        TXInspectType,
        PrivateKeySignAllType,
        PrivkeyType,
        PubKeyType,
    )
except:
    from cryptos.coins_async.base import BaseCoin
    from cryptos.utils import alist
    from cryptos.wallet import HDWallet
    from cryptos.electrumx_client.types import (
        ElectrumXBalanceResponse,
        ElectrumXMultiBalanceResponse,
        ElectrumXTx,
        ElectrumXMerkleResponse,
        ElectrumXUnspentResponse,
        ElectrumXMultiTxResponse,
        ElectrumXHistoryResponse,
    )
    from cryptos.types import (
        Tx,
        BlockHeader,
        BlockHeaderCallbackSync,
        AddressCallbackSync,
        AddressTXCallbackSync,
        MerkleProof,
        AddressBalance,
        TxOut,
        TxInput,
        TXInspectType,
        PrivateKeySignAllType,
        PrivkeyType,
        PubKeyType,
    )
from typing import Optional, Tuple, Any, List, Union, Dict, AnyStr, Type, Awaitable

# from typing import Optional, Tuple, Dict, Any, Awaitable, Callable


class BaseSyncCoin:
    timeout: int = 10
    is_closing: bool = False
    coin_class: Type[BaseCoin]
    _thread: threading.Thread = None
    pub_async_coin: Type[BaseCoin]

    """
    This class wraps the parent class async coroutine methods in synchronous methods.
    A new thread is created to run the parent class async coroutine methods in an asyncio event loop.
    The thread-safe janus.Queue is used to pass requests to the thread running the event loop.
    concurrent.futures.Future is used to return results and exceptions to the main thread.
    
    For comments explaining each method, check the async coin class.
    """

    def __init__(self, testnet: bool = False, use_ssl: bool = None, **kwargs):
        self._async_coin = self.coin_class(testnet=testnet, use_ssl=use_ssl, **kwargs)
        self._request_queue: Optional[
            janus.Queue[Tuple[Future, str, tuple, dict[str, Any]]]
        ] = None
        self._loop_is_started = threading.Event()
        self.pub_async_coin = self._async_coin
        # self.servers=self.coin_class.

    def __getattr__(self, item):
        return getattr(self._async_coin, item)

    def start_original(self):
        if not self._thread or not self._thread.is_alive():
            self._thread = threading.Thread(target=self.start_event_loop, daemon=True)
            self._thread.start()
        self._loop_is_started.wait(timeout=10)

    def start(self) -> None:
        """
        Starts the event loop in a separate thread.

        This method ensures that the event loop is running in a background thread.
        It checks if the thread is already running and starts a new thread if not.
        The `_loop_is_started` event is used to wait for the loop to start,
        preventing race conditions.

        Args:
            None

        Returns:
            None
        """
        if not self._thread or not self._thread.is_alive():
            self._thread = threading.Thread(target=self.start_event_loop, daemon=True)
            self._thread.start()
        self._loop_is_started.wait(timeout=10)

    def start_event_loop_original(self):
        asyncio.run(self.run())

    def start_event_loop(self) -> None:
        """
        Starts the asyncio event loop in a separate thread.

        This method is responsible for initializing and running the asyncio event loop.
        It uses `asyncio.run` to run the `self.run` coroutine, which likely contains the
        main logic of your event loop.

        Args:
            None

        Returns:
            None
        """
        asyncio.run(self.run())

    def get_server_file(self):
        return self.coin_class.explorer.servers

    async def run_original(self):
        self._request_queue = janus.Queue()
        fut: Optional[Future]
        method: str
        args: tuple
        kwargs: dict
        if not self.is_closing:
            try:
                asyncio.get_running_loop().call_soon(self._loop_is_started.set)
                while True:
                    val = await self._request_queue.async_q.get()
                    fut, method, args, kwargs = val
                    try:
                        if method == "_property":
                            coro = getattr(self._async_coin, args[0])
                        else:
                            coro = getattr(self._async_coin, method)(*args, **kwargs)
                            if inspect.isasyncgen(coro):
                                coro = alist(coro)
                        result = await asyncio.wait_for(fut=coro, timeout=self.timeout)
                        fut.set_result(result)
                    except BaseException as e:
                        fut.set_exception(e)
                    finally:
                        if method == "close":
                            break
            finally:
                if not self._async_coin.is_closing:
                    await self._async_coin.close()
            self._loop_is_started.clear()

    async def run(self) -> None:
        """
        Main event loop for processing requests.

        This coroutine runs continuously, handling requests from the `_request_queue`.
        It retrieves requests, executes the corresponding methods on the `_async_coin` object,
        and sends the results back to the caller.

        The loop also handles closing the `_async_coin` object when a "close" request is received.

        Args:
            None

        Returns:
            None
        """
        self._request_queue: janus.Queue = janus.Queue()
        fut: Optional[Future] = None
        method: str = ""
        args: Tuple[Any, ...] = ()
        kwargs: Dict[str, Any] = {}
        if not self.is_closing:
            try:
                asyncio.get_running_loop().call_soon(self._loop_is_started.set)
                while True:
                    val: Tuple[Future, str, Tuple[Any, ...], Dict[str, Any]] = (
                        await self._request_queue.async_q.get()
                    )
                    fut, method, args, kwargs = val
                    try:
                        if method == "_property":
                            coro: Awaitable[Any] = getattr(self._async_coin, args[0])
                        else:
                            coro: Awaitable[Any] = getattr(self._async_coin, method)(
                                *args, **kwargs
                            )
                            if inspect.isasyncgen(coro):
                                coro = alist(coro)
                        result: Any = await wait_for(coro, timeout=self.timeout)
                        fut.set_result(result)
                    except BaseException as e:
                        fut.set_exception(e)
                    finally:
                        if method == "close":
                            break
            finally:
                if not self._async_coin.is_closing:
                    await self._async_coin.close()
            self._loop_is_started.clear()

    def _run_async_original(self, method: str, *args, **kwargs):
        self.start()
        fut = Future()
        self._request_queue.sync_q.put((fut, method, args, kwargs))
        return fut.result(timeout=self.timeout * 2)

    def _run_async(self, method: str, *args: Any, **kwargs: Any) -> Any:
        """
        Executes a method asynchronously on a separate thread and returns the result.

        This method allows you to run methods of the class asynchronously.
        It starts the thread if it's not already running,
        enqueues the method call with its arguments, and waits for the result with a timeout.

        Args:
            method (str): The name of the method to execute.
            *args: Positional arguments to pass to the method.
            **kwargs: Keyword arguments to pass to the method.

        Returns:
            Any: The result of the executed method.

        Raises:
            TimeoutError: If the method execution takes longer than the specified timeout.
        """
        self.start()  # Start the thread if it's not already running
        fut = Future()  # Create a Future object to represent the asynchronous result
        self._request_queue.sync_q.put(
            (fut, method, args, kwargs)
        )  # Enqueue the method call
        return fut.result(
            timeout=self.timeout * 2
        )  # Wait for the result with a timeout

    def __del__(self):
        self.close()

    def close(self):
        self.is_closing = True
        if self._loop_is_started.is_set():
            fut = Future()
            self._request_queue.sync_q.put((fut, "close", (), {}))
            fut.result(timeout=100)

    def estimate_fee_per_kb(self, numblocks: int = 6) -> float:
        return self._run_async("estimate_fee_per_kb", numblocks=numblocks)

    def tx_size(self, txobj: Tx) -> float:
        return self._async_coin.tx_size(txobj)

    def estimate_fee(self, txobj: Tx, numblocks: int = 6) -> int:
        return self._run_async("estimate_fee", txobj, numblocks=numblocks)

    def raw_block_header(self, height: int) -> str:
        return self._run_async("raw_block_header", height)

    def block_header(self, height: int) -> BlockHeader:
        return self._run_async("block_header", height)

    def block_headers(self, *args: int) -> List[BlockHeader]:
        return self._run_async("block_headers", *args)

    def subscribe_to_block_headers(self, callback: BlockHeaderCallbackSync) -> None:
        return self._run_async("subscribe_to_block_headers", callback)

    def unsubscribe_from_block_headers(self) -> None:
        return self._run_async("unsubscribe_from_block_headers")

    @property
    def block(self) -> Tuple[int, str, BlockHeader]:
        return self._run_async("_property", "block")

    def confirmations(self, height: int) -> int:
        return self._run_async("confirmations", height)

    def subscribe_to_address(self, callback: AddressCallbackSync, addr: str) -> None:
        return self._run_async("subscribe_to_address", callback, addr)

    def unsubscribe_from_address(self, addr: str) -> None:
        return self._run_async("unsubscribe_from_address", addr)

    def subscribe_to_address_transactions(
        self, callback: AddressTXCallbackSync, addr: str
    ) -> None:
        return self._run_async("subscribe_to_address_transactions", callback, addr)

    def get_balance(self, addr: str) -> ElectrumXBalanceResponse:
        return self._run_async("get_balance", addr)

    def get_balances(self, *args: str) -> List[ElectrumXMultiBalanceResponse]:
        return self._run_async("get_balances", *args)

    def get_merkle(self, tx: ElectrumXTx) -> Optional[ElectrumXMerkleResponse]:
        return self._run_async("get_merkle", tx)

    def merkle_prove(self, tx: ElectrumXTx) -> MerkleProof:
        return self._run_async("merkle_prove", tx)

    def merkle_prove_by_txid(self, tx_hash: str) -> MerkleProof:
        return self._run_async("merkle_prove_by_txid", tx_hash)

    def unspent_original(
        self,
        addr: str,
        merkle_proof: bool = False,
    ) -> ElectrumXUnspentResponse:
        """
        Retrieves Unspent Tansaction Outputs (UTXOs) associated with a given address.

        This function queries the ElectrumX server to obtain a list of Unspent
        Transaction Outputs (UTXOs) that belong to the specified address. It can
        optionally include Merkle proofs for each UTXO.

        Args:
            addr (str): The Bitcoin address to query.
            merkle_proof (bool, optional): Whether to include Merkle proofs for each UTXO. Defaults to False.

        Returns:
            ElectrumXUnspentResponse: An object containing the unspent outputs.

        ElectrumXUnspentResponse:
            Represents a transaction in the ElectrumX protocol.

            This TypedDict defines the structure of a transaction
            object returned by the ElectrumX server.
            It includes information about the transaction's
            height, hash, fee, position in the block, value,
            and associated address.

            Attributes:
                height (int): The block height at which the transaction was included.
                tx_hash (str): The hexadecimal hash of the transaction.
                fee (NotRequired[int]): The transaction fee in satoshis. This field is optional.
                tx_pos (NotRequired[int]): The position of the transaction within the block. This field is optional.
                value (NotRequired[int]): The value of the transaction in satoshis. This field is optional.
                address (NotRequired[str]): The Bitcoin address associated with the transaction. This field is optional.

        """
        return self._run_async("unspent", addr, merkle_proof=merkle_proof)

    def unspent(
        self,
        addr: str,
        merkle_proof: bool = False,
    ) -> ElectrumXUnspentResponse:
        """
        Retrieves Unspent Transaction Outputs (UTXOs) associated with a given address.

        This function is similar to checking the
        **account balance on a bank account**.
        It queries the ElectrumX server to obtain a list of unspent
        transaction outputs (UTXOs) that belong to the specified address. These UTXOs represent the funds that are available to spend from that address.
        It can optionally include Merkle proofs for each UTXO.

        Args:
            addr (str): The Bitcoin address to query.
            merkle_proof (bool, optional): Whether to include Merkle proofs for each UTXO. Defaults to False.

        Returns:
            ElectrumXUnspentResponse: An object containing the unspent outputs.

        ElectrumXUnspentResponse:
            Represents a transaction in the ElectrumX protocol.

            This TypedDict defines the structure of a transaction
            object returned by the ElectrumX server.
            It includes information about the transaction's
            height, hash, fee, position in the block, value,
            and associated address.

            Attributes:
                height (int): The block height at which the transaction was included.
                tx_hash (str): The hexadecimal hash of the transaction.
                fee (NotRequired[int]): The transaction fee in satoshis. This field is optional.
                tx_pos (NotRequired[int]): The position of the transaction within the block. This field is optional.
                value (NotRequired[int]): The value of the transaction in satoshis. This field is optional.
                address (NotRequired[str]): The Bitcoin address associated with the transaction. This field is optional.

        """
        return self._run_async("unspent", addr, merkle_proof=merkle_proof)

    def get_unspents(
        self,
        *args: str,
        merkle_proof: bool = False,
    ) -> List[ElectrumXMultiTxResponse]:
        """
        Retrieves a list of Unspent Transaction Outputs (UTXOs) for the given addresses.

        This method utilizes the ElectrumX protocol to fetch UTXO information for the specified addresses.
        It optionally includes a Merkle proof for each UTXO if `merkle_proof` is set to `True`.

        Args:
            *args (str): A variable number of addresses to retrieve UTXOs for.
            merkle_proof (bool, optional): Whether to include Merkle proofs for each UTXO. Defaults to False.

        Returns:
            List[ElectrumXMultiTxResponse]: A list of ElectrumXMultiTxResponse objects, each representing an unspent transaction output.
            Each response object contains details about the UTXO (Unspent Transaction Outputs),
            including its value, height, and optionally a Merkle proof.
        Info:
            A Merkle proof is a method used to verify the
            presence and integrity of specific data within a
            dataset using a Merkle tree. It's a way to prove
            that a specific transaction exists within
            a block on the blockchain without having to download the entire block.
        Example:
            >>> unspents = client.get_unspents("bc1q...", "bc1p...")
            >>> for unspent in unspents:
            >>>     print(f"Value: {unspent.value}, Height: {unspent.height}")
        """
        return self._run_async("get_unspents", *args, merkle_proof=merkle_proof)

    def balance_merkle_proven(self, addr: str) -> int:
        return self._run_async("balance_merkle_proven", addr)

    def balances_merkle_proven(self, *args: str) -> List[AddressBalance]:
        return self._run_async("balances_merkle_proven", *args)

    def history(
        self, addr: str, merkle_proof: bool = False
    ) -> ElectrumXHistoryResponse:
        return self._run_async("history", addr, merkle_proof=merkle_proof)

    def get_histories(
        self, *args: str, merkle_proof: bool = False
    ) -> List[ElectrumXMultiTxResponse]:
        return self._run_async("get_histories", *args, merkle_proof=merkle_proof)

    def get_raw_tx(self, tx_hash: str) -> str:
        return self._run_async("get_raw_tx", tx_hash)

    def get_tx(self, txid: str) -> Tx:
        return self._run_async("get_tx", txid)

    def get_verbose_tx(self, txid: str) -> Dict[str, Any]:  # Make TypedDict
        return self._run_async("get_verbose_tx", txid)

    def get_txs(self, *args: str) -> List[Tx]:
        return self._run_async("get_txs", *args)

    def pushtx(self, tx: Union[str, Tx]):
        return self._run_async("pushtx", tx)

    def privtopub(self, privkey: PrivkeyType) -> str:  # type: ignore
        """
        Converts a private key to a public key.
        (one of the core magic functions in this code)

        Args:
            privkey (PrivkeyType): The private key to convert.

        Returns:
            str: The public key corresponding to the given private key.
        More Info:
            This is how the transaction is approved by the miners:
                1.Calculate a hash of the data:
                    The recipient (blockchain) calculates a hash of the data
                    (file, message, etc.) using the same hashing
                    algorithm that the sender(you with your private key) used.
                    This hash is a unique fingerprint of the data.
                2.Decrypt the digital signature:
                    The recipient uses the sender's public key
                    to decrypt the digital signature.
                    This reveals the original hash that the sender calculated.
                3.Compare the hashes:
                    The recipient compares the hash they
                    calculated in step 1 with the
                    hash they decrypted in step 2.
                4.Validation:
                    If the two hashes match, the signature is
                    considered valid. This means that
                    the data has not been altered since
                    it was signed and that the sender
                    actually signed the data. If the
                    hashes don't match, it means either the data has
                    been altered or the signature was forged.

        the Algo:
            explanation how ECDSA works.
            ECDSA stands for Elliptic Curve Digital Signature Algorithm.
            It's a type of public-key cryptography that uses elliptic
            curves to generate and verify digital signatures.

            Here's a simplified explanation:

            Key Generation:
                Each user generates a pair of keys:
                    a private key and a public key.
                    The private key is kept secret,
                    while the public key is shared with others.
            Signing:
                When a user wants to sign a message,
                they use their private key and a mathematical
                operation based on the elliptic curve to
                create a digital signature.
            Verification:
                Anyone can verify the signature using the
                sender's public key. They perform the
                same mathematical operation on the
                message and the signature, and if the
                results match, they know the signature is valid.

            ECDSA is used in many applications,
            including Bitcoin, where it is used to secure
            transactions. It is considered a very
            secure algorithm, and it is difficult for
            anyone to forge a signature or impersonate
            the owner of a private key.
        math:
            ECDSA relies on elliptic curve cryptography,
            which involves performing operations on points
            on an elliptic curve. These operations are based
            on the properties of the curve and involve concepts
            like point addition and scalar multiplication.

            The specific mathematical operations
            used in ECDSA are quite complex and involve:

            Hashing:
                The message is first hashed using a
                cryptographic hash function like SHA-256.
                This creates a fixed-size digest of the message.
            Point Multiplication:
                The private key is used to multiply a point
                on the elliptic curve.
                This results in a new point on the curve.
            Random Number Generation:
                A random number is generated,
                which is used in the signature calculation.
            Signature Calculation:
                The signature is calculated using the
                hash of the message, the random number,
                and the point obtained from the point multiplication.
            The signature consists of two components:
                r and s. These values are then used for verification.

            To verify the signature,
            the recipient uses the sender's
            public key and the same mathematical
            operations to calculate r and s.
            If the calculated values match the
            signature, the signature is considered valid.

        """
        return self._async_coin.privtopub(privkey=privkey)

    def pubtoaddr(self, pubkey: PubKeyType) -> str:  # type: ignore
        return self._async_coin.pubtoaddr(pubkey=pubkey)

    def privtoaddr(self, privkey: PrivkeyType) -> str:  # type: ignore
        return self._async_coin.privtoaddr(privkey=privkey)

    def privtop2pkh(self, privkey: PrivkeyType) -> str:  # type: ignore
        return self._async_coin.privtop2pkh(privkey=privkey)

    def pub_is_for_p2pkh_addr(self, pubkey: PubKeyType, address: str) -> bool:  # type: ignore
        return self._async_coin.pub_is_for_p2pkh_addr(pubkey, address)

    def wiftoaddr(self, privkey: PrivkeyType) -> str:  # type: ignore
        return self._async_coin.wiftoaddr(privkey)

    def electrum_address(self, masterkey: AnyStr, n: int, for_change: int = 0) -> str:
        return self._async_coin.electrum_address(masterkey, n, for_change=for_change)

    def encode_privkey(
        self, privkey: PrivkeyType, formt: str, script_type: str = "p2pkh"  # type: ignore
    ) -> PrivkeyType:  # type: ignore
        return self._async_coin.encode_privkey(privkey, formt, script_type)

    def is_p2pkh(self, addr: str) -> bool:
        return self._async_coin.is_p2pkh(addr=addr)

    def is_p2sh(self, addr: str) -> bool:
        return self._async_coin.is_p2sh(addr)

    def is_native_segwit(self, addr: str) -> bool:
        return self._async_coin.is_native_segwit(addr)

    def is_address(self, addr: str) -> bool:
        return self._async_coin.is_address(addr=addr)

    def is_cash_or_legacy_p2pkh_address(self, addr: str) -> bool:
        return self._async_coin.is_cash_or_legacy_p2pkh_address(addr)

    def maybe_legacy_segwit(self, addr: str) -> bool:
        return self._async_coin.maybe_legacy_segwit(addr)

    def is_p2wsh(self, addr: str) -> bool:
        return self._async_coin.is_p2wsh(addr)

    def is_segwit_or_p2sh(self, addr: str) -> bool:
        return self._async_coin.is_segwit_or_p2sh(addr)

    def is_segwit_or_multisig(self, addr: str) -> bool:
        return self._async_coin.is_segwit_or_p2sh(addr)

    def output_script_to_address(self, script: str) -> str:
        return self._async_coin.output_script_to_address(script)

    def scripttoaddr(self, script: str) -> str:
        return self._async_coin.scripttoaddr(script)

    def p2sh_scriptaddr(self, script: str) -> str:
        return self._async_coin.p2sh_scriptaddr(script)

    def p2sh_segwit_addr(self, script: str) -> str:
        return self._async_coin.p2sh_segwit_addr(script)

    def addrtoscript(self, addr: str) -> str:
        return self._async_coin.addrtoscript(addr)

    def addrtoscripthash(self, addr: str) -> str:
        return self._async_coin.addrtoscripthash(addr)

    def pubtop2wpkh_p2sh(self, pub: str) -> str:
        return self._async_coin.pubtop2wpkh_p2sh(pub)

    def privtop2wpkh_p2sh(self, priv: str) -> str:
        return self._async_coin.privtop2wpkh_p2sh(priv)

    def hash_to_segwit_addr(self, pub_hash: str) -> str:
        return self._async_coin.hash_to_segwit_addr(pub_hash)

    def scripthash_to_segwit_addr(self, script_hash: AnyStr) -> str:
        return self._async_coin.scripthash_to_segwit_addr(script_hash)

    def pubtosegwitaddress(self, pubkey) -> str:
        return self._async_coin.pubtosegwitaddress(pubkey=pubkey)

    def script_to_p2wsh(self, script) -> str:
        return self._async_coin.script_to_p2wsh(script)

    def mk_multisig_address(
        self, *args: str, num_required: int = None
    ) -> Tuple[str, str]:
        return self._async_coin.mk_multisig_address(*args, num_required=num_required)

    def mk_multsig_segwit_address(
        self, *args: str, num_required: int = None
    ) -> Tuple[str, str]:
        return self._async_coin.mk_multsig_segwit_address(
            *args, num_required=num_required
        )

    def sign(self, txobj: Union[Tx, AnyStr], i: int, priv: PrivkeyType) -> Tx:  # type: ignore
        return self._async_coin.sign(txobj, i, priv)

    def signall(self, txobj: Union[str, Tx], priv: PrivateKeySignAllType) -> Tx:  # type: ignore
        return self._async_coin.signall(txobj, priv)

    def multisign(self, tx: Union[str, Tx], i: int, script: str, pk) -> Tx:
        return self._async_coin.multisign(tx, i, script, pk)

    def mktx(
        self,
        ins: List[Union[TxInput, AnyStr]],
        outs: List[Union[TxOut, AnyStr]],
        locktime: int = 0,
        sequence: int = 0xFFFFFFFF,
    ) -> Tx:
        return self._async_coin.mktx(ins, outs, locktime=locktime, sequence=sequence)

    def mktx(
        self,
        ins: List[Union[TxInput, AnyStr]],
        outs: List[Union[TxOut, AnyStr]],
        locktime: int = 0,
        sequence: int = 0xFFFFFFFF,
    ) -> Tx:
        return self._async_coin.mktx(ins, outs, locktime=locktime, sequence=sequence)

    def mktx_with_change(
        self,
        ins: List[Union[TxInput, AnyStr, ElectrumXTx]],
        outs: List[Union[TxOut, AnyStr]],
        change_addr: str = None,
        fee: int = None,
        estimate_fee_blocks: int = 6,
        locktime: int = 0,
        sequence: int = 0xFFFFFFFF,
    ) -> Tx:
        return self._run_async(
            "mktx_with_change",
            ins,
            outs,
            change_addr=change_addr,
            fee=fee,
            estimate_fee_blocks=estimate_fee_blocks,
            locktime=locktime,
            sequence=sequence,
        )

    def preparemultitx(
        self,
        frm: str,
        outs: List[TxOut],
        change_addr: str = None,
        fee: int = None,
        estimate_fee_blocks: int = 6,
    ) -> Tx:
        return self._run_async(
            "preparemultitx",
            frm,
            outs,
            change_addr=change_addr,
            fee=fee,
            estimate_fee_blocks=estimate_fee_blocks,
        )

    def preparetx(
        self,
        frm: str,
        to: str,
        value: int,
        fee: int = None,
        estimate_fee_blocks: int = 6,
        change_addr: str = None,
    ) -> Tx:
        return self._run_async(
            "preparetx",
            frm,
            to,
            value,
            fee=fee,
            estimate_fee_blocks=estimate_fee_blocks,
            change_addr=change_addr,
        )

    def preparesignedmultirecipienttx(
        self,
        privkey: PrivateKeySignAllType,  # type: ignore
        frm: str,
        outs: List[TxOut],
        change_addr: str = None,
        fee: int = None,
        estimate_fee_blocks: int = 6,
    ) -> Tx:
        return self._run_async(
            "preparesignedmultirecipienttx",
            privkey,
            frm,
            outs,
            change_addr=change_addr,
            fee=fee,
            estimate_fee_blocks=estimate_fee_blocks,
        )

    def preparesignedtx(
        self,
        privkey: PrivateKeySignAllType,  # type: ignore
        frm: str,
        to: str,
        value: int,
        change_addr: str = None,
        fee: int = None,
        estimate_fee_blocks: int = 6,
    ) -> Tx:
        return self._run_async(
            "preparesignedtx",
            privkey,
            frm,
            to,
            value,
            change_addr=change_addr,
            fee=fee,
            estimate_fee_blocks=estimate_fee_blocks,
        )

    def send_to_multiple_receivers_tx(
        self,
        privkey: PrivateKeySignAllType,  # type: ignore
        addr: str,
        outs: List[TxOut],
        change_addr: str = None,
        fee: int = None,
        estimate_fee_blocks: int = 6,
    ):
        return self._run_async(
            "send_to_multiple_receivers_tx",
            privkey,
            addr,
            outs,
            change_addr=change_addr,
            fee=fee,
            estimate_fee_blocks=estimate_fee_blocks,
        )

    def send(
        self,
        privkey: PrivateKeySignAllType,  # type: ignore
        frm: str,
        to: str,
        value: int,
        change_addr: str = None,
        fee: int = None,
        estimate_fee_blocks: int = 6,
    ):
        return self._run_async(
            "send",
            privkey,
            frm,
            to,
            value,
            change_addr=change_addr,
            fee=fee,
            estimate_fee_blocks=estimate_fee_blocks,
        )

    def inspect(self, tx: Union[str, Tx]) -> TXInspectType:
        return self._run_async("inspect", tx)

    def wallet(self, seed: str, passphrase: str = None, **kwargs) -> HDWallet:
        return self._async_coin.wallet(seed, passphrase=passphrase, **kwargs)

    def watch_wallet_original(self, xpub: str, **kwargs) -> HDWallet:
        return self._async_coin.watch_wallet(xpub, **kwargs)

    def watch_wallet(
        self,
        xpub: str,
        **kwargs: Dict[str, Optional[str]],
    ) -> HDWallet:
        """
        Watches a wallet using an extended public key (xpub).

        This method allows you to track the balance and transactions of a
        wallet without having access to its private keys.
        It utilizes the `watch_wallet` method of the underlying asynchronous
        coin library (`_async_coin`) to achieve this.

        Args:
            xpub (str): The extended public key (xpub) of the wallet to watch.
            **kwargs (Dict[str, Optional[str]]):
                Optional keyword arguments that can be passed to the underlying `watch_wallet`
                method.
                These arguments can vary depending on the specific implementation of
                the asynchronous coin library.

        Returns:
            HDWallet: An instance of the `HDWallet` class representing the watched wallet.
                This instance can be used to access
                information about the wallet, such as its balance, transactions, and addresses.

        Example:
            >>> wallet = YourClass()
            >>> watched_wallet = wallet.watch_wallet(xpub='xpub661MyMwAqRbcFtXgS5sYJABqqG9YLmC4Q1z37oBkA76LEs6U8q8k6vF5tLP4fFzVzrYmsqYgjM3z8665Y8Pf5Y75z', network='testnet')
            >>> print(watched_wallet.get_balance())  # Access the wallet's balance
            >>> print(watched_wallet.get_transactions())  # Access the wallet's transactions
        """
        hd_wallet: HDWallet = self._async_coin.watch_wallet(xpub, **kwargs)
        return hd_wallet

    def p2wpkh_p2sh_wallet(
        self, seed: str, passphrase: str = None, **kwargs
    ) -> HDWallet:
        return self._async_coin.p2wpkh_p2sh_wallet(
            seed, passphrase=passphrase, **kwargs
        )

    def watch_p2wpkh_p2sh_wallet(self, xpub: str, **kwargs) -> HDWallet:
        return self._async_coin.watch_p2wpkh_p2sh_wallet(xpub, **kwargs)

    def p2wpkh_wallet(self, seed: str, passphrase: str = None, **kwargs) -> HDWallet:
        return self._async_coin.p2wpkh_wallet(seed, passphrase=passphrase, **kwargs)

    def watch_p2wpkh_wallet(self, xpub: str, **kwargs) -> HDWallet:
        return self._async_coin.watch_p2wpkh_wallet(xpub, **kwargs)

    def electrum_wallet(self, seed: str, passphrase: str = None, **kwargs) -> HDWallet:
        return self._async_coin.electrum_wallet(seed, passphrase=passphrase, **kwargs)

    def watch_electrum_wallet(self, xpub: str, **kwargs) -> HDWallet:
        return self._async_coin.watch_electrum_wallet(xpub, **kwargs)

    def watch_electrum_p2wpkh_wallet(self, xpub: str, **kwargs) -> HDWallet:
        return self._async_coin.watch_electrum_p2wpkh_wallet(xpub, **kwargs)

    def is_cash_address(self, addr: str) -> bool:
        return self._async_coin.is_cash_address(addr)

    def scripthash_to_cash_addr(self, scripthash: bytes) -> str:
        return self._async_coin.scripthash_to_cash_addr(scripthash)

    def p2sh_cash_addr(self, script: str) -> str:
        return self._async_coin.p2sh_cash_addr(script)

    def hash_to_cash_addr(self, pub_hash: AnyStr) -> str:
        return self._async_coin.hash_to_cash_addr(pub_hash)

    def pubtocashaddress(self, pubkey: str) -> str:
        return self._async_coin.pubtocashaddress(pubkey)

    def privtocashaddress(self, privkey: PrivkeyType) -> str:  # type: ignore
        return self._async_coin.privtocashaddress(privkey)

    def legacy_addr_to_cash_address(self, addr: str) -> str:
        return self._async_coin.legacy_addr_to_cash_address(addr)

    def cash_address_to_legacy_addr(self, addr: str) -> str:
        return self._async_coin.cash_address_to_legacy_addr(addr)

    def mk_multsig_cash_address(
        self, *args: str, num_required: int = None
    ) -> Tuple[str, str]:
        return self._async_coin.mk_multsig_cash_address(
            *args, num_required=num_required
        )

    def apply_multisignatures(self, txobj: Tx, i: int, script, *args):
        return self._async_coin.apply_multisignatures(txobj, i, script, *args)

    def calculate_fee(self, tx: Tx) -> int:
        return self._run_async("calculate_fee", tx)

    def privtosegwitaddress(self, privkey: PrivkeyType) -> str:  # type: ignore
        return self._async_coin.privtosegwitaddress(privkey)
