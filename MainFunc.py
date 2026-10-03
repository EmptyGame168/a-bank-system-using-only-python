# main function and interface to use bank 
import sys
from BankAdmin import BankManager
from savingAcc import saving_acc

def show_customer_menu():
    print("\n    CUSTOMER CONTROL MENU    ")
    print("1. View My Balance & History")
    print("2. Deposit Funds")
    print("3. Withdraw Funds")
    print("4. Transfer Money to Another Account")
    print("5. Open Term Deposit (Savings Accounts Only)")
    print("6. View / Redeem Active Term Deposits")
    print("7. Repay Active Loan")
    print("0. Switch / Logout")


def show_admin_menu():
    print("\n    ADMIN CONTROL PANEL    ")
    print("1. Create New Customer Account")
    print("2. View All System Accounts")
    print("3. Issue Bank Loan to Customer")
    print("4. Trigger System-Wide Interest & Term Deposit Maturity")
    print("5. View Bank Reserves, Loans & Revenue")
    print("6. Save Bank State to JSON")
    print("7. Load Bank State from JSON")
    print("0. Switch / Logout")

def customer_session(manager: BankManager):
    acc_id = input("\nEnter your Account ID to log in: ").strip()
    account = manager.get_account(acc_id)

    if not account:
        return

    print(f"\nWelcome back, {account.owner_name}!")

    while True:
        show_customer_menu()
        choice = input("Select an option (0-7): ").strip()

        if choice == "1":
            print(f"\nAccount ID: {account.account_id} | Type: {account.get_account_type()}")
            print(f"Liquid Balance: ${account.balance:.2f}")
            
            loan = manager.active_loans.get(account.account_id, 0.0)
            if loan > 0:
                print(f"Active Loan Owed: ${loan:.2f}")

            if isinstance(account, saving_acc):
                account.display_term_deposits()

            print("\nTransaction History:")
            for log in account.transaction_history:
                print(f"  - {log}")

        elif choice == "2":
            try:
                amt = float(input("Enter deposit amount ($): "))
                if account.deposit(amt):
                    print(f"Updated Balance: ${account.balance:.2f}")
            except ValueError:
                print("Invalid numerical input.")

        elif choice == "3":
            try:
                amt = float(input("Enter withdrawal amount ($): "))
                if account.withdraw(amt):
                    print(f"Updated Balance: ${account.balance:.2f}")
            except ValueError:
                print("Invalid numerical input.")

        elif choice == "4":
            receiver_id = input("Enter Recipient Account ID: ").strip()
            try:
                amt = float(input("Enter transfer amount ($): "))
                manager.transfer(account.account_id, receiver_id, amt)
            except ValueError:
                print("Invalid numerical input.")

        elif choice == "5":
            if isinstance(account, saving_acc):
                try:
                    amt = float(input("Amount to lock into Term Deposit ($): "))
                    years = int(input("Choose Term Duration (1, 3, or 5 years): "))
                    account.open_term_deposit(amt, years)
                except ValueError:
                    print("Invalid inputs.")
            else:
                print("Term deposits are exclusively available for Savings Accounts!")

        elif choice == "6":
            if isinstance(account, saving_acc):
                account.display_term_deposits()
                if account.term_deposits:
                    sub = input("\nAttempt redeeming a deposit? (y/n): ").strip().lower()
                    if sub == 'y':
                        dep_id = input("Enter Deposit ID (e.g., TD-1): ").strip()
                        account.redeem_term_deposit(dep_id)
            else:
                print("Only Savings Accounts have Term Deposits!")

        elif choice == "7":
            try:
                amt = float(input("Enter repayment amount ($): "))
                manager.repay_loan(account.account_id, amt)
            except ValueError:
                print("Invalid numerical input.")

        elif choice == "0":
            print("Logging out of customer session...")
            break
        else:
            print("Invalid menu selection.")

#admin session
def admin_session(manager: BankManager):
    password = input("\nEnter Admin Password: ").strip()
    if not manager.authenticate_admin(password):
        print("Access Denied: Incorrect Admin Password!")
        return

    print("\nAdmin Authentication Successful. Access Granted.")

    while True:
        show_admin_menu()
        choice = input("Select Admin Action (0-7): ").strip()

        if choice == "1":
            acc_id = input("New Account ID: ").strip()
            name = input("Owner Full Name: ").strip()
            acc_type = input("Account Type ('base' or 'savings'): ").strip()
            try:
                init_bal = float(input("Initial Deposit Amount ($): "))
                manager.create_account(acc_id, name, acc_type, init_bal)
            except ValueError:
                print("Invalid input.")

        elif choice == "2":
            manager.list_all_accounts()

        elif choice == "3":
            acc_id = input("Target Account ID for Loan: ").strip()
            try:
                amt = float(input("Approved Loan Amount ($): "))
                manager.issue_loan(acc_id, amt)
            except ValueError:
                print("Invalid input.")

        elif choice == "4":
            manager.process_system_interest()

        elif choice == "5":
            print(f"\n--- CENTRAL BANK SYSTEM RESERVES ---")
            print(f"Vault Reserves Available: ${manager.vault_reserve:.2f}")
            print(f"Total Bank Revenue:       ${manager.bank_revenue:.2f}")
            print(f"Active Loans Count:       {len(manager.active_loans)}")

        elif choice == "6":
            manager.save_state("bank_data.json")

        elif choice == "7":
            manager.load_state("bank_data.json")

        elif choice == "0":
            print("Exiting Admin Control Panel...")
            break
        else:
            print("Invalid admin option.")


#main
def main():
    manager = BankManager(vault_reserve=100000.0, loan_rate=0.08, admin_password="admin123")
    manager.load_state("bank_data.json")

    while True:
        print("\n--- LOGIN PORTAL ---")
        print("1. Login as Customer")
        print("2. Login as Administrator")
        print("0. Exit System")
        
        mode = input("Select Login Mode (0-2): ").strip()

        if mode == "1":
            customer_session(manager)
        elif mode == "2":
            admin_session(manager)
        elif mode == "0":
            save = input("Save bank data before exit? (y/n): ").strip().lower()
            if save == 'y':
                manager.save_state("bank_data.json")
            print("Exiting system. Goodbye!")
            sys.exit(0)
        else:
            print("Invalid option selected.")


if __name__ == "__main__":
    main()