import datetime as dt

def test_range(now_date_str, event_dates):
    now = dt.datetime.strptime(now_date_str, "%Y-%m-%d").date()
    
    w_monday = now - dt.timedelta(days=now.weekday())
    w_sunday = w_monday + dt.timedelta(days=6)
    nw_monday = w_monday + dt.timedelta(weeks=1)
    nw_sunday = nw_monday + dt.timedelta(days=6)
    
    events = {}
    for ev in event_dates:
        if isinstance(ev, str):
            d = dt.datetime.strptime(ev, "%Y-%m-%d %H:%M").date()
        else:
            d = ev
        
        in_week_w = w_monday <= d <= w_sunday
        in_week_nw = nw_monday <= d <= nw_sunday
        
        events[ev] = {
            "in_week": in_week_w, 
            "in_next": in_week_nw
        }
    
    return {
        "monday_week": w_monday, "sunday_week": w_sunday,
        "monday_next": nw_monday, "sunday_next": nw_sunday,
        "events": events
    }

# Тест 1: сегодня вторник 21 июля 2026 (weekday=2)
print("=== СЕГОДНЯ: вторник 21.07.2026 (weekday=2) ===")
res = test_range("2026-07-21", [
    "2026-07-21 18:30", 
    "2026-07-23 13:00"
])
for ev, r in res["events"].items():
    print(f"{ev}: week={r['in_week']}, next={r['in_next']}")

assert res["events"]["2026-07-21 18:30"]["in_week"] == True
assert res["events"]["2026-07-23 13:00"]["in_week"] == True

# Тест 2: сегодня понедельник 20 июля 2026 (weekday=0)  
print("\n=== СЕГОДНЯ: понедельник 20.07.2026 (weekday=0) ===")
res = test_range("2026-07-20", [
    "2026-07-20 18:30", 
    "2026-07-23 13:00"
])
for ev, r in res["events"].items():
    print(f"{ev}: week={r['in_week']}, next={r['in_next']}")

print("\nВсе тесты прошли!")
