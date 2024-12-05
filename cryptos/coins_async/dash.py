from .base import BaseCoin
from ..explorers import dash_siampm

# from pybitcointools.cryptos.explorers import dash_siampm
# from pybitcointools.cryptos.coins_async.base import BaseCoin


class Dash(BaseCoin):
    coin_symbol = "DASH"
    display_name = "Dash"
    segwit_supported = False
    magicbyte = 0x4C
    script_magicbyte = 0x10
    wif_prefix = 0xCC
    hd_path = 5
    client_kwargs = {
        "server_file": "dash.json",
    }
    testnet_overrides = {
        "display_name": "Dash Testnet",
        "coin_symbol": "DASHTEST",
        "magicbyte": 140,
        "script_magicbyte": 19,
        "wif_prefix": 0xEF,
        "hd_path": 1,
        "client_kwargs": {"server_file": "dash_testnet.json", "use_ssl": True},
        "xpriv_prefix": 0x04358394,
        "xpub_prefix": 0x043587CF,
    }
