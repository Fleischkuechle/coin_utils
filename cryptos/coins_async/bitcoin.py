from ..explorers import blockchain
from .base import BaseCoin
from ..main import *


class Bitcoin(BaseCoin):
    coin_symbol = "BTC"
    display_name = "Bitcoin"
    segwit_supported = True
    magicbyte = 0
    script_magicbyte = 5
    minimum_fee = 450  # satoshis minimum_fee/1 000 000 =minimum_fee_as_btc
    segwit_hrp = "bc"
    wif_prefix: int = 0x80
    client_kwargs = {
        "server_file": "bitcoin.json",
    }

    testnet_overrides = {
        "display_name": "Bitcoin Testnet",
        "coin_symbol": "BTCTEST",
        "magicbyte": 111,
        "script_magicbyte": 196,
        "segwit_hrp": "tb",
        "hd_path": 1,
        "wif_prefix": 0xEF,
        "minimum_fee": 1000,
        "client_kwargs": {"server_file": "bitcoin_testnet.json", "use_ssl": False},
        "electrum_pkey_format": "wif",
        "xprv_headers": {
            "p2pkh": 0x04358394,
            "p2wpkh-p2sh": 0x044A4E28,
            "p2wsh-p2sh": 0x295B005,
            "p2wpkh": 0x04358394,
            "p2wsh": 0x2AA7A99,
        },
        "xpub_headers": {
            "p2pkh": 0x043587CF,
            "p2wpkh-p2sh": 0x044A5262,
            "p2wsh-p2sh": 0x295B43F,
            "p2wpkh": 0x043587CF,
            "p2wsh": 0x2AA7ED3,
        },
    }
