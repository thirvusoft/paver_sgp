import datetime
from erpnext.hr.utils import validate_active_employee
from frappe.utils import getdate
from erpnext.payroll.doctype.salary_slip.salary_slip import SalarySlip, get_salary_component_data
import frappe
from frappe import _
from frappe.utils.data import flt
from frappe.utils import date_diff
from frappe.custom.doctype.property_setter.property_setter import make_property_setter
from ganapathy_pavers.ganapathy_pavers.doctype.employee_advance_tool.employee_advance_tool import create_employee_advance

class CustomSalary(SalarySlip):
    def validate_days_calc(self, event=None):
        if (self.start_date and self.end_date):
            self.days=date_diff(self.end_date, self.start_date) + 1
        
        mess = 0
        if (self.designation and self.company):
            if not (frappe.get_value("Designation", self.designation, "no_mess_amount")):
                mess = frappe.get_value("Company", self.company, "mess_charge_per_month")
        self.mess=mess
        return self

    def validate(self):
        self.status = self.get_status()
        validate_active_employee(self.employee)
        self.validate_dates()
        self.check_existing()
        if not self.salary_slip_based_on_timesheet:
            self.get_date_details()
        self.validate_days_calc()
        if not (len(self.get("earnings")) or len(self.get("deductions"))):
            # get details from salary structure
            self.get_emp_and_working_day_details()
        else:
            self.get_working_days_details(lwp = self.leave_without_pay)

        self.calculate_net_pay____()
        self.compute_year_to_date()
        self.compute_month_to_date()
        self.compute_component_wise_year_to_date()
        self.add_leave_balances()

        if frappe.db.get_single_value("Payroll Settings", "max_working_hours_against_timesheet"):
            max_working_hours = frappe.db.get_single_value("Payroll Settings", "max_working_hours_against_timesheet")
            if self.salary_slip_based_on_timesheet and (self.total_working_hours > int(max_working_hours)):
                frappe.msgprint(_("Total working hours should not be greater than max working hours {0}").
                                format(max_working_hours), alert=True)

    def calculate_net_pay____(self):
        if self.salary_structure:
            self.calculate_component_amounts("earnings")
        self.gross_pay = self.get_component_totals("earnings", depends_on_payment_days=1)
        self.base_gross_pay = flt(flt(self.gross_pay) * flt(self.exchange_rate), self.precision('base_gross_pay'))

        self.set_loan_repayment()
        self.set_precision_for_component_amounts()
        self.set_net_pay()

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
    
    def add_additional_salary_components(self, component_type):
        additional_salaries = get_additional_salaries(self.employee,
            self.start_date, self.end_date, component_type)

        for additional_salary in additional_salaries:
            self.update_component_row(
                get_salary_component_data(additional_salary.component),
                additional_salary.amount,
                component_type,
                additional_salary,
                is_recurring = additional_salary.is_recurring
            )

@frappe.whitelist(allow_guest=True)
def site_work_details(employee,start_date,end_date):
    job_worker = frappe.db.get_all('TS Job Worker Details',fields=['name1','parent','amount','start_date','end_date'])
    site_work=[]
    start_date=getdate(start_date)
    end_date=getdate(end_date)
    for data in job_worker:
            if data.name1 == employee and (data.start_date and data.start_date >= start_date) and (data.start_date and data.start_date <= end_date) and (data.end_date and data.end_date >= start_date) and (data.end_date and data.end_date <= end_date):
                site_work.append([data.parent,data.amount])
    employee_sal_bal=get_employee_salary_balance(employee, start_date)
    return {"site_work": site_work, "unbilled_salary_balance": employee_sal_bal[0], "last_salary_slip_date": employee_sal_bal[1], "undeducted_advances": get_undeducted_advances(start_date, end_date, employee)}

def get_undeducted_advances(start_date, end_date, employee, comp_type="Deduction"):
    additional_salary=frappe.db.sql(f"""
        select 
           SUM(additional_sal.amount - additional_sal.salary_slip_amount) as amount 
        from `tabAdditional Salary` additional_sal
        where 
            additional_sal.employee='{employee}' and additional_sal.docstatus = 1 and 
            additional_sal.type = "{comp_type}" and additional_sal.salary_slip_amount < additional_sal.amount and
            additional_sal.payroll_date <= "{end_date}"
    """)
    if additional_salary and additional_salary[0] and additional_salary[0][0]:
        return additional_salary[0][0]
    return 0

@frappe.whitelist(allow_guest=True)
def get_employee_salary_balance(employee, from_date):
    last_ss_date=frappe.db.sql(f"""
    SELECT MAX(ss.end_date) 
    FROM `tabSalary Slip` ss
    WHERE ss.employee = '{employee}' AND ss.docstatus=1
    """)
    amount=0
    conditions=f"""
    where jwd.name1='{employee}' and jwd.end_date < '{from_date}' 
    """
    if last_ss_date[0][0]:
        conditions+=f""" and jwd.start_date > '{datetime.datetime.strftime(last_ss_date[0][0], "%Y-%m-%d")}'"""
    date=from_date
    if isinstance(date, str):
        date=datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
    if not last_ss_date[0][0] or date>last_ss_date[0][0]:
        amount=frappe.db.sql(f"""
        SELECT sum(jwd.amount)
        from `tabProject` as site
        left outer join `tabTS Job Worker Details` as jwd
            on site.name = jwd.parent
        {conditions}
        """)[0][0] or 0
    return amount, last_ss_date[0][0]

def employee_update(doc,action):
    employee_doc = frappe.get_doc('Employee',doc.employee)
    if action=="on_submit":
        employee_doc.salary_balance=doc.total_unpaid_amount
    elif action=="on_cancel":
        ss_balance=frappe.get_all("Salary Slip", {"docstatus": 1, "employee": doc.employee}, pluck="total_unpaid_amount", order_by="end_date desc", limit=1)
        employee_doc.salary_balance=ss_balance[0] if ss_balance else employee_doc.salary_balance-(doc.total_amount-doc.total_paid_amount)
    employee_doc.save()

def validate_salaryslip(self, event=None):
    set_net_pay(self, event)
    validate_salary_slip(self, event)
    validate_contrator_welfare(self, event)

def employee_advance(self, event=None):
    if self.excess_amount_to_create_advance:
        if not self.branch:
            frappe.throw(f"""Field <b>Branch</b> is required for creating <b>Employee Advance</b> in <a href="/app/salary-slip/{self.name}"><b>{self.name}</b></a>""")
        if not self.advance_payment_mode:
            frappe.throw(f"""Field <b>Mode of Payment</b> is required for creating <b>Employee Advance</b> in <a href="/app/salary-slip/{self.name}"><b>{self.name}</b></a>""")
        adv=create_employee_advance(
            self.employee
            , flt(self.excess_amount_to_create_advance, 2)
            , self.posting_date
            , "Deduct from Salary"
            , self.advance_payment_mode
            , self.branch
            , salary_slip = self.name
            , commit = False
            )
        if self.deduct_advance:
            adv.reload()
            adv.update({
                "deduction_planning": [
                    {
                        "date": frappe.utils.add_to_date(self.end_date, days=7),
                        "amount": self.excess_amount_to_create_advance
                    }
                ]
            })
            adv.total_planned_deductions = self.excess_amount_to_create_advance
            adv.save('Update')


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
        commission=(ssa[0] if ssa else 0)-(ccr[0]['commission_rate'] if ccr and len(ccr)>0 and ccr[0].get("commission_rate") else 0)
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
        total_commission_rate=0
        if ccr and len(ccr)>0 and ccr[0]['commission_rate']:
            total_commission_rate=total_working_hour*ccr[0]['commission_rate']

        earning_total=0
        for i in self.earnings:
            if i.salary_component=='Contractor Welfare':
                pass
            elif(total_commission_rate):
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



            
@frappe.whitelist()
def get_additional_salaries(employee, start_date, end_date, component_type):
    comp_type = 'Earning' if component_type == 'earnings' else 'Deduction'

    # additional_sal = frappe.qb.DocType('Additional Salary')
    # component_field = additional_sal.salary_component.as_('component')
    # overwrite_field = additional_sal.overwrite_salary_structure_amount.as_('overwrite')

    # additional_salary_list = frappe.qb.from_(
    #     additional_sal
    # ).select(
    #     additional_sal.name, component_field, additional_sal.type,
    #     (additional_sal.amount - additional_sal.salary_slip_amount).as_("amount"), additional_sal.is_recurring, overwrite_field,
    #     additional_sal.deduct_full_tax_on_selected_payroll_date
    # ).where(
    #     (additional_sal.employee == employee)
    #     & (additional_sal.docstatus == 1)
    #     & (additional_sal.type == comp_type)
    #     & (additional_sal.salary_slip_amount < additional_sal.amount)
    # ).where(
    #     # additional_sal.payroll_date[start_date: end_date] |
    #     ((additional_sal.payroll_date <= end_date))
    # ).run(as_dict=True)


    additional_salary_list=frappe.db.sql(f"""
        select 
            additional_sal.name
            , additional_sal.salary_component as component
            , additional_sal.type
            , CASE
                WHEN additional_sal.ref_doctype = "Employee Advance"  AND IFNULL(additional_sal.ref_docname, "") != ""
                    THEN (
                        SELECT 
                            SUM(dp.amount)
                        FROM `tabDeduction Planning` dp
                        WHERE dp.date <= '{end_date}'
                        AND dp.date >= '{start_date}'
                        AND dp.parenttype='Employee Advance'
                        AND dp.parent=additional_sal.ref_docname
                    )
            END as amount
            , additional_sal.is_recurring
            , additional_sal.overwrite_salary_structure_amount as overwrite
            , additional_sal.deduct_full_tax_on_selected_payroll_date
        from `tabAdditional Salary` additional_sal
        where 
            additional_sal.employee='{employee}' and additional_sal.docstatus = 1 and 
            additional_sal.type = "{comp_type}" and additional_sal.salary_slip_amount < additional_sal.amount and
            additional_sal.payroll_date <= "{end_date}"
    """, as_dict=True)
    
    
    additional_salaries = []
    components_to_overwrite = []

    for d in additional_salary_list:
        if d.overwrite:
            if d.component in components_to_overwrite:
                frappe.throw(_("Multiple Additional Salaries with overwrite property exist for Salary Component {0} between {1} and {2}.").format(
                    frappe.bold(d.component), start_date, end_date), title=_("Error"))

            components_to_overwrite.append(d.component)

        additional_salaries.append(d)
    return additional_salaries

def additional_salary_update(self, event=None):
    for row in self.deductions:
        if row.additional_salary:
            previous_deduction=frappe.db.get_value("Additional Salary", row.additional_salary, "salary_slip_amount")
            additional_salary=frappe.get_doc("Additional Salary", row.additional_salary)
            if event=="on_submit":
                if row.amount + previous_deduction > additional_salary.amount:
                    frappe.throw(f"""Salary Deduction cannot be greater than Employee Advance or Additional Salary at #row {row.idx} for employee <b>{self.employee_name}{f" - {self.employee}" if self.employee!=self.employee_name else ""}</b>""")
                add_row=True
                for ss_row in additional_salary.salary_slip_reference:
                    if ss_row.salary_slip==self.name:
                        ss_row.amount+=row.amount
                        add_row=False
                if add_row:
                    additional_salary.update({
                        "salary_slip_reference": additional_salary.salary_slip_reference + [{"salary_slip": self.name, "amount": row.amount}]
                    })
                additional_salary.salary_slip_amount= row.amount + previous_deduction
                
            if event=="on_cancel" and (additional_salary.amount - row.amount)>=0:
                for ss_row in additional_salary.salary_slip_reference:
                        if ss_row.salary_slip==self.name:
                            ss_row.amount-=row.amount
                            add_row=False
                additional_salary.salary_slip_amount = additional_salary.salary_slip_amount - row.amount
            additional_salary.save('Update')

def remove_branch_read_only():
    make_property_setter("Salary Slip", "branch", "read_only", 0, "Check")