# Copyright (c) 2023, Thirvusoft and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	customer = filters.get("customer")
	sitework= filters.get("site_name")
	_type=filters.get("type")
	status=filters.get("status")
	
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	date = filters.get("date")
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")

	data=[]
	sw_filters={}

	if _type:
		sw_filters["type"] = _type
	if status:
		sw_filters["status"] = status
	if customer:
		sw_filters["customer"] = customer
	if sitework:
		sw_filters["name"] = sitework
	
	sw_list=frappe.get_all("Project", filters=sw_filters, order_by="name")
	
	table_name='tabPavers' if _type=="Pavers" else 'tabCompound Wall'
	field_name='required_area' if _type=="Pavers" else 'allocated_ft'
	
	jw_filter=""

	if not filters.get("include_other_works"):
		jw_filter=""" AND jw.other_work=0"""

	supply_only_filter = ""

	if filters.get("hide_supply_only"):
		supply_only_filter = f"""
		AND (SELECT COUNT(wc.name) FROM `{table_name}` wc WHERE wc.parent=sw.name AND wc.work != "Supply Only") > 0
		AND (SELECT COUNT(so.name) FROM `tabSales Order` so WHERE so.docstatus = 1 AND so.site_work=sw.name) > 0
		"""
	
	if filters.get("show_only_supply_only"):
		supply_only_filter = f"""
		AND (SELECT COUNT(wc.name) FROM `{table_name}` wc WHERE wc.parent=sw.name AND wc.work != "Supply Only") = 0
		AND (SELECT COUNT(so.name) FROM `tabSales Order` so WHERE so.docstatus = 1 AND so.site_work=sw.name) > 0
		"""

	working_status=""
	if filters.get("working_status") == "No Delivery":
		working_status += f"""  and (SELECT sum(ds1.delivered_stock_qty + ds1.returned_stock_qty)  FROM `tabDelivery Status` as ds1 WHERE ds1.parent=sw.name)=0"""
	elif filters.get("working_status") == "Delivery Started & No Laying":
		working_status += f"""  and (SELECT sum(ds1.delivered_stock_qty + ds1.returned_stock_qty)  FROM `tabDelivery Status` as ds1 WHERE ds1.parent=sw.name)>0 AND sw.total_layed_sqft=0"""
	elif filters.get("working_status") == "Delivery & Laying Started":
		working_status += f"""  and (SELECT sum(ds1.delivered_stock_qty + ds1.returned_stock_qty)  FROM `tabDelivery Status` as ds1 WHERE ds1.parent=sw.name)>0 AND sw.total_layed_sqft>0"""

	laying_query = f"""
		(SELECT sum(jw.sqft_allocated) FROM `tabTS Job Worker Details` as jw WHERE jw.parent=sw.name {jw_filter}) as total_laying,
		(SELECT sum(jw.completed_bundle) FROM `tabTS Job Worker Details` as jw WHERE jw.parent=sw.name {jw_filter}) as bundle_laying,
	"""

	date=from_date

	if to_date and not from_date:
		date = to_date

	date_filter=f"""jw.start_date = '{date}'"""

	if from_date and to_date:
		date_filter = f"""jw.start_date between '{from_date}' and '{to_date}' """
	
	date=from_date

	if to_date and not from_date:
		date = to_date

	date_filter=f"""jw.start_date = '{date}'"""

	if from_date and to_date:
		date_filter = f"""jw.start_date between '{from_date}' and '{to_date}' """
	
	if date:
		laying_query = f"""
			(SELECT sum(jw.sqft_allocated) FROM `tabTS Job Worker Details` as jw WHERE jw.parent=sw.name {jw_filter} AND jw.start_date < '{date}') as total_laying,
			(SELECT sum(jw.completed_bundle) FROM `tabTS Job Worker Details` as jw WHERE jw.parent=sw.name {jw_filter} AND jw.start_date < '{date}') as bundle_laying,
			(SELECT sum(jw.sqft_allocated) FROM `tabTS Job Worker Details` as jw WHERE jw.parent=sw.name {jw_filter} AND {date_filter}) as total_laying_date,
			(SELECT sum(jw.completed_bundle) FROM `tabTS Job Worker Details` as jw WHERE jw.parent=sw.name {jw_filter} AND {date_filter}) as bundle_laying_date,
			(SELECT sum(jw.sqft_allocated) FROM `tabTS Job Worker Details` as jw WHERE jw.parent=sw.name {jw_filter} AND jw.start_date = '{date}') as total_laying_date,
			(SELECT sum(jw.completed_bundle) FROM `tabTS Job Worker Details` as jw WHERE jw.parent=sw.name {jw_filter} AND jw.start_date = '{date}') as bundle_laying_date,
			(SELECT sum(jw.sqft_allocated) FROM `tabTS Job Worker Details` as jw WHERE jw.parent=sw.name {jw_filter} AND {date_filter}) as total_laying_date,
			(SELECT sum(jw.completed_bundle) FROM `tabTS Job Worker Details` as jw WHERE jw.parent=sw.name {jw_filter} AND {date_filter}) as bundle_laying_date,
		"""

	for sw in sw_list:		
		site_data=frappe.db.sql(f"""
			SELECT 
				sw.name as site_name,
				(
				SELECT 
					GROUP_CONCAT(
					IF(
						pav_cw.parent='{sw.name}'
						, pav_cw.item
						, NULL
					) 
					SEPARATOR ', '
					) 
				FROM `{table_name}` pav_cw
				WHERE pav_cw.work != "Supply Only"
				) as design,
				(SELECT sum(ps.{field_name}) FROM `{table_name}` as ps WHERE ps.parent='{sw.name}' AND ps.work != "Supply Only") as po_qty,
				(SELECT sum(ds.delivered_stock_qty + ds.returned_stock_qty) FROM `tabDelivery Status` as ds WHERE ds.parent='{sw.name}') as total_delivery,
				(SELECT sum(ds.delivered_bundle + ds.returned_bundle) FROM `tabDelivery Status` as ds WHERE ds.parent='{sw.name}') as bundle_delivery,
				{laying_query}
				(
					IFNULL((SELECT sum(ds.delivered_stock_qty + ds.returned_stock_qty) FROM `tabDelivery Status` as ds WHERE ds.parent='{sw.name}'), 0)
					- IFNULL((SELECT sum(jw.sqft_allocated) FROM `tabTS Job Worker Details` as jw WHERE jw.parent='{sw.name}' {jw_filter}), 0)
				) as site_stock,
				(
					IFNULL((SELECT sum(ds.delivered_bundle + ds.returned_bundle) FROM `tabDelivery Status` as ds WHERE ds.parent='{sw.name}'), 0)
					- IFNULL((SELECT sum(jw.completed_bundle) FROM `tabTS Job Worker Details` as jw WHERE jw.parent='{sw.name}' {jw_filter}), 0)
				) as bundle_site_stock,
				null as raw_material_fixed,
				null as raw_material_delivered
			FROM `tabProject` as sw
			WHERE sw.name='{sw.name}'
			{supply_only_filter}
			{working_status}
		""", as_dict=1)

		raw_material=frappe.db.sql(f"""
			SELECT 
				rw.item as raw_material
				, rw.qty as raw_material_fixed
				, (rw.delivered_quantity + rw.returned_quantity) as raw_material_delivered 
			FROM `tabRaw Materials` as rw 
			WHERE rw.parent='{sw.name}'
			AND rw.customer_scope = {filters.get("customer_scope", 0)} 
			AND rw.rate_inclusive = {filters.get("rate_inclusive", 0)}
		""", as_dict=1)
		if not raw_material and (filters.get("customer_scope", 0) or filters.get("rate_inclusive", 0)):
			continue

		if raw_material and site_data:
			for rm_idx in range(0, len(raw_material), 1):
				if rm_idx==0:
					site_data[0].update(raw_material[0])
				else:
					site_data.append(raw_material[rm_idx])
		if site_data:
			data += site_data or []

	columns=get_columns(filters)
	return columns,data
	

def get_columns(filters):

	columns = [
		{
			"label": ("Site Name"),
			"fieldtype": "Link",
			"fieldname": "site_name",
			"options":"Project",
			"width": 350
		},
		{
			"label": ("Design"),
			"fieldtype": "Data",
			"fieldname": "design",
			"width": 380
		},
		{
			"label": ("PO Qty"),
			"fieldtype": "Float",
			"fieldname": "po_qty",
			"width": 110
		},
		{
			"label": ("Total Delivery"),
			"fieldtype": "Float",
			"fieldname": "total_delivery",
			"width": 100
		},
		{
			"label": ("Total Laying"),
			"fieldtype": "Float",
			"fieldname": "total_laying",
			"width": 100
		},
		{
			"label": f"""Total Laying @ {frappe.utils.formatdate(filters.get("from_date", ""))} { f''' to {frappe.utils.formatdate(filters.get("to_date", ""))}''' if filters.get("to_date") else ""}""",
			"fieldtype": "Float",
			"fieldname": "total_laying_date",
			"hidden": not (filters.get("from_date") or filters.get("to_date")),
			"width": 100
		},
		{
		    "label": ("Stock @Site"),
		    "fieldtype": "Float",
		    "fieldname": "site_stock",
		    "width": 100
		},
		{
			"label": ("Bndl Del"),
			"fieldtype": "Float",
			"fieldname": "bundle_delivery",
			"width": 100
		},
		{
			"label": ("Bndl Laying"),
			"fieldtype": "Float",
			"fieldname": "bundle_laying",
			"width": 100
		},
		{
			"label": f"""Bndl Laying @ {frappe.utils.formatdate(filters.get("from_date", ""))} { f''' to {frappe.utils.formatdate(filters.get("to_date", ""))}''' if filters.get("to_date") else ""}""",
			"fieldtype": "Float",
			"fieldname": "bundle_laying_date",
			"hidden": not (filters.get("from_date") or filters.get("to_date")),
			"hidden": not filters.get("date"),
			"hidden": not (filters.get("from_date") or filters.get("to_date")),
			"width": 100
		},
		{
		    "label": ("Bndl Stock @Site"),
		    "fieldtype": "Float",
		    "fieldname": "bundle_site_stock",
		    "width": 100
		},
		{
			"label": ("Raw Material"),
			"fieldtype": "Data",
			"fieldname": "raw_material",
			"width": 150
		},
		{
			"label": ("Fixed Raw Material"),
			"fieldtype": "Float",
			"fieldname": "raw_material_fixed",
			"width": 100
		},
		{
			"label": ("Delivered Raw Material"),
			"fieldtype": "Float",
			"fieldname": "raw_material_delivered",
			"width": 100
		},
	]
	return columns
