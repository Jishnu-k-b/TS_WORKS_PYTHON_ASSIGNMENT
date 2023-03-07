import yfinance as yf

from company_parser import parse

from database import get_conn, insert_data, create_table, get_data_by_company, get_data_by_date_and_company, \
    get_data_by_start_date, update_database

from flask import Flask, render_template, request

app = Flask(__name__)

companies = parse()

get_conn()


@app.route('/')
def index():
    return render_template('index.html', companies=companies)


@app.route('/download_data', methods=['POST'])
def download_data():
    create_table()
    for company in companies:
        data = yf.download(company)
        insert_data(company, data)
    message = 'Data downloaded for all companies'
    return render_template('index.html', companies=companies, message=message)


@app.route('/view_data_of_company', methods=['GET', 'POST'])
def view_data_of_company():
    if request.method == 'POST':
        company_name = request.form['company_name']

        data_of_company = get_data_by_company(company_name)

        return render_template('view_data_of_company.html', data_of_company=data_of_company)

    return render_template('view_data_of_company.html')


@app.route('/view_data_specific_date', methods=['GET', 'POST'])
def view_data_specific_date():
    if request.method == "POST":
        specific_date_ = request.form.get('specific_date')
        company1 = request.form.get('company1')

    data = get_data_by_date_and_company(specific_date_, company1)
    if not data:
        message = 'Data not found for the selected date and company'
        return render_template('not_found.html', message=message)
    else:
        return render_template('view_data_specific_date.html', data=data, )


@app.route('/start_end', methods=['GET', 'POST'])
def start_end():
    if request.method == "POST":
        start_date = request.form.get('start_date')
        result = get_data_by_start_date(start_date)

    if not result:
        message = 'Data not found for the selected date and company'
        return render_template('not_found.html', message=message)
    else:
        return render_template('start_end.html', result=result)


@app.route('/update_data', methods=['GET', 'POST'])
def update_data():
    message = None
    if request.method == "POST":
        company = request.form.get('company')
        date = request.form['date']
        open = request.form['open']
        high = request.form['high']
        low = request.form['low']
        close = request.form['close']
        adj_close = request.form['adj_close']
        volume = request.form['volume']
        message = update_database(company, date, open, high, low, close, adj_close, volume)

    return render_template('update_data.html', companies=companies, message=message)


if __name__ == '__main__':
    app.run(debug=True)
