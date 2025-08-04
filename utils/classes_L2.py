import json
from requests import Session

from settings import path_to_hospitalsJson


class HistoryL2:
    """Класс истории болезни L2"""

    def __init__(self, connect: Session, number: int):
        self.__connect = connect
        self.number = number
        self.__headers_ui_stationar = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'DNT': '1',
            'Origin': 'http://192.168.10.161',
            'Referer': 'http://192.168.10.161/ui/stationar',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        }
        self.fio = self.__get_patient_info().split(',')[0].lower()
        self.birthday = self.__get_patient_info().split(',')[2].lstrip(' ').split(' ')[0]
        self.__path_to_hospitalsJson = path_to_hospitalsJson
        self.__examination_numbers = self.__get_research_numbers()
        self.first_examination = self.__create_first_examination()
        self.preoperative_examination = self.__create_preoperative_examination()
        self.operation = self.__create_operation()
        self.diaries = self.__create_diaries()
        self.finally_examination = self.__create_finally_examination()

    def __get_patient_info(self) -> str:
        """Получает данные пациента по номеру истории"""

        json_data = {
            'pk': self.number,
            'every': False,
        }

        response = self.__connect.post(
            'http://192.168.10.161/api/stationar/load',
            headers=self.__headers_ui_stationar,
            json=json_data,
            verify=False
        ).json()

        return response.get('data').get('patient').get('fio_age')

    def counts(self) -> dict:
        """Получает количество протоколов по раздела истории"""

        json_data = {
            'direction': self.number,
            'every': False,
        }

        response = self.__connect.post(
            'http://192.168.10.161/api/stationar/counts',
            headers=self.__headers_ui_stationar,
            json=json_data,
            verify=False,
        ).json()
        return response

    def __get_research_numbers(self) -> dict:
        """Получает номера всех записей в истории"""

        json_data = {
            'direction': self.number,
            'r_type': 'all',
            'every': False,
        }

        response = self.__connect.post(
            'http://192.168.10.161/api/stationar/directions-by-key',
            headers=self.__headers_ui_stationar,
            json=json_data,
            verify=False,
        ).json()

        research_numbers = {}
        for record in response.get('data'):
            if record.get('confirm'):
                if record.get('researches')[0] not in research_numbers:
                    research_numbers[record.get('researches')[0]] = [record.get('pk')]
                else:
                    research_numbers.get(record.get('researches')[0]).append(record.get('pk'))
        return research_numbers

    def __get_first_examination_data(self) -> list or bool:
        """
        Получает данные Первичного осмотра
        Здесь же можно и получать данные по процедурному листу или отдельным запросом???
        """
        first_examination_number = self.__examination_numbers.get('Первичный осмотр-травматология (при поступлении)')
        if first_examination_number:
            json_data = {
                'pk': first_examination_number[0],
                'force': True,
            }

            response = self.__connect.post(
                'http://192.168.10.161/api/directions/paraclinic_form',
                headers=self.__headers_ui_stationar,
                json=json_data,
                verify=False,
            ).json()
            return response.get('researches')[0].get('research').get('groups')
        else:
            return False

    def __get_preoperative_data(self):
        """Получает данные предоперационного эпикриза"""

        preoperative_numbers: list = self.__examination_numbers.get('Предоперационный эпикриз')
        if preoperative_numbers:
            answer = []
            for number in preoperative_numbers:
                json_data = {
                    'pk': number,
                    'force': True,
                }

                response = self.__connect.post(
                    'http://192.168.10.161/api/directions/paraclinic_form',
                    headers=self.__headers_ui_stationar,
                    json=json_data,
                    verify=False,
                ).json()
                answer.append(response.get('researches')[0].get('research').get('groups'))
            return answer
        else:
            return False

    def __get_operation_data(self) -> list or bool:
        """Получает данные об операциях"""

        operation_numbers: list = self.__examination_numbers.get('Протокол операции (тр)')
        if operation_numbers:
            answer = []
            for number in operation_numbers:
                json_data = {
                    'pk': number,
                    'force': True,
                }

                response = self.__connect.post(
                    'http://192.168.10.161/api/directions/paraclinic_form',
                    headers=self.__headers_ui_stationar,
                    json=json_data,
                    verify=False,
                ).json()
                answer.append(response.get('researches')[0].get('research').get('groups'))
            return answer
        else:
            return False

    def __get_diaries_data(self):
        """Получает данные из дневников"""

        diaries: list = self.__examination_numbers.get('Осмотр')
        if diaries:
            answer = []
            for number in diaries:
                json_data = {
                    'pk': number,
                    'force': True,
                }

                response = self.__connect.post(
                    'http://192.168.10.161/api/directions/paraclinic_form',
                    headers=self.__headers_ui_stationar,
                    json=json_data,
                    verify=False,
                ).json()
                answer.append(response.get('researches')[0].get('research').get('groups'))
            return answer
        else:
            return False

    def __get_finally_examination_data(self) -> list or bool:
        """Получает данные выписки"""

        finally_examination_number = self.__examination_numbers.get('Выписной эпикриз из медицинской карты стационарного больного.')
        if finally_examination_number:
            json_data = {
                'pk': finally_examination_number[0],
                'force': True,
            }

            response = self.__connect.post(
                'http://192.168.10.161/api/directions/paraclinic_form',
                headers=self.__headers_ui_stationar,
                json=json_data,
                verify=False,
            ).json()
            return response.get('researches')[0].get('research').get('groups')
        else:
            return False

    def __create_first_examination(self) -> dict or bool:
        """Возвращает обработанные данные Первичного осмотра"""

        first_examination_info = {}
        data = self.__get_first_examination_data()
        if data:
            for group in data:
                if group.get('pk') == 497:
                    for item in group.get('fields'):
                        key = item.get('title')
                        value = item.get('value')

                        if key in ('Дата поступления', 'Время поступления'):
                            first_examination_info[key] = value

                elif group.get('pk') == 498:
                    for item in group.get('fields'):
                        value = item.get('value')
                        first_examination_info['Жалобы'] = value

                elif group.get('title') == 'Анамнез заболевания':
                    for item in group.get('fields'):
                        key = item.get('title')
                        value = item.get('value')

                        if key in ('Диагноз направившего учреждения',
                                   'Виды транспортировки',
                                   'Номер направления') and value != '':
                            first_examination_info[key] = value

                        elif item.get('pk') == 18733 and value not in ('- Не выбрано', '-', 'ГСМП'):
                            first_examination_info[key] = value
                            with open(self.__path_to_hospitalsJson, 'r') as file:
                                hospitals = json.load(file)
                                hospital = hospitals.get(value)
                                first_examination_info['Org_id'] = hospital.get('Org_id')

                        elif key in ('Вид госпитализации',
                                     'Побочное действие лекарств (непереносимость)',
                                     'Обстоятельства травмы, заболевания',
                                     'Вид травмы'):
                            first_examination_info[key] = value

                        elif key == 'Дата выдачи направления' and value != '':
                            value = '.'.join(value.split('-')[::-1])
                            first_examination_info[key] = value

                elif group.get('title') == 'Данные объективного обследования.':
                    for item in group.get('fields'):
                        key = item.get('title')
                        value = item.get('value')

                        if key in ('Тяжесть состояния пациента', 'Уровень сознания по шкале Глазго', 'Положение'):
                            first_examination_info[key] = value

                elif group.get('title') == 'Локальный статус.':
                    for item in group.get('fields'):
                        if item.get('pk') == 1851:
                            first_examination_info['Локальный статус'] = item.get('value')

                elif group.get('title') == 'Дополнительные методы обследования.':
                    for item in group.get('fields'):
                        key = item.get('title')
                        value = item.get('value')

                        if key in ('Рентгенография', 'МСКТ', 'МРТ'):
                            first_examination_info[key] = value

                elif group.get('title') == 'Предварительный диагноз (диагноз при поступлении)':
                    for item in group.get('fields'):
                        key = item.get('title')
                        value = item.get('value')

                        if key in ('Основной диагноз (описание)',
                                   'Внешняя причина при травмах, отравлениях',
                                   'Осложнения основного заболевания',
                                   'Осложнения (код МКБ)',
                                   'Сопутствующие заболевания',
                                   'Сопутствующие (код МКБ)'):
                            first_examination_info[key] = value

                        elif key == 'код по МКБ':
                            value = json.loads(value)
                            first_examination_info[f'Основное ({key})'] = value.get('code')

                elif group.get('title') == 'План лечения':
                    for item in group.get('fields'):
                        key = item.get('title')
                        value = item.get('value')

                        if key in ('Физиотерапия', 'Манипуляции', 'Оперативное вмешательство'):
                            first_examination_info[key] = value

                        elif item.get('pk') == 1882:
                            first_examination_info['ЛФК и прочее'] = value

                elif group.get('title') == 'Фамилия, имя, отчество (при наличии) врача, должность, специальность':
                    for item in group.get('fields'):
                        if item.get('pk') == 19798:
                            first_examination_info['Врач'] = item.get('value')

            return first_examination_info
        else:
            return False

    def __create_preoperative_examination(self):
        """Возвращает обработанные данные предоперационного осмотра"""

        preoperative_examination_info = {}
        data = self.__get_preoperative_data()
        if data:
            for index, preoperative in enumerate(data):
                preoperative_examination_info[index] = {}
                for group in preoperative:
                    if group.get('pk') == 3581:
                        for item in group.get('fields'):
                            key = item.get('title')
                            value = item.get('value')
                            if key == 'Дата составления':
                                preoperative_examination_info[index][key] = value

                    elif group.get('title') == 'Диагноз':
                        for item in group.get('fields'):
                            key = item.get('title')
                            value = item.get('value')
                            if key in ('Основное заболевание',
                                       'Осложнение основного заболевания',
                                       'Внешняя причина при травмах, отравлениях',
                                       'Сопутствующие заболевания'):
                                preoperative_examination_info[index][key] = value

                    elif group.get('title') == 'Особенности анамнеза':
                        for item in group.get('fields'):
                            key = item.get('title')
                            value = item.get('value')
                            if item.get('pk') in (19640, 19447, 19448) and value != '':
                                preoperative_examination_info[index][key] = value

                    elif group.get('title') == 'Физикальное исследование, локальный статус':
                        for item in group.get('fields'):
                            key = item.get('title')
                            value = item.get('value')
                            if item.get('pk') in (24879, 24880, 19449) and value != '':
                                preoperative_examination_info[index][key] = value

                    elif group.get('pk') == 3587:
                        for item in group.get('fields'):
                            key = item.get('title')
                            value = item.get('value')
                            if value != '':
                                preoperative_examination_info[index][key] = value

                    elif group.get('pk') == 3589:
                        for item in group.get('fields'):
                            value = item.get('value')
                            if item.get('pk') in (19458,):
                                preoperative_examination_info[index]['Оперирующий врач'] = value
            return preoperative_examination_info
        else:
            return False

    def __create_operation(self):
        """Возвращает обработанные данные операций"""

        operation_info = {}
        data = self.__get_operation_data()
        if data:
            for index, operation in enumerate(data):
                operation_info[index] = {}
                for group in operation:
                    if group.get('pk') == 506:
                        for item in group.get('fields'):
                            key = item.get('title')
                            value = item.get('value')
                            if key in ('Дата проведения',
                                       'Время начала',
                                       'Дата окончания',
                                       'Время окончания',
                                       'Длительность операции'):
                                operation_info[index][key] = value

                    elif group.get('pk') == 507:
                        for item in group.get('fields'):
                            key = item.get('title')
                            value = item.get('value')
                            if key in ('Группа крови',
                                       'Название операции',
                                       'Код операции',
                                       'Категория сложности',
                                       'Оперативное вмешательство'):
                                operation_info[index][key] = value

                    elif group.get('title') == 'Операционная бригада.':
                        for item in group.get('fields'):
                            key = item.get('title')
                            value = item.get('value')
                            if key in ('Оперировал',
                                       'Ассистенты',
                                       'Анестезиолог',
                                       'Анестезист',
                                       'Операционная медицинская сестра'):
                                operation_info[index][key] = value

                    elif group.get('title') == 'Ход операции':
                        for item in group.get('fields'):
                            key = item.get('title')
                            value = item.get('value')
                            if item.get('pk') == 1873:
                                operation_info[index]['Ход операции'] = value
                            elif key in ('Метод обезболивания',):
                                operation_info[index][key] = value

                    elif group.get('pk') == 3640:
                        for item in group.get('fields'):
                            key = item.get('title')
                            value = item.get('value')
                            if value != '':
                                operation_info[index][key] = value

                    elif group.get('title') == 'Диагноз после оперативного вмешательства (операции):':
                        for item in group.get('fields'):
                            key = item.get('title')
                            value = item.get('value')
                            if value != '':
                                operation_info[index][key] = value
            return operation_info
        else:
            return False

    def __create_diaries(self):
        """Возвращает обработанные данные дневников"""

        diaries_info = {}
        data = self.__get_diaries_data()
        if data:
            for index, diary in enumerate(data):
                diaries_info[index] = {}
                for group in diary:
                    if group.get('pk') == 2928:
                        for item in group.get('fields'):
                            value = item.get('value')
                            diaries_info[index]['Осмотр'] = value

                    elif group.get('pk') == 511:
                        for item in group.get('fields'):
                            key = item.get('title')
                            value = item.get('value')
                            diaries_info[index][key] = value

                    elif group.get('pk') == 1191:
                        for item in group.get('fields'):
                            key = item.get('title')
                            value = item.get('value')
                            diaries_info[index][key] = value

                    elif group.get('pk') == 515:
                        for item in group.get('fields'):
                            key = item.get('title')
                            value = item.get('value')
                            if item.get('pk') in (1908,):
                                diaries_info[index]['Соматический статус'] = value
                            else:
                                diaries_info[index][key] = value

                    elif group.get('pk') == 516:
                        for item in group.get('fields'):
                            value = item.get('value')
                            if item.get('pk') in (1922,):
                                diaries_info[index]['Локальный статус'] = value

                    elif group.get('pk') == 3242:
                        for item in group.get('fields'):
                            key = item.get('title')
                            value = item.get('value')
                            diaries_info[index][key] = value

                    elif group.get('pk') == 520:
                        for item in group.get('fields'):
                            key = item.get('title')
                            value = item.get('value')
                            if item.get('pk') == 1939:
                                diaries_info[index]['Лечение 1'] = value
                            elif item.get('pk') == 16377:
                                diaries_info[index]['Выписан'] = value
                            else:
                                diaries_info[index][key] = value

            return diaries_info
        else:
            return False

    def __create_finally_examination(self):
        """Возвращает обработанные данные Выписки"""

        finally_examination_info = {}
        data = self.__get_finally_examination_data()
        if data:
            for group in data:
                if group.get('title') == 'Период нахождения в стационаре, дневном стационаре':
                    for item in group.get('fields'):
                        key = item.get('title')
                        value = item.get('value')
                        if key == 'Дата выписки' or key == 'Время выписки':
                            finally_examination_info[key] = value
                        elif key == 'Время выписки':
                            finally_examination_info[key] = value

                elif group.get('pk') == 529:
                    for item in group.get('fields'):
                        key = item.get('title')
                        value = item.get('value')
                        if key == 'Проведено койко-дней':
                            finally_examination_info[key] = value

                elif group.get('title') == 'Результат лечения':
                    for item in group.get('fields'):
                        key = item.get('title')
                        value = item.get('value')
                        if key in ('Исход госпитализации', 'Результат госпитализации'):
                            finally_examination_info[key] = value

                elif group.get('title') == 'Заключительный клинический диагноз ':
                    for item in group.get('fields'):
                        key = item.get('title')
                        value = item.get('value')
                        if key in ('Основной диагноз (описание)',
                                   'Основной диагноз по МКБ',
                                   'Осложнение основного диагноза (описание)',
                                   'Осложнение основного диагноза по МКБ',
                                   'Сопутствующий диагноз (описание)',
                                   'Сопутствующий диагноз по МКБ'):
                            finally_examination_info[key] = value

                elif group.get('title') == 'Состояние при поступлении':
                    for item in group.get('fields'):
                        key = item.get('title')
                        value = item.get('value')
                        if key in ('жалобы при поступлении', 'анамнез заболевания'):
                            finally_examination_info[key] = value
                        elif item.get('pk') == 20075:
                            finally_examination_info['осмотр(поступление)'] = value

                elif group.get('title') == 'Проведенное лечение':
                    for item in group.get('fields'):
                        key = item.get('title')
                        value = item.get('value')
                        if key == 'Консервативное':
                            finally_examination_info[key] = value

                elif group.get('title') == 'Состояние при выписке, трудоспособность, листок нетрудоспособности':
                    for item in group.get('fields'):
                        key = item.get('title')
                        value = item.get('value')
                        if item.get('pk') == 19408:
                            finally_examination_info['состояние при выписке'] = value
                        elif key in ('номер листка нетрудоспособности',
                                     'освобождение от работы с',
                                     'освобождение от работы по',
                                     'приступить к работе с',
                                     'продление листка нетрудоспособности',
                                     'Оформлен листок нетрудоспособности по уходу за больным членом семьи (фамилия, имя, отчество (при наличии)',
                                     'продление листка нетрудоспособности №',
                                     ) and value != '':
                            finally_examination_info[key] = value  # в этой функции сделать разделение по pk первичный и продолжение ЛН

                elif group.get('title') == 'Рекомендации':
                    for item in group.get('fields'):
                        key = item.get('title')
                        value = item.get('value')
                        if item.get('pk') in (1978, ) or key in ('Режим иммобилизации',
                                                                     'Уход за послеоперационной раной',
                                                                     'Физиолечение',
                                                                     'Медикаментозное лечение',
                                                                     'Ограничение физических нагрузок',
                                                                     'Реабилитация',
                                                                     'Лечащий врач',
                                                                     'Заведующий отделением'):
                            finally_examination_info[key] = value
                        elif item.get('pk') in (1988, ):
                            finally_examination_info['Рекомендации по рентгену'] = value

            return finally_examination_info
        else:
            return False

