from bticoin_transaction import BitcoinTransaction

if __name__ == "__main__":
    btc_tx = BitcoinTransaction()
    # ... (add inputs and outputs)
    transaction_hex = btc_tx.to_hex()
    btc_tx.print_transaction()
