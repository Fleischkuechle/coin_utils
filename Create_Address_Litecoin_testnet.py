from Create_Address_Helper import Create_Address_Helper
from typing import Tuple


class Create_Address_Litecoin:
    def __init__(
        self,
        testnet: bool = True,  # testnet
    ):
        self.coin_symbol: str = "ltc"
        self.create_address_helper: Create_Address_Helper = Create_Address_Helper(
            coin_symbol=self.coin_symbol,
            testnet=testnet,
        )

    def make_address_doge(
        self,
        print_result: bool = True,
    ) -> Tuple[str, str]:
        privkey: str = ""
        pub_address: str = ""
        privkey, pub_address = self.create_address_helper.make_address(
            print_result=print_result
        )

        return privkey, pub_address

    def print_available_coins(
        self,
    ):
        self.create_address_helper.print_available_coins()


if __name__ == "__main__":
    create_new_address: Create_Address_Litecoin = Create_Address_Litecoin()
    privkey: str = ""
    pub_address: str = ""
    privkey, pub_address = create_new_address.make_address_doge()
    # create_new_address.print_available_coins()
