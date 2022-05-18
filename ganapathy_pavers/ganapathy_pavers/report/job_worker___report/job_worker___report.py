# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

import frappe
from frappe import _
def execute(filters=None):
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	employee = filters.get("employee")
	site_name = filters.get("site_name")
	conditions = ""
	if from_date or to_date or employee or site_name:
		conditions = " where 1 = 1"
		
		if from_date and to_date:
			conditions += "  and jwd.start_date between '{0}' and '{1}' ".format(from_date, to_date)
		if employee:
			conditions += " and jwd.name1 ='{0}' ".format(employee)
		if site_name:
			conditions += " and site.name = '{0}' ".format(site_name)
	report_data = frappe.db.sql(""" select *,(amount + salary_balance - advance_amount) from (select jwd.name1,site.name,site.status,jwd.sqft_allocated,
										emp.salary_balance as salary_balance,jwd.amount as amount,
										(select sum(empadv.advance_amount - empadv.return_amount) from `tabEmployee Advance` as empadv where empadv.employee = jwd.name1 and docstatus = 1) as advance_amount
										from `tabProject` as site
										left outer join `tabTS Job Worker Details` as jwd
											on site.name = jwd.parent
										left outer join `tabEmployee` as emp
											on emp.employee = jwd.name1
										{0}
									group by jwd.name1,jwd.sqft_allocated)as total_cal
								""".format(conditions))
	data = [list(i) for i in report_data]
	job_worker=[frappe.get_all("Employee",fields=['employee_name'],filters={'name':i[0]})[0]['employee_name'] for i in data]
	for i in range(len(job_worker)):data[i][0] = str(job_worker[i])
	columns = get_columns()
	return columns, data

def get_columns():
	columns = [
		_("Job Worker") + ":Data/Employee:150",
		_("Site Name") + ":Link/Project:150",
		_("Status") + ":Data/Project:150",
		_("Completed Sqft") + ":Data:150",
		_("Salary Balance") + ":Currency:150",
		_("Amount") + ":Currency:150",
		_("Advance Amount") + ":Currency:150",
		_("Total Amount") + ":Currency:150",
		]
	
	return columns
