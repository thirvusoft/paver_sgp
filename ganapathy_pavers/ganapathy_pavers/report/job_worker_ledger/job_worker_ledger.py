# Copyright (c) 2023, Thirvusoft and contributors
# For license information, please see license.txt

import frappe

ss_filter_date="end_date"

def execute(filters=None):
	data = get_data(filters)
	columns = get_columns(filters, data)

	return columns, data

def get_data(filters=None):
	opening_balance=get_opening_balance(filters)
	
	jw_data=get_jw_data(filters)
	ss_data=get_salary_slip_data(filters)
	emp_adv_data=get_emp_adv_data(filters)

	data = jw_data + ss_data + emp_adv_data
	data.sort(key = lambda x: x.get("order_date", x.get("date", "")))

	data= opening_balance + data

	data += get_closing_balance(filters, data)

	return data

def get_opening_balance(filters=None):
	data=[]

	jw_opening_credit=get_jw_opening_balance(filters)
	ss_opening_debit=get_salary_slip_opening_balance(filters)
	emp_adv_opening_debit=get_emp_adv_opening_balance(filters)

	data.append({
		"voucher_type": "Opening Balance",
		"debit": 0,
		"debit": ss_opening_debit + emp_adv_opening_debit,
		"credit": jw_opening_credit,
		"bold": 1,
	})

	return data

def get_closing_balance(filters=None, source_data=[]):
	data=[]
	total_credit, total_debit = 0, 0

	for row in source_data:
		total_credit += row.get("credit", 0)
		total_debit += row.get("debit", 0)
	if len(source_data) > 1:
		data.append({
			"voucher_type": "Transaction Total",
			"debit": total_debit,
			"credit": total_credit,
			"bold": 1,
		})
	data.append({
		"voucher_type": "Closing Balance",
		"debit": 0,
		"credit": total_credit - total_debit,
		"bold": 1,
	})

	return data

def get_jw_opening_balance(filters=None):
	data=[]

	jw_conditions=" WHERE jw.parenttype='Project'"
	if filters.get("employee"):
		jw_conditions += f" AND jw.name1='{filters.get('employee')}'"
	if filters.get("from_date"):
		jw_conditions += f" AND jw.start_date<'{filters.get('from_date')}'"

	if filters.get("from_date"):
		query=f"""
			SELECT
				SUM(jw.amount)
			FROM `tabTS Job Worker Details` jw
			{jw_conditions} 
		"""

		data=frappe.db.sql(query, as_list=True)
	return (data[0][0] if data and data[0] else 0) or 0

def get_salary_slip_opening_balance(filters=None):
	data=[]

	jw_conditions=" WHERE ss.docstatus=1"
	if filters.get("employee"):
		jw_conditions += f" AND ss.employee='{filters.get('employee')}'"
	if filters.get("from_date"):
		jw_conditions += f" AND ss.{ss_filter_date}<'{filters.get('from_date')}'"

	if filters.get("from_date"):
		query=f"""
			SELECT
				SUM(ss.paid_amount)
			FROM `tabSalary Slip` ss
			{jw_conditions} 
		"""

		data=frappe.db.sql(query, as_list=True)
	return (data[0][0] if data and data[0] else 0) or 0

def get_emp_adv_opening_balance(filters):
	data = []

	emp_adv_conditions=" WHERE emp_adv.repay_unclaimed_amount_from_salary=1 AND emp_adv.docstatus=1"
	if filters.get("employee"):
		emp_adv_conditions += f" AND emp_adv.employee='{filters.get('employee')}'"
	if filters.get("from_date"):
		emp_adv_conditions += f" AND emp_adv.posting_date<'{filters.get('from_date')}'"

	if filters.get("from_date"):
		query=f"""
			SELECT
				SUM(emp_adv.advance_amount)
			FROM `tabEmployee Advance` emp_adv
			{emp_adv_conditions} 
		"""

		data=frappe.db.sql(query, as_list=True)
	return (data[0][0] if data and data[0] else 0) or 0

def get_salary_slip_data(filters=None):
	data=[]

	ss_conditions="WHERE ss.docstatus=1"

	if filters.get("employee"):
		ss_conditions += f" AND ss.employee='{filters.get('employee')}'"
	
	if filters.get("from_date"):
		ss_conditions += f" AND ss.{ss_filter_date}>='{filters.get('from_date')}'"
	
	if filters.get("to_date"):
		ss_conditions += f" AND ss.{ss_filter_date}<='{filters.get('to_date')}'"

	query=f"""
		SELECT 
			ss.{ss_filter_date} as order_date,
			ss.posting_date as date,
			'Salary Slip' as voucher_type,
			ss.name as voucher_no,
			(
				SELECT
					emp.employee_name
				FROM `tabEmployee` emp
				WHERE emp.name=ss.employee
			) as employee,
			(ss.paid_amount - ss.excess_amount_to_create_advance) as debit,
			0 as credit
		FROM `tabSalary Slip` as ss
		{ss_conditions}
	"""
	
	data=frappe.db.sql(query, as_dict = True)
	
	return data

def get_emp_adv_data(filters=None):
	data=[]

	emp_adv_conditions = "WHERE emp_adv.repay_unclaimed_amount_from_salary=1 AND emp_adv.docstatus=1"

	if filters.get("employee"):
		emp_adv_conditions += f" AND emp_adv.employee='{filters.get('employee')}'"
	
	if filters.get("from_date"):
		emp_adv_conditions += f" AND emp_adv.posting_date>='{filters.get('from_date')}'"
	
	if filters.get("to_date"):
		emp_adv_conditions += f" AND emp_adv.posting_date<='{filters.get('to_date')}'"


	query=f"""
		SELECT
			emp_adv.posting_date as date,
			'Employee Advance' as voucher_type,
			emp_adv.name as voucher_no,
			(
				SELECT
					emp.employee_name
				FROM `tabEmployee` emp
				WHERE emp.name=emp_adv.employee
			) as employee,
			emp_adv.advance_amount as debit,
			0 as credit
		FROM `tabEmployee Advance` emp_adv
		{emp_adv_conditions}
	"""

	data=frappe.db.sql(query, as_dict=True)
	return data

def get_jw_data(filters=None):
	data=[]
	jw_conditions=" WHERE jw.parenttype='Project'"

	if filters.get("employee"):
		jw_conditions += f" AND jw.name1='{filters.get('employee')}'"
	
	if filters.get("from_date"):
		jw_conditions += f" AND jw.start_date>='{filters.get('from_date')}'"
	
	if filters.get("to_date"):
		jw_conditions += f" AND jw.end_date<='{filters.get('to_date')}'"

	query=f"""
		SELECT
			jw.start_date as date,
			jw.parenttype as voucher_type,
			jw.parent as voucher_no,
			(
				SELECT
					emp.employee_name
				FROM `tabEmployee` emp
				WHERE emp.name=jw.name1
			) as employee,
			CASE
				WHEN jw.other_work=1
					THEN 'YES'
			END as other_work,
			jw.description_for_other_work as other_work_description,
			jw.item as item,
			jw.sqft_allocated as sqft,
			0 as debit,
			jw.amount as credit
		FROM `tabTS Job Worker Details` jw
		{jw_conditions}
		ORDER BY jw.start_date
	"""

	data=frappe.db.sql(query, as_dict = True)
	return data

def get_columns(filters=None, data=[]):
	other_work=bool(sum([1 for row in data if row.get("other_work")]))
	return [
		{
			"fieldname": "date",
			"label": "Date",
			"fieldtype": "Date",
			"width": 100,
		},
		{
			"fieldname": "voucher_type",
			"label": "Voucher Type",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"fieldname": "voucher_no",
			"label": "Voucher Name",
			"fieldtype": "Dynamic Link",
			"options": "voucher_type",
			"width": 250,
		},
		{
			"fieldname": "employee",
			"label": "Job Worker",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"fieldname": "other_work",
			"label": "Other Work",
			"fieldtype": "Data",
			"hidden": not other_work,
			"width": 50,
		},
		{
			"fieldname": "other_work_description",
			"label": "Other Work Description",
			"fieldtype": "Data",
			"hidden": not other_work,
			"width": 250,
		},
		{
			"fieldname": "item",
			"label": "Item",
			"fieldtype": "Link",
			"options": "Item",
			"width": 250,
		},
		{
			"fieldname": "sqft",
			"label": "Sqft",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"fieldname": "debit",
			"label": "Debit",
			"fieldtype": "Float",
			"default": 0,
			"width": 100,
		},
		{
			"fieldname": "credit",
			"label": "Credit",
			"fieldtype": "Float",
			"default": 0,
			"width": 100,
		},
		{
			"fieldname": "bold",
			"fieldtype": "Check",
			"hidden": 1,
		}
	]