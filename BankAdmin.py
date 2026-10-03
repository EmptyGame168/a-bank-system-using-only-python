# this is for bank admin or manager to manage entire bank system.
import json
import os 
import time
from BankAcc import bank_account
from savingAcc import saving_acc, TermInterest

class BankManager:

    def __init__(self, vault_reserve: float = 50000.0, loan_rate: float = 0.08, admin_password: str = "admin123"):
        self.accounts: dict[str, bank_account] = {}
        self.vault_reserve = float(vault_reserve)
        self.loan_rate = float(loan_rate)  # 8.0% annual interest on active loans
        self.active_loans: dict[str, float] = {}  # {account_id: remaining_principal}
        self.bank_revenue = 0.0
        self.admin_password = admin_password

    def authenticate_admin(self, input_password: str) -> bool:
        """Verifies if the entered password matches the admin password."""
        return input_password == self.admin_password

    def list_all_accounts(self):
        """Admin functionality: Overview of all customer accounts."""
        if not self.accounts:
            print("\nNo registered accounts in the system.")
            return

        print("\n" + "="*70)
        print(f"{'ACCOUNT ID':<12} | {'OWNER':<20} | {'TYPE':<25} | {'BALANCE':<10}")
        print("="*70)
        for acc in self.accounts.values():
            print(f"{acc.account_id:<12} | {acc.owner_name:<20} | {acc.get_account_type():<25} | ${acc.balance:<10.2f}")
        print("="*70)

    

    def create_account(
        self,
        account_id: str,
        owner_name: str,
        account_type: str,
        initial_balance: float = 0.0,
    ) -> bank_account | None:
        if account_id in self.accounts:
            print(f"Error: Account ID '{account_id}' already exists.")
            return None

        account_type_clean = account_type.strip().lower()

        if account_type_clean == "savings":
            acc = saving_acc(account_id, owner_name, initial_balance)
        elif account_type_clean in ("base", "checking", "main"):
            acc = bank_account(account_id, owner_name, initial_balance)
        else:
            print("Invalid account type! Use 'base' or 'savings'.")
            return None

        self.accounts[account_id] = acc
        print(
            f"Successfully created {acc.get_account_type()} for {owner_name} [{account_id}]."
        )
        return acc

    def get_account(self, account_id: str) -> bank_account | None:
        acc = self.accounts.get(account_id)
        if not acc:
            print(f"Account [{account_id}] not found.")
        return acc

    def transfer(
        self, sender_id: str, receiver_id: str, amount: float
    ) -> bool:
    
        sender = self.get_account(sender_id)
        receiver = self.get_account(receiver_id)

        if not sender or not receiver:
            return False

        if sender.withdraw(amount):
            receiver.deposit(amount)
            sender.transaction_history.append(
                f"Transfer Out: -${amount:.2f} to [{receiver_id}]"
            )
            receiver.transaction_history.append(
                f"Transfer In: +${amount:.2f} from [{sender_id}]"
            )
            print(
                f"Transferred ${amount:.2f} from [{sender_id}] to [{receiver_id}]."
            )
            return True
        return False

    # --- VAULT & LOAN SYSTEM ---
    def issue_loan(self, account_id: str, amount: float) -> bool:
        acc = self.get_account(account_id)
        if not acc:
            return False

        if amount <= 0:
            print("Loan amount must be greater than zero.")
            return False

        if amount > self.vault_reserve:
            print(
                f"Loan denied! Bank vault reserve insufficient. Available: ${self.vault_reserve:.2f}"
            )
            return False

        self.vault_reserve -= amount
        current_loan = self.active_loans.get(account_id, 0.0)
        self.active_loans[account_id] = current_loan + amount

        acc.balance += amount
        acc.transaction_history.append(
            f"Loan Approved: +${amount:.2f} (Total Outstanding: ${self.active_loans[account_id]:.2f})"
        )
        print(
            f"Loan of ${amount:.2f} issued to [{account_id}]. Vault balance: ${self.vault_reserve:.2f}"
        )
        return True

    def repay_loan(self, account_id: str, amount: float) -> bool:
        acc = self.get_account(account_id)
        if not acc:
            return False

        current_loan = self.active_loans.get(account_id, 0.0)
        if current_loan <= 0:
            print(f"No active loan found for account [{account_id}].")
            return False

        if amount <= 0 or amount > acc.balance:
            print(f"Invalid repayment amount or insufficient account funds.")
            return False

        repay_amount = min(amount, current_loan)
        if acc.withdraw(repay_amount):
            self.active_loans[account_id] -= repay_amount
            self.vault_reserve += repay_amount

            # Calculate interest portion earned by bank
            interest_paid = repay_amount * (self.loan_rate / 12)
            self.bank_revenue += interest_paid

            if self.active_loans[account_id] <= 0:
                del self.active_loans[account_id]
                print(f"Loan for [{account_id}] fully paid off!")

            acc.transaction_history.append(
                f"Loan Repayment: -${repay_amount:.2f}"
            )
            return True
        return False

    def process_system_interest(self) -> None:
        print("\n--- Processing Bank Interest Updates ---")
        for acc in self.accounts.values():
            if isinstance(acc, saving_acc):
                # 1. Apply low-tier flexible savings interest
                earned = acc.apply_savings_interest()
                if earned > 0:
                    print(
                        f"[{acc.account_id}] Flexible Interest Added: +${earned:.2f}"
                    )

                # 2. Check for matured term deposits
                matured_list = [
                    td for td in acc.term_deposits if td.is_matured()
                ]
                for td in matured_list:
                    acc.redeem_term_deposit(td.deposit_id)
                    print(
                        f"[{acc.account_id}] Auto-redeemed Matured Deposit [{td.deposit_id}]"
                    )

    def save_state(self, filepath: str = "bank_data.json") -> bool:
        """Serializes all accounts, term deposits, vault reserves, and loans to JSON.
        
        This function converts the in-memory bank state (accounts, vault reserves,
        active loans, and bank revenue) into a JSON file format so it can be
        persisted to disk for later restoration.
        
        Process:
        1. Build a dictionary containing scalar bank-level data (vault, loans, revenue)
        2. Iterate through all accounts and convert each one to a dictionary
        3. For savings accounts, include extra fields like tax_rate and term_deposits
        4. Write the complete data structure to a JSON file
        
        Args:
            filepath: Path where the JSON file will be saved
            
        Returns:
            True if save was successful
        """
        # Build the top-level data structure containing bank-wide state
        data = {
            "vault_reserve": self.vault_reserve,
            "loan_rate": self.loan_rate,
            "bank_revenue": self.bank_revenue,
            "active_loans": self.active_loans,
            "accounts": [],
        }

        # Convert each account object into a serializable dictionary
        for acc in self.accounts.values():
            acc_dict = {
                "account_id": acc.account_id,
                "owner_name": acc.owner_name,
                "balance": acc.balance,
                "transaction_history": acc.transaction_history,
                "is_savings": isinstance(acc, saving_acc),
            }

            # If this is a savings account, include savings-specific fields
            if isinstance(acc, saving_acc):
                acc_dict["tax_rate"] = acc.tax_rate
                acc_dict["next_deposit_id"] = acc.next_deposit_id
                # Serialize each term deposit with all its calculated values
                acc_dict["term_deposits"] = [
                    {
                        "deposit_id": td.deposit_id,
                        "principal": td.amountSaves,  # Use correct attribute name
                        "years": td.term_duration,
                        "annual_rate": td.annual_interest_rate,
                        "maturity_amount": td.maturity_amount,
                        "total_interest_earned": td.interest_earned,
                        "start_timestamp": td.start_time,
                        "duration_seconds": td.duration_seconds,
                        "maturity_timestamp": td.maturity_time,
                    }
                    for td in acc.term_deposits
                ]

            data["accounts"].append(acc_dict)

        # Write the serialized data to disk as formatted JSON
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4) 

        print(f"Bank state successfully saved to '{filepath}'.")
        return True

    def load_state(self, filepath: str = "bank_data.json") -> bool:
        """Loads state from JSON file and restores all objects.
        
        This function reads a previously saved JSON file and reconstructs the
        complete bank state including accounts, vault reserves, active loans,
        and term deposits. It's the counterpart to save_state().
        
        Process:
        1. Check if the save file exists
        2. Read and parse the JSON data
        3. Restore bank-level scalar values (vault, loans, revenue)
        4. Reconstruct each account object from its serialized dictionary
        5. For savings accounts, rebuild term deposit objects with their state
        
        Args:
            filepath: Path to the JSON file to load
            
        Returns:
            True if load was successful, False if file not found
        """
        # Check if the save file exists before attempting to load
        if not os.path.exists(filepath):
            print(f"Save file '{filepath}' not found.")
            return False

        # Read and parse the JSON data from disk
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Restore bank-level scalar values from the saved data
        self.vault_reserve = data.get("vault_reserve", 50000.0)
        self.loan_rate = data.get("loan_rate", 0.08)
        self.bank_revenue = data.get("bank_revenue", 0.0)
        self.active_loans = data.get("active_loans", {})
        self.accounts.clear()  # Clear any existing accounts before loading

        # Reconstruct each account object from its serialized dictionary
        for acc_dict in data.get("accounts", []):
            if acc_dict.get("is_savings"):
                # Create a new savings account instance
                acc = saving_acc(
                    account_id=acc_dict["account_id"],
                    owner_name=acc_dict["owner_name"],
                    initial_balance=acc_dict["balance"],
                    tax_rate=acc_dict.get("tax_rate", 0.10),
                )
                # Restore the deposit ID counter
                acc.next_deposit_id = acc_dict.get("next_deposit_id", 1)

                # Reconstruct Term Deposit objects from saved data
                for td_dict in acc_dict.get("term_deposits", []):
                    td = TermInterest(
                        deposit_id=td_dict["deposit_id"],
                        amountSaves=td_dict["principal"],
                        term_duration=td_dict["years"],
                        annual_interest_rate=td_dict["annual_rate"],
                    )
                    # Restore calculated maturity values and timestamps
                    td.maturity_amount = td_dict["maturity_amount"]
                    td.interest_earned = td_dict["total_interest_earned"]
                    td.start_time = td_dict["start_timestamp"]
                    td.duration_seconds = td_dict["duration_seconds"]
                    td.maturity_time = td_dict["maturity_timestamp"]
                    acc.term_deposits.append(td)

            else:
                # Create a new base bank account instance
                acc = bank_account(
                    account_id=acc_dict["account_id"],
                    owner_name=acc_dict["owner_name"],
                    initial_balance=acc_dict["balance"],
                )

            # Restore the transaction history for this account
            acc.transaction_history = acc_dict.get("transaction_history", [])
            self.accounts[acc.account_id] = acc

        print(f"Bank state successfully loaded from '{filepath}'.")
        return True