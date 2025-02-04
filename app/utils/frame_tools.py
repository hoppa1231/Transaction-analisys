import pandas as pd
from datetime import datetime
import re
from utils.pdf_tools import pdf_to_csv

df = pd.DataFrame()
type_buy = {}
name_buy = {}


def extract_english_words(text):
    words = re.findall(r"[A-Za-z.\-]+", text)
    return ' '.join(words) if words else None


def init_dataFrame():
    global df
    df = pd.read_csv('data/base/output.csv')
    df = df.iloc[:, 1:]
    df['price'] = df['price'].astype(float)
    df['datetime'] = pd.to_datetime(df['datetime'], format='%d.%m.%Y %H:%M', errors='coerce')
    
    df[['operation', 'type', 'describe']] = df['operation'].apply(lambda x: pd.Series(typizer(x)))

def init_csv():
    global type_buy
    try:
        with open('data/base/type_buy.txt') as file:
            for line in file:
                temp = line.strip().split(':')
        try:
            init_dataFrame()
        except FileNotFoundError:
            print('[LOAD] Create CSV document from extract PDF')
            pdf_to_csv()
            print("[INFO] Success create!")
            init_dataFrame()
            print('[INFO] Initialization DataFrame from CSV document')
        
    except Exception as e:
        print("[ERROR] Cannot open CSV")
        print(e)


def typizer(operation):
    global type_buy

    name, type, describe = "unknown", "none", ""

    if 'Оплата' in operation:
        name = extract_english_words(operation)
        if name in type_buy.keys():
            type = type_buy[name]
    elif 'перевод' in operation:
        operation = list(operation.split(', '))
        name = operation[1]
        type = 'transfer'
        describe = operation[-1]
    elif 'Перевод между' in operation:
        name = 'Перевод между счетами'
        type = 'transfer'
    else:
        name = operation

    return name, type, describe


def filter_price(start_date=None, end_date=None, sign='+'):
    global df
    # Если start_date не указан, берем начало текущего месяца
    if start_date is None:
        start_date = datetime.today().replace(day=1).strftime('%Y-%m-%d')

    # Если end_date не указан, берем текущую дату
    if end_date is None:
        end_date = datetime.today().strftime('%Y-%m-%d')

    # Фильтруем данные
    filtered_df = df[
        (df['price'] > 0 if sign == '+' else df['price'] < 0) &
        (df['datetime'] >= pd.to_datetime(start_date)) &
        (df['datetime'] <= pd.to_datetime(end_date))
    ]
    filtered_df = filtered_df.sort_values(by='price', key=lambda x: x.abs(), ascending=False)
    
    return filtered_df.to_dict(orient='records'), filtered_df['price'].sum()
init_csv()