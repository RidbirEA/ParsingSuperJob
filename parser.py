import requests
from bs4 import BeautifulSoup
import csv
import os.path
from tkinter import *


HOST = 'https://russia.superjob.ru'
HEADERS = {
	'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
	'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
}


# Получить список с данными
def get_content(html):
	soup = BeautifulSoup(html, 'html.parser')
	items = soup.find('div', class_='_1Ttd8 _2CsQi').find('div', class_="_1ID8B").find('div', class_="_3zucV undefined _3SGgo").find_all('div', class_="f-test-search-result-item")
	list = []
	for item in items:
		try:
			data = {
				'name': item.find('div', class_='_3mfro PlM3e _2JVkc _3LJqf').find('a', class_='icMQ_').get_text(),
				'town': item.find('span', class_='_3mfro f-test-text-company-item-location _9fXTd _2JVkc _2VHxz').find('span', class_=None).get_text(),
				'company': item.find('a', class_='_205Zx').get_text(), 
				'link': HOST + item.find('div', class_='_3mfro PlM3e _2JVkc _3LJqf').find('a', class_='icMQ_').get('href'),
				'price': item.find('span', class_='_3mfro _2Wp8I PlM3e _2JVkc _2VHxz').get_text(),
			}
			list.append(data)
		except:
			pass
	return list


# Перевести список в CSV файл
def get_csv(data, path):
	head = False if os.path.exists(path + '.csv') else True
	with open(path + '.csv', 'a', newline='') as file:
		writer = csv.writer(file, delimiter=';')
		writer.writerow(['Название', 'Город', 'Компания', 'Ссылка', 'Зарплата']) if head else None
		k = 1
		for item in data:
			try:
				writer.writerow(  [  item['name'], item['town'], item['company'], item['link'], item['price']  ]  )
			except UnicodeEncodeError:
				pass


# Интерфейс
def make_window():
	global dict
	list = ['Ссылка', 'Пагинации', 'Файл']
	window = Tk()
	form = Frame(window)
	form.pack()
	dict = {}
	for i in range(0, len(list)):
		Label(form, text=list[i]).grid(row=i, column=1)
		ent = Entry(form)
		ent.grid(row=i, column=2)
		dict[list[i]] = ent
	Button(window, text='Начать', command=parser).pack(side=RIGHT)
	return window


# Парсер
def parser():
	URL = dict['Ссылка'].get()
	URL = URL.split('?')[0]
	page = dict['Пагинации'].get().upper()
	path = dict['Файл'].get()
	list = []
	if page in {'ALL', 'ВСЕ'}:
		page = 1
		while True:
			print('Пагенация ' + page)
			html = requests.get(URL, headers=HEADERS, params={'page': page}).text
			if html.ok != True:
				return 'Ошибка сайта'
			data = get_content(html)
			if data == []:
				break
			else:
				list.extend(data)
				page += 1
	else: 
		try:
			page = int(page)
			for i in range(1, page + 1):
				print('Пагенация ' + str(i))
				html = requests.get(URL, headers=HEADERS, params={'page': i}).text
				data = get_content(html)
				list.extend(data)
		except:
			pass
	get_csv(list, path)
	Label(Tk(), text='Завершено').pack()
	

# Запуск
window = make_window()
window.mainloop()