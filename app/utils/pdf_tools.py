import PyPDF2
import pandas as pd
from utils import BASE_DIR


data_base = {
    'operation' : [],
    'datetime' : [],
    'price' : []
}


def table_in_text(text):
    name, datetime, price = '', '', ''

    data = text[ text.rfind('\nДоговора\n')+10 : text.rfind('Страница') ]
    if '₽В' in data: data = data[ : data.find('₽В')+1 ] + '\n'

    list_operation = data.split(' ₽\n')
    for operation in list_operation:
        operation = list(operation.split('\n'))
        price = operation[-1][ operation[-1].rfind(' ')+1 : ].replace(',', '.')
        if '–' in operation[-1]: price = price.replace('–', '-')
        if '+' in operation[-1]: price = price.replace('+', '')
        if '\xa0' in operation[-1]: price = price.replace('\xa0', '')
        
        time_cord = operation[-1].find(':')
        
        if len(operation) <= 2:
            date_cord = operation[0].rfind('.')
            datetime = operation[0][ date_cord-5 : ] + ' ' + operation[-1][ time_cord-2 : time_cord+3]
            name = operation[0][:date_cord-5]
        else:
            date_cord = operation[-2].rfind('.')
            datetime = operation[-2][ date_cord-5 : ] + ' ' + operation[-1][ time_cord-2 : time_cord+3]
            name = (' '.join(operation[ : -2]) + ' ' + operation[-2][:date_cord-5]).replace('  ', ' ')

        name = name.strip()
        datetime = datetime.strip()
        price = price.strip()

        if name == datetime == price: continue
        data_base['operation'].append(name)
        data_base['datetime'].append(datetime)
        data_base['price'].append(price)


def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        pages = reader.pages
        for page in range(2, len(pages)):
            text = pages[page].extract_text()
            if "Описание операции" in text:
                table_in_text(text)

def pdf_to_csv(filename='input.pdf'):
    global BASE_DIR
    extract_text_from_pdf(BASE_DIR + '/data/pdf/' + filename)
    df = pd.DataFrame(data_base)
    df.to_csv(BASE_DIR + '/data/base/output.csv')