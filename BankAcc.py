# this program will represent a entire system of bank 
# this is a parent class to manage individual own bank account

class bank_account():
    def __init__(self, acc_id, acc_name, balance = 0.0 ):
        self.acc_id = acc_id
        self.acc_name = acc_name
        self.balance = float(balance)
        self.transaction_history = []
    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            self.transaction_history.append(f"Deposited: ${amount:.2f}")
            print(f"Deposited: ${amount}. New balance: ${self.balance:.2f}")
        else:
            print("invalid amount")
    def withdraw(self, amount):
        if amount >= 0 and amount <= self.balance:
            balance -= amount
            self.transaction_history.append(f"Withdrew: ${amount:.2f}")
            print(f'withdrew: ${amount:.2f}. New balance: ${self.balance:.2f}')
        else:
            print("invalid amount")
    def get_statement(self) -> dict:
        return {
            "account_id": self.acc_id,
            "account_name": self.acc_name,
            "balance": self.balance,
            "transaction_history": self.transaction_history
        }
    def payment (self,amount, collector ):
        if amount >= 0 and amount <= self.balance:
            self.balance -= amount
            self.transaction_history.append(f"Payment of ${amount:.2f} made to {collector}")
            print(f"Payment of ${amount:.2f} made to {collector}. New balance: ${self.balance:.2f}")
        else:
            print("invalid amount")
    

