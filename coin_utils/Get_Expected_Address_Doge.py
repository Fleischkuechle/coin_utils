from Get_Expected_Address_Helper import Get_Expected_Address_Helper


class Get_Expected_Address_Doge:
    def __init__(
        self,
    ):

        self.coin_symbol: str = "doge"
        self.testnet: bool = False
        self.get_expected_address_helper: Get_Expected_Address_Helper = (
            Get_Expected_Address_Helper(
                coin_symbol=self.coin_symbol,
                testnet=self.testnet,
            )
        )

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
    # Created with Create_Address_Doge.py
    # doge:Private Key:        ea71e78cf1733347abb13b153d04a468093f160303255459e0505d274fa100ab
    # doge:Public_address:     DDASXg8LNY1gu2b5kCC5H1BpkhoD9UQihS
    addr: str = "DDASXg8LNY1gu2b5kCC5H1BpkhoD9UQihS"  # test address 300 doge 1
    privkey: str = (
        "ea71e78cf1733347abb13b153d04a468093f160303255459e0505d274fa100ab"  # the uncorrect private key for # test address 300 doge 1
    )
    get_expected_address_doge: Get_Expected_Address_Doge = Get_Expected_Address_Doge()

    address_match: bool = False
    address_match = get_expected_address_doge.address_check(
        addr=addr,
        privkey=privkey,
    )
    print(f"address_match = {address_match}")


if __name__ == "__main__":
    test()
