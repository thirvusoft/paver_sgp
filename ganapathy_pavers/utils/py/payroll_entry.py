from erpnext.payroll.doctype.payroll_entry.payroll_entry import ( PayrollEntry,get_existing_salary_slips)
from erpnext.payroll.doctype.salary_slip.salary_slip import SalarySlip
import frappe
from frappe.utils import getdate
from frappe import _
class MessExpense(PayrollEntry):
    @frappe.whitelist()
    def create_salary_slips(self):
        self.check_permission("write")
        employees = [emp.employee for emp in self.employees]
        food_count= [emp.total_time_of_food_taken for emp in self.employees]
        if employees:
            args = frappe._dict(
                {
                    "salary_slip_based_on_timesheet": self.salary_slip_based_on_timesheet,
                    "payroll_frequency": self.payroll_frequency,
                    "start_date": self.start_date,
                    "end_date": self.end_date,
                    "company": self.company,
                    "posting_date": self.posting_date,
                    "deduct_tax_for_unclaimed_employee_benefits": self.deduct_tax_for_unclaimed_employee_benefits,
                    "deduct_tax_for_unsubmitted_tax_exemption_proof": self.deduct_tax_for_unsubmitted_tax_exemption_proof,
                    "payroll_entry": self.name,
                    "exchange_rate": self.exchange_rate,
                    "currency": self.currency,
                }
            )
            if len(employees) > 30:
                frappe.enqueue(create_salary_slips_for_employees, timeout=600, posting_date=self.posting_date,employees=employees,args=args,food_count=food_count)
            else:
                create_salary_slips_for_employees(self.posting_date,self.start_date,self.end_date,employees, args,food_count, publish_progress=False)
                # since this method is called via frm.call this doc needs to be updated manually
                self.reload()
    @frappe.whitelist()
    def submit_salary_slips(self):
        self.check_permission("write")
        ss_list = self.get_sal_slip_list(ss_status=0)
        if len(ss_list) > 30:
            frappe.enqueue(
                submit_salary_slips_for_employees, timeout=600, payroll_entry=self, salary_slips=ss_list
            )
        else:
            submit_salary_slips_for_employees(self, ss_list, publish_progress=False)

def create_salary_slips_for_employees(posting_date,start_date,end_date,employees, args,food_count, publish_progress=True):
    salary_slips_exists_for = get_existing_salary_slips(employees, args)
    count = 0
    salary_slips_not_created = []
    index=0
    for emp in employees:
        if emp not in salary_slips_exists_for:
            args.update({"doctype": "Salary Slip", "total_time_of_food_taken": food_count[index]})
            args.update({"doctype": "Salary Slip", "employee": emp})
            employee=frappe.get_doc('Employee',emp)
            if(employee.designation=='Job Worker'):
                job_worker = frappe.db.get_all('TS Job Worker Details',fields=['name1','parent','amount','start_date','end_date'])
                site_work=[]
                total_amount=0
                start_date=getdate(start_date)
                end_date=getdate(end_date)
                for data in job_worker:
                    site_row = frappe._dict({})
                    if data.name1 == emp and data.start_date >= start_date and data.start_date <= end_date and data.end_date >= start_date and data.end_date <= end_date:
                        total_amount+=data.amount
                        site_row.update({'site_work_name':data.parent,'amount':data.amount})
                        site_work.append(site_row)
                args.update({"doctype": "Salary Slip", "total_amount": total_amount})    
                args.update({"doctype": "Salary Slip", "site_work_details": site_work})
                
            elif(employee.designation=='Contractor'):
                contractor=[]
                total_hours=0
                start_date=getdate(start_date)
                end_date=getdate(end_date)
                for data in frappe.db.get_list("Salary Slip", filters={'status': 'Submitted','designation':'Labour Worker'},fields=["name",'end_date','start_date','total_working_hours']):
                    contractor_row = frappe._dict({})
                    if data.start_date>=start_date and data.start_date<= end_date and data.end_date>=start_date and data.end_date<=end_date:
                        total_hours+=data.total_working_hours
                        welfare_amount = frappe.db.get_value("Company", employee.company,"contractor_welfare_commission")
                        contractor_row.update({'salary_component':'Contractor Welfare','amount':total_hours*welfare_amount})
                        contractor.append(contractor_row)

                #Salary structure Updation
                salary_structure=None
                for structure in frappe.get_all("Salary Structure Assignment",fields=["name","from_date",'salary_structure'],
                        filters={"employee": emp,'docstatus':1}, order_by="from_date",):
                    if(getdate(posting_date)>=structure['from_date']):
                        salary_structure=structure
                args.update({'doctype':'Salary Slip','salary_structure':salary_structure['salary_structure']})
               
                #Timesheet Updation
                timesheets = frappe.db.sql(
                    """ select * from `tabTimesheet` where employee = %(employee)s and start_date BETWEEN %(start_date)s AND %(end_date)s and (status = 'Submitted' or
                    status = 'Billed')""",
                    {"employee": emp, "start_date": start_date, "end_date": end_date},
                    as_dict=1,
                )
                hour_rate=frappe.db.get_value("Salary Structure", salary_structure['salary_structure'], "hour_rate")
                total_time_hours=0
                timesheet=[]
                for data in timesheets:
                    timesheets_row=frappe._dict({})
                    timesheets_row.update({"time_sheet": data.name, "working_hours": data.total_hours,"overtime_hours":data.overtime_hours})
                    total_time_hours+=data.total_hours
                    timesheet.append(timesheets_row)
                    
                args.update({"doctype": "Salary Slip", "timesheets": timesheet})
                
                total_days=0
                ot_hours=0.0
                for data in args.timesheets:
                    value = frappe.db.get_single_value('HR Settings', 'standard_working_hours')
                    if (data.working_hours)>=float(value):
                            total_days+=1
                    ot_hours+=data.overtime_hours
                
                args.update({"doctype": "Salary Slip", "total_overtime_hours": ot_hours})
                args.update({"doctype": "Salary Slip", "days_worked": total_days})
                args.update({"doctype": "Salary Slip", "hour_rate": hour_rate})
                args.update({"doctype": "Salary Slip", "total_working_hours": total_time_hours})

                contractor_row = frappe._dict({})
                contractor_row.update({'salary_component':frappe.db.get_value("Salary Structure", salary_structure['salary_structure'], "salary_component"),'amount':total_time_hours*hour_rate})
                contractor.append(contractor_row)
                args.update({"doctype": "Salary Slip", "earnings": contractor})

            ss = frappe.get_doc(args)
            ss.insert()
            count += 1
            if publish_progress:
                frappe.publish_progress(
                    count * 100 / len(set(employees) - set(salary_slips_exists_for)),
                    title=_("Creating Salary Slips..."),
                )
        else:
            salary_slips_not_created.append(emp)
        index+=1

    payroll_entry = frappe.get_doc("Payroll Entry", args.payroll_entry)
    payroll_entry.db_set("salary_slips_created", 1)
    payroll_entry.notify_update()
    if salary_slips_not_created:
        frappe.msgprint(
            _(
                "Salary Slips already exists for employees {}, and will not be processed by this payroll."
            ).format(frappe.bold(", ".join([emp for emp in salary_slips_not_created]))),
            title=_("Message"),
            indicator="orange",
        )

def submit_salary_slips_for_employees(payroll_entry, salary_slips, publish_progress=False):
    submitted_ss = []
    not_submitted_ss = []
    frappe.flags.via_payroll_entry = True

    count = 0
    for ss in salary_slips:
        ss_obj = frappe.get_doc("Salary Slip", ss[0])
        if ss_obj.net_pay < 0:
            not_submitted_ss.append(ss[0])
        else:
            try:
                ss_obj.submit()
                submitted_ss.append(ss_obj)
            except frappe.ValidationError:
                not_submitted_ss.append(ss[0])
        count += 1
        if publish_progress:
            frappe.publish_progress(count * 100 / len(salary_slips), title=_("Submitting Salary Slips..."))
    if submitted_ss:
        payroll_entry.make_accrual_jv_entry()
        frappe.msgprint(
            _("Salary Slip submitted for period from {0} to {1}").format(ss_obj.start_date, ss_obj.end_date)
        )

        payroll_entry.email_salary_slip(submitted_ss)

        payroll_entry.db_set("salary_slips_submitted", 1)
        payroll_entry.notify_update()

    salary_slip=[frappe.get_doc("Salary Slip",i) for i in frappe.get_all("Salary Slip",filters={'payroll_entry':payroll_entry.name})]
    single_slip=[{
    'Employee':i.employee,
    'Salary':i.net_pay
    }  for i in salary_slip]

    return html_history(single_slip,payroll_entry)


def html_history(single_slip,payroll_entry):
    html='<tr style="border: 1px solid #ddd; height:20px !important;">'+''.join([ 
        f'<th style="border-right: 1px solid #ddd;"><center>{i}</center></th>'for i in ['S.No','Employee','Salary Issued'] ])+'</tr>'
    td=[
        f'<tr style="text-align:center;border: 1px solid #ddd; height:20px !important;"><h1>'+
        f'<td style="border-right: 1px solid #ddd;">{i+1}</td>'+
        f'<td style="border-right: 1px solid #ddd;">{single_slip[i]["Employee"]}</td>'+
        f'<td style="border-right: 1px solid #ddd;">{single_slip[i]["Salary"]}</td>'+'</tr></h1>'
        for i in range(len(single_slip))
        ]
    value ='<table style="width:100%;border: 1px solid #ddd;border-collapse: collapse; ">'+html+''.join(td)+'</table>'
    frappe.set_value(payroll_entry.doctype, payroll_entry.name, "employee_salary_",value)
