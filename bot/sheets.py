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
