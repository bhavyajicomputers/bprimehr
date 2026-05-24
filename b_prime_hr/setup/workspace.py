import frappe

def create_workspace():
    if frappe.db.exists("Workspace", "Employee Self Service"):
        ws = frappe.get_doc("Workspace", "Employee Self Service")
    else:
        ws = frappe.new_doc("Workspace")
        ws.title = "Employee Self Service"
        ws.module = "B Prime HR"
        ws.public = 1

    ws.content = '''
[
  {
    "id": "offline_hr",
    "type": "shortcut",
    "data": {
      "shortcut_name": "B-Prime Offline HR",
      "link_to": "/offline-hr",
      "type": "URL",
      "color": "Green"
    }
  }
]
'''
    ws.save(ignore_permissions=True)
    frappe.db.commit()
