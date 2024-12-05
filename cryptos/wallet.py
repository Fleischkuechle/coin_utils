from ast import Dict
from .keystore import BIP32_KeyStore
from .main import *
from .transaction import select


class Wallet:
    """
    Represents a cryptocurrency wallet based on a BIP32 keystore.

    This class encapsulates the keystore, address derivations,
    transaction history, and other wallet-related information.

    Args:
        keystore (BIP32_KeyStore): The BIP32 keystore associated with the wallet.
        transaction_history (Any | None, optional): An optional list or other object representing the transaction history of the wallet. Defaults to None, in which case an empty list is used.
    """

    def __init__(
        self,
        keystore: BIP32_KeyStore,
        transaction_history: Any | None = None,
    ):
        """
        Initializes a new Wallet instance.

        This method sets up the wallet's keystore, address derivations,
        transaction history, and other relevant attributes.

        Args:
            keystore (BIP32_KeyStore): The BIP32 keystore associated with the wallet.
            transaction_history (Any | None, optional): An optional list or other object representing the transaction history of the wallet. Defaults to None, in which case an empty list is used.
        """
        self.coin: BaseCoin = keystore.coin
        self.keystore: BIP32_KeyStore = keystore
        self.address_derivations: Dict[str, str] = {}
        self.is_watching_only: bool = self.keystore.is_watching_only()
        self.transaction_history: Any = transaction_history or []
        self.xtype: str = self.keystore.xtype
        if self.keystore.electrum:
            self.script_type: str = self.keystore.xtype
        else:
            self.script_type: str = "p2pkh"

    def __init__original(self, keystore, transaction_history=None):
        self.coin = keystore.coin
        self.keystore = keystore
        self.address_derivations = {}
        self.is_watching_only = self.keystore.is_watching_only()
        self.transaction_history = transaction_history or []
        self.xtype = self.keystore.xtype
        if self.keystore.electrum:
            self.script_type = self.keystore.xtype
        else:
            self.script_type = "p2pkh"

    def privkey(self, address, formt="wif_compressed", password=None):
        if self.is_watching_only:
            return
        try:
            addr_derivation = self.address_derivations[address]
        except KeyError:
            raise Exception(
                "Address %s has not been generated yet. Generate new addresses with new_receiving_addresses or new_change_addresses methods"
                % address
            )
        pk, compressed = self.keystore.get_private_key(addr_derivation, password)
        return self.coin.encode_privkey(pk, formt, script_type=self.script_type)

    def export_privkeys(self, password=None):
        if self.is_watching_only:
            return
        return {
            "receiving": {
                addr: self.privkey(addr, password=password)
                for addr in self.receiving_addresses
            },
            "change": {
                addr: self.privkey(addr, password=password)
                for addr in self.change_addresses
            },
        }

    def receiving_address(self, index):
        pubkey = self.keystore.keypairs.keys()(index)
        address = self.pubtoaddr(pubkey)
        self.address_derivations[address] = pubkey
        return address

    def change_address(self, index):
        pubkey = self.keystore.keypairs.keys()(index)
        address = self.pubtoaddr(pubkey)
        self.address_derivations[address] = pubkey
        return address

    def pubtoaddr(self, pubkey):
        if self.xtype == "p2pkh":
            return self.coin.pubtoaddr(pubkey)
        elif self.xtype == "p2wpkh":
            return self.coin.pubtosegwitaddress(pubkey)
        elif self.xtype == "p2wpkh-p2sh":
            return self.coin.pubtop2wpkh_p2sh(pubkey)

    @property
    def addresses(self):
        return [self.pubtoaddr(pub) for pub in self.keystore.keypairs.keys()]

    @property
    def receiving_addresses(self):
        return self.addresses

    @property
    def change_addresses(self):
        return self.addresses

    def select_receive_address(self):
        return self.addresses[0]

    def select_change_address(self):
        return self.addresses[0]

    def new_receiving_address_range(self, num):
        return self.receiving_addresses[0]

    def new_change_address_range(self, num):
        return self.receiving_addresses[0]

    def new_receiving_addresses(self, num=10):
        return self.addresses

    def new_change_addresses(self, num=10):
        return self.addresses

    def new_receiving_address(self):
        return self.new_receiving_addresses(num=1)[0]

    def new_change_address(self):
        return self.new_change_addresses(num=1)[0]

    def is_mine(self, address):
        return address in self.addresses

    def is_change(self, address):
        return True

    def get_balances(self):
        return self.coin.get_balance(*self.addresses)

    def balance(self):
        balances = self.get_balances()
        confirmed_balance = sum(b["confirmed"] for b in balances)
        unconfirmed_balance = sum(b["unconfirmed"] for b in balances)
        return {
            "total": confirmed_balance + unconfirmed_balance,
            "unconfirmed": unconfirmed_balance,
            "confirmed": confirmed_balance,
        }

    def unspent(self, addresses=None, merkle_proof=False):
        addresses = addresses or self.addresses
        return self.coin.unspent(*addresses, merkle_proof=merkle_proof)

    def select_unspents(self, value, addresses=None, merkle_proof=False):
        unspents = self.unspent(addresses=addresses, merkle_proof=merkle_proof)
        return select(unspents, value)

    def history(self, addresses=None, merkle_proof=False):
        addresses = addresses or self.addresses
        return self.coin.history(*addresses, merkle_proof=merkle_proof)

    def synchronise(self):
        tx_hashes = [tx["tx_hash"] for tx in self.transaction_history]
        txs = self.history()
        new_txs = [tx for tx in txs if tx["tx_hash"] not in tx_hashes]
        self.transaction_history += self.coin.filter_by_proof(*new_txs)

    def sign(self, txobj, password=None):
        if self.is_watching_only:
            return
        pkeys_for = [inp["address"] for inp in txobj["ins"]]
        privkeys = {address: self.privkey("address", password) for address in pkeys_for}
        return self.coin.signall(txobj, privkeys)

    def pushtx(self, tx_hex):
        return self.coin.pushtx(tx_hex)

    def preparemultitx(
        self, outs, fee=50000, change_addr=None, fee_for_blocks=0, addresses=None
    ):
        change = change_addr or self.select_change_address()
        value = sum(out["value"] for out in outs) + fee
        ins = self.select_unspents(value, addresses=addresses)
        if self.coin.segwit_supported:
            if self.xtype == "p2pkh":
                for i in ins:
                    i["segwit"] = False
                    i["new_segwit"] = False
            elif self.xtype == "p2wpkh-p2sh":
                for i in ins:
                    i["segwit"] = True
                    i["new_segwit"] = False
            elif self.xtype == "p2wpkh":
                for i in ins:
                    i["segwit"] = True
                    i["new_segwit"] = True
        return self.coin.mktx_with_change(
            ins, outs, fee=fee, fee_for_blocks=fee_for_blocks, change=change
        )

    def preparetx(
        self, to, value, fee=50000, fee_for_blocks=0, change_addr=None, addresses=None
    ):
        outs = [{"address": to, "value": value}]
        return self.preparemultitx(
            outs,
            fee=fee,
            fee_for_blocks=fee_for_blocks,
            change_addr=change_addr,
            addresses=addresses,
        )

    def preparesignedtx(
        self,
        to,
        value,
        fee=50000,
        fee_for_blocks=0,
        change_addr=None,
        addresses=addresses,
        password=None,
    ):
        txobj = self.preparetx(
            to,
            value,
            fee=fee,
            fee_for_blocks=fee_for_blocks,
            change_addr=change_addr,
            addresses=addresses,
        )
        return self.sign(txobj, password=password)

    def preparesignedmultitx(
        self,
        outs,
        fee=50000,
        fee_for_blocks=0,
        change_addr=None,
        addresses=None,
        password=None,
    ):
        txobj = self.preparemultitx(
            outs,
            fee=fee,
            change_addr=change_addr,
            addresses=addresses,
            fee_for_blocks=fee_for_blocks,
        )
        return self.sign(txobj, password=password)

    def send(
        self,
        to,
        value,
        fee=50000,
        fee_for_blocks=0,
        change_addr=None,
        addresses=None,
        password=None,
    ):
        tx = self.preparesignedtx(
            to,
            value,
            fee=fee,
            fee_for_blocks=fee_for_blocks,
            change_addr=change_addr,
            addresses=addresses,
            password=password,
        )
        return self.pushtx(tx)

    def sendmultitx(
        self,
        outs,
        fee=50000,
        fee_for_blocks=0,
        change_addr=None,
        addresses=None,
        password=None,
    ):
        tx = self.preparesignedmultitx(
            outs,
            fee=fee,
            fee_for_blocks=fee_for_blocks,
            change_addr=change_addr,
            addresses=addresses,
            password=password,
        )
        return self.pushtx(tx)


class HDWallet_original(Wallet):
    def __init__(
        self,
        keystore,
        transaction_history=None,
        num_addresses=0,
        last_receiving_index=0,
        last_change_index=0,
    ):
        super(HDWallet, self).__init__(
            keystore,
            transaction_history=transaction_history,
        )
        self.last_receiving_index = last_receiving_index
        self.last_change_index = last_change_index
        self.new_receiving_addresses(num=num_addresses)
        self.new_change_addresses(num=num_addresses)
        self.used_addresses = self.get_used_addresses()
        self.xtype = self.keystore.xtype
        if self.keystore.electrum:
            self.script_type = self.keystore.xtype
        else:
            self.script_type = "p2pkh"

    def privkey(self, address, formt="wif_compressed", password=None):
        if self.is_watching_only:
            return
        try:
            addr_derivation = self.address_derivations[address]
        except KeyError:
            raise Exception(
                "Address %s has not been generated yet. Generate new address_derivations with new_receiving_addresses or new_change_addresses methods"
                % address
            )
        pk, compressed = self.keystore.get_private_key(addr_derivation, password)
        return self.coin.encode_privkey(pk, formt, script_type=self.script_type)

    def export_privkeys(self, password=None):
        if self.is_watching_only:
            return
        return {
            "receiving": {
                addr: self.privkey(addr, password=password)
                for addr in self.receiving_addresses
            },
            "change": {
                addr: self.privkey(addr, password=password)
                for addr in self.change_addresses
            },
        }

    def pubkey_receiving(self, index):
        return self.keystore.derive_pubkey(0, index)

    def pubkey_change(self, index):
        return self.keystore.derive_pubkey(1, index)

    def pubtoaddr(self, pubkey):
        if self.xtype == "p2pkh":
            return self.coin.pubtoaddr(pubkey)
        elif self.xtype == "p2wpkh":
            return self.coin.pubtosegwitaddress(pubkey)
        elif self.xtype == "p2wpkh-p2sh":
            return self.coin.pubtop2wpkh_p2sh(pubkey)

    def receiving_address(self, index: int):
        pubkey = self.pubkey_receiving(index)
        address = self.pubtoaddr(pubkey)
        self.address_derivations[address] = (0, index)
        return address

    def change_address(self, index):
        pubkey = self.pubkey_change(index)
        address = self.pubtoaddr(pubkey)
        self.address_derivations[address] = (1, index)
        return address

    @property
    def addresses(self):
        return self.address_derivations.keys()

    @property
    def receiving_addresses(self):
        return [
            addr
            for addr in self.address_derivations.keys()
            if not self.address_derivations[addr][0]
        ]

    @property
    def change_addresses(self):
        return [
            addr
            for addr in self.address_derivations.keys()
            if self.address_derivations[addr][0]
        ]

    def new_receiving_address_range(self, num: int):
        index: int = self.last_receiving_index
        return range(index, index + num)

    def new_change_address_range(self, num):
        index = self.last_change_index
        return range(index, index + num)

    def new_receiving_addresses(self, num: int = 10):
        addresses = list(
            map(self.receiving_address, self.new_receiving_address_range(num))
        )
        self.last_receiving_index += num
        return addresses

    def new_change_addresses(self, num=10):
        addresses = list(map(self.change_address, self.new_change_address_range(num)))
        self.last_change_index += num
        return addresses

    def new_receiving_address(self):
        return self.new_receiving_addresses(num=1)[0]

    def new_change_address(self):
        return self.new_change_addresses(num=1)[0]

    def select_receive_address(self):
        try:
            return next(
                addr
                for addr in self.receiving_addresses
                if addr not in self.used_addresses
            )
        except StopIteration:
            return self.new_receiving_address()

    def select_change_address(self):
        try:
            return next(
                addr
                for addr in self.receiving_addresses
                if addr not in self.used_addresses
            )
        except StopIteration:
            return self.new_change_address()

    def is_change(self, address):
        return address in self.change_addresses

    def get_used_addresses(self):
        return list(set([tx["addr"] for tx in self.transaction_history]))

    def synchronise(self):
        super(HDWallet, self).synchronise()
        self.used_addresses = self.get_used_addresses()


class HDWallet(Wallet):
    """
    Represents a hierarchical deterministic (HD) wallet, providing functionality for managing and deriving addresses,
    private keys, and public keys based on a BIP32 keystore.

    This class extends the `Wallet` class and leverages the BIP32 keystore for generating and managing addresses
    using a hierarchical deterministic approach. It supports both receiving and change addresses, allowing for
    flexible transaction management.

    Attributes:
        keystore (BIP32_KeyStore): The BIP32 keystore used for deriving addresses and keys.
        transaction_history (Any | None): A record of past transactions associated with the wallet.
        last_receiving_index (int): The index of the last generated receiving address.
        last_change_index (int): The index of the last generated change address.
        new_receiving_addresses (int): Number of new receiving addresses to be generated.
        new_change_addresses (int): Number of new change addresses to be generated.
        used_addresses (List[str]): List of addresses that have been used in transactions.
        xtype (str): The type of address derivation used (e.g., 'p2pkh', 'p2wpkh', 'p2wpkh-p2sh').
        script_type (str): The type of script used for address derivation (e.g., 'p2pkh', 'p2wpkh').
        address_derivations (Dict[str, Tuple[int, int]]): A dictionary mapping addresses to their derivation paths
                                                           (0 for receiving, 1 for change, index).

    Methods:
        privkey(address, formt="wif_compressed", password=None): Returns the private key associated with the given address.
        export_privkeys(password=None): Returns a dictionary containing all private keys associated with the wallet.
        pubkey_receiving(index): Returns the public key for the receiving address at the specified index.
        pubkey_change(index): Returns the public key for the change address at the specified index.
        pubtoaddr(pubkey): Converts a public key to a cryptocurrency address based on the wallet's address type.
        receiving_address(index: int): Generates a new receiving address at the specified index.
        change_address(index): Generates a new change address at the specified index.
        addresses: Returns a list of all addresses associated with the wallet.
        receiving_addresses: Returns a list of all receiving addresses associated with the wallet.
        change_addresses: Returns a list of all change addresses associated with the wallet.
        new_receiving_address_range(num: int): Generates a range of indices for new receiving addresses.
        new_change_address_range(num): Generates a range of indices for new change addresses.
        new_receiving_addresses(num: int = 10): Generates a specified number of new receiving addresses.
        new_change_addresses(num=10): Generates a specified number of new change addresses.
        new_receiving_address(): Generates a single new receiving address.
        new_change_address(): Generates a single new change address.
        select_receive_address(): Selects a unused receiving address or generates a new one if none are available.
        select_change_address(): Selects a unused change address or generates a new one if none are available.
        is_change(address): Checks if the given address is a change address.
        get_used_addresses(): Returns a list of addresses used in transactions from the transaction history.
        synchronise(): Synchronizes the wallet with the blockchain, updating used addresses.
    """

    def __init__(
        self,
        keystore: BIP32_KeyStore,
        transaction_history: Any | None = None,
        num_addresses: int = 0,
        last_receiving_index: int = 0,
        last_change_index: int = 0,
    ):
        super(HDWallet, self).__init__(
            keystore=keystore,
            transaction_history=transaction_history,
        )
        self.last_receiving_index = last_receiving_index
        self.last_change_index = last_change_index
        self.new_receiving_addresses(num=num_addresses)
        self.new_change_addresses(num=num_addresses)
        self.used_addresses = self.get_used_addresses()
        self.xtype = self.keystore.xtype
        if self.keystore.electrum:
            self.script_type = self.keystore.xtype
        else:
            self.script_type = "p2pkh"

    def privkey(self, address, formt="wif_compressed", password=None):
        if self.is_watching_only:
            return
        try:
            addr_derivation = self.address_derivations[address]
        except KeyError:
            raise Exception(
                "Address %s has not been generated yet. Generate new address_derivations with new_receiving_addresses or new_change_addresses methods"
                % address
            )
        pk, compressed = self.keystore.get_private_key(addr_derivation, password)
        return self.coin.encode_privkey(pk, formt, script_type=self.script_type)

    def export_privkeys(self, password=None):
        if self.is_watching_only:
            return
        return {
            "receiving": {
                addr: self.privkey(addr, password=password)
                for addr in self.receiving_addresses
            },
            "change": {
                addr: self.privkey(addr, password=password)
                for addr in self.change_addresses
            },
        }

    def pubkey_receiving(self, index):
        return self.keystore.derive_pubkey(0, index)

    def pubkey_change(self, index):
        return self.keystore.derive_pubkey(1, index)

    def pubtoaddr_original(self, pubkey):
        if self.xtype == "p2pkh":
            return self.coin.pubtoaddr(pubkey)
        elif self.xtype == "p2wpkh":
            return self.coin.pubtosegwitaddress(pubkey)
        elif self.xtype == "p2wpkh-p2sh":
            return self.coin.pubtop2wpkh_p2sh(pubkey)

    def pubtoaddr(self, pubkey):
        if self.xtype == "p2pkh":
            address_Base58_string: str = self.coin.pubtoaddr(pubkey=pubkey)
            return address_Base58_string
        elif self.xtype == "p2wpkh":
            return self.coin.pubtosegwitaddress(pubkey)
        elif self.xtype == "p2wpkh-p2sh":
            return self.coin.pubtop2wpkh_p2sh(pubkey)

    def receiving_address(self, index: int):
        pubkey = self.pubkey_receiving(index)
        address = self.pubtoaddr(pubkey)
        self.address_derivations[address] = (0, index)
        return address

    def change_address(self, index):
        pubkey = self.pubkey_change(index)
        address = self.pubtoaddr(pubkey)
        self.address_derivations[address] = (1, index)
        return address

    @property
    def addresses(self):
        return self.address_derivations.keys()

    @property
    def receiving_addresses(self):
        return [
            addr
            for addr in self.address_derivations.keys()
            if not self.address_derivations[addr][0]
        ]

    @property
    def change_addresses(self):
        return [
            addr
            for addr in self.address_derivations.keys()
            if self.address_derivations[addr][0]
        ]

    def new_receiving_address_range(self, num: int):
        index: int = self.last_receiving_index
        return range(index, index + num)

    def new_change_address_range(self, num):
        index = self.last_change_index
        return range(index, index + num)

    def new_receiving_addresses(self, num: int = 10):
        addresses = list(
            map(self.receiving_address, self.new_receiving_address_range(num))
        )
        self.last_receiving_index += num
        return addresses

    def new_change_addresses(self, num=10):
        addresses = list(map(self.change_address, self.new_change_address_range(num)))
        self.last_change_index += num
        return addresses

    def new_receiving_address(self):
        return self.new_receiving_addresses(num=1)[0]

    def new_change_address(self):
        return self.new_change_addresses(num=1)[0]

    def select_receive_address(self):
        try:
            return next(
                addr
                for addr in self.receiving_addresses
                if addr not in self.used_addresses
            )
        except StopIteration:
            return self.new_receiving_address()

    def select_change_address(self):
        try:
            return next(
                addr
                for addr in self.receiving_addresses
                if addr not in self.used_addresses
            )
        except StopIteration:
            return self.new_change_address()

    def is_change(self, address):
        return address in self.change_addresses

    def get_used_addresses(self):
        return list(set([tx["addr"] for tx in self.transaction_history]))

    def synchronise(self):
        super(HDWallet, self).synchronise()
        self.used_addresses = self.get_used_addresses()
