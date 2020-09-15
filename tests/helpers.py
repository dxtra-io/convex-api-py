"""
    Helpers for testing

"""




def auto_topup_account(convex, account, min_balance=None):
    amount = 10000000
    retry_counter = 100
    if min_balance is None:
        min_balance = amount
    balance = convex.get_balance(account)
    while balance < min_balance and retry_counter > 0:
        request_amount = convex.request_funds(amount, account)
        balance = convex.get_balance(account)
        retry_counter -= 1
