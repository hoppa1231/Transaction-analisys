import pandas as pd
from datetime import datetime
import re
from utils.pdf_tools import pdf_to_csv
from utils import BASE_DIR

df = pd.DataFrame()
type_buy = {}
name_buy = {}
organizations = []


def extract_english_words(text):
    words = re.findall(r"[A-Za-z.\-]+", text)
    return ' '.join(words) if words else None

def load_buyInfo():
    # Explicit UTF-8 to avoid locale-dependent decode errors
    with open(BASE_DIR + '/data/base/type_buy.txt', encoding='utf-8') as file:
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
    with open(BASE_DIR + '/data/base/type_buy.txt', 'w', encoding='utf-8') as file:
        file.write(text[:-1])

def init_dataFrame():
    global df
    df = pd.read_csv(BASE_DIR + '/data/base/output.csv')
    # Drop legacy index column if present
    if df.columns[0].startswith('Unnamed'):
        df = df.iloc[:, 1:]

    required_cols = {'operation', 'datetime', 'price'}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Отсутствуют колонки: {', '.join(missing)}")

    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['datetime'] = pd.to_datetime(df['datetime'], format='%d.%m.%Y %H:%M', errors='coerce', dayfirst=True)
    df['operation'] = df['operation'].astype(str)

    if len(df):
        def safe_typizer(op):
            try:
                res = typizer(str(op))
                if not isinstance(res, (list, tuple)):
                    return (str(res), 'none', '')
                if len(res) == 3:
                    return tuple(res)
                if len(res) > 3:
                    return tuple(res[:3])
                return tuple(list(res) + [''] * (3 - len(res)))
            except Exception:
                return (str(op), 'none', '')

        df[['operation', 'type', 'describe']] = df['operation'].apply(lambda x: pd.Series(safe_typizer(x)))
    else:
        df['type'] = []
        df['describe'] = []
    df = df.dropna(subset=['price', 'datetime'])

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


def refresh_data_from_pdf(filename, input_path=None):
    """Rebuild CSV and dataframe from a freshly uploaded PDF."""
    pdf_to_csv(filename=filename, input_path=input_path)
    init_dataFrame()


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

    if not filtered_df.empty:
        filtered_df = filtered_df.copy()
        filtered_df['datetime'] = filtered_df['datetime'].dt.strftime('%Y-%m-%d %H:%M')
    total = float(filtered_df['price'].sum()) if not filtered_df.empty else 0.0
    
    return filtered_df.to_dict(orient='records'), total

init_csv()
