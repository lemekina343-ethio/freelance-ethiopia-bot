import gspread
import uuid
import os
import json
import time
from datetime import date
from config import GOOGLE_SHEET_NAME

creds_json = os.getenv("GOOGLE_CREDENTIALS")
creds_dict = json.loads(creds_json)
gc = gspread.service_account_from_dict(creds_dict)
sh = gc.open(GOOGLE_SHEET_NAME)

users_ws = sh.worksheet("Users")
freelancers_ws = sh.worksheet("Freelancers")
jobs_ws = sh.worksheet("Jobs")
leads_ws = sh.worksheet("Leads")

def safe_append_row(worksheet, row, retries=3):
    for attempt in range(retries):
        try:
            worksheet.append_row(row)
            return True
        except gspread.exceptions.APIError as e:
            if attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
            else:
                raise e

def safe_update_cell(worksheet, row, col, value, retries=3):
    for attempt in range(retries):
        try:
            worksheet.update_cell(row, col, value)
            return True
        except gspread.exceptions.APIError as e:
            if attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
            else:
                raise e

def add_user(user_id, username, role, created_at):
    safe_append_row(users_ws, [user_id, username, role, created_at])

def add_freelancer(user_id, name, category, skills, experience, portfolio, location, rate, contact, portfolio_file_id="", portfolio_file_type=""):
    safe_append_row(freelancers_ws, [
        user_id, name, category, skills, experience, portfolio, location, rate, contact, "active", "", portfolio_file_id, portfolio_file_type
    ])

def add_job(client_user_id, client_name, title, category, description, budget, location_pref, contact):
    job_id = str(uuid.uuid4())[:8]
    safe_append_row(jobs_ws, [
        job_id, client_user_id, client_name, title, category, description, budget, location_pref, contact, "open", str(date.today())
    ])

def get_open_jobs():
    records = jobs_ws.get_all_records()
    return [r for r in records if r.get("status") == "open"]

def add_lead(lead_type, ref_id, from_user_id, to_user_id):
    lead_id = str(uuid.uuid4())[:8]
    safe_append_row(leads_ws, [
        lead_id, lead_type, ref_id, from_user_id, to_user_id, "True", str(date.today())
    ])

def get_active_freelancers():
    records = freelancers_ws.get_all_records()
    return [r for r in records if r.get("status") == "active"]

def get_all_jobs():
    return jobs_ws.get_all_records()

def get_all_freelancers():
    return freelancers_ws.get_all_records()

def set_job_status(job_id, new_status):
    cell = jobs_ws.find(job_id)
    safe_update_cell(jobs_ws, cell.row, 10, new_status)

def set_freelancer_status(user_id, new_status):
    cell = freelancers_ws.find(str(user_id))
    safe_update_cell(freelancers_ws, cell.row, 10, new_status)

def update_freelancer_field(user_id, field_name, new_value):
    field_columns = {
        "name": 2, "category": 3, "skills": 4, "experience": 5,
        "portfolio_links": 6, "location": 7, "rate": 8, "contact": 9
    }
    col = field_columns.get(field_name)
    if not col:
        return False

    records = freelancers_ws.get_all_records()
    user_rows = [i for i, r in enumerate(records) if str(r.get("user_id")) == str(user_id)]
    if not user_rows:
        return False

    row_index = user_rows[-1] + 2
    safe_update_cell(freelancers_ws, row_index, col, new_value)
    return True