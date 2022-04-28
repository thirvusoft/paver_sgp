from erpnext.payroll.doctype.payroll_entry.payroll_entry import ( PayrollEntry,get_existing_salary_slips)
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
                frappe.enqueue(create_salary_slips_for_employees, timeout=600, employees=employees,args=args,food_count=food_count)
            else:
                create_salary_slips_for_employees(self.start_date,self.end_date,employees, args,food_count, publish_progress=False)
				# since this method is called via frm.call this doc needs to be updated manually
                self.reload()

def create_salary_slips_for_employees(start_date,end_date,employees, args,food_count, publish_progress=True):
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
                start_date=getdate(start_date)
                end_date=getdate(end_date)
                for data in job_worker:
                    site_row = frappe._dict({})
                    if data.name1 == emp and data.start_date >= start_date and data.start_date <= end_date and data.end_date >= start_date and data.end_date <= end_date:
                        site_row.update({'site_work_name':data.parent,'amount':data.amount})
                    site_work.append(site_row)
                args.update({"doctype": "Salary Slip", "site_work_details": site_work})
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

