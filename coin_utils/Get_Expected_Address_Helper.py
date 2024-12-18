from typing import Optional

from cryptos import script_utils

from cryptos import coins_async
from cryptos import main


class Get_Expected_Address_Helper:
    def __init__(
        self,
        coin_symbol: str,
        testnet: bool,
    ):
        self.coin_symbol: str = coin_symbol
        self.testnet: bool = testnet
        # for printing
        self.line_length: int = 40
        self.line_symbol: str = "-"

    def get_expected_address(
        self,
        addr: str,
        privkey: str,
        base_coin: coins_async.BaseCoin,
    ):

        expected_addr: str = ""
        if base_coin.is_native_segwit(addr):
            expected_addr = base_coin.privtosegwitaddress(privkey=privkey)
        elif base_coin.is_p2sh(addr):
            expected_addr = base_coin.privtop2wpkh_p2sh(priv=privkey)
        elif base_coin.is_p2pkh(addr):
            try:
                expected_addr = base_coin.privtoaddr(privkey=privkey)
            except:
                return expected_addr
        elif len(addr) == 66:
            expected_addr = main.compress(main.privtopub(privkey))
        else:
            # pass
            return "Not known Address"
            # expected_addr = privtopub(privkey)
        return expected_addr

    def print_match(
        self,
        coin: str,
        expected_addr: str,
        addr: str,
    ):
        print(self.line_symbol * self.line_length)
        print(f"Expected address match:")
        print(f"Extracted from private key ({coin}): {expected_addr}")
        print(f"Given address({coin}):               {addr}")
        print(self.line_symbol * self.line_length)

    def print_miss_match(
        self,
        expected_addr: str,
        addr: str,
        coin: str,
    ):
        print(self.line_symbol * self.line_length)
        print(f"Address to private Key missmatch ({coin}):")
        print(f"Private key is for ths address ({coin}): {expected_addr}")
        print(f"not for the given addr({coin}):         {addr}")
        print(f"process stopped...")
        print(self.line_symbol * self.line_length)

    def print_not_proccessable(
        self,
        privkey: str,
        coin: str,
    ):
        print(self.line_symbol * self.line_length)
        print(f"Private Key error ({coin}) :")
        print(f"This private key is not proccessable:")

        print(f"{privkey}")
        print(f"process stopped...")
        print(self.line_symbol * self.line_length)

    def print_not_known_address(
        self,
        coin: str,
        addr: str,
    ):
        print(self.line_symbol * self.line_length)
        print(f"Unknown address type({coin}):")
        print(f"Given address({coin}):               {addr}")
        print(self.line_symbol * self.line_length)

    def address_check(
        self,
        coin: str,
        testnet: bool,
        addr: str,
        privkey: Optional[str] = None,
    ) -> bool:
        address_match: bool = False
        base_coin: coins_async.BaseCoin = script_utils.get_coin(
            coin_symbol=coin,
            testnet=testnet,
        )

        expected_addr: str = self.get_expected_address(
            addr=addr,
            privkey=privkey,
            base_coin=base_coin,
        )
        print(" ")
        if expected_addr != addr:

            if expected_addr == "":
                self.print_not_proccessable(
                    privkey=privkey,
                    coin=coin,
                )

                # return address_match
            elif expected_addr == "Not known Address":
                self.print_not_known_address(
                    coin=coin,
                    addr=addr,
                )
                # return address_match
            else:
                self.print_miss_match(
                    expected_addr=expected_addr,
                    addr=addr,
                    coin=coin,
                )

                # return
        else:
            address_match = True
            self.print_match(
                coin=coin,
                expected_addr=expected_addr,
                addr=addr,
            )
        return address_match


def test_doge():
    # Created with Create_Address_Doge.py
    # doge:Private Key:        ea71e78cf1733347abb13b153d04a468093f160303255459e0505d274fa100ab
    # doge:Public_address:     DDASXg8LNY1gu2b5kCC5H1BpkhoD9UQihS
    coin_symbol: str = "doge"
    testnet: bool = False
    addr: str = "DDASXg8LNY1gu2b5kCC5H1BpkhoD9UQihS"  # test address doge 1
    privkey: str = (
        "ea71e78cf1733347abb13b153d04a468093f160303255459e0505d274fa100ab"  # the uncorrect private key for # test address doge 1
    )

    get_expected_address_helper: Get_Expected_Address_Helper = (
        Get_Expected_Address_Helper(
            coin_symbol=coin_symbol,
            testnet=testnet,
        )
    )
    address_match: bool
    address_match = get_expected_address_helper.address_check(
        coin=coin_symbol,
        testnet=testnet,
        addr=addr,
        privkey=privkey,
    )

    print(f"address_match = {address_match}")


def test_btc():
    # Created with Create_Address_Btc.py
    # btc:Private Key:        8c6c77a7eb3a4bbbe7e988c4c2b48fbaeb73a31bd3ab3dd2b415e25e10d7e6df
    # btc:Public_address:     1JNiv4AHXzc2ZnN7oMaynQD5NjtZ2DZThy
    # btc:pub_address_segwit: bc1qs0v6c4vtfcltqzt5f0zkm3ctr7lrrtvhkz3y8z (newer btc address version)
    coin_symbol: str = "btc"
    testnet: bool = False
    addr: str = "bc1qs0v6c4vtfcltqzt5f0zkm3ctr7lrrtvhkz3y8z"  # test address doge 1
    privkey: str = (
        "8c6c77a7eb3a4bbbe7e988c4c2b48fbaeb73a31bd3ab3dd2b415e25e10d7e6df"  # the uncorrect private key for # test address doge 1
    )

    get_expected_address_helper: Get_Expected_Address_Helper = (
        Get_Expected_Address_Helper(
            coin_symbol=coin_symbol,
            testnet=testnet,
        )
    )

    address_match: bool
    address_match = get_expected_address_helper.address_check(
        coin=coin_symbol,
        testnet=testnet,
        addr=addr,
        privkey=privkey,
    )

    print(f"address_match = {address_match}")


if __name__ == "__main__":
    test_doge()
    test_btc()
