from bs4 import BeautifulSoup
import re
import os


# Вспомогательная функция, её наличие не обязательно и не будет проверяться
def build_tree(start, end, path):
    # Искать ссылки можно как угодно, не обязательно через re
    link_re = re.compile(r"^/wiki/([A-Za-z0-9_\(\)]+)$")
    # Словарь вида {"filename1": None, "filename2": None, ...}
    files = dict.fromkeys(os.listdir(path))
    # TODO Проставить всем ключам в files правильного родителя в значение, начиная от start
    marker = True
    i = 0
    step = dict()
    step[0] = [start]

    while marker and i < 10:
        step[i + 1] = list()
        for file in step[i]:

            with open("{}{}".format(path, file), 'r') as data:
                soup = BeautifulSoup(data, "lxml")
            section = soup.find(name='div', id='bodyContent')
            list_ = section.find_all(name='a', attrs={'href': link_re})

            list_of_avaible_pages = list()
            for tag in list_:
                tag = tag['href'][6:]

                if tag == end:
                    marker = False
                    files[tag] = file
                    break

                if tag in files and files[tag] is None:
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
    # print(bridge[::-1])
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
        with open("{}{}".format(path, file)) as data:
            soup = BeautifulSoup(data, "lxml")

        body = soup.find(id="bodyContent")

        # Количество картинок (img) с шириной (width) не меньше 200 +
        images = body.find_all(class_='image')
        imgs = 0
        headers = 0
        for image in images:
            if int(image.img['width']) >= 200:
                imgs += 1

        # Количество заголовков, первая буква текста внутри которого: E, T или C +
        reg_header = re.compile(r'^h\d*')
        all_headers = body.find_all(class_='mw-headline')
        all_headers = all_headers + \
            [i for i in body.find(class_='toctitle').find(reg_header)]
        for header in all_headers:

            if header.string is not None:

                if header.string[0] in 'ECT':
                    headers += 1

        linkslen = 0  # Длина максимальной последовательности ссылок, между которыми нет других тегов
        tag_a = body.find_next('a')
        max_len = 0
        index_key = 1
        debag_dict = dict()
        while tag_a is not None:
            debag_dict[index_key] = list()
            # print(tag_a.name)
            for broths in tag_a.find_next_siblings():
                debag_dict[index_key].append(broths)
                if True:
                    if broths.name is 'a':
                        linkslen += 1
                    else:
                        linkslen = 0
                        continue

            if max_len < linkslen:
                max_len = linkslen
                max_key = index_key
            index_key += 1
            linkslen = 0
            tag_a = tag_a.find_next('a')
        linkslen = max_len
        for i in debag_dict[max_key]:
            print(i)
        print('______________________________________________________________________')
        lists = 20  # Количество списков, не вложенных в другие списки

        out[file] = [imgs, headers, linkslen, lists]
    print(out)
    return out
