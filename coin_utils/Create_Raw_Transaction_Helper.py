from cryptos import coins
from cryptos import script_utils

from typing import Union

from cryptos.types import Tx, TxInput


class Create_Raw_Transaction_Helper:
    def __init__(
        self,
        coin_symbol: str,
        testnet: bool = False,
    ):
        self.coin_symbol: str = coin_symbol
        self.testnet: bool = testnet
        self.some_validate_link: str = (
            r"https://live.blockcypher.com/btc/address/1EfayE6j4nv6L13Q2BdDtys7Gs2b791ev4/"
        )
        self.some_validate_link_2: str = (
            r"https://blockexplorer.one/dogecoin/testnet/address/ns3c8yGKiTL1TGgQru9CFbSwGxgLt3EHph"
        )
        self.tutorial_link: str = (
            r"https://learnmeabitcoin.com/technical/transaction/input/sequence/"
        )
        self.good_fee_info: str = (
            r"https://learnmeabitcoin.com/technical/transaction/fee/#sats-per-vbyte"
        )

        self.margin1: int = 20
        self.margin2: int = 30
        self.line_length: int = 60
        self.line_symbol: str = "-"
        self.atomic_value_divider: int = (
            100000000  # 1 btc =100,000,000 Satoshis (atomic units)
        )
        self.transaction_type: str = "Raw Transaction (unsigned)"

    def get_coin_instance(self, coin_symbol: str = "btc") -> Union[
        coins.bitcoin.Bitcoin,
        coins.litecoin.Litecoin,
        coins.bitcoin_cash.BitcoinCash,
        coins.dash.Dash,
        coins.dogecoin.Doge,
        None,
    ]:
        """
        Returns an instance of the appropriate coin class based on the provided coin symbol.

        Args:
            self: The instance of the class calling this function.
            coin_symbol: The symbol of the coin to create an instance for.

        Returns:
            An instance of the appropriate coin class, or None if the coin is not supported.
        """
        if coin_symbol == "btc":
            coin = coins.bitcoin.Bitcoin(testnet=self.testnet)
        elif coin_symbol == "ltc":
            coin = coins.litecoin.Litecoin(testnet=self.testnet)
        elif coin_symbol == "bch":
            coin = coins.bitcoin_cash.BitcoinCash(testnet=self.testnet)
        elif coin_symbol == "dash":
            coin = coins.dash.Dash(testnet=self.testnet)
        elif coin_symbol == "doge":
            coin = coins.dogecoin.Doge(testnet=self.testnet)
        else:
            print(f"coin({coin_symbol}) not available. process stopped.")
            return None
        return coin

    def valid_address_check(
        self,
        frm_pub_address: str = "",
        to_pub_address: str = "",
        coin: Union[
            coins.bitcoin.Bitcoin,
            coins.litecoin.Litecoin,
            coins.bitcoin_cash.BitcoinCash,
            coins.dash.Dash,
            coins.dogecoin.Doge,
            None,
        ] = None,
    ) -> tuple[bool, bool]:
        if coin == None:
            return
        net: str = f"Mainnet"
        if self.testnet == True:
            net = f"Testnet"

        print(self.line_symbol * self.line_length)
        # frm_pub_address
        print(
            f"Checking if the frm_pub_address(sender) is a valid address for the  {self.coin_symbol} {net} network:"
        )
        print(f"frm_pub_address: {frm_pub_address}")
        # print(
        #     f"Checking if the from(sender) is a valid address for the {self.coin_symbol} network:{frm_pub_address}"
        # )
        frm_pub_address_is_valid: bool = coin.is_address(addr=frm_pub_address)
        if frm_pub_address_is_valid == False:
            # if self.coin_symbol == "doge":
            # print(f"TODO Check why it says that ->not a address: {frm_pub_address}")
            print(
                f"frm_pub_address seems to be a NOT valid {self.coin_symbol} {net} address:{frm_pub_address}"
            )
        else:
            print(
                f"frm_pub_address seems to be a valid {self.coin_symbol} {net} address:{frm_pub_address}"
            )
        # to_pub_address
        print(self.line_symbol * self.line_length)
        # print()
        print(self.line_symbol * self.line_length)
        print(
            f"Checking if the to_pub_address(recipant) is a valid address for the {self.coin_symbol} {net} network:"
        )
        print(f"to_pub_address: {to_pub_address}")

        to_pub_address_is_valid: bool = coin.is_address(addr=to_pub_address)
        if to_pub_address_is_valid == False:
            print(
                f"to_pub_address seems to be a NOT valid {self.coin_symbol} {net} address:{to_pub_address}"
            )

        else:
            print(
                f"to_pub_address seems to be a valid {self.coin_symbol} {net} address:{to_pub_address}"
            )
        print(self.line_symbol * self.line_length)
        return frm_pub_address_is_valid, to_pub_address_is_valid

    def is_integer(self, number):
        """Checks if a number is an integer, even if it's stored as a float."""
        return isinstance(number, int) or (
            isinstance(number, float) and number.is_integer()
        )

    # def create_raw_transaction(
    #     self,
    #     frm_pub_address: str = "",
    #     to_pub_address: str = "",
    #     print_result: bool = True,
    #     atomic_value_to_spent: float = 0,
    #     # fee: float = 0,
    # ) -> Tx:
    #     if frm_pub_address == "":
    #         print(f"pub_address is empty...")
    #         return
    #     if to_pub_address == "":
    #         print(f"pub_address is empty...")
    #         return

    #     if atomic_value_to_spent == 0:
    #         print(f"value_to_spent is 0")
    #         return
    #     if not self.is_integer(number=atomic_value_to_spent):
    #         print(f"value_to_spent is not an interger:{atomic_value_to_spent}")
    #         return
    #     # if fee == 0:
    #     #     print(f"fee is 0")
    #     #     return

    #     # ['btc', 'ltc', 'bch', 'dash', 'doge']
    #     coin: Union[
    #         coins.bitcoin.Bitcoin,
    #         coins.litecoin.Litecoin,
    #         coins.bitcoin_cash.BitcoinCash,
    #         coins.dash.Dash,
    #         coins.dogecoin.Doge,
    #         None,
    #     ] = self.get_coin_instance(coin_symbol=self.coin_symbol)

    #     if coin == None:
    #         print(f"coin({self.coin_symbol}) not available. process stoped. ")
    #         return
    #         # coin: BaseCoin = get_coin(coin_symbol=self.coin_symbol, testnet=testnet)
    #     print("-")

    #     tx: Tx = coin.preparetx(
    #         frm=frm_pub_address,
    #         to=to_pub_address,  # "myLktRdRh3dkK3gnShNj5tZsig6J1oaaJW",
    #         value=atomic_value_to_spent,
    #         # fee=fee,
    #     )

    #     if print_result:
    #         self.print_result(
    #             pub_address=frm_pub_address,
    #             tx=tx,
    #             coin_symbol=self.coin_symbol,
    #             to_pub_address=to_pub_address,
    #             value_to_spent=atomic_value_to_spent,
    #         )

    #     self.valid_address_check(
    #         frm_pub_address=frm_pub_address,
    #         to_pub_address=to_pub_address,
    #         coin=coin,
    #     )
    #     return tx
    def create_raw_transaction(
        self,
        frm_pub_address: str = "",
        to_pub_address: str = "",
        print_result: bool = True,
        atomic_value_to_spent: float = 0,
        # fee: float = 0,
    ) -> tuple[
        Tx,
        Union[
            coins.bitcoin.Bitcoin,
            coins.litecoin.Litecoin,
            coins.bitcoin_cash.BitcoinCash,
            coins.dash.Dash,
            coins.dogecoin.Doge,
            None,
        ],
    ]:
        if frm_pub_address == "":
            print(f"pub_address is empty...")
            return
        if to_pub_address == "":
            print(f"pub_address is empty...")
            return

        if atomic_value_to_spent == 0:
            print(f"value_to_spent is 0")
            return
        if not self.is_integer(number=atomic_value_to_spent):
            print(f"value_to_spent is not an interger:{atomic_value_to_spent}")
            return
        # if fee == 0:
        #     print(f"fee is 0")
        #     return

        # ['btc', 'ltc', 'bch', 'dash', 'doge']
        coin: Union[
            coins.bitcoin.Bitcoin,
            coins.litecoin.Litecoin,
            coins.bitcoin_cash.BitcoinCash,
            coins.dash.Dash,
            coins.dogecoin.Doge,
            None,
        ] = self.get_coin_instance(coin_symbol=self.coin_symbol)

        if coin == None:
            print(f"coin({self.coin_symbol}) not available. process stoped. ")
            return
            # coin: BaseCoin = get_coin(coin_symbol=self.coin_symbol, testnet=testnet)
        print("-")
        frm_pub_address_is_valid: bool = False
        to_pub_address_is_valid: bool = False
        frm_pub_address_is_valid, to_pub_address_is_valid = self.valid_address_check(
            frm_pub_address=frm_pub_address,
            to_pub_address=to_pub_address,
            coin=coin,
        )
        if frm_pub_address_is_valid == False:
            print(f"frm_pub_address_is_valid = False")
            print(f"Process stopped...")
            return None, None
        if to_pub_address_is_valid == False:
            print(f"to_pub_address_is_valid = False")
            print(f"Process stopped...")
            return None, None
        try:
            tx: Tx = coin.preparetx(
                frm=frm_pub_address,
                to=to_pub_address,
                value=atomic_value_to_spent,
            )
        except Exception as e:  # Catch any other exception
            print(f"A general exception occurred: {e}")
            print(f"process stopped...")
            return None, None
        if print_result:
            self.print_result(
                pub_address=frm_pub_address,
                tx=tx,
                coin_symbol=self.coin_symbol,
                to_pub_address=to_pub_address,
                value_to_spent=atomic_value_to_spent,
            )

        # frm_pub_address_is_valid, to_pub_address_is_valid=self.valid_address_check(
        #     frm_pub_address=frm_pub_address,
        #     to_pub_address=to_pub_address,
        #     coin=coin,
        # )
        return tx, coin

    def print_pretty(self, data):
        """Prints the data in a formatted table-like structure."""
        # Find the maximum length of each key for padding
        max_key_length = max(len(key) for key in data)

        # Print the header row
        print("-" * (max_key_length + 15))
        print(f"| {'Key':>{max_key_length}} | {'Value':>10} |")
        print("-" * (max_key_length + 15))

        # Print the key-value pairs
        for key, value in data.items():
            if isinstance(value, list):
                # Handle lists with nested dictionaries
                for i, item in enumerate(value):
                    print(f"| {' '*4}{key}: {i} |")
                    for inner_key, inner_value in item.items():
                        print(
                            f"| {' '*8}{inner_key:>{max_key_length}} | {inner_value} |"
                        )
                print("-" * (max_key_length + 15))
            else:
                print(f"| {key:>{max_key_length}} | {value} |")
                print("-" * (max_key_length + 15))

    def print_pretty_2(self, data):
        """Prints the data in a formatted table-like structure."""
        # Find the maximum length of each key for padding
        max_key_length = max(len(key) for key in data)

        # Print the header row
        print("-" * (max_key_length + 15))
        print(f"| {'Key':>{max_key_length}} | {'Value':>15} |")
        print("-" * (max_key_length + 15))

        # Print the key-value pairs
        for key, value in data.items():
            if isinstance(value, list):
                # Handle lists with nested dictionaries
                for i, item in enumerate(value):
                    print(f"| {' '*4}{key}: {i} |")
                    for inner_key, inner_value in item.items():
                        print(
                            f"| {' '*8}{inner_key:>{max_key_length}} | {inner_value:15} |"
                        )
                print("-" * (max_key_length + 15))
            else:
                print(f"| {key:>{max_key_length}} | {value:15} |")
                print("-" * (max_key_length + 15))

    def format_to_8_decimals(self, value: float) -> str:
        """Formats a  value to 8 decimal places."""
        return f"{value:.8f}"

    def fromat_to_full_coin_value(self, atomic_value: float) -> str:
        coin_value: float = self.calc_atomic_to_coin_value(atomic_value=atomic_value)
        coin_value_formated: str = self.format_to_8_decimals(value=coin_value)

        return coin_value_formated

    def calc_atomic_to_coin_value(self, atomic_value: float) -> float:

        coin_value: float = atomic_value / self.atomic_value_divider
        return coin_value

    def print_pretty_3(self, data):
        """Prints the data in a formatted table-like structure."""
        # Find the maximum length of each key for padding
        max_key_length = max(len(key) for key in data)

        # Print the header row
        print("-" * (max_key_length + 15))
        print(f"| {'Key':>{max_key_length}} | {'Value':<15} |")
        print("-" * (max_key_length + 15))
        # kuoni_str:str="kuonis(satoshis)"

        atomic: str = "(atomic(smallest unit))"

        # Print the key-value pairs
        for key, value in data.items():
            if isinstance(value, list):
                # Handle lists with nested dictionaries
                for i, item in enumerate(value):
                    print(f"| {' '*4}{key}: {i} |")
                    for inner_key, inner_value in item.items():
                        if inner_key == "value":
                            coin_value_formated: str = self.fromat_to_full_coin_value(
                                atomic_value=inner_value
                            )

                            print(
                                f"| {' '*8}{inner_key:>{max_key_length}} | {inner_value:<15} | {atomic}  ({coin_value_formated} {self.coin_symbol})"
                            )
                        else:
                            print(
                                f"| {' '*8}{inner_key:>{max_key_length}} | {inner_value:<15} |"
                            )
                print("-" * (max_key_length + 15))
            else:
                print(f"| {key:>{max_key_length}} | {value:<15} |")
                print("-" * (max_key_length + 15))

    def calc_fee_atomic(self, tx: Tx) -> float:
        """
        Calculates the transaction fee for a given transaction.

        This function takes a transaction object (Tx) as input and calculates the fee based on the
        total input value and the total output value. The fee is calculated as the difference
        between the total input value and the total output value.

        Args:
            tx (Tx): The transaction object for which to calculate the fee.

        Returns:
            float: The calculated transaction fee in Bitcoin (BTC).

        Example:
            >>> tx = Tx(...)  # Assuming tx is a valid transaction object
            >>> fee = self.calc_fee(tx)
            >>> print(fee)
            0.00000123  # Example fee value

        Note:
            This function assumes that the transaction object (Tx) is properly formatted and contains
            all the necessary information for fee calculation.
        """
        # txInput: TxInput = None

        total_input_value = sum([txInput["value"] for txInput in tx["ins"]])
        total_output_value = sum([output["value"] for output in tx["outs"]])
        fee_atomic = (
            total_input_value - total_output_value
        )  # / 100000000  # Convert satoshis to BTC
        return fee_atomic

    def print_fee_info(
        self,
        tx: Tx,
    ):
        fee_info_txt_1: str = (
            f"If you add up all the input values and subtract all the output values,"
        )
        fee_info_txt_2: str = (
            f"the amount left over is the fee. (the fee is calculated here self.client.estimate_fee(numblocks))"
        )
        fee_atomic: float = self.calc_fee_atomic(tx=tx)
        coin_value_formated: str = self.fromat_to_full_coin_value(
            atomic_value=fee_atomic
        )

        print(self.line_symbol * self.line_length)
        print(f"{fee_info_txt_1}")
        print(f"{fee_info_txt_2}")
        print(self.line_symbol * self.line_length)
        print(self.line_symbol * self.line_length)
        print(
            f"{'fee:'} {fee_atomic} ({coin_value_formated} {self.coin_symbol}) (fee is what the miners get for their work (miningpool)) "
        )
        print(self.line_symbol * self.line_length)
        print(self.line_symbol * self.line_length)
        fee_warning: str = (
            "Be careful, as any amount of satoshis left over in a transaction will be taken as the fee. Some people have mistakenly set large fees on their transactions by incorrectly sizing their outputs. For example, transaction cc455ae816e6cdafdb58d54e35d4f46d860047458eacf1c7405dc634631c570d had a 291.240900 BTC fee on it."
        )
        print(f"{fee_warning}")
        print(self.line_symbol * self.line_length)
        print(self.line_symbol * self.line_length)
        print(f"good_fee_info link: {self.good_fee_info}")
        print(self.line_symbol * self.line_length)

    def print_result(
        self,
        pub_address: str,
        tx: Tx,
        coin_symbol: str,
        to_pub_address: str = "",
        value_to_spent: float = 0,
    ):
        atomic: str = "atomic(smallest unit)"
        net: str = f"Mainnet(the real {self.coin_symbol} blockchain)"
        if self.testnet == True:
            net = f"Testnet(the test net for {self.coin_symbol}.)"

        print(self.line_symbol * self.line_length)
        # {'Value':<15}

        value_to_spent_full_coin_value: str = self.fromat_to_full_coin_value(
            atomic_value=value_to_spent
        )
        print(f"New {self.transaction_type} Transaction:")
        left_padding: int = 15
        print(f"{'coin:':>{left_padding}} {coin_symbol}")
        print(f"{'from:':>{left_padding}} {pub_address}")
        print(f"{'to:':>{left_padding}} {to_pub_address}")
        print(
            f"{'value_to_spent:':>{left_padding}} {value_to_spent} {atomic} ({value_to_spent_full_coin_value} {coin_symbol})"
        )
        print(self.line_symbol * self.line_length)

        print(self.line_symbol * self.line_length)
        print(f"Network: {net} {self.transaction_type}")
        print(self.line_symbol * self.line_length)

        self.print_pretty_3(data=tx)
        self.print_fee_info(tx=tx)
        self.print_some_links()

    def print_only_transaction(
        self,
        pub_address: str,
        tx: Tx,
        coin_symbol: str,
        to_pub_address: str = "",
        value_to_spent: float = 0,
    ):
        atomic: str = "atomic(smallest unit)"
        net: str = f"Mainnet(the real {self.coin_symbol} blockchain)"
        if self.testnet == True:
            net = f"Testnet(the test net for {self.coin_symbol}.)"

        # print(
        #     self.line_symbol * self.line_length
        #     + f"------{self.transaction_type}--start"
        # )

        # {'Value':<15}

        value_to_spent_full_coin_value: str = self.fromat_to_full_coin_value(
            atomic_value=value_to_spent
        )
        print(self.line_symbol * self.line_length)
        print(f"New {self.transaction_type} Transaction:")
        left_padding: int = 15
        print(f"{'coin:':>{left_padding}} {coin_symbol}")
        print(f"{'from:':>{left_padding}} {pub_address}")
        print(f"{'to:':>{left_padding}} {to_pub_address}")
        print(
            f"{'value_to_spent:':>{left_padding}} {value_to_spent} {atomic} ({value_to_spent_full_coin_value} {coin_symbol})"
        )
        print(self.line_symbol * self.line_length)

        print(self.line_symbol * self.line_length)
        print(f"Network: {net} {self.transaction_type}")
        print(self.line_symbol * self.line_length)
        print(
            f"------{self.transaction_type}--start"
            + self.line_symbol * self.line_length
        )
        self.print_pretty_3(data=tx)
        print(
            f"------{self.transaction_type}--end" + self.line_symbol * self.line_length
        )
        # self.print_fee_info(tx=tx)
        # self.print_some_links()

    def print_some_links(
        self,
    ):
        print(self.line_symbol * self.line_length)
        print(f"really helpfull infos: {self.tutorial_link}")
        print(self.line_symbol * self.line_length)

        print(self.line_symbol * self.line_length)
        print(f"some link: {self.some_validate_link}")
        print(f"some link: {self.some_validate_link_2}")
        print(self.line_symbol * self.line_length)

    def print_available_coins(
        self,
    ):

        # print()
        print(self.line_symbol * self.line_length)
        print(f"Available Coins: {script_utils.coin_list}")
        print(self.line_symbol * self.line_length)


if __name__ == "__main__":
    coin_symbol: str = "btc"
    create_raw_transaction_helper: Create_Raw_Transaction_Helper = (
        Create_Raw_Transaction_Helper(coin_symbol=coin_symbol)
    )
    # privkey: str = ""
    # pub_address: str = ""
    frm_pub_address: str = (
        "bc1qte0s6pz7gsdlqq2cf6hv5mxcfksykyyyjkdfd5"  # mainnet address
    )
    # to_pub_address: str = "39C7fxSzEACPjM78Z7xdPxhf7mKxJwvfMJ"
    to_pub_address: str = "myLktRdRh3dkK3gnShNj5tZsig6J1oaaJW"  # testnet address
    to_pub_address: str = "1PuJjnF476W3zXfVYmJfGnouzFDAXakkL4"  # mainnet address
    print_result: bool = True

    atomic_value_to_spent: float = 300
    tx: Tx
    coin: Union[
        coins.bitcoin.Bitcoin,
        coins.litecoin.Litecoin,
        coins.bitcoin_cash.BitcoinCash,
        coins.dash.Dash,
        coins.dogecoin.Doge,
        None,
    ]

    tx, coin = create_raw_transaction_helper.create_raw_transaction(
        frm_pub_address=frm_pub_address,
        to_pub_address=to_pub_address,
        print_result=print_result,
        atomic_value_to_spent=atomic_value_to_spent,
    )


# Let's imagine you're planning a trip and want to send some Bitcoin to a friend who's going to handle the travel expenses. You're concerned about security and want to sign the transaction offline. Here's how you can do it:

# **Scenario:**

# - You have a Bitcoin wallet on your laptop (let's call it Wallet A).
# - Your friend has a hardware wallet (let's call it Wallet B).
# - You want to send 0.1 BTC to your friend's Bitcoin address.

# **Steps:**

# 1. **Prepare the Unsigned Transaction:**
#    - **Open Wallet A:**  Launch your Bitcoin wallet on your laptop.
#    - **Create the Transaction:**  Navigate to the "Send" or "Transaction" section of your wallet.
#    - **Enter Details:**
#      - **Recipient Address:** Enter your friend's Bitcoin address from Wallet B.
#      - **Amount:** Enter 0.1 BTC.
#      - **Fee:** Choose a suitable transaction fee.
#    - **Generate the Unsigned Transaction:** Your wallet will create an unsigned transaction. This will typically be in a Partially Signed Bitcoin Transaction (PSBT) format.

# 2. **Export the Unsigned Transaction:**
#    - **Save the PSBT:**  Your wallet will allow you to export the unsigned transaction as a file (usually with a .psbt extension).
#    - **Transfer the File:**  Send this file to your friend (perhaps via email or a secure messaging app).

# 3. **Offline Signing with Hardware Wallet:**
#    - **Connect to Hardware Wallet:** Your friend will connect their hardware wallet (Wallet B) to their computer.
#    - **Import the PSBT:** They will import the .psbt file into their hardware wallet software.
#    - **Review and Sign:**  The hardware wallet software will display the transaction details. Your friend will need to review the information carefully and then use the hardware wallet to sign the transaction. This step is crucial for security, as the private key remains securely within the hardware wallet.

# 4. **Export the Signed Transaction:**
#    - **Save the Signed PSBT:**  The hardware wallet will create a new PSBT file containing the signed transaction.
#    - **Transfer the File:**  Your friend will send this signed PSBT file back to you.

# 5. **Broadcast the Transaction:**
#    - **Import the Signed PSBT:**  You will import the signed PSBT file back into your wallet (Wallet A).
#    - **Broadcast:**  Your wallet will then broadcast the signed transaction to the Bitcoin network.

# **Important Considerations:**

# - **Security:**  The hardware wallet is essential for offline signing. It ensures that your private key never leaves the device, even when you're connected to the internet.
# - **Verification:**  Always double-check the transaction details before signing. Make sure the recipient address, amount, and fee are correct.
# - **Backup:**  Always back up your wallet data, including any private keys or seed phrases.

# This example illustrates how you can create a secure Bitcoin transaction by signing it offline using a hardware wallet. It emphasizes the importance of security and control over your private keys.


# process
# Or if you prefer to verify the tx (for example, at https://live.blockcypher.com/btc/decodetx/) you can break it into two steps:

# > from cryptos import *
# > c = Bitcoin(testnet=True)
# > tx = c.preparesignedtx("89d8d898b95addf569b458fbbd25620e9c9b19c9f730d5d60102abbabcb72678", "tb1qsp907fjefnpkczkgn62cjk4ehhgv2s805z0dkv", "tb1q95cgql39zvtc57g4vn8ytzmlvtt43skngdq0ue", 5000)
# > serialize(tx)
# '010000000001014ae7e7fdead71cc8303c5b5e68906ecbf978fb9d84f5f9dd505823356b9a1d6e0000000000ffffffff0288130000000000001600142d30807e2513178a791564ce458b7f62d758c2d3a00f000000000000160014804aff26594cc36c0ac89e95895ab9bdd0c540ef02483045022100cff4e64a4dd0f24c1f382e4b949ae852a89a5f311de50cd13d3801da3669675c0220779ebcb542dc80dae3e16202c0b58dd60261662f3b3a558dca6ddf22e30ca4230121031f763d81010db8ba3026fef4ac3dc1ad7ccc2543148041c61a29e883ee4499dc00000000'
# > c.pushtx(tx)
# '6a7c437b0de10c42f2e9e18cc004e87712dbda73a851a0ea6774749a290c7e7d'


# > tx = coin.preparetx(address, "myLktRdRh3dkK3gnShNj5tZsig6J1oaaJW", 1100000, 50000)


# def main(random_256_bit_hex: str):

#     coin_symbol: str = "btc"
#     testnet: bool = False
#     coin: BaseCoin = get_coin(coin_symbol=coin_symbol, testnet=testnet)
#     # mnemonic.entropy_to_words(os.urandom(16))
#     mnemonic_words_seed: str = mnemonic.entropy_to_words(entbytes=os.urandom(20))

#     is_checksum_valid, is_wordlist_valid = keystore.bip39_is_checksum_valid(
#         mnemonic=mnemonic_words_seed
#     )
#     passphrase: str = "test"
#     # TODO wallet fertig machen
#     wallet: HDWallet = coin.wallet(seed=mnemonic_words_seed, passphrase=passphrase)
#     margin: int = 47
#     print("")
#     print("-" * 40)
#     print("Available Coins:")
#     print("-" * 40)
#     for coin_str in coin_list:
#         print(coin_str)
#     # print("-" * 40)

#     print("\n" + "-" * 40)
#     print("Generated Keys:")
#     print("-" * 40)
#     print(f"{'Key Type':<{margin}} {'Value':<60}")

#     # random_256_bit_hex: str = generate_private_key()
#     print(f"{coin_symbol}:{'random (256_bit_hex):':<{margin}}{random_256_bit_hex:<60}")
#     public_coin_address: str = coin.privtoaddr(privkey=random_256_bit_hex)
#     print(f"{coin_symbol}:{'Public_address:':<{margin}}{public_coin_address:<60}")
#     # coin.watch_wallet
#     watch_wallet: HDWallet = coin.watch_wallet(xpub=public_coin_address)
#     priv_key_hex_compr = coin.encode_privkey(
#         privkey=random_256_bit_hex,
#         formt="hex_compressed",
#     )

#     print(
#         f"{coin_symbol}:{'Private Key (hex_compressed)':<{margin}}{priv_key_hex_compr:<60}"
#     )

#     pub_key_hash_wif_compressed = coin.encode_privkey(
#         privkey=random_256_bit_hex,
#         formt="wif_compressed",
#         script_type="p2pkh",
#     )
#     print(
#         f"{coin_symbol}:{'Public Address (wif_compressed):':<{margin}}{pub_key_hash_wif_compressed:<60}"
#     )
#     # print(f"{'P2PKH Address':<{margin}} {coin.privtoaddr(pub_key_hash_wif_compressed):<60}")

#     if coin.segwit_supported:
#         private_key_p2wpkh_p2sh = coin.encode_privkey(
#             random_256_bit_hex,
#             formt="wif_compressed",
#             script_type="p2wpkh-p2sh",
#         )
#         print(
#             f"{coin_symbol}:{'WIF P2WPKH-P2SH':<{margin}}{private_key_p2wpkh_p2sh:<60}"
#         )
#         pay_to_witness_public_key_hash_address = coin.privtop2wpkh_p2sh(
#             private_key_p2wpkh_p2sh
#         )

#         print(
#             f"{coin_symbol}:{'P2WPKH-P2SH':<{margin}}{pay_to_witness_public_key_hash_address:<60}"
#         )
#         private_key_p2wpkh = coin.encode_privkey(
#             random_256_bit_hex,
#             formt="wif_compressed",
#             script_type="p2wpkh",
#         )
#         print(
#             f"{coin_symbol}:{'WIF Native Segwit P2WPKH':<{margin}}{private_key_p2wpkh:<60}"
#         )
#         P2WPKH_address: str = coin.privtosegwitaddress(
#             privkey=private_key_p2wpkh,
#         )
#         print(f"{coin_symbol}:{'P2WPKH Address':<{margin}}{P2WPKH_address:<60}")

#     print("\n" + "-" * 40)
#     print("Key (Address) Types:")
#     print("-" * 40)

#     print(
#         f"{'WIF: (Wallet Import Format):':<{margin}}{'- A standard format for storing private keys.':<60}"
#     )

#     print(
#         f"{'P2PKH: (Pay-to-Public-Key-Hash):':<{margin}}{'- P2PKH addresses start with a 1.':<60}"
#     )
#     print(
#         f"{'P2WPKH: (Pay-to-Witness-Public-Key-Hash):':<{margin}}{'- A Segwit address type (prefix of bc1q) public address.':<60}"
#     )

#     print(
#         f"{'P2WPKH-P2SH: (Pay-to-Witness-Public-Key-Hash):':<{margin}}{'- nested in P2SH  A Segwit address type.':<60}"
#     )
