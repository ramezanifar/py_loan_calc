import yaml
import os
from datetime import datetime
import logging
from tabulate import tabulate


def monthly_payment(Loan, n, interest_rate):
    r = interest_rate / 12 / 100
    PMT_raw = Loan * r * (1 + 1 / ((1 + r) ** n - 1))  # Monthly payment
    PMT = round(PMT_raw, 2)
    return PMT


def find_payment_table(Loan, n, interest_rate, PMT, extra_principle, Escrow):
    """
    This method is used to find a table of payment details for the duration of the term
    extra_principle
    :param Loan:
    :param n:
    :param interest_rate:
    :param PMT:
    :param extra_principle:  List of optional extra payment for all months
    :return:
    """
    r = interest_rate / 12 / 100
    data = []
    Total_Principal_Paid = 0  # Every month this extra principle is payed optionally
    Total_Interest_Paid = 0
    Total_Paid = 0
    Balance = Loan  # Initialization
    for i in range(n):
        I_raw = (Loan-Total_Principal_Paid) * r  # Interest for this mont
        I = round(I_raw, 2)  # Mandatory interest for this month
        Total_Interest_Paid += I
        P = PMT - I  # Mandatory principle for this month
        optional_pay = extra_principle[i]
        # In case extra payment is made, loan will be paid off before term. Some corrections needed here
        if P > Balance:
            P = Balance
            optional_pay = 0  # No extra pay is needed
            terminate = True
        elif P + extra_principle[i] > Balance:
            optional_pay = Balance - P  # Less extra payment is needed
            terminate = True
        else:
            terminate = False

        Total_Principal_Paid = Total_Principal_Paid + P + optional_pay
        due = I + P + optional_pay + Escrow
        Total_Paid += due
        Balance = Loan - Total_Principal_Paid
        temp = {"Month": i + 1,
                "Interest": I,
                "Total Interest": Total_Interest_Paid,
                "Principal": P,
                "Optional Pay": optional_pay,
                "Total Principal": Total_Principal_Paid,
                "Payment": due,
                "Total Payment": Total_Paid,
                "Balance": Balance}

        data.append(temp)

        if terminate == True:
            break  # Exit the loop

    return data

def analyze_refinance_fee(data_ref, data_mod, fee):
    """ This method is used to analyse refinancing fee to see where the break even point is
    Algorithm: Find the accumulative interest saving by comparing refinancing plan and modified plan
    At the point, saving is greater than refinancing fees, it is the break even point. This point shows you should
    keep the property or you loose money on refinancing fees
    """
    m = min(len(data_ref), len(data_mod))
    break_even_point = len(data_ref)  # Initialization
    for i in range(m):
        interest_saving = data_mod[i]['Total Interest'] - data_ref[i]['Total Interest']
        if interest_saving > fee:
            break_even_point = i + 1
            break

    return break_even_point


def pretty_table(data):
    """ Prepare for Pretty Print in a table"""
    # Extract headers
    header = data[0].keys()

    table = []
    for row in data:
        row_val = []
        for h in header:
            row_val.append(row[h])

        table.append(row_val)


    return table, header

def find_optional_pay(term, opt_pay_recur, opt_pay_custom):
    """ This method is used to find the list of optional payments for each month"""
    opt = [opt_pay_recur] * term  # Initialize optional payment
    for this_month in opt_pay_custom.keys():
        if this_month <= term:  # Check if the month is valid
            opt[this_month-1] += opt_pay_custom[this_month]  # Add the custom payment

    return opt

def print_messages(loan, escrow, interest_rate, term, due):
    logging.info("Loan amount: {}".format(loan))
    logging.info("Escrow: {}".format(escrow))
    logging.info("Interest rate: {}".format(interest_rate))
    logging.info("Duration in months: {}".format(term))
    logging.info("Minimum monthly payment: {}".format(due))
    logging.info('\n')


def main():
    """ Main method of the project"""

    # Set up the result folder
    if os.path.isdir("./Output") == False:  # The result are put in this filder
        os.mkdir("./Output")
    # datetime object containing current date and time
    now = datetime.now()
    dt_string = now.strftime("%d_%m_%Y %H%M%S")
    res_file = "./Output/result_" + dt_string + ".txt"
    # Setup the logger
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[
            logging.FileHandler(res_file),
            logging.StreamHandler()
        ]
    )
    logging.info("Welcome to the loan calculator application!")
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    logging.info("This calcualtion was run on {}".format(dt_string))
    # Read the setting file
    with open("setting.yaml", 'r') as stream:
        try:
            inp = (yaml.safe_load(stream))
        except yaml.YAMLError as exc:
            logging.info("The setting file has bad format")
            logging.error(exc)
            logging.info("Application is terminating")

    # Store setting in local variables

    # Read and store settings for original loan
    loan = inp["Original Plan"]['Loan']
    escrow_orig = inp["Original Plan"]['Escrow']
    interest_rate_orig = inp["Original Plan"]['Interest Rate']
    term_orig = inp["Original Plan"]['Term']
    opt_pay_recur_orig = inp["Original Plan"]['Optional Payments']['Recurrent']
    opt_pay_custom_orig = inp["Original Plan"]['Optional Payments']['Custom']

    # Read and store settings for refinance plan
    escrow_ref = inp["Refinance"]['Escrow']
    interest_rate_ref = inp["Refinance"]['Interest Rate']
    term_ref = inp["Refinance"]['Term']
    start_ref = inp["Refinance"]['Start']
    opt_pay_recur_ref = inp["Refinance"]['Optional Payments']['Recurrent']
    opt_pay_custom_ref = inp["Refinance"]['Optional Payments']['Custom']
    fee_ref = inp["Refinance"]['Fee']

    # Original loan
    logging.info('\n')
    logging.info('-----------------------------')
    logging.info("Calculation for original loan")
    logging.info('-----------------------------')
    logging.info('\n')
    PMT_orig = monthly_payment(loan, term_orig, interest_rate_orig)  # Find monthly payment
    opt_orig = find_optional_pay(term_orig, opt_pay_recur_orig, opt_pay_custom_orig)  # Find list of optional payments

    data_orig = find_payment_table(loan, term_orig, interest_rate_orig, PMT_orig, opt_orig, escrow_orig)
    table, header = pretty_table(data_orig)

    print_messages(loan, escrow_orig, interest_rate_orig, term_ref, PMT_orig + escrow_orig)
    logging.info(tabulate(table, headers=header, tablefmt="github", numalign="left"))

    # Refinance
    logging.info('\n')
    logging.info('---------------------------')
    logging.info("Calculation for refinancing")
    logging.info('---------------------------')
    logging.info('\n')
    loan_ref = data_orig[start_ref]['Balance']  # Outstanding balance after s month of payment
    PMT_ref = monthly_payment(loan_ref, term_ref, interest_rate_ref)  # Find monthly payment
    opt_ref = find_optional_pay(term_ref, opt_pay_recur_ref, opt_pay_custom_ref)  # Find list of optional payments
    data_ref = find_payment_table(loan_ref, term_ref, interest_rate_ref, PMT_ref, opt_ref, escrow_ref)
    table_ref, header = pretty_table(data_ref)

    print_messages(loan_ref, escrow_ref, interest_rate_ref, term_ref, PMT_ref + escrow_ref)
    logging.info(tabulate(table_ref, headers=header, tablefmt="github", numalign="left"))
    # Modify original payment with extra principle that is paid in refinance
    PMT_diff = PMT_ref - PMT_orig  # Payment difference
    if PMT_diff > 0:
        logging.info('\n')
        logging.info('---------------------------------------------------------------------')
        logging.info("Adjusting the original plan with extra principle paid for refinancing")
        logging.info("Explain:")
        msg = """In the refinance plan, an extra amount of ${} is paid monthly. For apple to apple comaprision, this extra amount is added as an optional payment to the original plan from months {} onwards""".format(round(PMT_diff,2), start_ref)
        logging.info(msg)
        logging.info('---------------------------------------------------------------------')
        logging.info('\n')
        """In the refinance plan, the monthly payment is  greater than that of original plan. For an apple to apple
        comparision, we add the extra monthly payment to the original plan and recalculate everything"""
        pay_adjust = [0] * start_ref + [PMT_diff] * (term_orig - start_ref)  # extra payment for apple to apple comparision
        # Add the adjustment to the optional payment of the original payment
        opt_mod = []
        for this_opt, this_adjust in zip(opt_orig, pay_adjust):
            opt_mod.append(this_opt + this_adjust)
        data_mod = find_payment_table(loan, term_orig, interest_rate_orig, PMT_orig, opt_mod, escrow_orig)  # Recalculate the payment with the extra payment
        table_mod, header = pretty_table(data_mod)
        print_messages(loan, escrow_orig, interest_rate_orig, term_ref, PMT_orig + escrow_orig)
        term_mod = len(data_mod)
        logging.info(tabulate(table_mod, headers=header, tablefmt="github", numalign="left"))
    else:
        data_mod = data_orig
        term_mod = len(data_mod)

    # Analysis
    logging.info('\n')
    logging.info('--------')
    logging.info('Summary')
    logging.info('--------')
    logging.info('\n')
    total_i_orig = data_orig[-1]['Total Interest']  # Total interest paid in the original plan
    total_i_ref = data_ref[-1]['Total Interest']  # Total interest paid in refinancing plan
    total_i_mod = data_mod[-1]['Total Interest']  # Total interest paid in the modified original plan

    total_cost_orig = data_orig[-1]['Total Payment']  # Total interest paid in the original plan
    total_cost_ref = data_ref[-1]['Total Payment']  # Total interest paid in refinancing plan
    total_cost_mod = data_mod[-1]['Total Payment']  # Total interest paid in the modified original plan

    summary = [['Original', len(data_orig), interest_rate_orig, PMT_orig + escrow_orig, total_i_orig, total_cost_orig],
               ['Refinance', len(data_ref), interest_rate_ref, PMT_ref + escrow_ref, total_i_ref, total_cost_ref],
               ['Modified Original', len(data_mod), interest_rate_orig, PMT_orig + escrow_orig, total_i_mod, total_cost_mod]]

    logging.info(tabulate(summary, headers=['Method', 'Months', 'Interest Rate', 'Monthly Payment', 'Total Interest', 'Total of All Costs'], tablefmt="github", numalign="left"))
    logging.info('\n')

    # Analyse saving on the interest in refinancing
    ref_saving = round(total_i_mod - total_i_ref,2) - fee_ref
    if ref_saving > 0:
        msg = 'Your saving by refinancing is: {}'.format(ref_saving)
        logging.info(msg)
    else:
        msg = 'Your loosing this much by refinancing : {}'.format(-ref_saving)
        logging.info(msg)

    # Analyse break even point
    break_even_point = analyze_refinance_fee(data_ref, data_mod, fee_ref)
    msg = 'The break even point (month that saving on interest is equal to refinancing fee) is: {}'.format(break_even_point)
    logging.info(msg)


if __name__ == '__main__':
    main()

