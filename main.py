import random
import re
import string

import js # type: ignore
from pyodide.ffi import create_proxy # type: ignore
from pyscript import document # type: ignore

EQUIPMENT = [
    {
        "id": "laptops", 
        "name": "Laptops", 
        "category": "Devices", 
        "price": "₱75–₱100", 
        "unit": "per full day", 
        "hourly": None, 
        "full": (75, 100),
        "img": "images/laptops.jpg"
    },
    {
        "id": "tablets", 
        "name": "Tablets", 
        "category": "Devices", 
        "price": "₱75–₱100", 
        "unit": "per full day", 
        "hourly": None, 
        "full": (75, 100),
        "img": "images/tablets.jpg"
    },
    {
        "id": "scientific-calculators", 
        "name": "Scientific Calculators", 
        "category": "Devices", 
        "price": "from ₱15", 
        "unit": "per hour", 
        "hourly": 15, 
        "full": None,
        "img": "images/scientific-calculators.jpg"
    },
    {
        "id": "power-banks", 
        "name": "Power Banks", 
        "category": "Power", 
        "price": "from ₱15", 
        "unit": "per hour", 
        "hourly": 15, 
        "full": None,
        "img": "images/power-banks.jpg"
    },
    {
        "id": "universal-laptop-chargers", 
        "name": "Universal Laptop Chargers", 
        "category": "Power", 
        "price": "from ₱20", 
        "unit": "per hour", 
        "hourly": 20, 
        "full": None,
        "img": "images/universal-laptop-chargers.jpg"
    },
    {
        "id": "power-strip-extension-cords", 
        "name": "Power Strip Extension Cords", 
        "category": "Power", 
        "price": "from ₱15", 
        "unit": "per hour", 
        "hourly": 15, 
        "full": None,
        "img": "images/power-strip-extension-cords.jpg"
    },
    {
        "id": "portable-projectors", 
        "name": "Portable Projectors", 
        "category": "Presentation & Audio", 
        "price": "₱150", 
        "unit": "per full day", 
        "hourly": None, 
        "full": (150, 150),
        "img": "images/portable-projectors.jpg"
    },
    {
        "id": "wireless-presenter-clickers", 
        "name": "Wireless Presenter Clickers", 
        "category": "Presentation & Audio", 
        "price": "from ₱15", 
        "unit": "per hour", 
        "hourly": 15, 
        "full": None,
        "img": "images/wireless-presenter-clickers.jpg"
    },
    {
        "id": "noise-canceling-headphones", 
        "name": "Noise-Canceling Headphones", 
        "category": "Presentation & Audio", 
        "price": "from ₱25", 
        "unit": "per hour", 
        "hourly": 25, 
        "full": None,
        "img": "images/noise-canceling-headphones.jpg"
    },
    {
        "id": "usb-flash-drives-ssds", 
        "name": "USB Flash Drives / External SSDs", 
        "category": "Storage & Hubs", 
        "price": "from ₱20", 
        "unit": "per hour", 
        "hourly": 20, 
        "full": None,
        "img": "images/usb-flash-drives-ssds.jpg"
    },
    {
        "id": "usb-c-multiport-hubs", 
        "name": "USB-C Multiport Hubs", 
        "category": "Storage & Hubs", 
        "price": "from ₱25", 
        "unit": "per hour", 
        "hourly": 25, 
        "full": None,
        "img": "images/usb-c-multiport-hubs.jpg"
    },
    {
        "id": "type-c-fast-charging-cables", 
        "name": "Type-C Fast Charging Cables", 
        "category": "Cables", 
        "price": "from ₱15", 
        "unit": "per hour", 
        "hourly": 15, 
        "full": None,
        "img": "images/type-c-fast-charging-cables.jpg"
    },
    {
        "id": "lightning-ios-cables", 
        "name": "Lightning / iOS Cables", 
        "category": "Cables", 
        "price": "from ₱15", 
        "unit": "per hour", 
        "hourly": 15, 
        "full": None,
        "img": "images/lightning-ios-cables.jpg"
    },
    {
        "id": "micro-usb-cables", 
        "name": "Micro-USB Cables", 
        "category": "Cables", 
        "price": "from ₱15", 
        "unit": "per hour", 
        "hourly": 15, 
        "full": None,
        "img": "images/micro-usb-cables.jpg"
    },
    {
        "id": "hdmi-cables", 
        "name": "HDMI Cables", 
        "category": "Cables", 
        "price": "from ₱15", 
        "unit": "per hour", 
        "hourly": 15, 
        "full": None,
        "img": "images/hdmi-cables.jpg"
    },
]

CATEGORIES = ["All", "Devices", "Power", "Presentation & Audio", "Storage & Hubs", "Cables"]
STUDENT_ID_PATTERN = re.compile(r"^[A-Za-z0-9-]{4,20}$")

state = {"category": "All", "selected": set(), "review": None}


def peso(amount):
    return f"₱{amount:,}"


def money_range(low, high):
    return peso(low) if low == high else f"{peso(low)}–{peso(high)}"


def esc(text):
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def estimate(items, period, hours):
    low_total = 0
    high_total = 0
    unavailable = []
    for item in items:
        if period == "hourly":
            if item["hourly"] is None:
                unavailable.append(item["name"])
                continue
            low = high = item["hourly"] * hours
        else:
            if item["full"] is None:
                unavailable.append(item["name"])
                continue
            low, high = item["full"]
        low_total += low
        high_total += high
    return low_total, high_total, unavailable


def valid_hours(raw):
    try:
        return 1 <= int(raw) <= 12
    except (TypeError, ValueError):
        return False


def clamp_hours(raw):
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return 1
    return min(12, max(1, value))


def checked(name):
    return document.querySelector(f'input[name="{name}"]:checked').value


def set_checked(name, value):
    document.querySelector(f'input[name="{name}"][value="{value}"]').checked = True


def selected_items():
    return [item for item in EQUIPMENT if item["id"] in state["selected"]]


def render_categories():
    buttons = []
    for name in CATEGORIES:
        pressed = "true" if name == state["category"] else "false"
        buttons.append(f'<button type="button" class="chip" data-category="{esc(name)}" aria-pressed="{pressed}">{esc(name)}</button>')
    document.getElementById("categories").innerHTML = "".join(buttons)


def render_list():
    chosen = selected_items()
    panel = document.getElementById("list")
    actions = document.getElementById("list-actions")
    if not chosen:
        panel.innerHTML = '<p class="muted dark-muted">Your rental list is empty. Select items below to add them.</p>'
        actions.hidden = True
        return
    names = ", ".join(esc(item["name"]) for item in chosen)
    label = "item" if len(chosen) == 1 else "items"
    panel.innerHTML = f"<p><strong>Your rental list ({len(chosen)} {label}):</strong> {names}</p>"
    actions.hidden = False


def render_grid():
    query = document.getElementById("search").value.strip().lower()
    visible = [
        item
        for item in EQUIPMENT
        if (state["category"] == "All" or item["category"] == state["category"])
        and query in item["name"].lower()
    ]
    document.getElementById("count").textContent = f"Showing {len(visible)} of {len(EQUIPMENT)} items"
    if not visible:
        document.getElementById("grid").innerHTML = '<p class="empty">No equipment matches your search.</p>'
        return
    cards = []
    for item in visible:
        pressed = "true" if item["id"] in state["selected"] else "false"
        img_path = item["img"]
        cards.append(
            f'<li><button type="button" class="card" data-id="{item["id"]}" aria-pressed="{pressed}">'
            f'<div class="card-img-wrap"><img src="{img_path}" alt="{esc(item["name"])}" class="card-real-img" onerror="this.style.display=\'none\'" /></div>'
            f'<span class="card-name">{esc(item["name"])}</span>'
            f'<span class="card-cat">{esc(item["category"])}</span>'
            f'<span class="card-price">{esc(item["price"])}</span>'
            f'<span class="card-unit">{esc(item["unit"])}</span>'
            "</button></li>"
        )
    document.getElementById("grid").innerHTML = "".join(cards)


def render_all():
    render_categories()
    render_grid()
    render_list()


def show_modal():
    document.getElementById("rental-modal").hidden = False


def hide_modal(event=None):
    document.getElementById("rental-modal").hidden = True
    document.getElementById("modal-step-form").hidden = False
    document.getElementById("review").hidden = True
    document.getElementById("success").hidden = True


def choose_mode(mode):
    set_checked("mode", mode)
    sync_reserve_fields()
    show_modal()


def on_reserve_for_later(event=None):
    choose_mode("reserve")


def on_rent_now(event=None):
    choose_mode("rent")


def sync_reserve_fields(event=None):
    document.getElementById("date-field").hidden = checked("mode") != "reserve"
    document.getElementById("hours-field").hidden = checked("period") != "hourly"
    mode = checked("mode")
    title = "Reserve your items" if mode == "reserve" else "Rent items now"
    subtitle = "Tell us who is renting, when, and how you want to pay." if mode == "reserve" else "Tell us who is renting and how you want to pay."
    document.getElementById("modal-title").textContent = title
    document.getElementById("modal-subtitle").textContent = subtitle
    update_calculator()


def update_calculator(event=None):
    item = next(i for i in EQUIPMENT if i["id"] == document.getElementById("calc-item").value)
    period = checked("calc-period")
    document.getElementById("calc-hours-field").hidden = period != "hourly"
    hours = clamp_hours(document.getElementById("calc-hours").value)
    low, high, unavailable = estimate([item], period, hours)
    result = document.getElementById("calc-result")
    if unavailable:
        label = "hourly" if period == "hourly" else "full-day"
        result.textContent = f"{item['name']} is not available for {label} rentals."
    else:
        result.textContent = money_range(low, high)


def fill_calculator_options():
    options = "".join(f'<option value="{item["id"]}">{esc(item["name"])}</option>' for item in EQUIPMENT)
    document.getElementById("calc-item").innerHTML = options


def set_error(field, message):
    document.getElementById(f"err-{field}").textContent = message


def clear_errors():
    for field in ["name", "studentId", "date", "hours", "items"]:
        set_error(field, "")


def on_form_submit(event):
    event.preventDefault()
    clear_errors()

    name = document.getElementById("name").value.strip()
    student_id = document.getElementById("student-id").value.strip()
    mode = checked("mode")
    period = checked("period")
    date = document.getElementById("date").value
    hours = clamp_hours(document.getElementById("hours").value)
    items = selected_items()

    errors = {}
    if len(name) < 2:
        errors["name"] = "Enter your full name."
    if not STUDENT_ID_PATTERN.match(student_id):
        errors["studentId"] = "Use 4 to 20 letters, numbers, or dashes."
    if mode == "reserve" and not date:
        errors["date"] = "Choose a pickup date."
    if period == "hourly" and not valid_hours(document.getElementById("hours").value):
        errors["hours"] = "Choose between 1 and 12 hours."
    if not items:
        errors["items"] = "Select at least one item above."

    for field, message in errors.items():
        set_error(field, message)
    if errors:
        return

    low, high, unavailable = estimate(items, period, hours)
    state["review"] = {
        "name": name,
        "student_id": student_id,
        "mode": mode,
        "period": period,
        "hours": hours,
        "date": date,
        "payment": checked("payment"),
        "items": items,
        "low": low,
        "high": high,
        "unavailable": unavailable,
    }
    render_review()


def render_review():
    review = state["review"]
    body = document.getElementById("review-body")
    is_reserve = review["mode"] == "reserve"
    period_text = "Hourly" if review["period"] == "hourly" else "Full day"
    if review["period"] == "hourly":
        period_text += f" · {review['hours']} hr"
    payment_labels = {"pickup": "Pay at pickup", "gcash": "GCash", "card": "Credit or debit card"}
    
    item_names = ", ".join(esc(item['name']) for item in review["items"])
    
    warning = ""
    if review["unavailable"]:
        warning = '<p class="warn">Some items are not available for this period. Go back and change the period or remove those items.</p>'
    
    pickup = esc(review["date"]) if is_reserve else "Today, at the booth"
    
    body.innerHTML = (
        f'<div class="modal-item-summary"><span>{item_names}</span><span>{money_range(review["low"], review["high"])}</span></div>'
        f"{warning}"
        '<dl class="modal-dl-grid">'
        f"<div><dt>Renter</dt><dd>{esc(review['name'])}</dd></div>"
        f"<div><dt>Student ID</dt><dd>{esc(review['student_id'])}</dd></div>"
        f"<div><dt>{'Pickup date' if is_reserve else 'Pickup'}</dt><dd>{pickup}</dd></div>"
        f"<div><dt>Rental period</dt><dd>{period_text}</dd></div>"
        f"<div><dt>Payment</dt><dd>{payment_labels[review['payment']]}</dd></div>"
        "</dl>"
        '<div class="modal-total-box"><p>Estimated total</p><h3>' + money_range(review["low"], review["high"]) + '</h3></div>'
        '<p class="muted">The final total is confirmed at the booth based on how long you keep each item.</p>'
    )
    
    confirm = document.getElementById("confirm")
    confirm.disabled = bool(review["unavailable"])
    confirm.textContent = "Confirm reservation" if is_reserve else "Confirm rental"
    
    document.getElementById("modal-step-form").hidden = True
    document.getElementById("review").hidden = False


def on_back(event=None):
    document.getElementById("review").hidden = True
    document.getElementById("modal-step-form").hidden = False


def on_confirm(event=None):
    review = state["review"]
    if not review or review["unavailable"]:
        return
    characters = string.ascii_uppercase + string.digits
    code = "BM-" + "".join(random.choices(characters, k=4))
    is_reserve = review["mode"] == "reserve"
    when = f"on {esc(review['date'])}" if is_reserve else "now"
    
    item_names = ", ".join(esc(item['name']) for item in review["items"])
    
    document.getElementById("success-body").innerHTML = (
        f"<p>Your reference code is <strong>{code}</strong>. Pick up your items at the BorrowMate booth {when} "
        "and bring your student ID.</p>"
        f'<div class="modal-item-summary"><span>{item_names}</span></div>'
        f'<p class="muted"><strong>Estimated total:</strong> {money_range(review["low"], review["high"])}</p>'
    )
    
    state["selected"].clear()
    state["review"] = None
    document.getElementById("review").hidden = True
    document.getElementById("success").hidden = False
    render_all()


def on_grid_click(event):
    card = event.target.closest("[data-id]")
    if not js.Boolean(card):
        return
    item_id = card.getAttribute("data-id")
    if item_id in state["selected"]:
        state["selected"].discard(item_id)
    else:
        state["selected"].add(item_id)
    render_all()


def on_category_click(event):
    button = event.target.closest("[data-category]")
    if not js.Boolean(button):
        return
    state["category"] = button.getAttribute("data-category")
    render_all()


def on_clear_list(event=None):
    state["selected"].clear()
    render_all()


def bind(element_id, event_name, handler):
    document.getElementById(element_id).addEventListener(event_name, create_proxy(handler))


fill_calculator_options()
render_all()
sync_reserve_fields()

bind("search", "input", lambda event: render_grid())
bind("grid", "click", on_grid_click)
bind("categories", "click", on_category_click)
bind("clear-list", "click", on_clear_list)
bind("reserve-for-later", "click", on_reserve_for_later)
bind("rent-now", "click", on_rent_now)
bind("modal-close", "click", hide_modal)
bind("success-done", "click", hide_modal)
bind("reserve-form", "submit", on_form_submit)
bind("back", "click", on_back)
bind("confirm", "click", on_confirm)
bind("calc-item", "change", update_calculator)
bind("calc-hours", "input", update_calculator)
bind("hours", "input", sync_reserve_fields)

for radio in document.querySelectorAll('input[name="calc-period"]'):
    radio.addEventListener("change", create_proxy(update_calculator))
for radio in document.querySelectorAll('input[name="mode"]'):
    radio.addEventListener("change", create_proxy(sync_reserve_fields))
for radio in document.querySelectorAll('input[name="period"]'):
    radio.addEventListener("change", create_proxy(sync_reserve_fields))