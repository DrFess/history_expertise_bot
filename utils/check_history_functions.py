from datetime import datetime
from pprint import pprint

from requests import Session

from settings import login_l2, password_l2
from utils.classes_L2 import HistoryL2


def authorization_l2(connect, login, password):
    """Авторизация в L2"""
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'DNT': '1',
        'Origin': 'http://192.168.10.161',
        'Referer': 'http://192.168.10.161/ui/login',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
        'X-KL-kav-Ajax-Request': 'Ajax_Request',
    }

    json_data = {
        'username': f'{login}',
        'password': f'{password}',
        'totp': '',
    }

    response = connect.post('http://192.168.10.161/api/users/auth', headers=headers, json=json_data, verify=False)
    return response.status_code, response.json(), response.cookies


def get_patients_in_beds(connect: Session):
    """Запрос на получение пациентов на койках"""

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Content-Type': 'application/json',
        'Origin': 'http://192.168.10.161',
        'Proxy-Connection': 'keep-alive',
        'Referer': 'http://192.168.10.161/ui/chambers',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
    }

    json_data = {
        'department_pk': 181,
    }

    response = connect.post(
        'http://192.168.10.161/api/chambers/get-chambers-and-beds',
        headers=headers,
        json=json_data,
        verify=False,
    ).json()
    return response.get('data')


def get_patients_out_beds(connect: Session):
    """Запрос на получение пациентов вне палат"""

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Content-Type': 'application/json',
        'Origin': 'http://192.168.10.161',
        'Proxy-Connection': 'keep-alive',
        'Referer': 'http://192.168.10.161/ui/chambers',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
    }

    json_data = {
        'department_pk': 181,
    }

    response = connect.post(
        'http://192.168.10.161/api/chambers/get-patients-without-bed',
        headers=headers,
        json=json_data,
        verify=False,
    ).json()
    return response.get('data')


def search_history_numbers(data: list) -> list:
    """Распарсить данные и получить список из номеров историй"""

    result = []
    for item in data:
        if item.get('beds'):
            for bed in item.get('beds'):
                if bed.get('patient'):
                    result.append(bed.get('patient')[0].get('direction_pk'))
        elif item.get('direction_pk'):
            result.append(item.get('direction_pk'))
    return result


def get_all_histories_data(connect: Session) -> list[HistoryL2]:
    """Функция для получения данных по всем историям из Палат"""
    patients_in_ward = search_history_numbers(get_patients_in_beds(connect))
    patients_out_ward = search_history_numbers(get_patients_out_beds(connect))
    patients_in_ward.extend(patients_out_ward)

    current_patients_l2 = [
        HistoryL2(
            connect=connect,
            number=int(history_number)
        ) for history_number in patients_in_ward]

    return current_patients_l2


def check_first_examination(history: HistoryL2):
    """Функция для проверки первичного осмотра"""
    date_start = history.first_examination.get('Дата поступления')
    time_start = history.first_examination.get('Время поступления')
    date_examination = history.first_examination.get('Дата осмотра')
    time_examination = history.first_examination.get('Время осмотра')
    if date_start and time_start and date_examination and time_examination:
        datetime_start = f'{date_start} {time_start}'
        datetime_start_t = datetime.strptime(datetime_start, "%Y-%m-%d %H:%M")

        datetime_examination = f'{date_examination} {time_examination}'
        datetime_examination_t = datetime.strptime(datetime_examination, "%Y-%m-%d %H:%M")

        delta = datetime_examination_t - datetime_start_t
        if delta.seconds // 3600 > 2:
            return f'{history.number} Дата и время осмотра позднее на 2 часа от поступления. {history.first_examination.get('Врач')}'
        elif delta.seconds // 3600 < 0:
            return f'{history.number} Ошибка в дате или времени первичного осмотра. {history.first_examination.get('Врач')}'
        else:
            return False

    else:
        return False


def check_medical_examination(history: HistoryL2):
    """Функция для проверки осмотра"""
    pass


def check_operation(history: HistoryL2):
    """Функция для проверки операций"""
    if history.operation:
        pass


def check_history(session: Session) -> str:
    report = ''

    authorization_l2(session, login=login_l2, password=password_l2)

    data = get_all_histories_data(session)
    for item in data:
        first_time_error = check_first_examination(item)
        if first_time_error:
            report += first_time_error
    """Написать общую функцию для проверки историй"""
    return report
