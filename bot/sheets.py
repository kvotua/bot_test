import httplib2
import googleapiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
from core.utils.dbconnect import Request
import asyncpg
import logging


# print("https://docs.google.com/spreadsheets/d/" + spreadsheetId)


class Sheet:
    def __init__(self) -> None:
        CREDENTIALS_FILE = "ponarth-orders-from-bot-fb34becd5654.json"
        self.spreadsheetId = "1iVmuc_nyK_6PyOZKoU7u3untW07onARXwEz_BHa3afI"
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
                    "type": "user",
                    "role": "writer",
                    "emailAddress": "solomennicova555@gmail.com",
                },
                fields="id",
            )
            .execute()
        )

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

    def save_order(self, order_info: list, order_data: list, date, sheet_id):
        data_write = []
        for i in order_info:
            data_write.append(i)
        for i in order_data:
            data_write.append(i)

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
        try:
            sheet_values_res = results["valueRanges"][0]["values"]
            logging.info(sheet_values_res)
        except:
            return
        len_colmn = len(sheet_values_res)
        ranges_res_all = ranges.split("!")[1].split(":")
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
        return f"{ranges_res[0]}{ranges_res_int}"

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
                return
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
