# Copyright (c) 2023, Thirvusoft and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	columns, data = get_columns(filters), get_data(filters)
	return columns, data

def get_data(filters=None):
	data=[]
	as_filters={"docstatus": 1}
	if filters.get("employee"):
		as_filters["employee"]=filters.get("employee")
	additional_salaries = frappe.db.get_all("Additional Salary", filters=as_filters, fields=["name", "employee", "employee_name", "amount", "salary_slip_amount"], order_by="employee_name")
	if filters.get("show_salary_slips"):
		for row in additional_salaries:
			conditions=f""" where ads.docstatus=1 and ads.name='{row.name}' and IFNULL(ssr.salary_slip, "")!="" and IFNULL(ssr.amount, 0)>0"""
			if filters.get("employee"):
				conditions+=f""" and ads.employee='{filters.get("employee")}"""
			ss_data=frappe.db.sql(f"""
				select ssr.salary_slip, ssr.amount as salary_slip_amount
				from `tabSalary Slip Reference` ssr left outer join `tabAdditional Salary` as ads
				on ads.name=ssr.parent
				{conditions}
			""", as_dict=True)
			if ss_data:
				amount=row.get('amount', 0)
				salary_slip_amount=row.get('salary_slip_amount', 0)
				row.amount=None
				row.salary_slip_amount=None
				data.append(row)
				data+=ss_data
				data.append({
					"salary_slip": "</a><span style='color: orange;font-weight: bold;' data-name='Total Span'>Total<span><a>",
					"amount": f"<b>{amount}</b>",
					"salary_slip_amount": f"<b>{salary_slip_amount}</b>"
				})
			else:
				data.append(row)
	else:
		return additional_salaries

	return data

def get_columns(filters=None):
	return [
		{
			"fieldname": "employee",
			"fieldtype": "Link",
			"options": "Employee",
			"label": "Employee"
		},
		{
			"fieldname": "employee_name",
			"fieldtype": "Data",
			"label": "Employee Name"
		},
		{
			"fieldname": "salary_slip",
			"fieldtype": "Link",
			"label": "Salary Slip",
			"options": "Salary Slip"
		},
		{
			"fieldname": "salary_slip_amount",
			"fieldtype": "Data",
			"label": "Deduction Amount",
		},
		{
			"fieldname": "amount",
			"fieldtype": "Data",
			"label": "Advance Amount",
		}
	]