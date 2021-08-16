import pandas as pd
import numpy_financial as npf
import matplotlib.pyplot as plt 
import seaborn as sns 



    

def payments_per_period(rate_in_months, per, period_in_months, principal): 
    # The interest payment for a given period 
    rate_in_months = rate_in_months / 100 / 12
    period_in_months = period_in_months * 12
    interest_payment = npf.ipmt(rate_in_months, per, period_in_months, -principal)

    # The principal payment for a given period
    principal_payment = npf.ppmt(rate_in_months, per, period_in_months, -principal)

    total_payment = interest_payment + principal_payment

    print(f'Period # {per}')
    print('Interest Payment: {:,.2f}'.format(interest_payment))
    print('Principal Payment: {:,.2f}'.format(principal_payment))
    print('Total Payment: {:,.2f}'.format(total_payment))
    print('Split: {:.2%} Interest {:,.2%} Principal'.format(interest_payment / total_payment, principal_payment / total_payment))


def create_table(start_date, rate_in_months, period_in_years, principal, additional_pmt, show = True):
    period_in_months = period_in_years * 12
    rate_in_months = rate_in_months / 100 / 12
    rng = pd.date_range(start= pd.to_datetime(start_date).date(), periods= period_in_months, freq='MS')
    rng

    # Creading the data frame 

    df = pd.DataFrame(index=rng, columns=['Payment','Principal','Interest','Additional Principal','Balance'])
    df.index.name = "Period"

    # Adding the payment is easy since it will always be the same

    df['Payment'] = npf.pmt(rate_in_months, period_in_months, principal)

    # The principal and interest change over time but since we can grab the periods using df.index, we can just use that in our formula
    df['Principal'] = npf.ppmt(rate_in_months, df.reset_index().index + 1, period_in_months, -principal)
    df['Interest'] = npf.ipmt(rate_in_months, df.reset_index().index + 1, period_in_months, -principal)
    df['Additional Principal'] = additional_pmt

    df['Cumulative Principal'] = (df['Principal'] + df['Additional Principal']).cumsum()
    df['Cumulative Principal'] = df['Cumulative Principal'].clip(upper = principal)
    df['Balance'] = principal - df['Cumulative Principal']
    pd.set_option('display.max_rows', None)

    
    # There is a better way to do the below thing but im too tired to figure it out 
    if (df['Balance'] <= 0).sum() == 0:
        if show == True: 
            print(f"Total Interest Paid: ${df['Interest'].sum():,.2f}")
            display(df.round(2))
        else: 
            return df
    elif (df['Balance'] <= 0).sum() >= 1:
        df = df.reset_index()
        last_payment = df[df['Balance'] <= 0][:1].index
        df.loc[last_payment, "Principal"] = df.loc[last_payment[0] - 1, "Balance"]
        df.loc[last_payment, "Payment"] = - df.loc[last_payment[0], ["Principal", "Interest"]].sum()
        df.loc[last_payment, "Additional Principal"] = 0
        df = df.loc[0:last_payment[0]]
        if show == True:
            print(f"Total Interest Paid: ${df['Interest'].sum():,.2f}")
            df = df.set_index('Period')
            pd.options.display.float_format = '{:,}'.format
            display(df.round(2))
        else: 
            return df

### Creating the amortization graph
def create_graph(start_date, rate_in_months, period_in_years, principal, additional_pmt):
   """ This function takes in the input data and then displays a graph representing the balance of an amortized loan"""
   df = create_table(
        start_date,
        rate_in_months,
        period_in_years,
        principal,
        additional_pmt,
        show=False,
    )
   if additional_pmt == 0:
      display(x=sns.lineplot(x="Period", y="Balance", data=df))
   else:
      base_df = create_table(
         start_date, rate_in_months, period_in_years, principal, 0, show=False
      )
      display(
         x=sns.lineplot(
            x="Period", y="Balance", data=df, label="With Additional Payments"
         ),
         y=sns.lineplot(
            x="Period",
            y="Balance",
            data=base_df,
            label="Without additional Payments",
         ),
         z=plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.0),
      )
