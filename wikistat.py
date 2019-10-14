from bs4 import BeautifulSoup
import re
import os
import requests


# Вспомогательная функция, её наличие не обязательно и не будет проверяться
def build_tree(start, end, path):
    # Искать ссылки можно как угодно, не обязательно через re
    link_re = re.compile(r"^/wiki/([A-Za-z0-9_\(\)]+)$")
    # Словарь вида {"filename1": None, "filename2": None, ...}
    files = dict()
    # TODO Проставить всем ключам в files правильного родителя в значение, начиная от start
    marker = True
    i = 0
    step = dict()
    step[0] = [start]

    while marker and i < 10:
        step[i + 1] = list()
        for file in step[i]:
            page = requests.get(
                'https://en.wikipedia.org/wiki/{}'.format(file)).text
            soup = BeautifulSoup(page, "lxml")
            # with open("{}{}".format(path, file), 'r') as data:
            #     soup = BeautifulSoup(data, "lxml")
            section = soup.find(name='div', id='bodyContent')
            list_ = section.find_all(name='a', attrs={'href': link_re})

            list_of_avaible_pages = list()
            for tag in list_:
                tag = tag['href'][6:]

                if tag == end:
                    marker = False
                    files[tag] = file
                    break
                elif tag not in files:
                    files[tag] = file
                    step[i + 1].append(tag)

        i += 1

    # print(files[end])

    return files


# Вспомогательная функция, её наличие не обязательно и не будет проверяться
def build_bridge(start, end, path):
    files = build_tree(start, end, path)
    bridge = [end]
    key = end
    while key != start:
        bridge.append(files[key])
        key = files[key]
    print(bridge[::-1])
    return bridge[::-1]


def parse(start, end, path):
    """
    Если не получается найти список страниц bridge, через ссылки на которых можно добраться от start до end, то,
    по крайней мере, известны сами start и end, и можно распарсить хотя бы их: bridge = [end, start]. Оценка за тест,
    в этом случае, будет сильно снижена, но на минимальный проходной балл наберется, и тест будет пройден.
    Чтобы получить максимальный балл, придется искать все страницы. Удачи!
    """

    # Искать список страниц можно как угодно, даже так: bridge = [end, start]
    bridge = build_bridge(start, end, path)

    # Когда есть список страниц, из них нужно вытащить данные и вернуть их
    out = {}
    for file in bridge:

        page = requests.get(
            'https://en.wikipedia.org/wiki/{}'.format(file)).text
        soup = BeautifulSoup(page, "lxml")

        body = soup.find(id="bodyContent")

        # TODO посчитать реальные значения
        images = body.find_all(class_='image')
        imgs = 0
        headers = 0
        for image in images:
            if int(image.img['width']) >= 200:
                imgs += 1
        reg_header = re.compile(r'^h\d*')
        all_headers = body.find_all(class_='mw-headline')
        all_headers = all_headers + [i for i in body.find(
            class_='toctitle').find(reg_header)]
        for header in all_headers:

            if header.string is not None:

                if header.string[0] == 'E':
                    headers += 1
                    print('<{}> {} <{}>'.format(
                        header.name, header.string, header.name))
                if header.string[0] == 'C':
                    headers += 1
                    print('<{}> {} <{}>'.format(
                        header.name, header.string, header.name))
                if header.string[0] == 'T':
                    print('<{}> {} <{}>'.format(
                        header.name, header.string, header.name))
                    headers += 1

        # Количество картинок (img) с шириной (width) не меньше 200 +
        # Количество заголовков, первая буква текста внутри которого: E, T или C +
        linkslen = 15  # Длина максимальной последовательности ссылок, между которыми нет других тегов
        lists = 20  # Количество списков, не вложенных в другие списки

        out[file] = [imgs, headers, linkslen, lists]
    print(out)
    return out
