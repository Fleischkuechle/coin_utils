from Print_UTXOS_Account_Balance_helper import (
    Print_UTXOS_Account_Balance_Merkle_Proof_helper,
)


class Print_UTXOS_Account_Balance_doge_testnet:
    def __init__(
        self,
        testnet: bool = True,  # testnet
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
    print_account_balance_doge: Print_UTXOS_Account_Balance_doge_testnet = (
        Print_UTXOS_Account_Balance_doge_testnet()
    )

    # pub_address: str = (
    #     "nZBUZ985136wmU5s7U7Y9o2js5j7Qx9DpC"  # testnet address(print account balance not working)
    # )
    # pub_address: str = "nsNcfcmsSD2vev59TFW83RMdKrsejdhL99"
    pub_address: str = "nqedQEDCgwrXqLd2JrrpCfD9Tcz384rdHA"
    print_account_balance_doge.print_account_balance(pub_address=pub_address)
