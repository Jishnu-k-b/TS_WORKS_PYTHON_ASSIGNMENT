import yfinance as yf

import sqlite3

import configparser

import datetime

from flask import Flask, render_template, request

app = Flask(__name__)

config = configparser.ConfigParser()

config.read('config.ini')

companies = config['DEFAULT']['companies'].split(',')


def get_conn():
    return sqlite3.connect('finance_data.db')


@app.route('/')
def index():
    return render_template('index.html', companies=companies)


@app.route('/load_data', methods=['POST'])
def load_data():
    conn = get_conn()
    cursor = conn.cursor()

    for company in companies:
        data = yf.download(company)
        cursor.execute('''
         CREATE TABLE IF NOT EXISTS finance_data (

            company text,

            date text,

            open real,

            high real,

            low real,

            close real,

            adj_close real,

            volume real,

            PRIMARY KEY (company, date)

        )
        ''')
        for i in range(len(data)):
            cursor.execute('''
            INSERT OR REPLACE INTO finance_data (

                company,
                

                date,

                open,

                high,

                low,

                close,

                adj_close,

                volume
                )
                VALUES (?,?,?,?,?,?,?,?)
                ''', (
                company,
                data.index[i].strftime('%d-%m-%Y'),
                data.iloc[i]['Open'],
                data.iloc[i]['High'],
                data.iloc[i]['Low'],
                data.iloc[i]['Close'],
                data.iloc[i]['Adj Close'],
                data.iloc[i]['Volume'],
            ))
            conn.commit()
    conn.close()
    message = 'Data downloaded for all companies'
    return render_template('index.html', companies=companies, message=message)


@app.route('/view_data_of_company', methods=['GET', 'POST'])
def view_data_of_company():
    if request.method == 'POST':
        company_name = request.form['company_name']

        conn = get_conn()

        cursor = conn.cursor()

        cursor.execute("SELECT * FROM finance_data WHERE company = ?", (company_name,))

        data_of_company = cursor.fetchall()

        conn.close()

        return render_template('view_data_of_company.html', data_of_company=data_of_company)

    return render_template('view_data_of_company.html')


@app.route('/view_data_specific_date', methods=['GET', 'POST'])
def view_data_specific_date():
    conn = get_conn()
    cursor = conn.cursor()
    if request.method == "POST":
        specific_date_ = request.form.get('specific_date')
        company1 = request.form.get('company1')

    date_obj = datetime.datetime.strptime(specific_date_, '%Y-%m-%d')
    formatted_date = date_obj.strftime('%d-%m-%Y')

    cursor.execute("SELECT * FROM finance_data WHERE date = ? AND company = ? ", (formatted_date, company1,))

    data = cursor.fetchall()

    conn.close()

    if not data:
        message = 'Data not found for the selected date and company'
        return render_template('not_found.html', message=message)
    else:
        return render_template('view_data_specific_date.html', data=data, )


@app.route('/start_end', methods=['GET', 'POST'])
def start_end():
    conn = get_conn()
    cursor = conn.cursor()
    if request.method == "POST":
        start_date = request.form.get('start_date')

    date_obj = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    s_date = date_obj.strftime('%d-%m-%Y')

    cursor.execute("SELECT * FROM finance_data WHERE date = ?", (s_date,))
    result = cursor.fetchall()
    conn.close()

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

        date_obj = datetime.datetime.strptime(date, '%Y-%m-%d')
        new_date = date_obj.strftime('%d-%m-%Y')

        conn = get_conn()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE finance_data
            SET open=?, high=?, low=?, close=?, adj_close=?, volume=?
            WHERE company=? AND date=?
        ''', (open, high, low, close, adj_close, volume, company, new_date))

        conn.commit()
        conn.close()

        if cursor.rowcount > 0:
            message = 'Data updated for {} on {}'.format(company, date)
        else:
            message = "Error updating data."

    return render_template('update_data.html', companies=companies, message=message)


if __name__ == '__main__':
    app.run(debug=True)
