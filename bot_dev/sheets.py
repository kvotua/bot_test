import httplib2
import googleapiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
from core.utils.dbconnect import Request
import asyncpg
from env import spreadsheetid
import logging


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

    def link(self):
        return f"https://docs.google.com/spreadsheets/d/{self.spreadsheetId}"

    def create_new_spreadsheet(self):
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

    def get_name_sheet_by_id(self, sheet_id: int):
        spreadsheet = (
            self.service.spreadsheets().get(spreadsheetId=self.spreadsheetId).execute()
        )
        sheetList = spreadsheet.get("sheets")
        for sheet in sheetList:
            id = sheet["properties"]["sheetId"]
            if id == sheet_id:
                return sheet["properties"]["title"]

    def save_order(self, order_info: list, order_data: dict, date):
        data_write = []
        for i in order_info:
            data_write.append(i)
        for key, value in order_data.items():
            data_write.append([key, value])
        logging.info(data_write)
        place = self.what_is_position_for_write_order(date)
        column_start = place[3]
        ranges = (
            f"{self.get_name_sheet_by_id(place[2])}!{place[0]}{column_start}:{place[1]}"
        )
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
                            "values": data_write,
                        }
                    ],
                },
            )
            .execute()
        )
        end_cell = self.what_is_position_for_write_order(date)

        logging.info(
            f"range {ranges} in new kind {place[2]}, {place[4]}{column_start}:{place[5]}{end_cell[3]}"
        )

        width_cell_main_line = 10 * (len(data_write[0][1])) / 2
        if width_cell_main_line < 90:
            width_cell_main_line = 100
        result2 = (
            self.service.spreadsheets()
            .batchUpdate(
                spreadsheetId=self.spreadsheetId,
                body={
                    "requests": [
                        {
                            "updateDimensionProperties": {
                                "range": {
                                    "sheetId": place[2],
                                    "dimension": "COLUMNS",
                                    "startIndex": place[5],
                                    "endIndex": (place[5] + 1),
                                },
                                "properties": {"pixelSize": width_cell_main_line},
                                "fields": "pixelSize",
                            }
                        },
                    ]
                },
            )
            .execute()
        )
        logging.info(f"размер в пикселях: {width_cell_main_line}")
        result3 = (
            self.service.spreadsheets()
            .batchUpdate(
                spreadsheetId=self.spreadsheetId,
                body={
                    "requests": [
                        {
                            "updateBorders": {
                                "range": {
                                    "sheetId": place[2],
                                    "startRowIndex": (int(column_start) - 1),
                                    "endRowIndex": (int(end_cell[3]) - 1),
                                    "startColumnIndex": place[4],
                                    "endColumnIndex": (place[5] + 1),
                                },
                                "bottom": {
                                    "style": "SOLID",
                                    "width": 1,
                                    "color": {
                                        "red": 0,
                                        "green": 0,
                                        "blue": 0,
                                        "alpha": 1,
                                    },
                                },
                                "top": {
                                    "style": "SOLID",
                                    "width": 1,
                                    "color": {
                                        "red": 0,
                                        "green": 0,
                                        "blue": 0,
                                        "alpha": 1,
                                    },
                                },
                                "left": {
                                    "style": "SOLID",
                                    "width": 1,
                                    "color": {
                                        "red": 0,
                                        "green": 0,
                                        "blue": 0,
                                        "alpha": 1,
                                    },
                                },
                                "right": {
                                    "style": "SOLID",
                                    "width": 1,
                                    "color": {
                                        "red": 0,
                                        "green": 0,
                                        "blue": 0,
                                        "alpha": 1,
                                    },
                                },
                                "innerHorizontal": {
                                    "style": "DASHED",
                                    "width": 1,
                                    "color": {
                                        "red": 0,
                                        "green": 0,
                                        "blue": 0,
                                        "alpha": 1,
                                    },
                                },
                                "innerVertical": {
                                    "style": "DASHED",
                                    "width": 1,
                                    "color": {
                                        "red": 0,
                                        "green": 0,
                                        "blue": 0,
                                        "alpha": 1,
                                    },
                                },
                            }
                        },
                        {
                            "repeatCell": {
                                "cell": {
                                    "userEnteredFormat": {
                                        "horizontalAlignment": "CENTER",
                                        "backgroundColor": {
                                            "red": 0.8,
                                            "green": 1,
                                            "blue": 0.8,
                                            "alpha": 1,
                                        },
                                        "textFormat": {"bold": True, "fontSize": 10},
                                        "wrapStrategy": "WRAP",
                                    }
                                },
                                "range": {
                                    "sheetId": place[2],
                                    "startRowIndex": (int(column_start) - 1),
                                    "endRowIndex": int(column_start),
                                    "startColumnIndex": place[4],
                                    "endColumnIndex": (place[5] + 1),
                                },
                                "fields": "userEnteredFormat",
                            }
                        },
                    ]
                },
            )
            .execute()
        )

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

    def what_is_position_for_write_order(self, date):
        id = self.create_week_by_day(date=date)
        week = self.get_week_by_day(date)
        place = 0
        for i in range(len(week)):
            if week[i] == date.strftime("%d-%m-%Y"):
                place = i
        place = place * 2
        logging.info(f"place: {place}")
        logging.info(f"sheet name: {self.get_name_sheet_by_id(id)}")
        first_column = f"{self.sheet_column[place]}"
        second_column = f"{self.sheet_column[place+1]}"
        first = 2
        second = 7
        ranges = f"{self.get_name_sheet_by_id(id)}!{first_column}{first}:{second_column}{second}"
        logging.info(f"start range {ranges}")
        cell_start = self.check_cell_empty(ranges=ranges)
        while cell_start == None:
            first += 5
            second += 5
            ranges = f"{self.get_name_sheet_by_id(id)}!{first_column}{first}:{second_column}{second}"
            logging.info(ranges)
            cell_start = self.check_cell_empty(ranges=ranges)

        column = [
            first_column,
            second_column,
            id,
            cell_start,
            place,
            (place + 1),
        ]
        logging.info(f"column info : {column}")
        return column

    def check_cell_empty(self, ranges):
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

    def create_now_week(self):
        date = datetime.now()
        week = self.get_week_by_day(date)
        spreadsheet = (
            self.service.spreadsheets().get(spreadsheetId=self.spreadsheetId).execute()
        )
        sheetList = spreadsheet.get("sheets")
        for sheet in sheetList:
            sheet_name = sheet["properties"]["title"]
            if sheet_name == week[0]:
                logging.info(f"{sheet_name} - {week[0]} - now check")
                return sheet["properties"]["sheetId"]
        id = self.write_week(week)
        return id

    def create_week_by_day(self, date):
        week = self.get_week_by_day(date)
        spreadsheet = (
            self.service.spreadsheets().get(spreadsheetId=self.spreadsheetId).execute()
        )
        sheetList = spreadsheet.get("sheets")
        for sheet in sheetList:
            sheet_name = sheet["properties"]["title"]
            if sheet_name == week[0]:
                logging.info(f"{sheet_name} - {week[0]}")
                return sheet["properties"]["sheetId"]
        id = self.write_week(week)
        return id

    def get_week_by_day(self, date: datetime):
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

    def write_week(self, week: list):
        sheet = self.create_sheet(week[0])
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

    def create_sheet(self, start_date: datetime):
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
                                        "rowCount": 50,
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

    def new_weeks(self, count_week: int):
        date = datetime.now()

    def add_order(self):
        logging.info("")
