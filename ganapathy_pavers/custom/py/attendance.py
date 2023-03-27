import frappe
from ganapathy_pavers.custom.py.employee_checkin import check_in_out
from ganapathy_pavers.custom.py.employee_atten_tool import update_attendance_to_checkin

def attendance_submit(self, event = None):
    update_attendance_to_checkin(self, event)
    self.reload()
    check_in_out(self, event)
    