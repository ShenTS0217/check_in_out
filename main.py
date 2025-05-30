import os
import requests
from datetime import datetime

LOGIN_URL = "https://www.tofel.com.tw/api/_account/loginjwt"
ATTENDANCE_URL = "https://www.tofel.com.tw/api/HCM/HCM01M1CheckIns/SearchHCM01M1CheckInsMonthlyAttendance"
CHANNEL_ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")
USER_ID = os.environ.get("USER_ID")
LOGIN_PAYLOAD = {
    "Account": os.environ.get("Account"),
    "Password": os.environ.get("Password"), 
    "Tenant": ""
}
LOGIN_HEARDES = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}

response = requests.post(LOGIN_URL, json=LOGIN_PAYLOAD, headers=LOGIN_HEARDES)
data = response.json()
token = data.get("access_token")

today_str = datetime.now().strftime("%Y-%m-%d")
date_obj = datetime.strptime(today_str, "%Y-%m-%d")

ATTENDANCE_HEARDES = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}

ATTENDANCE_PAYLOAD = {
        "Year": date_obj.year,
        "Month": date_obj.month,
        "Page": 1,
        "Limit": 31,
        "SortInfo": None,
        "ITCode": "",
        "DeviceIdId": None,
        "Source": "",
        "CheckType": "",
        "CreateBy": "",
        "UpdateBy": ""
    }

response = requests.post(ATTENDANCE_URL, json=ATTENDANCE_PAYLOAD, headers=ATTENDANCE_HEARDES)

if response.status_code == 200:
    data = response.json()
    all_records = data.get("Data", [])
    today_record = next((rec for rec in all_records if rec.get("HCM01M1CheckIns_CheckInTime") == today_str), None)

    time = today_record["HCM01M1CheckIns_CheckInTime"] or "日期：沒有資料"
    checkin = today_record.get("HCM01M1CheckIns_CheckIn") or "上班：沒有資料"
    checkout = today_record.get("HCM01M1CheckIns_CheckOut") or "下班：沒有資料"
    text = "日期：" + time + "\n" + checkin + "\n" + checkout
else:
    text = "資料抓取失敗！"

message = {
    "to": USER_ID,
    "messages": [
        {
            "type": "text",
            "text": text
        }
    ]
}


LINE_HEADERS = {
    "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
    "Content-Type": "application/json"
}
response = requests.post("https://api.line.me/v2/bot/message/push", headers=LINE_HEADERS, json=message)
