import pandas as pd
from datetime import datetime

df = pd.DataFrame()
type_buy = {}

def init_csv():
    global df, type_buy
    try:
        df = pd.read_csv('data/base/output.csv')
        df = df.iloc[:, 1:]
        df['price'] = df['price'].astype(float)
        df['datetime'] = pd.to_datetime(df['datetime'], format='%d.%m.%Y %H:%M', errors='coerce')
                
        df['type'] = 'other'

        print(df.head())
        with open('data/base/type_buy.txt') as file:
            type_buy = dict([list(i.split(':')) for i in  file.read().split('\n')])
    except Exception as e:
        print("[ERROR] Cannot open CSV")
        print(e)


def typizer(operation):
    global type_buy

    if 'Оплата' in operation:
        pass
    elif 'перевод' in operation:
        pass
    elif 'Перевод между' in operation:
        pass
    


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