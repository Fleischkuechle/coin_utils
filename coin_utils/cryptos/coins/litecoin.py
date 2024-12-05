# try:
#     from pybitcointools.cryptos.coins_async.litecoin import Litecoin as AsyncLitecoin
# except:
#     from cryptos.coins_async.litecoin import Litecoin as AsyncLitecoin


from cryptos.coins_async.litecoin import Litecoin as AsyncLitecoin
from .base import BaseSyncCoin


class Litecoin(BaseSyncCoin):
    coin_class = AsyncLitecoin
