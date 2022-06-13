from time import time
from frappe.utils import (getdate,flt)
from erpnext.payroll.doctype.salary_slip.salary_slip import SalarySlip
import frappe
class CustomSalary(SalarySlip):
    def set_time_sheet(self):
        if self.salary_slip_based_on_timesheet:
            self.set("timesheets", [])
            timesheets = frappe.db.sql(
                """ select * from `tabTimesheet` where employee = %(employee)s and start_date BETWEEN %(start_date)s AND %(end_date)s and (status = 'Submitted' or
                status = 'Billed')""",
                {"employee": self.employee, "start_date": self.start_date, "end_date": self.end_date},
                as_dict=1,
            )
            for data in timesheets:
                self.append("timesheets", {"time_sheet": data.name, "working_hours": data.total_hours,"overtime_hours":data.overtime_hours})   
            total_days=0
            ot_hours=0.0
            for data in self.timesheets:
                value = frappe.db.get_single_value('HR Settings', 'standard_working_hours')
                if (data.working_hours)>=float(value):
                        total_days+=1
                ot_hours+=data.overtime_hours
            self.total_overtime_hours=ot_hours
            self.days_worked=total_days

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

# def round_off(doc,action):
#         net_pay=(round(doc.net_pay))%10
#         # if(net_pay<=2):
#         #     frappe.db.set_value('Salary Slip',doc.name,'rounded_total',round(doc.net_pay)-net_pay)
#         #     frappe.db.set_value('Salary Slip',doc.name,'net_pay',round(doc.net_pay)-net_pay)
        
#         # elif(net_pay>2):
#         #     value = 10- net_pay
#         #     frappe.db.set_value('Salary Slip',doc.name,'rounded_total',round(doc.net_pay)+value)
#         #     frappe.db.set_value('Salary Slip',doc.name,'net_pay',round(doc.net_pay)+value)

def set_net_pay(self,event):
    earnings=self.earnings
    if self.designation=='Job Worker':
        for row in range(len(earnings)):
            if(earnings[row].salary_component=='Basic'):
                earnings[row].amount=self.total_paid_amount
        self.update({
            'earnings':earnings,
            'gross_pay':self.total_paid_amount,
        })

    # Calculation of net Pay by round off
    if self.gross_pay:
        net_pay=(round(self.gross_pay))%10
        if(net_pay<=2):
            self.rounded_total=round(self.gross_pay)-net_pay
            self.net_pay=round(self.gross_pay)-net_pay
        
        elif(net_pay>2):
            value = 10- net_pay
            self.rounded_total=round(self.gross_pay)+value
            self.net_pay=round(self.gross_pay)+value

        #Calculation of year to date
        SalarySlip.compute_year_to_date(self)
        
        #Calculation of Month to date
        SalarySlip.compute_month_to_date(self)
        SalarySlip.compute_component_wise_year_to_date(self)
        SalarySlip.set_net_total_in_words(self)