import httplib2
import googleapiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from dateutil.relativedelta import relativedelta
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

    def create_now_week(self):
        date = datetime.now()
        self.write_week(self.get_week_by_day(date))

    def create_week_by_day(self, date):
        week = self.get_week_by_day(date)
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
