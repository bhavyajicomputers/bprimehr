import frappe


def create_workspace():
    if frappe.db.exists("Workspace", "Employee Self Service"):
        ws = frappe.get_doc("Workspace", "Employee Self Service")
    else:
        ws = frappe.new_doc("Workspace")
        ws.title = "Employee Self Service"
        ws.module = "HR"
        ws.public = 1

    ws.content = '''
[
  {
    "id": "offline_hr",
    "type": "shortcut",
    "data": {
      "shortcut_name": "Offline HR Checkin & Activity",
      "link_to": "/offline-hr",
      "type": "URL",
      "color": "Green"
    }
  },
  {
    "id": "leave_application",
    "type": "shortcut",
    "data": {
      "shortcut_name": "Leave Application",
      "link_to": "Leave Application",
      "type": "DocType",
      "color": "Blue"
    }
  },
  {
    "id": "expense_claim",
    "type": "shortcut",
    "data": {
      "shortcut_name": "Expense Claim",
      "link_to": "Expense Claim",
      "type": "DocType",
      "color": "Orange"
    }
  },
  {
    "id": "attendance_request",
    "type": "shortcut",
    "data": {
      "shortcut_name": "Attendance Request",
      "link_to": "Attendance Request",
      "type": "DocType",
      "color": "Purple"
    }
  }
]
'''
    ws.save(ignore_permissions=True)
    frappe.db.commit()
