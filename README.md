# py_loan_calc
python script to calculate loan payment plans, refinance, etc.
# Description
This python script can calculate a loan payment plan. It outputs a table listing the details of payments for each month. If you intend to refinance an existing mortgage plan, this script helps compare the two plans and show the benefit or drawback of refinancing.
# Dependencies
The python script requires yaml and tabulate modules.
# Setting
There is a setting.yaml that you need to fill out. It asks for the amount of the loan, loan terms, interest rate, etc.
 # Output
In this tutorial, we work out the math behind paying back a loan. Assume you have borrowed an amount of money equal to PV from a lender. You are obligated to return that money plus an interest as a thank you to the loaner. The interest is proportional to the amount of loan for a given period of time. For every day that you hold on to that money, you owe a proportion of it to the lender. This proportion is called interest rate. In the real world, the interest rate is given for a year. A reasonable interest rate is 3% to 5%.  
Example: If you borrow $1000 for a year and the interest rate is 5%, after one year, you have to return
$1000 + 0.05 x $1000 = $1050
That means in addition to the principal value, you pay $50 as interest.
Loan payments recur monthly. In that case the interest rate is divided by 12.   
Assume we want to return a portion of the loan equal to p<sub>1</sub> after the first month. This portion is called principal. If the montly interest rate is r, we also owe `r.PV` as interest because we held the loan for a full month and the interest rate for one month is r and the interest value is proportional to the amount of loan. So the first payment is:  
T1 = p<sub>1</sub> + r PV  
From now on we owe PV - p<sub>1</sub> to the lender. Using the same argument, in the second month we should pay a portion that goes toward the proncipal and pay the interest for the money we owe during this month.
T2 = p<sub>2</sub> + r (PV - p<sub>1</sub> )
