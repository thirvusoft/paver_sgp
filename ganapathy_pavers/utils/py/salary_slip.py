from frappe.utils import getdate
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

@frappe.whitelist(allow_guest=True)
def site_work_details(employee,start_date,end_date):
    job_worker = frappe.db.get_all('TS Job Worker Details',fields=['name1','parent','amount','start_date','end_date'])
    site_work=[]
    start_date=getdate(start_date)
    end_date=getdate(end_date)
    for data in job_worker:
            if data.name1 == employee and data.start_date >= start_date and data.start_date <= end_date and data.end_date >= start_date and data.end_date <= end_date:
                site_work.append([data.parent,data.amount])
    return site_work

def employee_update(doc,action):
    employee_doc = frappe.get_doc('Employee',doc.employee)
    employee_doc.salary_balance=doc.total_unpaid_amount
    employee_doc.save()

def round_off(doc,action):
        net_pay=(round(doc.net_pay))%10
        if(net_pay<=2):
            frappe.db.set_value('Salary Slip',doc.name,'rounded_total',round(doc.net_pay)-net_pay)
            frappe.db.set_value('Salary Slip',doc.name,'net_pay',round(doc.net_pay)-net_pay)
        
        elif(net_pay>2):
            value = 10- net_pay
            print(round(doc.net_pay)+value)
            frappe.db.set_value('Salary Slip',doc.name,'rounded_total',round(doc.net_pay)+value)
            frappe.db.set_value('Salary Slip',doc.name,'net_pay',round(doc.net_pay)+value)

