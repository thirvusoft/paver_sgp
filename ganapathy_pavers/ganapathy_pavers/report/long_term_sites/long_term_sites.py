# Copyright (c) 2023, Thirvusoft and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	columns, data = get_columns(filters), get_data(filters)
	chart_data = {
		"data": {
			"labels": [(i.get('site') or '') for i in data],
			"datasets": [{"values": [(i.get('days') or 0) for i in data]}],
		},
		"type": "bar",
	}

	desc = """<b>No of Days</b> was calculated by getting difference between minimum and maximum dates in <b>Sales Order, Sales Invoice, Delivery Note, Job Worker Laying Details</b>"""
	return columns, data, desc, chart_data

def get_data(filters):
	DATE_QUERY = lambda site : f"""
		(
			SELECT
				MIN(so.transaction_date) as min_date,
				MAX(so.transaction_date) as max_date
			FROM `tabSales Order` so
			WHERE 
				so.site_work = '{site}' AND
				so.docstatus = 1
		)
		UNION
		(
			SELECT
				MIN(si.posting_date) as min_date,
				MAX(si.posting_date) as max_date
			FROM `tabSales Invoice` si
			WHERE 
				si.site_work = '{site}' AND
				si.docstatus = 1
		)
		UNION
		(
			SELECT
				MIN(dn.posting_date) as min_date,
				MAX(dn.posting_date) as max_date
			FROM `tabDelivery Note` dn
			WHERE 
				dn.site_work = '{site}' AND
				dn.docstatus = 1
		)
		UNION
		(
			SELECT
				MIN(jw.start_date) as min_date,
				MAX(jw.end_date) as max_date
			FROM `tabTS Job Worker Details` jw
			WHERE
				jw.parenttype = 'Project' AND
				jw.parent = '{site}'
		)
	"""

	site_query = f"""
		SELECT
			sw.name as site
		FROM `tabProject` sw 
		WHERE
			CASE
				WHEN IFNULL('{filters.get('type') or ''}', '') != ''
					THEN sw.type = '{filters.get('type') or ''}'
				ELSE 1=1
			END AND
			CASE
				WHEN IFNULL({len(filters.get('status') or [])}, 0) != 0
					THEN sw.status in ({', '.join(f"'{i}'" for i in (filters.get('status') or ['', '']))})
				ELSE 1=1
			END AND
			CASE
				WHEN IFNULL('{filters.get('customer') or ''}', '') != ''
					THEN (
							sw.customer = '{filters.get('customer') or ''}'
							OR
							'{filters.get('customer') or ''}' in (
								SELECT
									cus.customer
								FROM `tabTS Customer` cus
								WHERE
									cus.parenttype = "Project" AND
									cus.parent = sw.name
							)
						)
				ELSE 1=1
			END AND
			CASE 
				WHEN IFNULL('{1 if filters.get('status') == ['Completed'] else 0}', '0') = '1'
					THEN CASE
							WHEN IFNULL('{filters.get('from_date') or ''}', '') != ''
								THEN sw.completion_date >= '{filters.get('from_date') or ''}'
							ELSE 1=1
						END AND
						CASE
							WHEN IFNULL('{filters.get('to_date') or ''}', '') != ''
								THEN sw.completion_date <= '{filters.get('to_date') or ''}'
							ELSE 1=1
						END
				ELSE 1=1
			END
		"""
	sitelist = frappe.db.sql(site_query, as_dict=True)
	data = []

	for site in sitelist:
		data += frappe.db.sql(f"""
					SELECT
						sw.name as site,
						TIMESTAMPDIFF(
		      			DAY, 
		      			(
							SELECT
		      					MIN(min_query.min_date)
		      				FROM ({DATE_QUERY(site=site.get("site"))}) as min_query
		      			), 
		      			(
							SELECT
		      					MAX(max_query.max_date)
		      				FROM ({DATE_QUERY(site=site.get("site"))}) as max_query
		      			)
		      		) + 1 as days
					FROM `tabProject` sw
					WHERE
						sw.name = '{site.get("site")}'
				""", as_dict=True)
	data.sort(key = lambda x: x.get('days') or 0, reverse=True)

	if filters.get('limit'):
		data = data[0:filters.get('limit')]

	return data

def get_columns(filters):
	return [
		{
			'fieldname': 'site',
			'label': 'Site',
			'fieldtype': 'Link',
			'options': 'Project',
			'width': 200
		},
		{
			'fieldname': 'days',
			'label': 'No of Days',
			'fieldtype': 'Int',
			'width': 200,
		},
	]