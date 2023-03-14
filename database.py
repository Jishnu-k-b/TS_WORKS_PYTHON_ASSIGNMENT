import sqlite3
import datetime
from company_parser import parse

companies = parse()


def get_conn():
    return sqlite3.connect('finance_data.db')


def create_table():
    with get_conn() as conn:
        cursor = conn.cursor()
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


def insert_data(company, data):
    with get_conn() as conn:
        cursor = conn.cursor()
        for i in range(len(data)):
            cursor.execute('''
                INSERT OR IGNORE INTO finance_data (
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


def get_data_by_company(company_name):
    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM finance_data WHERE company = ?", (company_name,))
        data_of_company = cursor.fetchall()
    return data_of_company


def get_data_by_date_and_company(date_str, company_name):
    with get_conn() as conn:
        cursor = conn.cursor()
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        formatted_date = date_obj.strftime('%d-%m-%Y')
        cursor.execute("SELECT * FROM finance_data WHERE date = ? AND company = ? ", (formatted_date, company_name,))
        data = cursor.fetchall()
    return data


def get_data_by_start_date(start_date):
    with get_conn() as conn:
        cursor = conn.cursor()
        date_obj = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        s_date = date_obj.strftime('%d-%m-%Y')
        cursor.execute("SELECT * FROM finance_data WHERE date = ?", (s_date,))
        result = cursor.fetchall()
    return result


def update_database(company, date_str, open, high, low, close, adj_close, volume):
    with get_conn() as conn:
        cursor = conn.cursor()
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        new_date = date_obj.strftime('%d-%m-%Y')
        cursor.execute('''
            UPDATE finance_data
            SET open=?, high=?, low=?, close=?, adj_close=?, volume=?
            WHERE company=? AND date=?
        ''', (open, high, low, close, adj_close, volume, company, new_date))
        conn.commit()
        if cursor.rowcount > 0:
            message = 'Data updated for {} on {}'.format(company, new_date)
        else:
            message = "Error updating data"

    return message
