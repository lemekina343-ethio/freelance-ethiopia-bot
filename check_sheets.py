import gspread

gc = gspread.service_account(filename="credentials.json")
for sh in gc.openall():
    print(sh.title)