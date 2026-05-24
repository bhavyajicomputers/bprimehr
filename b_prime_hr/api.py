import frappe
from frappe import _
from frappe.utils import now_datetime, nowdate, get_datetime


def _has_field(doctype, fieldname):
    try:
        meta = frappe.get_meta(doctype)
        return bool(meta.has_field(fieldname))
    except Exception:
        return False


def _set_if_has(doc, fieldname, value):
    if value is None:
        value = ""
    if doc.meta.has_field(fieldname):
        doc.set(fieldname, value)


def _get_employee_for_user(user=None):
    user = user or frappe.session.user
    employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
    if not employee:
        frappe.throw(_("No Employee record is linked with user {0}. Please set Employee → User ID.").format(user))
    return employee


def _get_default_company_name():
    company = frappe.defaults.get_user_default("Company")
    if not company:
        company = frappe.db.get_value("Company", {}, "name")
    return company or "B-Prime HR"


@frappe.whitelist()
def get_bootstrap():
    employee = _get_employee_for_user()
    employee_name = frappe.db.get_value("Employee", employee, "employee_name") or employee

    return {
        "company_name": frappe.db.get_single_value("B-Prime HR Settings", "company_name")
            if frappe.db.exists("DocType", "B-Prime HR Settings") else _get_default_company_name(),
        "brand_color": "#0f766e",
        "employee": employee,
        "employee_name": employee_name,
        "server_time": now_datetime(),
    }


def _reverse_geocode(latitude, longitude):
    if not latitude or not longitude:
        return {}

    try:
        google_settings = frappe.get_doc("Google Settings", "Google Settings")
    except Exception:
        return {}

    if not getattr(google_settings, "enable", 0) or not getattr(google_settings, "api_key", None):
        return {}

    latlng = f"{latitude},{longitude}"
    api_key = google_settings.api_key
    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={latlng}&key={api_key}"

    try:
        res = frappe.make_get_request(url)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "B-Prime HR Reverse Geocode Failed")
        return {}

    if not res or res.get("status") != "OK" or not res.get("results"):
        return {}

    # Prefer a rich address over a plus_code-only result
    result = None
    for candidate in res.get("results", []):
        if candidate.get("formatted_address") and "plus_code" not in candidate.get("types", []):
            result = candidate
            break
    result = result or res["results"][0]

    data = {
        "address": result.get("formatted_address") or "",
        "formatted_address": result.get("formatted_address") or "",
        "place_id": result.get("place_id") or "",
        "city": "",
        "state": "",
        "area": "",
        "country": "",
    }

    for item in result.get("address_components", []):
        types = item.get("types", [])
        long_name = item.get("long_name") or ""

        if "locality" in types:
            data["city"] = long_name
        elif "administrative_area_level_2" in types and not data["city"]:
            data["city"] = long_name
        elif "administrative_area_level_1" in types:
            data["state"] = long_name
        elif "sublocality" in types or "sublocality_level_1" in types:
            data["area"] = long_name
        elif "neighborhood" in types and not data["area"]:
            data["area"] = long_name
        elif "country" in types:
            data["country"] = long_name

    return data


def _client_time_or_now(client_time):
    if client_time:
        try:
            return get_datetime(client_time)
        except Exception:
            pass
    return now_datetime()


def _create_checkin(employee, log_type, latitude, longitude, accuracy=None, client_time=None, source=None, activity_name=None):
    address = _reverse_geocode(latitude, longitude)

    doc = frappe.new_doc("Employee Checkin")
    doc.employee = employee
    doc.log_type = log_type
    doc.time = _client_time_or_now(client_time)

    _set_if_has(doc, "latitude", latitude)
    _set_if_has(doc, "longitude", longitude)
    _set_if_has(doc, "accuracy", accuracy)
    _set_if_has(doc, "address", address.get("address"))
    _set_if_has(doc, "formatted_address", address.get("formatted_address"))
    _set_if_has(doc, "city", address.get("city"))
    _set_if_has(doc, "state", address.get("state"))
    _set_if_has(doc, "area", address.get("area"))
    _set_if_has(doc, "country", address.get("country"))
    _set_if_has(doc, "place_id", address.get("place_id"))
    _set_if_has(doc, "custom_source", source or "Offline HR")
    if activity_name:
        _set_if_has(doc, "custom_employee_activity", activity_name)

    doc.insert(ignore_permissions=False)
    return doc.name


def _activity_duration(from_time, to_time):
    if not from_time or not to_time:
        return ""
    try:
        diff = get_datetime(to_time) - get_datetime(from_time)
        total = int(diff.total_seconds())
        if total < 0:
            return ""
        h = total // 3600
        m = (total % 3600) // 60
        s = total % 60
        return f"{h}:{m}:{s}"
    except Exception:
        return ""


def _create_activity_start(employee, payload, latitude, longitude, accuracy=None):
    address = _reverse_geocode(latitude, longitude)
    doc = frappe.new_doc("Employee Activity")
    doc.employee = employee

    start_time = _client_time_or_now(payload.get("client_time"))

    _set_if_has(doc, "activity", payload.get("activity") or "General Activity")
    _set_if_has(doc, "customer_name", payload.get("customer_name"))
    _set_if_has(doc, "remarks", payload.get("remarks"))
    _set_if_has(doc, "started", 1)
    _set_if_has(doc, "stoped", 0)
    _set_if_has(doc, "from_time", start_time)
    _set_if_has(doc, "from_date1", nowdate())
    _set_if_has(doc, "latitude", latitude)
    _set_if_has(doc, "longitude", longitude)
    _set_if_has(doc, "accuracy", accuracy)
    _set_if_has(doc, "address", address.get("address"))
    _set_if_has(doc, "formatted_address", address.get("formatted_address"))
    _set_if_has(doc, "city", address.get("city"))
    _set_if_has(doc, "state", address.get("state"))
    _set_if_has(doc, "place_id", address.get("place_id"))
    _set_if_has(doc, "custom_source", "Offline HR")

    doc.insert(ignore_permissions=False)
    return doc.name


def _stop_activity(employee, payload, latitude, longitude, accuracy=None):
    address = _reverse_geocode(latitude, longitude)
    activity_name = payload.get("activity_name")

    if activity_name and frappe.db.exists("Employee Activity", activity_name):
        doc = frappe.get_doc("Employee Activity", activity_name)
        if doc.employee != employee:
            frappe.throw(_("You cannot stop another employee's activity."))
    else:
        # Find latest running activity
        running = frappe.get_all(
            "Employee Activity",
            filters={"employee": employee, "started": 1},
            fields=["name"],
            order_by="creation desc",
            limit=1,
        )
        if not running:
            frappe.throw(_("No running Employee Activity found to stop."))
        doc = frappe.get_doc("Employee Activity", running[0].name)

    stop_time = _client_time_or_now(payload.get("client_time"))

    _set_if_has(doc, "started", 0)
    _set_if_has(doc, "stoped", 1)
    _set_if_has(doc, "to_time", stop_time)
    _set_if_has(doc, "out_latitude", latitude)
    _set_if_has(doc, "out_longitude", longitude)
    _set_if_has(doc, "out_accuracy", accuracy)
    _set_if_has(doc, "out_address", address.get("address"))
    _set_if_has(doc, "out_city", address.get("city"))
    _set_if_has(doc, "out_state", address.get("state"))
    _set_if_has(doc, "time_taken", _activity_duration(doc.get("from_time"), stop_time))

    doc.save(ignore_permissions=False)
    return doc.name


@frappe.whitelist()
def sync_event(payload):
    """Sync one offline event.

    payload fields:
    - action: CHECKIN, CHECKOUT, ACTIVITY_START, ACTIVITY_STOP
    - latitude, longitude, accuracy
    - client_time ISO string
    - activity, customer_name, remarks, activity_name
    """
    if isinstance(payload, str):
        frappe.parse_json(payload)
        payload = frappe.parse_json(payload)

    employee = _get_employee_for_user()

    action = payload.get("action")
    latitude = payload.get("latitude")
    longitude = payload.get("longitude")
    accuracy = payload.get("accuracy")

    if not latitude or not longitude:
        frappe.throw(_("Latitude and longitude are required."))

    activity_name = None
    checkin_name = None

    if action == "CHECKIN":
        checkin_name = _create_checkin(employee, "IN", latitude, longitude, accuracy, payload.get("client_time"), "Offline HR")

    elif action == "CHECKOUT":
        checkin_name = _create_checkin(employee, "OUT", latitude, longitude, accuracy, payload.get("client_time"), "Offline HR")

    elif action == "ACTIVITY_START":
        activity_name = _create_activity_start(employee, payload, latitude, longitude, accuracy)
        checkin_name = _create_checkin(employee, "IN", latitude, longitude, accuracy, payload.get("client_time"), "Offline HR", activity_name)

    elif action == "ACTIVITY_STOP":
        activity_name = _stop_activity(employee, payload, latitude, longitude, accuracy)
        checkin_name = _create_checkin(employee, "OUT", latitude, longitude, accuracy, payload.get("client_time"), "Offline HR", activity_name)

    else:
        frappe.throw(_("Invalid action: {0}").format(action))

    frappe.db.commit()

    return {
        "ok": True,
        "action": action,
        "employee": employee,
        "checkin": checkin_name,
        "activity": activity_name,
        "synced_at": now_datetime(),
    }
