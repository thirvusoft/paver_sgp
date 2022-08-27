import frappe
from frappe.utils import add_to_date, get_datetime, get_time_str, time_diff_in_hours


def working_hr(self, event):
    if(self.log_type!="OUT"):
        return
    employee=self.employee
    if(frappe.get_all("Employee Checkin", {'employee':employee, 'log_type':'IN'})):
        doc=frappe.get_last_doc("Employee Checkin", {'employee':employee, 'log_type':'IN'})
        diff_hrs= time_diff_in_hours(self.time, doc.time)
        return emp_hrs(diff_hrs, employee)

def emp_hrs(diff_hrs, employee):
    if (diff_hrs>24):
        frappe.throw('Working Hours Greater Then Today Working Hours, Please Check Checkin, Checkout Time')
    if (diff_hrs<=24):
        doc=frappe.get_last_doc('Attendance', {'employee':employee})
        frappe.db.set_value(doc.doctype, doc.name, "working_hours",  diff_hrs)
        if diff_hrs==8.0:
            frappe.set_value(doc.doctype, doc.name, "one_day_hours",  '8.0')
            frappe.set_value(doc.doctype, doc.name, "full_day_working",  '1')
        if diff_hrs<8.0:
            frappe.set_value(doc.doctype, doc.name, "one_day_hours",  diff_hrs)
        if diff_hrs>8.0:
            day_ot=diff_hrs - 8.0
            frappe.set_value(doc.doctype, doc.name, "ot_hours",  day_ot)
            frappe.set_value(doc.doctype, doc.name, "one_day_hours",  '8.0')
            frappe.set_value(doc.doctype, doc.name, "full_day_working",  '1')
