from .bitcoin import BaseCoin

# from pybitcointools.cryptos.coins_async.bitcoin import BaseCoin


class Doge(BaseCoin):
    """
    Represents Dogecoin, a cryptocurrency, within a Python framework.

    This class inherits from the BaseCoin class, providing core functionality for
    handling cryptocurrencies.
    It defines specific attributes tailored to Dogecoin,
    including its coin symbol, display name, network parameters,
    and client configuration.

    Attributes:
        coin_symbol (str): The ticker symbol for Dogecoin, which is "DOGE".
        display_name (str): The full name of the cryptocurrency, "Dogecoin".
        segwit_supported (bool): Indicates whether Dogecoin supports SegWit (Segregated Witness), a technology that
            improves transaction efficiency and reduces fees. False for Dogecoin.
        magicbyte (int): A hexadecimal value representing the magic byte used in Dogecoin's network for identifying
            the blockchain. Value is 0x1e.
        minimum_fee (int): The minimum fee (in satoshis) required for a Dogecoin transaction. Value is 300000.
        script_magicbyte (int): Another hexadecimal value representing the magic byte used in Dogecoin's network
            for identifying scripts. Value is 0x16.
        wif_prefix (int): The prefix used for Wallet Import Format (WIF) private keys in Dogecoin. Value is 0x9e.
        segwit_hrp (str): The human-readable part (HRP) used for Bech32 addresses in Dogecoin. Value is "doge".
        hd_path (int): The default path for generating hierarchical deterministic (HD) wallets for Dogecoin.
            Value is 3.
        client_kwargs (dict): A dictionary containing configuration settings for interacting with a Dogecoin client,
            including the server file and whether to use SSL.
        xpriv_prefix (int): The prefix used for extended private keys (xpriv) in Dogecoin. Value is 0x02facafd.
        xpub_prefix (int): The prefix used for extended public keys (xpub) in Dogecoin. Value is 0x02fac398.
        testnet_overrides (dict): A dictionary containing attributes that override the mainnet values when working
            with the Dogecoin testnet. This allows for testing and development without impacting real transactions.

    Example:
        >>> doge = Doge()
        >>> doge.coin_symbol
        'DOGE'
        >>> doge.magicbyte
        0x1e
    """

    coin_symbol = "DOGE"
    display_name = "Dogecoin"
    segwit_supported = False
    magicbyte = 0x1E
    minimum_fee = 300000
    script_magicbyte = 0x16
    wif_prefix: int = 0x9E
    segwit_hrp = "doge"
    hd_path = 3
    client_kwargs = {"server_file": "doge.json", "use_ssl": False}
    xpriv_prefix = 0x02FACAFD
    xpub_prefix = 0x02FAC398
    testnet_overrides = {
        "display_name": "Dogecoin Testnet",
        "coin_symbol": "Dogecoin",
        "magicbyte": 0x71,
        "script_magicbyte": 0xC4,
        "hd_path": 1,
        "wif_prefix": 0xF1,
        "segwit_hrp": "xdoge",
        "minimum_fee": 300000,
        "client_kwargs": {"server_file": "doge_testnet.json", "use_ssl": False},
        "xpriv_prefix": 0x04358394,
        "xpub_prefix": 0x043587CF,
    }
