from Get_Expected_Address_Helper import Get_Expected_Address_Helper


class Get_Expected_Address_Btc:
    def __init__(
        self,
    ):

        self.coin_symbol: str = "btc"
        self.testnet: bool = False
        self.get_expected_address_helper: Get_Expected_Address_Helper = (
            Get_Expected_Address_Helper(
                coin_symbol=self.coin_symbol,
                testnet=self.testnet,
            )
        )

    # def address_check(
    #     self,
    #     addr: str,
    #     privkey: str,
    # ):
    #     try:
    #         self.get_expected_address_helper.address_check(
    #             coin=self.coin_symbol,
    #             testnet=self.testnet,
    #             addr=addr,
    #             privkey=privkey,
    #         )
    #     except Exception as e:
    #         print(f"Exception: {e}")
    def address_check(
        self,
        addr: str,
        privkey: str,
    ) -> bool:
        address_match: bool = False
        try:
            address_match = self.get_expected_address_helper.address_check(
                coin=self.coin_symbol,
                testnet=self.testnet,
                addr=addr,
                privkey=privkey,
            )
            return address_match
        except Exception as e:
            print(f"Exception: {e}")
            return address_match


def test():
    # Created with Create_Address_Btc.py
    # btc:Private Key:        8c6c77a7eb3a4bbbe7e988c4c2b48fbaeb73a31bd3ab3dd2b415e25e10d7e6df
    # btc:Public_address:     1JNiv4AHXzc2ZnN7oMaynQD5NjtZ2DZThy
    # btc:pub_address_segwit: bc1qs0v6c4vtfcltqzt5f0zkm3ctr7lrrtvhkz3y8z (newer btc address version)
    addr: str = "bc1qs0v6c4vtfcltqzt5f0zkm3ctr7lrrtvhkz3y8z"  # test address doge 1
    privkey: str = (
        "8c6c77a7eb3a4bbbe7e988c4c2b48fbaeb73a31bd3ab3dd2b415e25e10d7e6df"  # the uncorrect private key for # test address doge 1
    )
    get_expected_address_btc: Get_Expected_Address_Btc = Get_Expected_Address_Btc()
    address_match: bool = False
    address_match = get_expected_address_btc.address_check(
        addr=addr,
        privkey=privkey,
    )
    print(f"address_match = {address_match}")


if __name__ == "__main__":
    test()
