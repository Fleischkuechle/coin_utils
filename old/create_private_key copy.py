from cryptos.main import *
from cryptos.script_utils import get_coin, coin_list


def main():
    print(coin_list)
    coin_symbol: str = "btc"
    testnet: bool = False
    coin: BaseCoin = get_coin(coin_symbol=coin_symbol, testnet=testnet)

    private_key: str = generate_private_key()
    # private_key_compressed = encode_privkey(private_key, formt="hex_compressed")
    private_key_compressed = coin.encode_privkey(private_key, formt="hex_compressed")
    print(f"Private key: {private_key_compressed}")
    private_key_p2pkh = coin.encode_privkey(
        private_key, formt="wif_compressed", script_type="p2pkh"
    )
    print(f"WIF(Wallet Import Format) P2PKH: {private_key_p2pkh}")
    print(f"P2PKH Address: {coin.privtoaddr(private_key_p2pkh)}")
    if coin.segwit_supported:
        private_key_p2wpkh_p2sh = coin.encode_privkey(
            private_key,
            formt="wif_compressed",
            script_type="p2wpkh-p2sh",
        )
        print(f"WIF(Wallet Import Format) P2WPKH-P2SH: {private_key_p2wpkh_p2sh}")
        pay_to_witness_public_key_hash_address = coin.privtop2wpkh_p2sh(
            private_key_p2wpkh_p2sh
        )

        print(
            f"P2WPKH-P2SH(pay_to_witness_public_key_hash_address) Segwit Address: {pay_to_witness_public_key_hash_address}"
        )
        private_key_p2wpkh = coin.encode_privkey(
            private_key, formt="wif_compressed", script_type="p2wpkh"
        )
        print(f"WIF(Wallet Import Format) Native Segwit P2WPKH: {private_key_p2wpkh}")
        print(
            f"Native Segwit P2WPKH Address: {coin.privtosegwitaddress(private_key_p2wpkh)}"
        )


if __name__ == "__main__":
    main()
