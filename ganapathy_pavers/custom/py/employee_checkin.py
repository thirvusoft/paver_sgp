import frappe
from frappe.utils.data import time_diff_in_hours
from datetime import date, timedelta, datetime

from erpnext.hr.doctype.shift_type.shift_type import process_auto_attendance_for_all_shifts
def mark_attendance():
    get_shift_type=frappe.db.get_all("Shift Type" ,pluck="name")
    last_att_sync = frappe.db.get_single_value("Thirvu HR Settings", "last_attendance_sync")
    last_checkin_sync = frappe.db.get_single_value("Thirvu HR Settings", "last_sync_of_without_log")
    for i in get_shift_type:
        frappe.db.set_value("Shift Type", i, "process_attendance_after", last_att_sync)
        frappe.db.set_value("Shift Type", i, "last_sync_of_checkin", last_checkin_sync)
    process_auto_attendance_for_all_shifts()
    
def check_in_out(self, event):
    emp_checkin_hours=frappe.get_all('Employee Checkin', 
    {'attendance': self.name},
    ["log_type","time"])
    current_log="IN"
    total_hours=[]
    temp_hour=[]
    for i in emp_checkin_hours:
        if i.log_type==current_log:
            temp_hour.append(i.time)
            if current_log=="OUT":
                total_hours.append(temp_hour)
                temp_hour=[]
                current_log="IN"
                continue
            if current_log=="IN":
                current_log="OUT"
    hours=0
    hours_to_reduce=0
    if self.ts_employee_attendance_tool:
        ts_emp=frappe.get_doc("TS Employee Attendance Tool", self.ts_employee_attendance_tool)
        for row in ts_emp.employee_detail:
            if row.employee == self.employee:
                hours_to_reduce = row.hours_to_reduce

    for j in total_hours:
       hours+=(time_diff_in_hours(j[1],j[0]))
    if self.ts_employee_attendance_tool and hours_to_reduce:
        hours-=hours_to_reduce
    frappe.db.set_value(self.doctype, self.name, 'working_hours',hours)
    return ot_hours_cal(self, float(hours))

def ot_hours_cal(self, hours):
    day_ot=hours % 8.0
    frappe.db.set_value(self.doctype, self.name, "ot_hours",  day_ot)
    frappe.db.set_value(self.doctype, self.name, "one_day_hours",  (hours//8)*8)
    frappe.db.set_value(self.doctype, self.name, "full_day_workings",  hours//8)