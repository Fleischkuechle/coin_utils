from Print_UTXOS_Account_Balance_helper import (
    Print_UTXOS_Account_Balance_Merkle_Proof_helper,
)


class Print_UTXOS_Account_Balance_doge:
    def __init__(
        self,
        testnet: bool = False,
    ):
        self.coin_symbol: str = "doge"  # coin_symbol
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
    print_UTXOS_account_balance_doge: Print_UTXOS_Account_Balance_doge = (
        Print_UTXOS_Account_Balance_doge()
    )

    pub_address: str = "DEi98svyRa5HrgVRXqi3irmTi5VVmAbJus"  ########

    print_UTXOS_account_balance_doge.print_account_balance(pub_address=pub_address)
