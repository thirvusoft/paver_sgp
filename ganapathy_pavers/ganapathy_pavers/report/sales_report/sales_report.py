# Copyright (c) 2023, Thirvusoft and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns, data = get_columns(filters), get_data(filters)
	return columns, data

def get_columns(filters):
	columns = [
		{
			"label": ("Customer"),
			"fieldtype": "Link",
			"fieldname": "customer",
			'options':'Customer',
			"width": 350
		},
		{
			"label": ("Invoice Amount"),
			"fieldtype": "Currency",
			"fieldname": "invoice_amount",
			"width": 380
		}
	]
	return columns

def get_data(filters):
	si_filters = f" si.docstatus = 1"
	if filters.get('branch'):
		si_filters += f" and si.branch = '{filters.get('branch')}'"
	
	if filters.get('site_work'):
		si_filters += f" and si.site_work = '{filters.get('site_work')}'"
	
	if filters.get('from_date') and filters.get('to_date'):
		si_filters += f" and si.posting_date between '{filters.get('from_date')}' and '{filters.get('to_date')}' "

	data = frappe.db.sql(f'''
				select si.customer,sum(si.base_net_total) as invoice_amount from `tabSales Invoice` as si where {si_filters} group by si.customer
	
	''',as_dict=1)
	
	total_data = frappe.db.sql(f'''
				select sum(si.base_net_total) as invoice_amount from `tabSales Invoice` as si where {si_filters}
	
	''',as_dict=1)

	bank_data = frappe.db.sql(f'''
				SELECT
					CASE
						WHEN br.is_accounting = 1 THEN '<b>Bank Total</b>'
						ELSE '<b>Cash Total</b>'
					END AS customer,
					SUM(si.base_net_total) AS invoice_amount
				FROM
					`tabSales Invoice` AS si
				LEFT JOIN
					`tabBranch` AS br ON si.branch = br.name
				WHERE
					{si_filters}
				GROUP BY
					si.branch
				ORDER BY
					si.branch DESC

	
	''',as_dict=1)
	
	data.append({
		'customer':"<b>Total Amount</b>",
		'invoice_amount':total_data[0]['invoice_amount'] if total_data else 0
	})
	data += bank_data
	# data.append({
	# 	'party':"<b>Bank Total</b>",
	# 	'paid_amount':bank_data[0]['paid_amount'] if bank_data else 0
	# })
	# data.append({
	# 	'party':"<b>Cash Total</b>",
	# 	'paid_amount':bank_data[0]['paid_amount'] if bank_data else 0

	# })
	return data