import frappe
from frappe.utils import add_to_date, get_datetime, get_time_str, time_diff_in_hours


def working_hr(self, event):
    if(self.log_type!="OUT"):
        return
    employee=self.employee
    doc=frappe.get_last_doc("Employee Checkin", {'employee':employee, 'log_type':'IN', 'docstatus':1})
    diff_hrs= time_diff_in_hours(self.time, doc.time)
    return emp_hrs(diff_hrs, employee)

def emp_hrs(diff_hrs, employee):
   doc=frappe.get_last_doc('Attendance', {'employee':employee})
   frappe.set_value(doc.doctype, doc.name, "employee_working_hours",  diff_hrs)