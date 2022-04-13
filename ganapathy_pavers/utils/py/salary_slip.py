from dataclasses import fields
import email
from erpnext.payroll.doctype.salary_slip.salary_slip import SalarySlip
import frappe
class CustomSalary(SalarySlip):
    def set_time_sheet(self):
            if self.salary_slip_based_on_timesheet:
                self.set("timesheets", [])
                employee= frappe.get_doc("Employee", {"name":self.employee})
                email=employee.user_id
                timesheets = frappe.get_list('Timesheet',filters=
                [["start_date", ">=", self.start_date],
			    ["end_date", "<=", self.end_date],
                ['status','=','Submitted']],
                fields=["name","_assign",'total_hours']);
                for data in timesheets:
                    if email in data._assign:
                        self.append("timesheets", {"time_sheet": data.name, "working_hours": data.total_hours})