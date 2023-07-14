import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint
from datetime import datetime
import requests
import socket

from subprocess import check_output

ips = check_output(["hostname", "--all-ip-addresses"])
print(ips)
local_ip = str(ips).split(" ")[0]


# Authorize the API
scope = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.file",
]
file_name = "client_key.json"
creds = ServiceAccountCredentials.from_json_keyfile_name(file_name, scope)
client = gspread.authorize(creds)


robot_name = "martha-pink"


# Fetch the sheet
sheet = client.open("martha robot ip").sheet1

search = sheet.find(robot_name)
ip = requests.get('https://api.ipify.org').content.decode('utf8')
print(ip)
# hostname = socket.getfqdn()
# print(hostname)
# ip = socket.gethostbyname_ex(hostname)
# print(ip)
now = datetime.now()
if search:
    row = sheet.row_values(search.row)
    #    if row[1] == ip:
    if False:
        exit(0)
    else:
        #        inp = input(f"Do you want to update the ip from {row[1]} to {ip}?")

        loc = "A" + str(search.row)
        print("updating " + loc)
        print("from " + str(row))
        newrow = [
            robot_name,
            str(ip),
            now.strftime("%d/%m/%Y"),
            now.strftime("%H:%M:%S"),
        ]
        print("to be " + str(newrow))
        sheet.update(loc, [newrow])
else:
    sheet.append_row(
        [robot_name, str(ip), now.strftime("%d/%m/%Y"), now.strftime("%H:%M:%S")]
    )
