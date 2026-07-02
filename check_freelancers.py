from google_sheets import get_active_freelancers

freelancers = get_active_freelancers()
if freelancers:
    print("Keys found:", list(freelancers[0].keys()))
    print(freelancers[0])
else:
    print("No active freelancers found.")