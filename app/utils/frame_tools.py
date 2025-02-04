import pandas as pd
from datetime import datetime
import re
from utils.pdf_tools import pdf_to_csv

df = pd.DataFrame()
type_buy = {}
name_buy = {}
organizations = []


def extract_english_words(text):
    words = re.findall(r"[A-Za-z.\-]+", text)
    return ' '.join(words) if words else None

def load_buyInfo():
    with open('data/base/type_buy.txt') as file:
        for line in file:
            organization, type, name = line.strip().split(':')
            type_buy[organization] = type
            name_buy[organization] = name
            organizations.append(organization)

def add_buyInfo(organization, type, name):
    type_buy[organization] = type
    name_buy[organization] = name
    organizations.append(organization)

def save_buyInfo():
    text = ''
    for organization in organizations:
        type, name = type_buy[organization], name_buy[organization]
        text += organization+':'+type+':'+name+'\n'
    with open('data/base/type_buy.txt', 'w') as file:
        file.write(text[:-1])

def init_dataFrame():
    global df
    df = pd.read_csv('data/base/output.csv')
    df = df.iloc[:, 1:]
    df['price'] = df['price'].astype(float)
    df['datetime'] = pd.to_datetime(df['datetime'], format='%d.%m.%Y %H:%M', errors='coerce')
    
    df[['operation', 'type', 'describe']] = df['operation'].apply(lambda x: pd.Series(typizer(x)))

def init_csv():
    try:
        load_buyInfo()
        try:
            init_dataFrame()
        except FileNotFoundError:
            print('[LOAD] Create CSV document from extract PDF')
            pdf_to_csv()
            print("[INFO] Success create!")
            init_dataFrame()
            print('[INFO] Initialization DataFrame from CSV document')
        
    except Exception as e:
        print("[ERROR]", e)


def find_info(name):
    if name in organizations:
        return type_buy[name], name_buy[name]
    else:
        return 'none', name


def typizer(operation):
    name, type, describe = "unknown", "none", ""

    if 'Оплата' in operation:
        if 'QR' in operation:
            if operation.count('(') == 1:
                name = operation[ operation.find('(')+1 : operation.find(')') ].strip()
            elif operation.count('(') == 2:
                name = operation[ operation.find('(')+1 : operation.rfind('(') ].strip()
            name = name.replace('_P_QR', '')
            type, name = find_info(name)
        else:
            name = extract_english_words(operation)
            type, name = find_info(name)
    elif 'перевод' in operation:
        operation = list(operation.split(', '))
        name = operation[1]
        type = 'transfer'
        describe = operation[-1]
    elif 'Перевод между' in operation:
        name = 'Перевод между счетами'
        type = 'transfer'
    elif 'Возврат средств СБП QR (Сервисы Яндекса)' in operation:
        name = 'Возврат Сервисы Яндекса'
        type = 'return'
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