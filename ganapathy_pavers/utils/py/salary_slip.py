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
            if data.name1 == employee and (data.start_date and data.start_date >= start_date) and (data.start_date and data.start_date <= end_date) and (data.end_date and data.end_date >= start_date) and (data.end_date and data.end_date <= end_date):
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
def validate_salaryslip(self, event):
    set_net_pay(self, event)
    validate_salary_slip(self, event)
    validate_contrator_welfare(self, event)


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
        net_pay=(round(self.gross_pay) - round(self.total_deduction))%10
        if(net_pay<=2):
            self.rounded_total=round(self.gross_pay - round(self.total_deduction))-net_pay
            self.net_pay=round(self.gross_pay - round(self.total_deduction))-net_pay
        
        elif(net_pay>2):
            value = 10- net_pay
            self.rounded_total=round(self.gross_pay - round(self.total_deduction))+value
            self.net_pay=round(self.gross_pay - round(self.total_deduction))+value

        #Calculation of year to date
        SalarySlip.compute_year_to_date(self)
        
        #Calculation of Month to date
        SalarySlip.compute_month_to_date(self)
        SalarySlip.compute_component_wise_year_to_date(self)
        SalarySlip.set_net_total_in_words(self)
def validate_salary_slip(self, event):
    if self.designation=="Labour Worker":
        ssa=frappe.get_all("Salary Structure Assignment", filters={'employee':self.employee, 'docstatus':1,'designation':"Labour Worker"}, pluck="base")
        employee=frappe.get_value("Employee",self.employee,'reports_to')
        ccr=frappe.get_all("Contractor Commission Rate", filters={'name':employee},fields=['contractor','commission_rate'])
        commission=ssa[0]-ccr[0]['commission_rate']
        basic=commission*self.total_working_hour
        if len(self.earnings)==0:
            self.update({'earnings':[{'salary_component':'Basic'}]})
        earning_total=0
        for i in self.earnings:
            if i.salary_component=='Basic':
                i.amount=basic
            earning_total=earning_total+i.amount
        self.gross_pay=earning_total
        if self.gross_pay:
            net_pay=(round(self.gross_pay) - round(self.total_deduction))%10
            if(net_pay<=2):
                self.rounded_total=round(self.gross_pay - round(self.total_deduction))-net_pay
                self.net_pay=round(self.gross_pay - round(self.total_deduction))-net_pay
            
            elif(net_pay>2):
                value = 10- net_pay
                self.rounded_total=round(self.gross_pay - round(self.total_deduction))+value
                self.net_pay=round(self.gross_pay - round(self.total_deduction))+value
        #Calculation of year to date
        SalarySlip.compute_year_to_date(self)
        
        #Calculation of Month to date
        SalarySlip.compute_month_to_date(self)
        SalarySlip.compute_component_wise_year_to_date(self)
        SalarySlip.set_net_total_in_words(self)

        

def validate_contrator_welfare(self, event):
    if self.designation=="Operator":
        emp=frappe.get_all("Employee",filters={'status':"Active",'reports_to':self.employee},pluck='name')
        ccr=frappe.get_all("Contractor Commission Rate", filters={'name':self.employee},fields=['contractor','commission_rate'])
        start_date=self.start_date
        end_date=self.end_date
        cond=""
        if(len(emp)==1):
            cond += f"employee='{emp[0]}' and "
        elif(len(emp) > 1):
            cond += f"employee in {tuple(emp)} and "
        total_working_hour = frappe.db.sql(
                    f""" select sum(time_to_sec(timediff(check_out, check_in)))/(60*60) as time, parent from `tabTS Employee Details` where {cond}  check_in BETWEEN '{self.start_date}' AND '{self.end_date}' and docstatus=1""",
                    as_dict=1,
                )
        if len(total_working_hour):
            total_working_hour=total_working_hour[0]['time']
        else:
            total_working_hour=0
        total_commission_rate=total_working_hour*ccr[0]['commission_rate']

        earning_total=0
        for i in self.earnings:
            if i.salary_component=='Contractor Welfare':
                pass
            else:
                self.append('earnings',dict(salary_component='Contractor Welfare', amount=round(total_commission_rate)))
            earning_total=earning_total+i.amount
            self.gross_pay=earning_total
        if self.gross_pay:
            net_pay=(round(self.gross_pay) - round(self.total_deduction))%10
            if(net_pay<=2):
                self.rounded_total=round(self.gross_pay - round(self.total_deduction))-net_pay
                self.net_pay=round(self.gross_pay - round(self.total_deduction))-net_pay
            
            elif(net_pay>2):
                value = 10- net_pay
                self.rounded_total=round(self.gross_pay - round(self.total_deduction))+value
                self.net_pay=round(self.gross_pay - round(self.total_deduction))+value
        #Calculation of year to date
        SalarySlip.compute_year_to_date(self)
        
        #Calculation of Month to date
        SalarySlip.compute_month_to_date(self)
        SalarySlip.compute_component_wise_year_to_date(self)
        SalarySlip.set_net_total_in_words(self)



            
