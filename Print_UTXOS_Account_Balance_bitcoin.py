from Print_UTXOS_Account_Balance_helper import (
    Print_UTXOS_Account_Balance_Merkle_Proof_helper,
)


class Print_UTXOS_Account_Balance_bitcoin:
    def __init__(
        self,
        testnet: bool = False,
    ):
        self.coin_symbol: str = "btc"  # coin_symbol
        self.testnet: bool = testnet
        self.print_result: str = True
        self.print_account_balance_helper: (
            Print_UTXOS_Account_Balance_Merkle_Proof_helper
        ) = Print_UTXOS_Account_Balance_Merkle_Proof_helper(
            coin_symbol=self.coin_symbol,
            testnet=self.testnet,
        )

    def print_account_balance(self, pub_address: str = ""):
        if pub_address == "":
            print(f"pub_address is empty...")
            return

        # electrumXTx_list: ElectrumXUnspentResponse =
        self.print_account_balance_helper.balance_online_lookup(
            print_result=self.print_result,
            pub_address=pub_address,
            coin_symbol=self.coin_symbol,
        )


if __name__ == "__main__":
    print_account_balance_bitcoin: Print_UTXOS_Account_Balance_bitcoin = (
        Print_UTXOS_Account_Balance_bitcoin()
    )
    # pub_address: str = "bc1pypendmmvk5mlryvcwkmmzn52cfrjrwpktlk3x9pftnnsz055asdqk93mgd"
    # pub_address: str = "bc1qte0s6pz7gsdlqq2cf6hv5mxcfksykyyyjkdfd5"
    pub_address: str = "1FUhaUyPaMALxLuAgh6TFbt9YxcUMtDAcj"
    print_account_balance_bitcoin.print_account_balance(pub_address=pub_address)
