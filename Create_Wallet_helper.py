import os
from cryptos import main
from cryptos import coins
from cryptos import script_utils

from typing import Tuple, Union

from cryptos.wallet import HDWallet
from cryptos import mnemonic
from cryptos import keystore
from cryptos.wallet import HDWallet
from cryptos.types import Tx


class Create_Wallet_helper:
    def __init__(
        self,
        coin_symbol: str,
        testnet: bool = False,
    ):
        self.coin_symbol: str = coin_symbol
        self.testnet: bool = testnet
        self.some_validate_link: str = (
            r"https://live.blockcypher.com/btc/address/1EfayE6j4nv6L13Q2BdDtys7Gs2b791ev4/"
        )
        self.some_validate_link_2: str = (
            r"https://blockexplorer.one/dogecoin/testnet/address/ns3c8yGKiTL1TGgQru9CFbSwGxgLt3EHph"
        )
        self.margin1: int = 20
        self.margin2: int = 30
        self.line_length: int = 60
        self.line_symbol: str = "-"

    def get_coin_instance(self, coin_symbol: str = "btc") -> Union[
        coins.bitcoin.Bitcoin,
        coins.litecoin.Litecoin,
        coins.bitcoin_cash.BitcoinCash,
        coins.dash.Dash,
        coins.dogecoin.Doge,
        None,
    ]:
        """
        Returns an instance of the appropriate coin class based on the provided coin symbol.

        Args:
            self: The instance of the class calling this function.
            coin_symbol: The symbol of the coin to create an instance for.

        Returns:
            An instance of the appropriate coin class, or None if the coin is not supported.
        """
        if coin_symbol == "btc":
            coin = coins.bitcoin.Bitcoin(testnet=self.testnet)
        elif coin_symbol == "ltc":
            coin = coins.litecoin.Litecoin(testnet=self.testnet)
        elif coin_symbol == "bch":
            coin = coins.bitcoin_cash.BitcoinCash(testnet=self.testnet)
        elif coin_symbol == "dash":
            coin = coins.dash.Dash(testnet=self.testnet)
        elif coin_symbol == "doge":
            coin = coins.dogecoin.Doge(testnet=self.testnet)
        else:
            print(f"coin({coin_symbol}) not available. process stopped.")
            return None
        return coin

    def make_wallet(
        self,
        # xpub_extended_public_key: str = "",
        print_result: bool = True,
    ) -> HDWallet:

        # ['btc', 'ltc', 'bch', 'dash', 'doge']
        coin: Union[
            coins.bitcoin.Bitcoin,
            coins.litecoin.Litecoin,
            coins.bitcoin_cash.BitcoinCash,
            coins.dash.Dash,
            coins.dogecoin.Doge,
            None,
        ] = self.get_coin_instance(coin_symbol=self.coin_symbol)

        if coin == None:
            print(f"coin({self.coin_symbol}) not available. process stoped. ")
            return
            # coin: BaseCoin = get_coin(coin_symbol=coin_symbol, testnet=testnet)
        print("-")

        mnemonic_words_seed: str = mnemonic.entropy_to_words(entbytes=os.urandom(20))
        if mnemonic_words_seed:

            print(self.line_symbol * self.line_length)
            print(f"created mnemonic_words_seed(wordlist_english):")
            print(f"mnemonic_words_seed: {mnemonic_words_seed}")
            print(self.line_symbol * self.line_length)

        is_checksum_valid, is_wordlist_valid = keystore.bip39_is_checksum_valid(
            mnemonic=mnemonic_words_seed
        )
        print(self.line_symbol * self.line_length)
        print(f"Checking mnemonic_words_seed if it is valid:")
        print(
            f"is_checksum_valid, is_wordlist_valid = keystore.bip39_is_checksum_valid(mnemonic=mnemonic_words_seed)"
        )
        print(f"is_checksum_valid: {is_checksum_valid}")
        print(f"is_wordlist_valid: {is_wordlist_valid}")
        print(self.line_symbol * self.line_length)
        if is_checksum_valid == False:
            print(f"is_checksum_valid=False at: {mnemonic_words_seed}")
            return

        if is_wordlist_valid == False:
            print(f"is_wordlist_valid=False at: {is_wordlist_valid}")
            return

        # passphrase: str = "test"
        ## TODO wallet fertig machen
        # wallet: HDWallet = coin.wallet(seed=mnemonic_words_seed, passphrase=passphrase)
        passphrase: str = "test"
        hd_wallet: HDWallet = coin.wallet(
            seed=mnemonic_words_seed,
            passphrase=passphrase,
        )
        xpub: str = hd_wallet.keystore.xpub
        xprv: str = hd_wallet.keystore.xprv
        is_watching_only: bool = hd_wallet.is_watching_only

        print(self.line_symbol * self.line_length)
        print(f"created new wallet for {coin_symbol}")
        print(self.line_symbol * self.line_length)

        print(self.line_symbol * self.line_length)
        print(f"hd_wallet.keystore.xpub: {xpub}")
        print(f"hd_wallet.keystore.xprv: {xprv}")
        print(f"hd_wallet.is_watching_only: {is_watching_only}")
        print(self.line_symbol * self.line_length)

        new_receiving_address: str = hd_wallet.new_receiving_address()
        new_receiving_address_priv_key: str = hd_wallet.privkey(
            address=new_receiving_address
        )
        new_change_address: str = hd_wallet.new_change_address()

        new_change_address_priv_key: str = hd_wallet.privkey(address=new_change_address)
        print(self.line_symbol * self.line_length)
        print(f"created new adresses in the new  {coin_symbol} wallet.")
        print(f"hd_wallet.new_receiving_address(): {new_receiving_address}")
        print(
            f"hd_wallet.privkey(address=new_receiving_address): {new_receiving_address_priv_key} (normally not shown)"
        )
        print(f"hd_wallet.new_change_address(): {new_change_address}")
        print(
            f"hd_wallet.privkey(address=new_change_address): {new_change_address_priv_key} (normally not shown)"
        )
        print(self.line_symbol * self.line_length)

        # if coin.is_segwit_or_p2sh(addr=pub_address) == False:
        #     print(f"{self.coin_symbol} not a address: {pub_address}")
        coin_is_address: bool = coin.is_address(addr=new_receiving_address)
        if coin_is_address == False:
            print(
                f"coin.is_address(addr=new_receiving_address) says false for:{new_receiving_address}"
            )
        coin_is_address = False
        coin_is_address: bool = coin.is_address(addr=new_change_address)
        if coin_is_address == False:
            print(
                f"coin.is_address(addr=new_change_address) says false for:{new_change_address}"
            )
        wallet_addresses = hd_wallet.addresses
        print(self.line_symbol * self.line_length)
        print(
            f"wallet_addresses=hd_wallet.addresses. (showing all addresses in the wallet)"
        )
        print(f"{wallet_addresses}")
        print(self.line_symbol * self.line_length)

        print(self.line_symbol * self.line_length)
        print(f"test it: {self.some_validate_link}")
        print(self.line_symbol * self.line_length)
        print(self.line_symbol * self.line_length)
        print(f"test it(testnet): {self.some_validate_link_2}")
        print(self.line_symbol * self.line_length)

        return hd_wallet

    def print_result(
        self,
        pub_address: str,
    ):
        net: str = f"Mainnet(the real {self.coin_symbol} blockchain)"
        if self.testnet == True:
            net = f"Testnet(the test net for {self.coin_symbol}.)"
        print(f"here are the printed result this is a TODO")

        # # print("\n" + self.line_symbol * self.line_length)
        # print(self.line_symbol * self.line_length)
        # print(f"Created {self.coin_symbol} address  Network: {net}")
        # print(self.line_symbol * self.line_length)

        # print(
        #     f"{self.coin_symbol}:{'Private Key:':<{self.margin1}}{privkey:<{self.margin2}}"
        # )

        # print(
        #     f"{self.coin_symbol}:{'Public_address:':<{self.margin1}}{pub_address:<{self.margin2}}"
        # )

        # if pub_address_segwit != "":
        #     segwit_info_short: str = "(newer btc address version)"
        #     print(
        #         f"{self.coin_symbol}:{'pub_address_segwit:':<{self.margin1}}{pub_address_segwit:<{self.margin2}} {segwit_info_short}"
        #     )
        #     segwit_info: str = (
        #         f"A SegWit address is a newer type of Bitcoin address that uses a different format than traditional Bitcoin addresses. SegWit stands for 'Segregated Witness,' and it's a way to improve the efficiency and security of Bitcoin transactions. (starts with(bc1))"
        #     )

        #     print(self.line_symbol * self.line_length)
        #     print(f"{segwit_info}")
        #     print(self.line_symbol * self.line_length)

        # print(self.line_symbol * self.line_length)
        # print(f"test it: {self.some_validate_link}")
        # print(self.line_symbol * self.line_length)
        # print(self.line_symbol * self.line_length)
        # print(f"test it(testnet): {self.some_validate_link_2}")
        # print(self.line_symbol * self.line_length)

    def print_available_coins(
        self,
    ):

        # print()
        print(self.line_symbol * self.line_length)
        print(f"Available Coins: {script_utils.coin_list}")
        print(self.line_symbol * self.line_length)


# def main(random_256_bit_hex: str):

#     coin_symbol: str = "btc"
#     testnet: bool = False
#     coin: BaseCoin = get_coin(coin_symbol=coin_symbol, testnet=testnet)
#     # mnemonic.entropy_to_words(os.urandom(16))
#     mnemonic_words_seed: str = mnemonic.entropy_to_words(entbytes=os.urandom(20))

#     is_checksum_valid, is_wordlist_valid = keystore.bip39_is_checksum_valid(
#         mnemonic=mnemonic_words_seed
#     )
#     passphrase: str = "test"
#     # TODO wallet fertig machen
#     wallet: HDWallet = coin.wallet(seed=mnemonic_words_seed, passphrase=passphrase)
#     margin: int = 47
#     print("")
#     print("-" * 40)
#     print("Available Coins:")
#     print("-" * 40)
#     for coin_str in coin_list:
#         print(coin_str)
#     # print("-" * 40)

#     print("\n" + "-" * 40)
#     print("Generated Keys:")
#     print("-" * 40)
#     print(f"{'Key Type':<{margin}} {'Value':<60}")

#     # random_256_bit_hex: str = generate_private_key()
#     print(f"{coin_symbol}:{'random (256_bit_hex):':<{margin}}{random_256_bit_hex:<60}")
#     public_coin_address: str = coin.privtoaddr(privkey=random_256_bit_hex)
#     print(f"{coin_symbol}:{'Public_address:':<{margin}}{public_coin_address:<60}")
#     # coin.watch_wallet
#     watch_wallet: HDWallet = coin.watch_wallet(xpub=public_coin_address)
#     priv_key_hex_compr = coin.encode_privkey(
#         privkey=random_256_bit_hex,
#         formt="hex_compressed",
#     )

#     print(
#         f"{coin_symbol}:{'Private Key (hex_compressed)':<{margin}}{priv_key_hex_compr:<60}"
#     )

#     pub_key_hash_wif_compressed = coin.encode_privkey(
#         privkey=random_256_bit_hex,
#         formt="wif_compressed",
#         script_type="p2pkh",
#     )
#     print(
#         f"{coin_symbol}:{'Public Address (wif_compressed):':<{margin}}{pub_key_hash_wif_compressed:<60}"
#     )
#     # print(f"{'P2PKH Address':<{margin}} {coin.privtoaddr(pub_key_hash_wif_compressed):<60}")

#     if coin.segwit_supported:
#         private_key_p2wpkh_p2sh = coin.encode_privkey(
#             random_256_bit_hex,
#             formt="wif_compressed",
#             script_type="p2wpkh-p2sh",
#         )
#         print(
#             f"{coin_symbol}:{'WIF P2WPKH-P2SH':<{margin}}{private_key_p2wpkh_p2sh:<60}"
#         )
#         pay_to_witness_public_key_hash_address = coin.privtop2wpkh_p2sh(
#             private_key_p2wpkh_p2sh
#         )

#         print(
#             f"{coin_symbol}:{'P2WPKH-P2SH':<{margin}}{pay_to_witness_public_key_hash_address:<60}"
#         )
#         private_key_p2wpkh = coin.encode_privkey(
#             random_256_bit_hex,
#             formt="wif_compressed",
#             script_type="p2wpkh",
#         )
#         print(
#             f"{coin_symbol}:{'WIF Native Segwit P2WPKH':<{margin}}{private_key_p2wpkh:<60}"
#         )
#         P2WPKH_address: str = coin.privtosegwitaddress(
#             privkey=private_key_p2wpkh,
#         )
#         print(f"{coin_symbol}:{'P2WPKH Address':<{margin}}{P2WPKH_address:<60}")

#     print("\n" + "-" * 40)
#     print("Key (Address) Types:")
#     print("-" * 40)

#     print(
#         f"{'WIF: (Wallet Import Format):':<{margin}}{'- A standard format for storing private keys.':<60}"
#     )

#     print(
#         f"{'P2PKH: (Pay-to-Public-Key-Hash):':<{margin}}{'- P2PKH addresses start with a 1.':<60}"
#     )
#     print(
#         f"{'P2WPKH: (Pay-to-Witness-Public-Key-Hash):':<{margin}}{'- A Segwit address type (prefix of bc1q) public address.':<60}"
#     )

#     print(
#         f"{'P2WPKH-P2SH: (Pay-to-Witness-Public-Key-Hash):':<{margin}}{'- nested in P2SH  A Segwit address type.':<60}"
#     )


if __name__ == "__main__":
    coin_symbol: str = "btc"
    create_wallet_watch_only: Create_Wallet_helper = Create_Wallet_helper(
        coin_symbol=coin_symbol
    )
    # privkey: str = ""
    # pub_address: str = ""
    # pub_address: str = "DEi98svyRa5HrgVRXqi3irmTi5VVmAbJus"  # not a xpub
    pub_address: str = (
        "bc1qte0s6pz7gsdlqq2cf6hv5mxcfksykyyyjkdfd5"  # this is not a xpub
    )
    hd_wallet: HDWallet = create_wallet_watch_only.make_wallet()
    # if hd_wallet:
    #     hd_wallet_addresses = hd_wallet.addresses
    #     # watch_wallet.preparetx()
    #     print(f"hd_wallet_addresses:{hd_wallet_addresses}")
    #     # create_new_address.print_available_coins()


# process
# Or if you prefer to verify the tx (for example, at https://live.blockcypher.com/btc/decodetx/) you can break it into two steps:

# > from cryptos import *
# > c = Bitcoin(testnet=True)
# > tx = c.preparesignedtx("89d8d898b95addf569b458fbbd25620e9c9b19c9f730d5d60102abbabcb72678", "tb1qsp907fjefnpkczkgn62cjk4ehhgv2s805z0dkv", "tb1q95cgql39zvtc57g4vn8ytzmlvtt43skngdq0ue", 5000)
# > serialize(tx)
# '010000000001014ae7e7fdead71cc8303c5b5e68906ecbf978fb9d84f5f9dd505823356b9a1d6e0000000000ffffffff0288130000000000001600142d30807e2513178a791564ce458b7f62d758c2d3a00f000000000000160014804aff26594cc36c0ac89e95895ab9bdd0c540ef02483045022100cff4e64a4dd0f24c1f382e4b949ae852a89a5f311de50cd13d3801da3669675c0220779ebcb542dc80dae3e16202c0b58dd60261662f3b3a558dca6ddf22e30ca4230121031f763d81010db8ba3026fef4ac3dc1ad7ccc2543148041c61a29e883ee4499dc00000000'
# > c.pushtx(tx)
# '6a7c437b0de10c42f2e9e18cc004e87712dbda73a851a0ea6774749a290c7e7d'


# > tx = coin.preparetx(address, "myLktRdRh3dkK3gnShNj5tZsig6J1oaaJW", 1100000, 50000)
