import requests
from bs4 import BeautifulSoup
from PIL import Image
import base64
import json


def solve_captcha():
    captcha_res = requests.get(url="https://мвд.рф/captcha")
    captcha_img = captcha_res.content

    with open("captcha.jpeg", "wb") as f:
        f.write(captcha_img)

    img = Image.open("captcha.jpeg")
    img.show()
    captcha_text = input("Введите текст с изображения\n")

    return captcha_text, captcha_res.cookies


def get_wanted(captcha, cookie):
    while True:
        full_name = input("Введите Фамилию, Имя, Отчество через пробел\n")
        date_of_birth = input("Введите дату рождения в формате ДД ММ ГГГГ\n")

        if len(date_of_birth.split()) != 3 or len(full_name.split()) != 3:
            print("Неверный формат ФИО или даты рождения, попробуйте еще раз\n")
            continue

        day, month, year = date_of_birth.split()
        last_name, first_name, patronymic = full_name.split()

        if len(day) != 2 or len(month) != 2 or len(year) != 4:
            print("Неверно введена дата рождения, попробуйте еще раз\n")
            continue

        break

    payload = {
        "s_family": last_name,
        "fio": first_name,
        "s_patr": patronymic,
        "d_year": year,
        "d_month": month,
        "d_day": day,
        "email": "test@test.com",
        "captcha": captcha
    }

    response = requests.get(url="https://мвд.рф/wanted",
                            params=payload, cookies=cookie)
    soup = BeautifulSoup(response.text, "lxml")

    try:
        exists = bool(
            int(soup.find("div", class_="bs-count m-b15").text.strip()[-1]))
    except AttributeError:
        print("Неверно введена каптча")
        exit()
    photo_b64_string = None

    if exists:
        try:
            image_tag = soup.find("div", class_="bs-item-image").find("img")
        except AttributeError:
            pass
        else:
            photo_url = image_tag["src"]
            photo_res = requests.get("https:" + photo_url)
            photo_b64_bytes = base64.b64encode(photo_res.content)
            photo_b64_string = photo_b64_bytes.decode()

    return payload, exists, photo_b64_string


def create_output_file(payload, exists, photo_b64):
    output_dict = {
        "last_name": payload["s_family"],
        "first_name": payload["fio"],
        "patronymic": payload["s_patr"],
        "day_of_birth": payload["d_year"],
        "month_of_birth": payload["d_month"],
        "year_of_birth": payload["d_day"],
        "photo_b64": photo_b64,
        "exists": exists,
    }

    with open("output.json", "w") as f:
        json.dump(output_dict, f, indent=2, ensure_ascii=False)


def main():
    captcha, cookie = solve_captcha()
    payload, exists, photo_b64 = get_wanted(captcha, cookie)
    create_output_file(payload, exists, photo_b64)


if __name__ == "__main__":
    main()
