from Print_UTXOS_Account_Balance_helper import (
    Print_UTXOS_Account_Balance_Merkle_Proof_helper,
)


class Print_UTXOS_Account_Balance_bitcoin_testnet:
    def __init__(
        self,
        testnet: bool = True,  # testnet
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
    print_account_balance_bitcoin: Print_UTXOS_Account_Balance_bitcoin_testnet = (
        Print_UTXOS_Account_Balance_bitcoin_testnet()
    )

    testnet_address: str = "mzSYL9XK3sy1e3Hyj1s1rQo7S666oRKWLz"
    print_account_balance_bitcoin.print_account_balance(pub_address=testnet_address)

    # # testnet_address_segwit: str = "tb1qqd28xqjhe2unmm0zpp7e6lhyh0wtf039353adt"
    # testnet_address_segwit: str = "tb1qcwu4p9akzdupqwc3fev2tjq9jpthc062zk0uaf"
    # print_account_balance_bitcoin.print_account_balance(
    #     pub_address=testnet_address_segwit
    # )
