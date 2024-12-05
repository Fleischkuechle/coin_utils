from cryptos.main import *
from cryptos.script_utils import get_coin, coin_list

# from pybitcointools import cryptos
from cryptos import mnemonic
from cryptos import keystore
from cryptos.wallet import HDWallet


def main(random_256_bit_hex: str):

    coin_symbol: str = "btc"
    testnet: bool = False
    coin: BaseCoin = get_coin(coin_symbol=coin_symbol, testnet=testnet)
    # mnemonic.entropy_to_words(os.urandom(16))
    mnemonic_words: str = mnemonic.entropy_to_words(entbytes=os.urandom(20))

    is_checksum_valid, is_wordlist_valid = keystore.bip39_is_checksum_valid(
        mnemonic=mnemonic_words
    )
    passphrase: str = "test"
    # TODO wallet fertig machen
    wallet: HDWallet = coin.wallet(seed=mnemonic_words, passphrase=passphrase)
    margin: int = 47
    print("")
    print("-" * 40)
    print("Available Coins:")
    print("-" * 40)
    for coin_str in coin_list:
        print(coin_str)
    # print("-" * 40)

    print("\n" + "-" * 40)
    print("Generated Keys:")
    print("-" * 40)
    print(f"{'Key Type':<{margin}} {'Value':<60}")

    # random_256_bit_hex: str = generate_private_key()
    print(f"{coin_symbol}:{'random (256_bit_hex):':<{margin}}{random_256_bit_hex:<60}")
    public_coin_address: str = coin.privtoaddr(privkey=random_256_bit_hex)
    print(f"{coin_symbol}:{'Public_address:':<{margin}}{public_coin_address:<60}")
    # coin.watch_wallet
    watch_wallet: HDWallet = coin.watch_wallet(xpub=public_coin_address)
    priv_key_hex_compr = coin.encode_privkey(
        privkey=random_256_bit_hex,
        formt="hex_compressed",
    )

    print(
        f"{coin_symbol}:{'Private Key (hex_compressed)':<{margin}}{priv_key_hex_compr:<60}"
    )

    pub_key_hash_wif_compressed = coin.encode_privkey(
        privkey=random_256_bit_hex,
        formt="wif_compressed",
        script_type="p2pkh",
    )
    print(
        f"{coin_symbol}:{'Public Address (wif_compressed):':<{margin}}{pub_key_hash_wif_compressed:<60}"
    )
    # print(f"{'P2PKH Address':<{margin}} {coin.privtoaddr(pub_key_hash_wif_compressed):<60}")

    if coin.segwit_supported:
        private_key_p2wpkh_p2sh = coin.encode_privkey(
            random_256_bit_hex,
            formt="wif_compressed",
            script_type="p2wpkh-p2sh",
        )
        print(
            f"{coin_symbol}:{'WIF P2WPKH-P2SH':<{margin}}{private_key_p2wpkh_p2sh:<60}"
        )
        pay_to_witness_public_key_hash_address = coin.privtop2wpkh_p2sh(
            private_key_p2wpkh_p2sh
        )

        print(
            f"{coin_symbol}:{'P2WPKH-P2SH':<{margin}}{pay_to_witness_public_key_hash_address:<60}"
        )
        private_key_p2wpkh = coin.encode_privkey(
            random_256_bit_hex,
            formt="wif_compressed",
            script_type="p2wpkh",
        )
        print(
            f"{coin_symbol}:{'WIF Native Segwit P2WPKH':<{margin}}{private_key_p2wpkh:<60}"
        )
        P2WPKH_address: str = coin.privtosegwitaddress(
            privkey=private_key_p2wpkh,
        )
        print(f"{coin_symbol}:{'P2WPKH Address':<{margin}}{P2WPKH_address:<60}")

    print("\n" + "-" * 40)
    print("Key (Address) Types:")
    print("-" * 40)

    print(
        f"{'WIF: (Wallet Import Format):':<{margin}}{'- A standard format for storing private keys.':<60}"
    )

    print(
        f"{'P2PKH: (Pay-to-Public-Key-Hash):':<{margin}}{'- P2PKH addresses start with a 1.':<60}"
    )
    print(
        f"{'P2WPKH: (Pay-to-Witness-Public-Key-Hash):':<{margin}}{'- A Segwit address type (prefix of bc1q) public address.':<60}"
    )

    print(
        f"{'P2WPKH-P2SH: (Pay-to-Witness-Public-Key-Hash):':<{margin}}{'- nested in P2SH  A Segwit address type.':<60}"
    )


if __name__ == "__main__":
    random_256_bit_hex: str = generate_private_key()
    # random_256_bit_hex: str = (
    #     "d88dc3d60f94a4ec31b04e54b45fc5e640e0f1204a63cee11214b927636f479a"
    # )
    main(random_256_bit_hex=random_256_bit_hex)

    # main(random_256_bit_hex=random_256_bit_hex)


# > from cryptos import *
# > c = Bitcoin(testnet=True)
# > priv = sha256('a big long brainwallet password')
# > priv
# '89d8d898b95addf569b458fbbd25620e9c9b19c9f730d5d60102abbabcb72678'
# > pub = c.privtopub(priv)
# > pub
# '041f763d81010db8ba3026fef4ac3dc1ad7ccc2543148041c61a29e883ee4499dc724ab2737afd66e4aacdc0e4f48550cd783c1a73edb3dbd0750e1bd0cb03764f'
# > addr = c.pubtoaddr(pub)
# > addr
# 'mwJUQbdhamwemrsR17oy7z9upFh4JtNxm1'
# > inputs = c.unspent(addr)
# > inputs
# [{'height': 0, 'tx_hash': '6d7a1b133f5ad2ce77d8980a1c84d7b595e4085d5a4a6d347e8a92df6ffc31f5', 'tx_pos': 0, 'value': 7495, 'address': 'mwJUQbdhamwemrsR17oy7z9upFh4JtNxm1'}, {'height': 0, 'tx_hash': 'e1e7b62e5eb4d399c75649e9256a91f0371268ca265ab9265a433bb263baf2f2', 'tx_pos': 0, 'value': 1866771, 'address': 'mwJUQbdhamwemrsR17oy7z9upFh4JtNxm1'}]
# > outs = [{'value': 1000000, 'address': 'tb1q95cgql39zvtc57g4vn8ytzmlvtt43skngdq0ue'}, {'value': sum(i['value'] for i in inputs) - 1000000 - 750 , 'address': 'mwJUQbdhamwemrsR17oy7z9upFh4JtNxm1'}]
# outs
# [{'value': 1000000, 'address': 'tb1q95cgql39zvtc57g4vn8ytzmlvtt43skngdq0ue'}, {'value': 873516, 'address': 'mwJUQbdhamwemrsR17oy7z9upFh4JtNxm1'}]
# > tx = c.mktx(inputs,outs)
# > tx
# {'locktime': 0, 'version': 1, 'ins': [{'height': 0, 'tx_hash': '6d7a1b133f5ad2ce77d8980a1c84d7b595e4085d5a4a6d347e8a92df6ffc31f5', 'tx_pos': 0, 'value': 7495, 'address': 'mwJUQbdhamwemrsR17oy7z9upFh4JtNxm1', 'script': '', 'sequence': 4294967295}, {'height': 0, 'tx_hash': 'e1e7b62e5eb4d399c75649e9256a91f0371268ca265ab9265a433bb263baf2f2', 'tx_pos': 0, 'value': 1866771, 'address': 'mwJUQbdhamwemrsR17oy7z9upFh4JtNxm1', 'script': '', 'sequence': 4294967295}], 'outs': [{'value': 1000000, 'script': '00142d30807e2513178a791564ce458b7f62d758c2d3'}, {'value': 873516, 'script': '76a914ad25bdf0fdfd21ca91a82449538dce47f8dc213d88ac'}]}
# > tx2 = c.signall(tx, priv)
# > tx2
# {'locktime': 0, 'version': 1, 'ins': [{'height': 0, 'tx_hash': '6d7a1b133f5ad2ce77d8980a1c84d7b595e4085d5a4a6d347e8a92df6ffc31f5', 'tx_pos': 0, 'value': 7495, 'address': 'mwJUQbdhamwemrsR17oy7z9upFh4JtNxm1', 'script': '473044022012ba62de78427811650f868209572404a0846bf60b3a3705799877bb5351827702202bcadc067f5dce01ecf10306e033a905a156aec71d769bcffc0e221a0c91c6030141041f763d81010db8ba3026fef4ac3dc1ad7ccc2543148041c61a29e883ee4499dc724ab2737afd66e4aacdc0e4f48550cd783c1a73edb3dbd0750e1bd0cb03764f', 'sequence': 4294967295}, {'height': 0, 'tx_hash': 'e1e7b62e5eb4d399c75649e9256a91f0371268ca265ab9265a433bb263baf2f2', 'tx_pos': 0, 'value': 1866771, 'address': 'mwJUQbdhamwemrsR17oy7z9upFh4JtNxm1', 'script': '47304402205c9b724d2499f167b9557b8efd13b8b2109ae287b712f2db1d3d46cfc31c71a702201a74bda43116977c4605d499177152afd3965b2fe586f3236053786ef19e96090141041f763d81010db8ba3026fef4ac3dc1ad7ccc2543148041c61a29e883ee4499dc724ab2737afd66e4aacdc0e4f48550cd783c1a73edb3dbd0750e1bd0cb03764f', 'sequence': 4294967295}], 'outs': [{'value': 1000000, 'script': '00142d30807e2513178a791564ce458b7f62d758c2d3'}, {'value': 873516, 'script': '76a914ad25bdf0fdfd21ca91a82449538dce47f8dc213d88ac'}]}
# > tx3 = serialize(tx2)
# > tx3
# '0100000002f531fc6fdf928a7e346d4a5a5d08e495b5d7841c0a98d877ced25a3f131b7a6d000000008a473044022012ba62de78427811650f868209572404a0846bf60b3a3705799877bb5351827702202bcadc067f5dce01ecf10306e033a905a156aec71d769bcffc0e221a0c91c6030141041f763d81010db8ba3026fef4ac3dc1ad7ccc2543148041c61a29e883ee4499dc724ab2737afd66e4aacdc0e4f48550cd783c1a73edb3dbd0750e1bd0cb03764ffffffffff2f2ba63b23b435a26b95a26ca681237f0916a25e94956c799d3b45e2eb6e7e1000000008a47304402205c9b724d2499f167b9557b8efd13b8b2109ae287b712f2db1d3d46cfc31c71a702201a74bda43116977c4605d499177152afd3965b2fe586f3236053786ef19e96090141041f763d81010db8ba3026fef4ac3dc1ad7ccc2543148041c61a29e883ee4499dc724ab2737afd66e4aacdc0e4f48550cd783c1a73edb3dbd0750e1bd0cb03764fffffffff0240420f00000000001600142d30807e2513178a791564ce458b7f62d758c2d32c540d00000000001976a914ad25bdf0fdfd21ca91a82449538dce47f8dc213d88ac00000000'
# > c.pushtx(tx3)
# 'd5b5b148285da8ddf9d719627c21f5cbbb3e17ae315dbb406301b9ac9c5621e5'
