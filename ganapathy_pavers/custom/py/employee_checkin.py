import frappe
from frappe.utils import date_diff
from frappe.utils.data import time_diff_in_hours
def check_in_out(self, event):
    emp_checkin_hours=frappe.get_all('Employee Checkin', 
    {'employee': self.employee, 'time': ['between',[self.attendance_date,self.attendance_date]]},
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
    for j in total_hours:
       hours+=(time_diff_in_hours(j[1],j[0]))
    frappe.db.set_value(self.doctype, self.name, 'working_hours',hours)
    return ot_hours_cal(self, float(hours))

def ot_hours_cal(self, hours):
    if hours==8.0:
        frappe.set_value(self.doctype, self.name, "one_day_hours",  '8.0')
        frappe.set_value(self.doctype, self.name,"full_day_workings",  '1')
    if (hours<8.0):
        frappe.set_value(self.doctype, self.name, "one_day_hours",  hours)
    if (hours>8.0):
        day_ot=hours - 8.0
        frappe.set_value(self.doctype, self.name, "ot_hours",  day_ot)
        frappe.set_value(self.doctype, self.name, "one_day_hours",  '8.0')
        frappe.set_value(self.doctype, self.name, "full_day_workings",  '1')