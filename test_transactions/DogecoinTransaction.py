from BaseTransaction import BaseTransaction


class DogecoinTransaction(BaseTransaction):
    def __init__(self, sender, receiver, amount):
        super().__init__(sender, receiver, amount)
        self.transaction_fee = 0.001  # Dogecoin transaction fee, generally lower

    def validate_transaction(self):
        # Dogecoin may have different validation rules
        return (
            self.amount > 0 and self.sender != self.receiver and self.amount <= 100000
        )  # Example limit
