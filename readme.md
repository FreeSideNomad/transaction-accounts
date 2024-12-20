
## Setup Instructions

After cloning the repository, you need to set the execute permissions for the `init-db.sh` script. This can be done using Git Bash or WSL on Windows, or a terminal on macOS/Linux.

### Using Git Bash or WSL on Windows

1. Open Git Bash or your WSL terminal.
2. Navigate to the directory containing the `init-db.sh` file.
3. Run the following command:

    ```sh
    chmod +x init-db.sh
    ```

### Using Terminal on macOS/Linux

1. Open your terminal.
2. Navigate to the directory containing the `init-db.sh` file.
3. Run the following command:

    ```sh
    chmod +x init-db.sh
    ```

This will ensure that the script has the necessary execute permissions when running the Docker container.

# Transaction Accounts

This library provides basic functionality for working with transaction accounts.

You can use it to make any type of transaction account, such as a savings account, a credit card, or a loan.

Assume we would like to create simple Savings Account that has 3 types of balances:

- current balance
- interest accrued
- withholding tax

We would like to have 4 types of transactions:

- deposit
- interest accrued
- interest capitalized
- withholding tax

We would like to have 2 types of schedules:

- accrual schedule
- compounding schedule

We would like to have interest rate with 3 tiers:

- 0 - 10000: 3%
- 10000 - 50000: 3.5%
- 50000+: 4%

We would like to have monthly fee of 1.00 charged at the end of each month to the account before interest is accrued.

Deposit transaction will increase current balance, and it will be used to deposit money to the account.
This transaction will be externally created and posted to the account.

Interest accrued transaction will increase interest accrued balance, and it will be used to accrue interest on the
account.

Interest will be accrued daily, and it will be calculated based on current balance and interest rate.

Interest capitalized transaction will increase current balance and decrease interest accrued balance.
This transaction will be internally created and posted to the account at the end of each month.

Withholding tax transaction will decrease withholding tax balance, and it will be used to pay withholding tax on the
account.
It will be calculated as 20% of interest capitalized transaction.

We will use accrual schedule to accrue interest daily, and we will use compounding schedule to capitalize interest at
the end of each month.

We will use interest rate to calculate interest.

We will use trigger transaction to calculate withholding tax.

We will use monthly fee property to specify monthly fee. This amount will be charged at the end of each month.

Note that this framework is not limited to this configuration, and it can be used to create any type of transaction
account.

You can define custom calculations when calculating either schedules or transactions. In this context you can use any of
the following variables:

- account: Account
- transaction: Transaction
- config: Configuration

Example of this calculation can be found in [Savings account](./tests/SavingsAccount.xlsx) workbook.

Here is a code that will create this configuration:

```python
def create_savings_account() -> AccountType:
    acc = AccountType(name="savingsAccount", label="Savings Account")

    current = acc.add_position_type("current", "current balance")
    interest_accrued = acc.add_position_type("accrued", "interest accrued")
    withholding = acc.add_position_type("withholding", "withholding tax")

    montly_fee = acc.add_property_type("monthlyFee", "Monthly Fee", DataType.DECIMAL, True)

    acc.add_transaction_type("deposit", "Deposit") \
        .add_position_rule(TransactionOperation.CREDIT, current)

    fee_tt = acc.add_transaction_type("fee", "Fee") \
        .add_position_rule(TransactionOperation.DEBIT, current)

    interest_accrued_tt = acc.add_transaction_type("interestAccrued", "Interest Accrued") \
        .add_position_rule(TransactionOperation.CREDIT, interest_accrued)

    capitalized_tt = acc.add_transaction_type("capitalized", "Interest Capitalized") \
        .add_position_rule(TransactionOperation.CREDIT, current) \
        .add_position_rule(TransactionOperation.DEBIT, interest_accrued)

    withholding_tt = acc.add_transaction_type("withholdingTax", "Withholding Tax") \
        .add_position_rule(TransactionOperation.CREDIT, withholding)

    accrual_schedule = ScheduleType(name="accrual", label="Accrual Schedule", frequency=ScheduleFrequency.DAILY,
                                    end_type=ScheduleEndType.NO_END,
                                    business_day_adjustment=BusinessDayAdjustment.NO_ADJUSTMENT,
                                    interval_expression="1", start_date_expression="account.start_date")

    acc.add_schedule_type(accrual_schedule)

    compounding_schedule = ScheduleType(name="compounding", label="Compounding Schedule",
                                        frequency=ScheduleFrequency.MONTHLY,
                                        end_type=ScheduleEndType.NO_END,
                                        business_day_adjustment=BusinessDayAdjustment.NO_ADJUSTMENT,
                                        interval_expression="1",
                                        start_date_expression="account.start_date + relativedelta(month=+1) + relativedelta(days=-1)")

    acc.add_schedule_type(compounding_schedule)

    acc.add_scheduled_transaction(compounding_schedule, ScheduledTransactionTiming.END_OF_DAY,
                                  fee_tt,
                                  "account.monthlyFee")

    acc.add_scheduled_transaction(accrual_schedule, ScheduledTransactionTiming.END_OF_DAY,
                                  interest_accrued_tt,
                                  "account.current * accountType.interest.get_rate(account.current) / Decimal(365)")

    acc.add_scheduled_transaction(compounding_schedule, ScheduledTransactionTiming.END_OF_DAY,
                                  capitalized_tt, "account.accrued")

    interest_rate = acc.add_rate_type("interest", "Interest Rate")

    interest_rate.add_tier(Decimal(10000), Decimal(0.03))
    interest_rate.add_tier(Decimal(100000), Decimal(0.035))
    interest_rate.add_tier(Decimal(50000), Decimal(0.04))

    acc.add_trigger_transaction(capitalized_tt, withholding_tt, "transaction.amount * Decimal(0.2)")

    return acc
```

Given configuration, we can create an account:

```python

 def test_valuation(self):
        account_type = create_savings_account()

        account = Account(start_date=date(2019, 1, 1), account_type_name=account_type.name,
                          account_type=account_type, properties={"monthlyFee": Decimal(1.00)})

        valuation = AccountValuation(account, account_type, date(2020, 1, 1))

        deposit_transaction_type = account_type.get_transaction_type("deposit")

        external_transactions = group_by_date([
            ExternalTransaction(transaction_type_name=deposit_transaction_type.name,
                                amount=Decimal(1000), value_date=date(2019, 1, 1))])

        valuation.forecast(date(2020, 1, 1), external_transactions)

        self.assertAlmostEqual(account.positions['current'].amount, Decimal(1018.24775), places=4)
        self.assertAlmostEqual(account.positions['withholding'].amount, Decimal(6.04955), places=4)
        self.assertAlmostEqual(account.transactions[1].amount, Decimal('0.08219'), places=4)
```
