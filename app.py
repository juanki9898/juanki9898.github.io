from flask import Flask, render_template, request
import math

app = Flask(__name__)

class COLOR:
    GREEN   = "\033[92m"
    CYAN    = "\033[96m"
    YELLOW  = "\033[33m"
    ENDC    = "\033[0m"

class Label:
    INVESTMENT  = "investment"
    BOND        = "bond"
    SIMPLE      = "simple"
    COMPOUND    = "compound"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    investment_type = request.form.get('investment_type')
    if investment_type == Label.INVESTMENT:
        deposit_amount = float(request.form.get('deposit_amount'))
        interest_rate = float(request.form.get('interest_rate'))
        duration_total = int(request.form.get('duration_total'))
        interest_type = request.form.get('interest_type')

        investment_value = deposit_amount
        duration_current = 0
        interest_paid = 0
        interest_prior = 0

        def interest_compound():
            return investment_value * interest_rate / 100

        def interest_simple():
            return deposit_amount * interest_rate / 100

        def value_compound():
            return deposit_amount * math.pow(1 + interest_rate / 100, duration_total)

        def value_simple():
            return deposit_amount * (1 + interest_rate / 100 * duration_total)

        if interest_type == Label.COMPOUND:
            interest_fn = interest_compound
            value_fn = value_compound
        elif interest_type == Label.SIMPLE:
            interest_fn = interest_simple
            value_fn = value_simple
        else:
            raise NotImplementedError(f"Unknown interest type '{interest_type}'")

        projection = []

        while duration_current <= duration_total:
            relative_value = 100 * investment_value / deposit_amount
            projection.append({
                'duration': duration_current,
                'investment_value': round(investment_value, 2),
                'relative_value': round(relative_value, 1),
                'interest_prior': round(interest_prior, 2),
                'interest_paid': round(interest_paid, 2)
            })

            interest_prior = interest_fn()
            interest_paid += interest_prior
            investment_value += interest_prior
            duration_current += 1

        total_interest = value_fn() - deposit_amount
        final_value = value_fn()

        return render_template('result.html', investment=True, projection=projection,
                               total_interest=total_interest, final_value=final_value)

    elif investment_type == Label.BOND:
        house_value = float(request.form.get('house_value'))
        interest_rate = float(request.form.get('interest_rate'))
        months_total = int(request.form.get('months_total'))

        monthly_interest = interest_rate / 12
        monthly_payment = (house_value * (monthly_interest / 100)) / (
            1 - (1 + monthly_interest / 100) ** (-months_total)
        )
        capital_payment = (house_value * (monthly_interest / 100)) / (
            -1 + (1 + monthly_interest / 100) ** (months_total)
        )

        projection = []
        months_accum = 0
        loaned_amount = house_value
        owned_amount = 0
        total_paid = 0
        interest_paid = 0

        while months_accum <= months_total:
            projection.append({
                'months_accum': months_accum,
                'loaned_amount': round(loaned_amount, 2),
                'owned_amount': round(owned_amount, 2),
                'total_paid': round(total_paid, 2),
                'interest_paid': round(interest_paid, 2)
            })

            months_accum += 1
            loaned_amount -= capital_payment
            owned_amount += capital_payment
            total_paid += monthly_payment
            interest_paid += monthly_payment - capital_payment
            capital_payment *= 1 + monthly_interest / 100

        total_paid -= monthly_payment

        return render_template('result.html', bond=True, projection=projection,
                               total_paid=total_paid, interest_paid=interest_paid,
                               monthly_payment=monthly_payment)

if __name__ == '__main__':
    app.run(debug=True)
