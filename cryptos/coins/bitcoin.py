from .base import BaseSyncCoin
from ..coins_async import Bitcoin as AsyncBitcoin

# except:
#     from cryptos.coins_async.bitcoin import Bitcoin as AsyncBitcoin
#     from cryptos.coins_async.bitcoin import Bitcoin as AsyncBitcoin

# from .base import BaseSyncCoin


class Bitcoin(BaseSyncCoin):
    coin_class = AsyncBitcoin
