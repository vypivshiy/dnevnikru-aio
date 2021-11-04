import asyncio
from os import getenv, listdir, remove
from session import DiaryAPI
"""
Модуль авторизации и загрузки html страниц для теста парсеров
"""

try:
    import dotenv
except (ImportError, ModuleNotFoundError):
    raise ImportError(
        """
Для корректной работы тестов необходимо установить python-dotenv,
создать файл .env и добавить поля:
login=  # логин дневникру
password=  # пароль дневникру
date=  # дата, за которую гарантированно вернёт дневник за неделю
""")

dotenv.load_dotenv()
login = getenv("login")
password = getenv("password")
date = getenv("date")


def save(name: str, html: str):
    with open(f"{name}.html", "w") as f:
        f.write(html)


def remove_files():
    for file in listdir():
        if file.endswith(".html"):
            remove(file)


def open_html(file):
    with open(file) as f:
        return f.read()


async def download():
    print("auth")
    async with DiaryAPI(login, password) as d:
        await d.auth()
        p_id, s_id, c_id = d.get_profile_id, d.get_school_id, d.get_class_id

        print("download diary page")
        year = date.split(".")[-1]
        url = d.WEEK_DIARY_URI + p_id + "/" + s_id + "/" + year + "/" + date
        resp = await (await d.request_get(url)).text()
        save("diary", resp)

        print("download calendar_birthdays page")
        resp = await (await d.request_get(d.BIRTHDAY_URI, params={"school": s_id, "view": "calendar"})).text()
        save("bday_calendar", resp)

        print("download userfeed page")
        resp = await (await d.request_get(d.USER_URI)).text()
        save("userfeed", resp)

        print("download school page")
        resp = await (
            await d.request_get(d.SCHOOL_URI, params={"school": s_id, "view": "members", "group": "all"})).text()
        save("school", resp)
        print("download bday-near page")
        resp = await (await d.request_get(d.BIRTHDAY_URI, params={"school": s_id, "group": "all"})).text()
        save("bday_near", resp)

        print("download class page")
        resp = await (await d.request_get(d.CLASS_URI, params={"class": c_id, "view": "members"})).text()
        save("class_users", resp)

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(download())
    print("done")
