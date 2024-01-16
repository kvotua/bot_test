import httplib2
import googleapiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials

CREDENTIALS_FILE = "ponarth-orders-from-bot-fb34becd5654.json"
spreadsheetId = "1iVmuc_nyK_6PyOZKoU7u3untW07onARXwEz_BHa3afI"
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    CREDENTIALS_FILE,
    [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ],
)
httpAuth = credentials.authorize(httplib2.Http())
service = googleapiclient.discovery.build("sheets", "v4", http=httpAuth)

sheet_rows = 2
last_row = 0
sheet_id = 0
sheet_count = 1
max_sheets = 200


def read_data():
    f = open("sheet_data.txt", "r")
    read_str = f.readlines()
    temp = []
    for i in read_str:
        temp.append(i.split("=")[1].replace("\n", ""))
    spreadsheetId = temp[0]
    sheet_rows = temp[1]
    last_row = temp[2]
    sheet_id = temp[3]
    sheet_count = temp[4]


def write_data():
    f = open("sheet_data.txt", "a+")
    write_str = f"spreadsheetId={spreadsheetId}\n"
    write_str += f"sheet_rows={sheet_rows}\n"
    write_str += f"last_row={last_row}\n"
    write_str += f"sheet_id={sheet_id}\n"
    write_str += f"sheet_count={sheet_count}\n"
    f.writelines(write_str)


driveService = googleapiclient.discovery.build("drive", "v3", http=httpAuth)
access = (
    driveService.permissions()
    .create(
        fileId=spreadsheetId,
        body={
            "type": "user",
            "role": "writer",
            "emailAddress": "solomennicova555@gmail.com",
        },
        fields="id",
    )
    .execute()
)

# print("https://docs.google.com/spreadsheets/d/" + spreadsheetId)
