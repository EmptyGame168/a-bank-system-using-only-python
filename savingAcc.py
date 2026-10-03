# this is a subclass of bank_account to manage saving account
import time
from BankAcc import bank_account

class TermInterest():
    def __init__(self, deposit_id,amountSaves,term_duration,annual_interest_rate):
        self.deposit_id = deposit_id
        self.amountSaves = float(amountSaves)
        self.term_duration = int(term_duration)
        self.annual_interest_rate = float(annual_interest_rate)

        # Compund interest: P(1+r/n)^(nt)
        self.maturity_amount = round(self.amountSaves * (1 + self.annual_interest_rate) ** self.term_duration, 2)
        self.interest_earned = round(self.maturity_amount - self.amountSaves, 2)
        self.duration_seconds = term_duration * 10
        self.maturity_time = time.time() + self.term_duration * 365 * 24 * 60 * 60
        self.start_time = time.time()
    def is_matured(self):
        return time.time() - self.start_time >= self.maturity_time
    def time_remaining(self):
        remaining_time = self.maturity_time - time.time()
        if remaining_time > 0:
            return remaining_time
        else:
            return 0

class saving_acc(bank_account):
    TERM_RATES = { # to manage duration to interest_rate
        1: 0.01,
        5: 0.025, # 5 years plan: 2.5% per years
        10:0.05, 
    }
    def __init__(self, acc_id, acc_name, initial_balance = 0.0, tax_rate = 0.10):
        super().__init__(acc_id, acc_name, initial_balance) # to call construccctor of parent class.
        self.tax_rate = float(tax_rate)
        self.term_deposits: list[TermInterest] = []
        self.next_deposit_id = 1
    def get_tiered_interest_rate(self) -> float:
        """Calculates tiered interest rate strictly on flexible savings balance."""
        if self.balance >= 10000.0:
            return 0.001  # 1.0%
        elif self.balance >= 5000.0:
            return 0.005  # 0.5%
        elif self.balance >= 1000.0:
            return 0.003  # 0.3%
        else:
            return 0.001  # 0.1% base rate

    def apply_saving_interest(self) -> float:
        if self.balance <= 0:
            return 0.0

        current_rate = self.get_tiered_interest_rate()
        gross_interest = self.balance * current_rate
        tax_amount = gross_interest * self.tax_rate
        net_interest = gross_interest - tax_amount

        self.balance += net_interest
        self.transaction_history.append(f"Savings Tier Interest ({current_rate * 100:.1f}%): +${net_interest:.2f} (Tax: ${tax_amount:.2f})"
        )
        return net_interest
    def open_term_deposit(self, amount: float, years: int) -> bool:
        if years not in self.TERM_RATES:
            print("Invalid duration! Choose 1, 5, or 10 years.")
            return False

        if amount <= 0 or amount > self.balance:
            print(f"Insufficient savings funds! Available: ${self.balance:.2f}")
            return False

        self.balance -= amount
        rate = self.TERM_RATES[years]
        deposit_id = f"TD-{self.next_deposit_id}"
        self.next_deposit_id += 1

        deposit = TermInterest(deposit_id, amount, years, rate)
        self.term_deposits.append(deposit)

        self.transaction_history.append(
            f"Locked ${amount:.2f} into {years}-Year Term Deposit [{deposit_id}] at {rate * 100:.1f}% APY"
        )
        return True
    def redeem_term_deposit(self, deposit_id: str) -> bool:
        for deposit in self.term_deposits:
            if deposit.deposit_id == deposit_id:
                if not deposit.is_matured():
                    print(f"[{deposit_id}] is still locked!")
                    return False

                self.balance += deposit.maturity_amount
                self.term_deposits.remove(deposit)
                self.transaction_history.append(f"Redeemed [{deposit_id}]: +${deposit.maturity_amount:.2f}")
                return True
        return False
    def get_account_type(self) -> str:
        current_rate = self.get_tiered_interest_rate()
        return f"Savings Account (Current Tier Rate: {current_rate * 100:.1f}%)"