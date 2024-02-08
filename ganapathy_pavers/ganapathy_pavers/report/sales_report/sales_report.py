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
			"label": ("Type"),
			"fieldtype": "Data",
			"fieldname": "type",
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
			
	if filters.get('type'):
		si_filters += f" and ifnull(si.type, 'No Type') = '{filters.get('type')}'"

	if filters.get('from_date') and filters.get('to_date'):
		si_filters += f" and si.posting_date between '{filters.get('from_date')}' and '{filters.get('to_date')}' "

	_data = frappe.db.sql(f'''
				select 
					si.customer,
					case when ifnull(si.type, '') = '' then 'No Type' else si.type end as type,
					sum(si.base_net_total) as invoice_amount 
				from `tabSales Invoice` as si 
				where 
					{si_filters} 
				group by 
					si.customer, 
					case when ifnull(si.type, '') = '' then 'No Type' else si.type end 
				order by
					ifnull(si.type, ''), 
					si.customer
	
	''',as_dict=1)
	
	data = []
	current_type, total = '', 0
	for idx in range(len(_data)):
		if idx == 0 or idx == len(_data)-1:
			current_type = _data[idx].type
			total += _data[idx].invoice_amount
			data.append(_data[idx])
			
			if (idx == len(_data)-1):
				data.append({
					"customer": f"{current_type}",
					"invoice_amount": total
				})
		else:
			if current_type != _data[idx].type:
				data.append({
					"customer": f"{current_type}",
					"invoice_amount": total
				})
				current_type = _data[idx].type
				total = _data[idx].invoice_amount
				data.append(_data[idx])
			else:
				total += _data[idx].invoice_amount
				data.append(_data[idx])

	total_data = frappe.db.sql(f'''
				select sum(si.base_net_total) as invoice_amount from `tabSales Invoice` as si where {si_filters}
	
	''',as_dict=1)
	data.append({})
	bank_data = frappe.db.sql(f'''
				SELECT
					CASE
						WHEN br.is_accounting = 1 THEN CONCAT('Bank Total - ', case when ifnull(si.type, '') = '' then 'No Type' else si.type end, '')
						ELSE CONCAT('Total - ', case when ifnull(si.type, '') = '' then 'No Type' else si.type end, '')
					END AS customer,
					SUM(si.base_net_total) AS invoice_amount
				FROM
					`tabSales Invoice` AS si
				LEFT JOIN
					`tabBranch` AS br ON si.branch = br.name
				WHERE
					{si_filters}
				GROUP BY
					si.branch,
					ifnull(si.type, '')
				ORDER BY
					si.branch DESC, ifnull(si.type, '')
	''',as_dict=1)
	data += bank_data
	data.append({})
	data.append({
		'customer':"Total Amount",
		'invoice_amount':total_data[0]['invoice_amount'] if total_data else 0
	})

	return data