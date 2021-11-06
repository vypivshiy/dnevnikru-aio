
Неофициальный __асинхронный__ API для работы с dnevnik.ru
___

Работает на основе прямой авторизации на сайт и парсинга html страниц с помощью aiohttp + bs4, так как официально 
получить доступ к их API может быть проблемой.

За идею взят проект синхронной библиотеки [paracosm17](https://github.com/paracosm17/dnevnikru)

**Requirements:**:
```
aiohttp
bs4
lxml
```
___
# Install:
```
pip install dnevnikru_aio
```
___
# Функции:
* Получение страницы дневника за неделю: расписание, оценки, число прогулов, домашние задания
* Получение пользователей
* Получение именинников
* Поддержка авторизации как через дневник.ру, так и через госуслуги
___
# Example:

```python
from dnevnik import Dnevnik
import asyncio


async def main():
    login, password = "cyberkid", "qwerty1"
    async with Dnevnik(login, password) as d:
        print("Авторизация на дневник.ру")
        await d.auth()
        # получения списка одноклассников
        class_users = await d.get_class_users()
        print("Одноклассники:", class_users.count)
        print(*[u.full_name for u in class_users.items[:5]], sep="\n")
        # календарь с числом именинников
        print("Календарь с месяцем, днём и ссылкой на него")
        # TODO, сделать запросы через этот объект для поиска именинников
        cal = await d.calendar_birthdays()
        print(*[f"{d.month_int()} {d.day} {d.count}" for d in cal.days[:12]])
        # близ именинники
        print("Именинники")
        async for users in d.birthdays_near(max_pages=1):
            print(users.count)
            print(*[u.full_name for u in users.items[:3]], end="...")
        # поиск всех людей
        print("\nВсе люди:")
        async for users in d.get_all_peoples(max_pages=1):
            print(users.count)
            print(*[u.full_name for u in users.items[:3]], sep="\n", end="...")
        # поиск по строке
        print("\nПоиск Олегов:")
        async for users in d.search_people(name="Олег", max_page=1):
            print(users.count)
            print(*[u.full_name for u in users.items[:3]], sep="\n", end="...")
        # дневник на неделю
        print("\nРасписание:")
        diary = await d.get_diary("29.09.2076")
        print(diary.info)
        for sc in diary.get_schedules:
            print(sc.day)
            print(sc.items)
            print()

# output example
# имена вымышленные все совпадения с реальностью случайны
'''
Авторизация на дневник.ру
Одноклассники: 30
Серёга Михаил Михаилович
Капитан Прайс
Джонни Сильверхенд
Александр Курицин
Илья Муромец Андреевич
Календарь с ДР
1 1 6 1 2 2 1 3 3 1 4 4 1 5 4 1 6 4 1 7 6 1 8 4 1 9 3 1 10 4 1 11 3 1 12 6
Именинники
28
Шелли Леонова Алекс Мерсер Заболотный Юрий Иванович Даниил Милохин Сергеевич...
Все люди:
1518
Иван Дурак
Аркадий Аркадиевич
Семён Персунов...
Поиск Олегов:
34
Газизов Рустем Олегович
Олег Картофельный Чай
Газманов Олег...
Расписание:
Сильверхендов Джонни  Школа №1 г. Найтсити"  0-undefined  2076 / 2077  с 29.09 по 05.10
понедельник
('Литература', 'Литература', 'Химия', 'Обществознание', 'Физкультура', 'История')

вторник
('Алгебра', 'Геометрия', 'Биология', 'Физика', 'Физика', 'География')

среда
('Физика', 'Алгебра', 'Инф. и ИКТ', 'Инф. и ИКТ', 'Обществознание', 'Англ. язык', 'ОБЖ')

четверг
('Алгебра', 'Геометрия', 'Англ. язык', 'Инф. и ИКТ', 'Инф. и ИКТ', 'Физика', 'Рус. язык')

пятница
('Физкультура', 'История', 'Алгебра', 'Химия', 'Литература', 'Физика', 'Англ. язык')

суббота
[]

воскресенье
[]

'''


if __name__ == '__main__':
    asyncio.run(main())
```
---
# Если авторизация работает _только_ через госуслуги:

~~Ну блин жааааль.~~ Необходимо дополнительно установить _playwright_ для эмуляции браузера:
```
pip install playwright
install playwright
```
Пример авторизации госуслуги:
```python
import asyncio
from session_gos import GosDiary
from gos_regions import KIROV_REGION  # ваш регион, в котором находится дневник

async def main():
    login, password = "79123456789", "qwerty123"
    gos_d = GosDiary(login, password, region_url=KIROV_REGION)
    diary = await gos_d.auth()
    async with diary as d:
        await d.get_class_users()
        # ... далее работа аналогична с классом Dnevnik
        
        
asyncio.get_event_loop().run_until_complete(main())
```

___
# TODO:
- [X] Добавить авторизацию через госуслуги
- [ ] Добавить 2FA госуслуги
- [ ] добавить некоторых методов для объектов
- [x] добавить автотесты
- [x] Поправить doc-strings
- [ ] Сделать страницу с документацией и примерами
- [ ] рефакторинг кода (рефакторинг???)
- [ ] опубликовать модуль на pypi
- [ ] сделать репозиторий-пример простого telegram бота для работы с этой библиотекой
