from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
import frappe
import json
from frappe.utils.csvutils import getlink


@frappe.whitelist()
def attenance(table_list, atten_date, checkout, company):
    table_list=json.loads(table_list)
    doc1=frappe.get_single('Global Defaults')
    if(not doc1.default_company and not company):
        frappe.throw('Please Enter Default Company in '+getlink('global-defaults','Global Defaults'))
    frappe.errprint(table_list)
    for i in table_list:
        doc = frappe.new_doc("Attendance")
        doc.update({
            'employee':i.get("employee"),
            'status':"Present",
            'attendance_date': i.get('check_in') or atten_date,
            'company': company if(company) else doc1.default_company
        })
        doc.insert(ignore_permissions=True)
        doc.submit()

    return checkin(table_list, atten_date, checkout)


def checkin(table_list, atten_date, checkout):
    for i in table_list:
         if i.get('check_in') or atten_date:
            doc = frappe.new_doc("Employee Checkin")
            doc.update({
                'employee':i.get("employee"),
                'log_type':"IN",
                'time': i.get('check_in') or atten_date,
            })
            doc.insert(ignore_permissions=True)
            doc.submit()
         if i.get('check_out') or checkout:
            doc1 = frappe.new_doc("Employee Checkin")
            doc1.update({
                'employee':i.get("employee"),
                'log_type':"OUT",
                'time': i.get('check_out') or checkout,
            })
            doc1.insert(ignore_permissions=True)
            doc1.submit()