import re  #regex для парсинга текста

from pdfminer.high_level import extract_text


def pdf_scraper(filepath, filename):
    """ Функция предназначена для автоматического извлечения следующих параметров из PDF-файла с постановлением:
    - Имя файла
    - № постановления
    - Дата нарушения
    - Время нарушения
    - Адрес нарушения
    - Госномер автомобиля
    - Сумма штрафа
    - СТС
    Функция принимает путь к папке с файлом и имя файла
    Функция возвращает словарь вида {параметр:значение} """

    # пустой словарь для сохранения данных
    scraped_data = {}

    # считываем текстовые данные и заполняем список
    text = extract_text(filepath + filename).replace('\n', ' ')

    ticket_id = (re.findall('(?:ПОСТАНОВЛЕНИЕ\s*|ПОСТАНОВЛЕНИЕ\s*№)(.\d*)', text))[0]  # номер постановления
    date = re.findall('(?:УСТАНОВИЛ:\s*MMM|УСТАНОВИЛ:\s*)(\d{1,2}\.\d{1,2}\.\d{2,4})', text)[0]  # дата
    time = re.findall('(\d{1,2}\:\d{1,2}\:\d{1,2})', text)[0]  # время
    address = re.findall('(?:адресу\s+|адресу:)(.*)(?:зафиксировано|водитель|транспортное|,\s*собственник)', text)[0]  # адрес
    license_no = re.findall('(?:знак\s+|ГРЗ\s+)(\D{1}\d{3}\D{2}\d{2,3}|\D{2}\d{6})(?:\s*|,)', text)[0]  # госномер
    temp = re.findall('размере\s*(.*?)\s*руб.', text)[0]  # размер штрафа, символьный
    fine = int(''.join(re.findall('\d+', temp)))  # размер штрафа, числовой
    sts = int(re.findall('(?:СТС:|СТС\s*)(.\d+)', text)[0])  # СТС

    # сохраним результат в список
    scraped_data['Номер файла'] = filename[:-4]  # удаляем формат файла (последние 4 символа)
    scraped_data['Постановление'] = ticket_id
    scraped_data['Дата'] = date
    scraped_data['Время'] = time
    scraped_data['Адрес'] = address
    scraped_data['Гос номер'] = license_no
    scraped_data['Сумма штрафа'] = fine
    scraped_data['Номер СТС'] = sts

    # возвращаем словарь
    return scraped_data
