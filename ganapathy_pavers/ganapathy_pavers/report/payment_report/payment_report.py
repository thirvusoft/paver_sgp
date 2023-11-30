# Copyright (c) 2023, Thirvusoft and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns, data = get_columns(filters), get_data(filters)
	return columns, data

def get_columns(filters):
	columns = [
		{
			"label": ("Party"),
			"fieldtype": "Data",
			"fieldname": "party",
			"width": 350
		},
		{
			"label": ("Type"),
			"fieldtype": "Data",
			"fieldname": "type",
			"width": 350
		},
		{
			"label": ("Paid Amount"),
			"fieldtype": "Currency",
			"fieldname": "paid_amount",
			"width": 380
		}
	]
	return columns

def get_data(filters):
	pe_filters = f" pe.docstatus = 1 and pe.party_type = '{filters.get('party')}' "
	if filters.get('branch'):
		pe_filters += f" and pe.branch = '{filters.get('branch')}'"
		
	if filters.get('type'):
		pe_filters += f" and pe.type = '{filters.get('type')}'"

	if filters.get('site_work'):
		pe_filters += f" and pe.site_work = '{filters.get('site_work')}'"
	
	if filters.get('from_date') and filters.get('to_date'):
		pe_filters += f" and pe.posting_date between '{filters.get('from_date')}' and '{filters.get('to_date')}' "

	_data = frappe.db.sql(f'''
				select 
					pe.party,
					case when ifnull(pe.type, '') = '' then 'No Type' else pe.type end as type,
					sum(pe.paid_amount) as paid_amount 
				from `tabPayment Entry` as pe 
				where 
					{pe_filters} 
				group by
				 	pe.party,
					case when ifnull(pe.type, '') = '' then 'No Type' else pe.type end
				order by 
					pe.type,
					pe.party
	
	''',as_dict=1)
	
	data = []
	current_type, total = '', 0
	for idx in range(len(_data)):
		frappe.errprint(idx == 0 or idx == len(_data)-1)
		if idx == 0 or idx == len(_data)-1:
			current_type = _data[idx].type
			total += _data[idx].paid_amount
			data.append(_data[idx])
			
			if (idx == len(_data)-1):
				data.append({
					"party": f"{current_type}",
					"paid_amount": total
				})
		else:
			if current_type != _data[idx].type:
				data.append({
					"party": f"{current_type}",
					"paid_amount": total
				})
				current_type = _data[idx].type
				total = _data[idx].paid_amount
				data.append(_data[idx])
			else:
				total += _data[idx].paid_amount
				data.append(_data[idx])
	data.append({})
	total_data = frappe.db.sql(f'''
				select sum(pe.paid_amount) as paid_amount from `tabPayment Entry` as pe where {pe_filters}
	
	''',as_dict=1)

	bank_data = frappe.db.sql(f'''
				SELECT
					CASE
						WHEN br.is_accounting = 1 THEN CONCAT('Bank Total - ',case when ifnull(pe.type, '') = '' then 'No Type' else pe.type end, '')
						ELSE CONCAT('Total - ',case when ifnull(pe.type, '') = '' then 'No Type' else pe.type end, '')
					END AS party,
					SUM(pe.paid_amount) AS paid_amount
				FROM
					`tabPayment Entry` AS pe
				LEFT JOIN
					`tabBranch` AS br ON pe.branch = br.name
				WHERE
					{pe_filters}
				GROUP BY
					pe.branch,
					case when ifnull(pe.type, '') = '' then 'No Type' else pe.type end
				ORDER BY
					pe.branch DESC,
					pe.type

	
	''',as_dict=1)

	data += bank_data
	data.append({})
	data.append({
		'party':"Total Amount",
		'paid_amount':total_data[0]['paid_amount'] if total_data else 0
	})
	
	return data