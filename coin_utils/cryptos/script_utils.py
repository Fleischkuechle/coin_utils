from cryptos.coins_async import BaseCoin, Bitcoin, BitcoinCash, Dash, Litecoin, Doge


coins = {c.coin_symbol: c for c in (Bitcoin, Litecoin, BitcoinCash, Dash, Doge)}


def get_coin_original(coin_symbol: str, testnet: bool) -> BaseCoin:
    symbol = coin_symbol.upper()
    return coins[symbol](testnet=testnet)


def get_coin(coin_symbol: str, testnet: bool) -> BaseCoin:
    """
    Retrieves a coin object based on its symbol and testnet status.

    This function looks up the coin class associated with the provided symbol in the `coins` dictionary and instantiates it with the specified testnet flag.

    Args:
        coin_symbol (str): The symbol of the desired cryptocurrency (e.g., 'BTC', 'ETH').
        testnet (bool): Whether to use the testnet network for the coin.

    Returns:
        BaseCoin: An instance of the coin class corresponding to the provided symbol and testnet status.
    """
    symbol = coin_symbol.upper()
    return coins[symbol](testnet=testnet)


coin_list = [c.lower() for c in coins.keys()]
