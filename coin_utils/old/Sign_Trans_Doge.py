from cryptos import main
from cryptos import coins


class Sign_Trans_Doge:
    def __init__(self):
        self.coin_symbol: str = "doge"

    def print_result(
        self,
    ):
        pass


if __name__ == "__main__":
    coin: coins.dogecoin.Doge = coins.dogecoin.Doge()
    privkey: str = ""
    pub_address: str = ""
    privkey: str = main.generate_private_key()
    pub_address: str = coin.privtoaddr(privkey=privkey)

    sign_trans_doge: Sign_Trans_Doge = Sign_Trans_Doge()
    inputs = coin.unspent(addr=pub_address)
    print()
