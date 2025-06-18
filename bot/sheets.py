import httplib2
import googleapiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
from core.utils.dbconnect import Request
import asyncpg
from env import spreadsheetid
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
import functools


# print("https://docs.google.com/spreadsheets/d/" + spreadsheetId)


class Sheet:
    def __init__(self) -> None:
        CREDENTIALS_FILE = "ponarth-orders-from-bot-fb34becd5654.json"
        self.spreadsheetId = spreadsheetid
        self.sheetId = 0
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(
            CREDENTIALS_FILE,
            [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ],
        )
        self.httpAuth = self.credentials.authorize(httplib2.Http())
        self.service = googleapiclient.discovery.build(
            "sheets", "v4", http=self.httpAuth
        )
        self.driveService = googleapiclient.discovery.build(
            "drive", "v3", http=self.httpAuth
        )
        self.access = (
            self.driveService.permissions()
            .create(
                fileId=self.spreadsheetId,
                body={
                    "type": "anyone",
                    "role": "writer",
                },
                fields="id",
            )
            .execute()
        )
        self.executor = ThreadPoolExecutor(max_workers=3) 

    async def link(self):
        return f"https://docs.google.com/spreadsheets/d/{self.spreadsheetId}"

    async def create_new_spreadsheet(self):
        spreadsheet = (
            self.service.spreadsheets()
            .create(
                body={
                    "properties": {
                        "title": f"Заказы",
                        "locale": "ru_RU",
                    },
                    "sheets": [
                        {
                            "properties": {
                                "sheetType": "GRID",
                                "sheetId": 0,
                                "title": "Лист номер один",
                                "gridProperties": {"rowCount": 100, "columnCount": 15},
                            }
                        }
                    ],
                }
            )
            .execute()
        )
        spreadsheetId = spreadsheet["spreadsheetId"]
        access = (
            self.driveService.permissions()
            .create(
                fileId=spreadsheetId,
                body={
                    "type": "anyone",
                    "role": "writer",
                },
                fields="id",
            )
            .execute()
        )
        spread = [
            spreadsheetId,
            f"https://docs.google.com/spreadsheets/d/{spreadsheetId}",
        ]
        return spread

    week = {
        0: "понедельник",
        1: "вторник",
        2: "среда",
        3: "четверг",
        4: "пятница",
        5: "суббота",
        6: "воскресенье",
    }

    async def get_name_sheet_by_id(self, sheet_id: int):
        spreadsheet = (
            self.service.spreadsheets().get(spreadsheetId=self.spreadsheetId).execute()
        )
        sheetList = spreadsheet.get("sheets")
        for sheet in sheetList:
            id = sheet["properties"]["sheetId"]
            if id == sheet_id:
                return sheet["properties"]["title"]
            
    async def save_order(self, order_info: list, order_data: list, date):
        """Асинхронное сохранение заказа в Google Sheets без блокировки основного потока"""
        loop = asyncio.get_running_loop()
        
        # Создаем синхронную функцию-обертку
        def _sync_save():
            try:
                # Подготовка данных
                data_write = []
                data_write.extend(order_info)
                data_write.extend(order_data)
                logging.info(f"Данные для записи: {data_write}")

                # Синхронные версии асинхронных методов
                place = self._what_is_position_for_write_order_sync(date)
                sheet_name = self._get_name_sheet_by_id_sync(place[2])
                
                # Формирование диапазона
                column_start = place[3]
                ranges = f"{sheet_name}!{place[0]}{column_start}:{place[1]}"
                
                # Запись данных
                self.service.spreadsheets().values().batchUpdate(
                    spreadsheetId=self.spreadsheetId,
                    body={
                        "valueInputOption": "USER_ENTERED",
                        "data": [{
                            "range": ranges,
                            "majorDimension": "ROWS",
                            "values": data_write,
                        }]
                    }
                ).execute()

                # Получение конечной позиции
                end_cell = self._what_is_position_for_write_order_sync(date)
                logging.info(f"Диапазон записи: {ranges}")

                # Настройка форматирования
                self._apply_formatting(place, end_cell, data_write)
                
                return True
            except Exception as e:
                logging.error(f"Ошибка при сохранении: {str(e)}")
                raise

        # Запускаем синхронную операцию в отдельном потоке
        try:
            await loop.run_in_executor(
                self.executor,
                _sync_save
            )
            logging.info("Заказ успешно сохранен")
        except Exception as e:
            logging.error(f"Ошибка в асинхронной обертке: {str(e)}")
            raise

    # async def save_order(self, order_info: list, order_data: list, date):
    #     loop = asyncio.get_running_loop()
    #     def _sync_save():
    #     data_write = []
    #     for i in order_info:
    #         data_write.append(i)
    #     for i in order_data:
    #         data_write.append(i)
    #     logging.info(data_write)
    #     place = await self.what_is_position_for_write_order(date)
    #     column_start = place[3]
    #     ranges = f"{await self.get_name_sheet_by_id(place[2])}!{place[0]}{column_start}:{place[1]}"
    #     result = (
    #         self.service.spreadsheets()
    #         .values()
    #         .batchUpdate(
    #             spreadsheetId=self.spreadsheetId,
    #             body={
    #                 "valueInputOption": "USER_ENTERED",
    #                 "data": [
    #                     {
    #                         "range": ranges,
    #                         "majorDimension": "ROWS",
    #                         "values": data_write,
    #                     }
    #                 ],
    #             },
    #         )
    #         .execute()
    #     )
    #     end_cell = await self.what_is_position_for_write_order(date)

    #     logging.info(
    #         f"range {ranges} in new kind {place[2]}, {place[4]}{column_start}:{place[5]}{end_cell[3]}"
    #     )

    #     width_cell_main_line = 10 * (len(data_write[0][1])) / 2
    #     if width_cell_main_line < 90:
    #         width_cell_main_line = 150
    #         result2 = (
    #             self.service.spreadsheets()
    #             .batchUpdate(
    #                 spreadsheetId=self.spreadsheetId,
    #                 body={
    #                     "requests": [
    #                         {
    #                             "updateDimensionProperties": {
    #                                 "range": {
    #                                     "sheetId": place[2],
    #                                     "dimension": "COLUMNS",
    #                                     "startIndex": place[5],
    #                                     "endIndex": (place[5] + 1),
    #                                 },
    #                                 "properties": {"pixelSize": width_cell_main_line},
    #                                 "fields": "pixelSize",
    #                             }
    #                         },
    #                     ]
    #                 },
    #             )
    #             .execute()
    #         )
    #     else:
    #         result2 = (
    #             self.service.spreadsheets()
    #             .batchUpdate(
    #                 spreadsheetId=self.spreadsheetId,
    #                 body={
    #                     "requests": [
    #                         {
    #                             "updateDimensionProperties": {
    #                                 "range": {
    #                                     "sheetId": place[2],
    #                                     "dimension": "COLUMNS",
    #                                     "startIndex": place[5],
    #                                     "endIndex": (place[5] + 1),
    #                                 },
    #                                 "properties": {"pixelSize": width_cell_main_line},
    #                                 "fields": "pixelSize",
    #                             }
    #                         },
    #                     ]
    #                 },
    #             )
    #             .execute()
    #         )
    #     logging.info(f"размер в пикселях: {width_cell_main_line}")
    #     result3 = (
    #         self.service.spreadsheets()
    #         .batchUpdate(
    #             spreadsheetId=self.spreadsheetId,
    #             body={
    #                 "requests": [
    #                     {
    #                         "updateBorders": {
    #                             "range": {
    #                                 "sheetId": place[2],
    #                                 "startRowIndex": (int(column_start) - 1),
    #                                 "endRowIndex": (int(end_cell[3]) - 1),
    #                                 "startColumnIndex": place[4],
    #                                 "endColumnIndex": (place[5] + 1),
    #                             },
    #                             "bottom": {
    #                                 "style": "SOLID",
    #                                 "width": 1,
    #                                 "color": {
    #                                     "red": 0,
    #                                     "green": 0,
    #                                     "blue": 0,
    #                                     "alpha": 1,
    #                                 },
    #                             },
    #                             "top": {
    #                                 "style": "SOLID",
    #                                 "width": 1,
    #                                 "color": {
    #                                     "red": 0,
    #                                     "green": 0,
    #                                     "blue": 0,
    #                                     "alpha": 1,
    #                                 },
    #                             },
    #                             "left": {
    #                                 "style": "SOLID",
    #                                 "width": 1,
    #                                 "color": {
    #                                     "red": 0,
    #                                     "green": 0,
    #                                     "blue": 0,
    #                                     "alpha": 1,
    #                                 },
    #                             },
    #                             "right": {
    #                                 "style": "SOLID",
    #                                 "width": 1,
    #                                 "color": {
    #                                     "red": 0,
    #                                     "green": 0,
    #                                     "blue": 0,
    #                                     "alpha": 1,
    #                                 },
    #                             },
    #                             "innerHorizontal": {
    #                                 "style": "DASHED",
    #                                 "width": 1,
    #                                 "color": {
    #                                     "red": 0,
    #                                     "green": 0,
    #                                     "blue": 0,
    #                                     "alpha": 1,
    #                                 },
    #                             },
    #                             "innerVertical": {
    #                                 "style": "DASHED",
    #                                 "width": 1,
    #                                 "color": {
    #                                     "red": 0,
    #                                     "green": 0,
    #                                     "blue": 0,
    #                                     "alpha": 1,
    #                                 },
    #                             },
    #                         }
    #                     },
    #                     {
    #                         "repeatCell": {
    #                             "cell": {
    #                                 "userEnteredFormat": {
    #                                     "horizontalAlignment": "CENTER",
    #                                     "backgroundColor": {
    #                                         "red": 0.8,
    #                                         "green": 1,
    #                                         "blue": 0.8,
    #                                         "alpha": 1,
    #                                     },
    #                                     "textFormat": {"bold": True, "fontSize": 10},
    #                                     "wrapStrategy": "WRAP",
    #                                 }
    #                             },
    #                             "range": {
    #                                 "sheetId": place[2],
    #                                 "startRowIndex": (int(column_start) - 1),
    #                                 "endRowIndex": int(column_start),
    #                                 "startColumnIndex": place[4],
    #                                 "endColumnIndex": (place[5] + 1),
    #                             },
    #                             "fields": "userEnteredFormat",
    #                         }
    #                     },
    #                 ]
    #             },
    #         )
    #         .execute()
    #     )

    sheet_column = {
        0: "A",
        1: "B",
        2: "C",
        3: "D",
        4: "E",
        5: "F",
        6: "G",
        7: "H",
        8: "I",
        9: "J",
        10: "K",
        11: "L",
        12: "M",
        13: "N",
    }

    def _get_name_sheet_by_id_sync(self, sheet_id: int):
        """Синхронная версия получения имени листа"""
        spreadsheet = self.service.spreadsheets().get(
            spreadsheetId=self.spreadsheetId
        ).execute()
        for sheet in spreadsheet.get("sheets", []):
            if sheet["properties"]["sheetId"] == sheet_id:
                return sheet["properties"]["title"]
        return None

    def _apply_formatting(self, place, end_cell, data_write):
        """Синхронное применение форматирования"""
        width_cell_main_line = max(150, 10 * len(data_write[0][1]) / 2)
        
        requests = [
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": place[2],
                        "dimension": "COLUMNS",
                        "startIndex": place[5],
                        "endIndex": place[5] + 1,
                    },
                    "properties": {"pixelSize": width_cell_main_line},
                    "fields": "pixelSize",
                }
            },
            {
                "updateBorders": {
                    "range": {
                        "sheetId": place[2],
                        "startRowIndex": int(place[3]) - 1,
                        "endRowIndex": int(end_cell[3]) - 1,
                        "startColumnIndex": place[4],
                        "endColumnIndex": place[5] + 1,
                    },
                    "bottom": {"style": "SOLID", "width": 1, "color": {"red": 0, "green": 0, "blue": 0, "alpha": 1}},
                    "top": {"style": "SOLID", "width": 1, "color": {"red": 0, "green": 0, "blue": 0, "alpha": 1}},
                    "left": {"style": "SOLID", "width": 1, "color": {"red": 0, "green": 0, "blue": 0, "alpha": 1}},
                    "right": {"style": "SOLID", "width": 1, "color": {"red": 0, "green": 0, "blue": 0, "alpha": 1}},
                    "innerHorizontal": {"style": "DASHED", "width": 1, "color": {"red": 0, "green": 0, "blue": 0, "alpha": 1}},
                    "innerVertical": {"style": "DASHED", "width": 1, "color": {"red": 0, "green": 0, "blue": 0, "alpha": 1}},
                }
            },
            {
                "repeatCell": {
                    "cell": {
                        "userEnteredFormat": {
                            "horizontalAlignment": "CENTER",
                            "backgroundColor": {"red": 0.8, "green": 1, "blue": 0.8, "alpha": 1},
                            "textFormat": {"bold": True, "fontSize": 10},
                            "wrapStrategy": "WRAP",
                        }
                    },
                    "range": {
                        "sheetId": place[2],
                        "startRowIndex": int(place[3]) - 1,
                        "endRowIndex": int(place[3]),
                        "startColumnIndex": place[4],
                        "endColumnIndex": place[5] + 1,
                    },
                    "fields": "userEnteredFormat",
                }
            }
        ]
        
        self.service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadsheetId,
            body={"requests": requests}
        ).execute()

    def _what_is_position_for_write_order_sync(self, date):
        """Синхронная версия поиска позиции для записи заказа"""
        # Создаем неделю и получаем ID листа
        id = self._create_week_by_day_sync(date=date)
        
        # Получаем дни недели
        week = self._get_week_by_day_sync(date)
        
        # Находим позицию текущего дня в неделе
        place = 0
        for i in range(len(week)):
            if week[i] == date.strftime("%d-%m-%Y"):
                place = i
        place = place * 2
        
        logging.info(f"Найдена позиция: {place}")
        logging.info(f"Имя листа: {self._get_name_sheet_by_id_sync(id)}")
        
        # Определяем колонки
        first_column = f"{self.sheet_column[place]}"
        second_column = f"{self.sheet_column[place+1]}"
        first_row = 2
        second_row = 7
        
        # Формируем диапазон для проверки
        ranges = f"{self._get_name_sheet_by_id_sync(id)}!{first_column}{first_row}:{second_column}{second_row}"
        logging.info(f"Начальный диапазон: {ranges}")
        
        # Проверяем пустые ячейки
        cell_start = self._check_cell_empty_sync(ranges=ranges)
        while cell_start is None:
            first_row += 5
            second_row += 5
            ranges = f"{self._get_name_sheet_by_id_sync(id)}!{first_column}{first_row}:{second_column}{second_row}"
            logging.info(f"Новый диапазон: {ranges}")
            cell_start = self._check_cell_empty_sync(ranges=ranges)

        # Формируем результат
        column_info = [
            first_column,
            second_column,
            id,
            cell_start,
            place,
            (place + 1),
        ]
        logging.info(f"Информация о колонке: {column_info}")
        
        return column_info

    def _create_week_by_day_sync(self, date):
        """Синхронная версия создания недели"""
        week = self._get_week_by_day_sync(date)
        spreadsheet = self.service.spreadsheets().get(
            spreadsheetId=self.spreadsheetId
        ).execute()
        
        for sheet in spreadsheet.get("sheets", []):
            if sheet["properties"]["title"] == week[0]:
                return sheet["properties"]["sheetId"]
        
        return self._write_week_sync(week)

    def _get_week_by_day_sync(self, date):
        """Синхронная версия получения дней недели"""
        day_week = date.weekday()
        now_week = []
        relative_delta = relativedelta(days=day_week)
        relative_delta_one_day = relativedelta(days=1)
        
        start_week_day = date.date() - relative_delta
        now_week.append(start_week_day.strftime("%d-%m-%Y"))
        
        for i in range(6):
            date_date = datetime.strptime(now_week[i], "%d-%m-%Y").date()
            day = (date_date + relative_delta_one_day).strftime("%d-%m-%Y")
            now_week.append(day)
        
        return now_week

    def _check_cell_empty_sync(self, ranges):
        """Синхронная проверка пустых ячеек"""
        results = self.service.spreadsheets().values().batchGet(
            spreadsheetId=self.spreadsheetId,
            ranges=ranges,
            valueRenderOption="FORMATTED_VALUE",
            dateTimeRenderOption="FORMATTED_STRING"
        ).execute()
        
        try:
            sheet_values_res = results["valueRanges"][0]["values"]
            logging.info(sheet_values_res)
        except KeyError:
            try_range = ranges.split("!")[1].split(":")[0]
            try_range_0 = ""
            for char in try_range:
                if char.isdigit():
                    try_range_0 += char
            return try_range_0
        
        ranges_parts = ranges.split("!")[1].split(":")
        start_row = ""
        for char in ranges_parts[0]:
            if char.isdigit():
                start_row += char
        
        if len(sheet_values_res) < (int(ranges_parts[1][1:]) - int(start_row) + 1):
            return str(int(start_row) + len(sheet_values_res))
        
        return None
    async def check_cell_empty(self, ranges):
        results = (
            self.service.spreadsheets()
            .values()
            .batchGet(
                spreadsheetId=self.spreadsheetId,
                ranges=ranges,
                valueRenderOption="FORMATTED_VALUE",
                dateTimeRenderOption="FORMATTED_STRING",
            )
            .execute()
        )
        sheet_values_res: list = []
        try_range = ranges.split("!")[1].split(":")[0]
        try_range_0 = ""
        # A1:B1
        ranges_res_all = ranges.split("!")[1].split(":")

        for i in range(len(try_range)):
            if i != 0:
                # 1 or 12 or 133
                try_range_0 += str(ranges_res_all[0][i])
        try:
            sheet_values_res = results["valueRanges"][0]["values"]
            logging.info(sheet_values_res)
        except:
            logging.info(try_range_0)
            return try_range_0
        len_colmn = len(sheet_values_res)
        ranges_res_0 = ""
        ranges_res_1 = ""
        for i in range(len(ranges_res_all[0])):
            if i != 0:
                ranges_res_0 += str(ranges_res_all[0][i])
        for i in range(len(ranges_res_all[1])):
            if i != 0:
                ranges_res_1 += str(ranges_res_all[1][i])
        logging.info(f"{ranges_res_all} {ranges_res_0} {ranges_res_1}")

        if (int(ranges_res_1) - int(ranges_res_0) + 1) == len_colmn:
            return

        cell1 = 0
        cell2 = 0
        for colm in range(len_colmn):
            cell1 = colm
            if len(sheet_values_res[colm]) != 0:
                if sheet_values_res[colm][0] == "":
                    logging.info(
                        f"sheet_values_res[colm][0] = {sheet_values_res[colm][0]}, sheet_values_res[colm][1] = {sheet_values_res[colm][1]}"
                    )
        ranges_res = ranges.split("!")[1].split(":")[0]
        logging.info(ranges_res)
        ranges_res_int: int = int(ranges_res_0) + cell1 + 1
        return f"{ranges_res_int}"

    async def create_now_week(self):
        date = datetime.now()
        week = await self.get_week_by_day(date)
        spreadsheet = (
            self.service.spreadsheets().get(spreadsheetId=self.spreadsheetId).execute()
        )
        sheetList = spreadsheet.get("sheets")
        for sheet in sheetList:
            sheet_name = sheet["properties"]["title"]
            if sheet_name == week[0]:
                logging.info(f"{sheet_name} - {week[0]} - now check")
                return sheet["properties"]["sheetId"]
        id = await self.write_week(week)
        return id

    async def create_week_by_day(self, date):
        week = await self.get_week_by_day(date)
        spreadsheet = (
            self.service.spreadsheets().get(spreadsheetId=self.spreadsheetId).execute()
        )
        sheetList = spreadsheet.get("sheets")
        for sheet in sheetList:
            sheet_name = sheet["properties"]["title"]
            if sheet_name == week[0]:
                logging.info(f"{sheet_name} - {week[0]}")
                return sheet["properties"]["sheetId"]
        id = await self.write_week(week)
        return id

    async def get_week_by_day(self, date: datetime):
        day_week = datetime.weekday(date)
        now_week = []
        relative_delta = relativedelta(days=day_week)
        relative_delta_one_day = relativedelta(days=1)
        start_week_day = date.date() - relative_delta
        now_week.append(start_week_day.strftime("%d-%m-%Y"))
        for i in range(6):
            date_date = datetime.strptime(now_week[i], "%d-%m-%Y").date()
            day = (date_date + relative_delta_one_day).strftime("%d-%m-%Y")
            now_week.append(day)
        return now_week

    write_dates = None
    count_place_for_date = 2

    async def write_week(self, week: list):
        sheet = await self.create_sheet(week[0])
        sheet_name = sheet["title"]
        ranges = f"{sheet_name}!A1"
        week_x2 = []
        for i in range(len(week)):
            week_x2.append(f"{self.week[i]} - {week[i]}")
            week_x2.append("")

        i = 0
        while i < 14:
            merge_cells = (
                self.service.spreadsheets()
                .batchUpdate(
                    spreadsheetId=self.spreadsheetId,
                    body={
                        "requests": [
                            {
                                "mergeCells": {
                                    "range": {
                                        "sheetId": sheet["sheetId"],
                                        "startRowIndex": 0,
                                        "endRowIndex": 1,
                                        "startColumnIndex": i,
                                        "endColumnIndex": i + self.count_place_for_date,
                                    },
                                    "mergeType": "MERGE_ALL",
                                }
                            }
                        ]
                    },
                )
                .execute()
            )
            i += self.count_place_for_date

        new_week: list = []
        new_week.append(week_x2)

        result = (
            self.service.spreadsheets()
            .values()
            .batchUpdate(
                spreadsheetId=self.spreadsheetId,
                body={
                    "valueInputOption": "USER_ENTERED",
                    "data": [
                        {
                            "range": ranges,
                            "majorDimension": "ROWS",
                            "values": new_week,
                        }
                    ],
                },
            )
            .execute()
        )
        logging.info(result)

        return sheet["sheetId"]

    async def create_sheet(self, start_date: datetime):
        title_list = f"{start_date}"
        new_sheet = (
            self.service.spreadsheets()
            .batchUpdate(
                spreadsheetId=self.spreadsheetId,
                body={
                    "requests": [
                        {
                            "addSheet": {
                                "properties": {
                                    "title": title_list,
                                    "gridProperties": {
                                        "rowCount": 250,
                                        "columnCount": 14,
                                    },
                                }
                            }
                        }
                    ]
                },
            )
            .execute()
        )

        return new_sheet["replies"][0]["addSheet"]["properties"]

    async def new_weeks(self, count_week: int):
        date = datetime.now()

    async def add_order(self):
        logging.info("")
