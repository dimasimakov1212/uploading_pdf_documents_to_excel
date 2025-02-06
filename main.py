import os
import shutil
from tkinter import *
from tkinter import messagebox

import pandas as pd

from services import pdf_scraper, reading_existing_file_excel

# следующие ссылки необходимо заменить на необходимые
path_pdf = 'docs/pdf/'  # папка с исходными документами
path_pdf_done = 'docs/pdf/done/'  # папка с обработанными документами
path_pdf_error = 'docs/pdf/error/'  # папка с необработанными документами
path_excel = 'docs/excel/'  # папка с excel документами
all_fines_file = path_excel + 'все_штрафы.xlsx'  # итоговый файл со всеми штрафами
low_fines_file = path_excel + 'штрафы_до_2500.xlsx'  # итоговый файл с маленькими штрафами
middle_fines_file = path_excel + 'штрафы_2500_5000.xlsx'  # итоговый файл со средними штрафами
high_fines_file = path_excel + 'штрафы_от_5000.xlsx'  # итоговый файл с большими штрафами
addresses_fines_file = path_excel + 'адреса_штрафов.xlsx'  # итоговый файл со штрафами по адресам

# получаем список с данными
data = reading_existing_file_excel(all_fines_file)
start_num = len(data)

documents_count = 0  # количество документов для обработки

documents = os.listdir(path_pdf)  # список элементов для обработки

for document in documents:
    full_document_path = os.path.join(path_pdf, document)

    if os.path.isfile(full_document_path):  # Проверяем, что это файл
        documents_count += 1

        try:
            data.append(pdf_scraper(path_pdf, document))

            # Перемещение файла в папку для обработанных документов
            shutil.move(full_document_path, os.path.join(path_pdf_done, document))

        except (IndexError, ValueError) as err:

            # Перемещение файла в папку для документов с ошибками
            shutil.move(full_document_path, os.path.join(path_pdf_error, document))
            print(f'Ошибка при парсинге документа: {document}.')

    else:
        print(f'Пропущен не файл: {document}')

documents_count_text = f'Найдено для обработки {documents_count} документов'
print(documents_count_text)

success_documents_text = ''
error_documents_text = f'Не обработано {documents_count - (len(data) - start_num)} документов'

if documents_count > 0:
    success_documents_text = (f'Успешно проанализировано '
                              f'{len(data) - start_num} ({int((len(data) - start_num)/documents_count * 100)}%) '
                              f'документов')
    print(success_documents_text)

if len(data) > 0:
    # преобразуем получившийся список в датафрейм
    df_all = pd.DataFrame(data)
    df_all.index += 1  # нумерация с 1

    # проверка на сумму штрафа
    df_all['Сумма штрафа более 5000'] = df_all['Сумма штрафа'] > 5000


    # агрегация по адресам с количеством штрафов по каждому адресу
    agg_table = df_all.groupby('Адрес').size().reset_index(name='Количество')
    agg_table.index += 1  # нумерация с 1

    # переименуем колонки
    agg_table.index.names = ['№']
    agg_table.rename(columns={'Адрес':'Адрес местоположения'}, inplace=True)

    # датафрейм с результатом скрапинга
    df_all.head()

    # создаем 3 новых датафрейма
    df_low = df_all.loc[df_all['Сумма штрафа'] < 2500]
    df_mid = df_all.loc[(df_all['Сумма штрафа'] >= 2500) & (df_all['Сумма штрафа'] < 5000)]
    df_high = df_all.loc[df_all['Сумма штрафа'] >= 5000]

    df_low.head()
    df_mid.head()
    df_high.head()

    # экспортировать как таблицы Excel
    df_all.to_excel(all_fines_file)
    df_low.to_excel(low_fines_file)
    df_mid.to_excel(middle_fines_file)
    df_high.to_excel(high_fines_file)
    agg_table.to_excel(addresses_fines_file)

# Чтение данных из Excel файла
list_of_dicts = reading_existing_file_excel(all_fines_file)
print('Итоговый файл содержит', len(list_of_dicts), 'записей')

def close_program():
    """ Закрывает окно программы """
    if messagebox.askokcancel('Завершение работы программы', 'Хотите выйти?'):
        tk.destroy()

# окно уведомления о завершении работы программы
tk = Tk()

tk.title('Загрузка штрафов из постановлений PDF в таблицы Excel')
tk.protocol("WM_DELETE_WINDOW", close_program)
tk.resizable(None, None)  # запрет на растягивание окна по горизонтали и вертикали
tk.wm_attributes("-topmost", 1)  # расположение окна поверх других окон
tk.iconbitmap("Icon_docs.ico")

# параметры окна
window_width = 600
window_height = 200

# создаем окно программы
canvas = Canvas(tk, width=window_width, height=window_height, highlightthickness=0)
canvas.pack()

canvas.create_text(window_width / 2, 20, text=documents_count_text, font=('Arial', 11), anchor='n')
canvas.create_line(50, 50, 550, 50, width=1)
canvas.create_text(window_width / 2, 70, text=success_documents_text, font=('Arial', 11), anchor='n')
if documents_count - (len(data) - start_num) > 0:
    canvas.create_text(window_width / 2, 90, text=error_documents_text, font=('Arial', 11), anchor='n')

tk.mainloop()


if __name__ == '__main__':
    pass
