import os
import requests
from datetime import datetime

LOGIN_URL = "https://www.tofel.com.tw/api/_account/loginjwt"
ATTENDANCE_URL = "https://www.tofel.com.tw/api/HCM/HCM01M1CheckIns/SearchHCM01M1CheckInsMonthlyAttendance"
CHANNEL_ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")
USER_ID = os.environ.get("USER_ID")
LOGIN_PAYLOAD = {
    "Account": os.environ.get("ACCOUNT"),
    "Password": os.environ.get("PASSWORD"), 
    "Tenant": ""
}
LOGIN_HEARDES = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}

def send_line_notify(text):
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
    
    try:
        response = requests.post("https://api.line.me/v2/bot/message/push", headers=LINE_HEADERS, json=message)
        response.raise_for_status()
        print("LINE 推送成功！")
    except Exception as e:
        print("LINE 推送失敗：", e)



try:
    # login ...
    response = requests.post(LOGIN_URL, json=LOGIN_PAYLOAD, headers=LOGIN_HEARDES)
    response.raise_for_status()
    data = response.json()
    token = data.get("access_token")
except Exception as e:
    print("Login Error: ", e)
    token = None
    

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


if token:
    try:
        # 查詢...
        response = requests.post(ATTENDANCE_URL, json=ATTENDANCE_PAYLOAD, headers=ATTENDANCE_HEARDES)
        response.raise_for_status()
        data = response.json()
        all_records = data.get("Data", [])
        today_record = next((rec for rec in all_records if rec.get("HCM01M1CheckIns_CheckInTime") == today_str), None)

        time = today_record.get("HCM01M1CheckIns_CheckInTime") or "日期：沒有資料"
        checkin = today_record.get("HCM01M1CheckIns_CheckIn") or "上班：沒有資料"
        checkout = today_record.get("HCM01M1CheckIns_CheckOut") or "下班：沒有資料"
        text = "日期：" + time + "\n" + checkin + "\n" + checkout

        print("查詢成功！")
        send_line_notify(text)
    except Exception as e:
        print("查詢失敗: ", e)
        send_line_notify("查詢失敗!")
else:
    print("Token not found!")
    send_line_notify("查詢失敗！")
