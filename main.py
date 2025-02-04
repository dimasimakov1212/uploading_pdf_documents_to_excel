import os

from pdfminer.layout import LTTextContainer

import pandas as pd

from services import pdf_scraper

# следующие ссылки необходимо заменить на адреса папок в GDrive
path_to_notebook = '/content/drive/MyDrive/NetologyDS/O2RUS/'  # ссылка на папку с блокнотом (сюда будут сохраняться результаты)
path = path_to_notebook + 'RDF/'  # ссылка на папку с документами

# итерация по файлам с запуском функции pdf_scraper, в случае ошибки выводим название проблемного документа

data = []  # пустой список для словарей
tickets = os.listdir(path)  # список файлов в директории

for document in tickets:
    try:
        data.append(pdf_scraper(path, document))
    except (IndexError, ValueError) as err:
        print(f'Ошибка при парсинге документа: {document}.')

print(f'В директории {len(tickets)} документов.\nУспешно проанализировано {len(data)} ({int(len(data)/len(tickets)*100)}%) документов.')

# преобразовываем получившийся список в датафрейм
df = pd.DataFrame(data)

# нумерация с 1
df.index += 1

# проверка на сумму штрафа
df['Сумма штрафа более 5000'] = df['Сумма штрафа'] > 5000

# агрегация по адресам и с количеством штрафов по каждому адресу
agg_table = df.groupby('Адрес').size().reset_index(name='Количество')

# индексация с 1
agg_table.index += 1

# переименуем колонки
agg_table.index.names = ['№']
agg_table.rename(columns={'Адрес':'Адрес местоположения'}, inplace=True)

# датафрейм с результатом скрапинга
df.head()

# создаем 3 новых датафрейма
df_low = df.loc[df['Сумма штрафа'] < 2500]
df_mid = df.loc[(df['Сумма штрафа'] >= 2500) & (df['Сумма штрафа'] < 5000)]
df_high = df.loc[df['Сумма штрафа'] >= 5000]

df_low.head()
df_mid.head()
df_high.head()

# экспортировать как таблицы Excel
# по умолчанию экспорт осуществляется в ту же папку, где находится ярлык RDF
df.to_excel(path_to_notebook + 'штрафы.xlsx')
df_low.to_excel(path_to_notebook + 'штрафы_низк.xlsx')
df_mid.to_excel(path_to_notebook + 'штрафы_средн.xlsx')
df_high.to_excel(path_to_notebook + 'штрафы_выс.xlsx')
agg_table.to_excel(path_to_notebook + 'аг_штрафы.xlsx')


if __name__ == '__main__':

    print('')
