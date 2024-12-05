from cryptos.types import Tx
from Create_Raw_Transaction_Helper import Create_Raw_Transaction_Helper


class Create_Raw_Transaction_Btc:
    def __init__(
        self,
        # coin_symbol: str,
        testnet: bool = False,
    ):
        self.coin_symbol: str = "btc"
        self.testnet: bool = testnet
        self.create_raw_transaction_helper: Create_Raw_Transaction_Helper = (
            Create_Raw_Transaction_Helper(
                coin_symbol=self.coin_symbol,
                testnet=testnet,
            )
        )

    def create_raw_transaction_btc(
        self,
        frm_pub_address: str = "",
        to_pub_address: str = "",
        print_result: bool = True,
        atomic_value_to_spent: int = 0,  # satoshis
        # fee: float = 0,
    ) -> Tx:
        if frm_pub_address == "":
            print(f"pub_address is empty...")
            return
        if to_pub_address == "":
            print(f"pub_address is empty...")
            return

        if atomic_value_to_spent == 0:
            print(f"value_to_spent is 0")
            return
        # if fee == 0:
        #     print(f"fee is 0")
        #     return
        tx: Tx = self.create_raw_transaction_helper.create_raw_transaction(
            frm_pub_address=frm_pub_address,
            to_pub_address=to_pub_address,
            print_result=print_result,
            atomic_value_to_spent=atomic_value_to_spent,
            # fee=fee,
        )

        return tx

    def print_available_coins(
        self,
    ):
        self.create_raw_transaction_helper.print_available_coins()


if __name__ == "__main__":
    testnet: bool = False
    # coin_symbol: str = "btc"
    create_raw_transaction: Create_Raw_Transaction_Btc = Create_Raw_Transaction_Btc(
        testnet=testnet
    )
    frm_pub_address: str = (
        "bc1qte0s6pz7gsdlqq2cf6hv5mxcfksykyyyjkdfd5"  # mainnet address
    )
    # to_pub_address: str = "39C7fxSzEACPjM78Z7xdPxhf7mKxJwvfMJ"
    # to_pub_address: str = "myLktRdRh3dkK3gnShNj5tZsig6J1oaaJW"
    # to_pub_address: str = "myLktRdRh3dkK3gnShNj5tZsig6J1oaaJW"  # testnet address
    to_pub_address: str = "1PuJjnF476W3zXfVYmJfGnouzFDAXakkL4"  # mainnet address
    print_result: bool = True

    # value_to_spent: float = 0.00001
    atomic_value_to_spent: float = 300  # in atomic (satoshis)
    # fee: float = 100
    tx: Tx = create_raw_transaction.create_raw_transaction_btc(
        frm_pub_address=frm_pub_address,
        to_pub_address=to_pub_address,
        print_result=print_result,
        atomic_value_to_spent=atomic_value_to_spent,
        # fee=fee,
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
