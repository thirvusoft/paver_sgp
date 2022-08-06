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
    self.working_hours=hours