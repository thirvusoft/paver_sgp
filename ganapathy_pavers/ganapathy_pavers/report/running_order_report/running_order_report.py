# Copyright (c) 2023, Thirvusoft and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	customer = filters.get("customer")
	sitework= filters.get("site_name")
	_type=filters.get("type")
	status=filters.get("status")
	
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
	
	sw_list=frappe.get_all("Project", filters=sw_filters)
	
	table_name='tabPavers' if _type=="Pavers" else 'tabCompound Wall'
	field_name='required_area' if _type=="Pavers" else 'allocated_ft'
	
	jw_filter=""

	if not filters.get("include_other_works"):
		jw_filter=""" AND jw.other_work=0"""

	working_status=""
	if filters.get("working_status") == "No Delivery":
		working_status += f"""  and (SELECT sum(ds1.delivered_stock_qty + ds1.returned_stock_qty)  FROM `tabDelivery Status` as ds1 WHERE ds1.parent=sw.name)=0"""
	elif filters.get("working_status") == "Delivery Started & No Laying":
		working_status += f"""  and (SELECT sum(ds1.delivered_stock_qty + ds1.returned_stock_qty)  FROM `tabDelivery Status` as ds1 WHERE ds1.parent=sw.name)>0 AND sw.total_layed_sqft=0"""
	elif filters.get("working_status") == "Delivery & Laying Started":
		working_status += f"""  and (SELECT sum(ds1.delivered_stock_qty + ds1.returned_stock_qty)  FROM `tabDelivery Status` as ds1 WHERE ds1.parent=sw.name)>0 AND sw.total_layed_sqft>0"""

	for sw in sw_list:		
		site_data=frappe.db.sql(f"""
			SELECT 
				sw.name as site_name,
				(
				SELECT 
					GROUP_CONCAT(
					IF(
						parent='{sw.name}'
						, item
						, NULL
					) 
					SEPARATOR ', '
					) 
				FROM `{table_name}`
				) as design,
				(SELECT sum(ps.{field_name}) FROM `{table_name}` as ps WHERE ps.parent='{sw.name}') as po_qty,
				(SELECT sum(ds.delivered_stock_qty + ds.returned_stock_qty) FROM `tabDelivery Status` as ds WHERE ds.parent='{sw.name}') as total_paver_delivery,
				(SELECT sum(jw.sqft_allocated) FROM `tabTS Job Worker Details` as jw WHERE jw.parent='{sw.name}' {jw_filter}) as total_laying,
				(
					(SELECT sum(ds.delivered_stock_qty + ds.returned_stock_qty) FROM `tabDelivery Status` as ds WHERE ds.parent='{sw.name}')
					- (SELECT sum(jw.sqft_allocated) FROM `tabTS Job Worker Details` as jw WHERE jw.parent='{sw.name}' {jw_filter})
				) as paver_stock_site 
			FROM `tabProject` as sw
			WHERE sw.name='{sw.name}'
			{working_status}
		""", as_dict=1)
		print(site_data)
		raw_material=frappe.db.sql(f"""
			SELECT 
				rw.item as raw_material
				, rw.qty as raw_material_fixed
				, (rw.delivered_quantity + rw.returned_quantity) as raw_material_delivered 
			FROM `tabRaw Materials` as rw 
			WHERE rw.parent='{sw.name}'
		""", as_dict=1)

		if raw_material and site_data:
			for rm_idx in range(0, len(raw_material), 1):
				if rm_idx==0:
					site_data[0].update(raw_material[0])
				else:
					site_data.append(raw_material[rm_idx])
		if site_data:
			data += site_data or []

	columns=get_columns()
	return columns,data
	

def get_columns():

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
			"label": ("Total Paver Delivery"),
			"fieldtype": "Float",
			"fieldname": "total_paver_delivery",
			"width": 150
		},
		{
			"label": ("Raw Material"),
			"fieldtype": "Data",
			"fieldname": "raw_material",
			"width": 150
		},
		{
			"label": ("Raw Material Fixed"),
			"fieldtype": "Data",
			"fieldname": "raw_material_fixed",
			"width": 150
		},
		{
			"label": ("Raw Material Delivered"),
			"fieldtype": "Data",
			"fieldname": "raw_material_delivered",
			"width": 170
		},
		{
			"label": ("Total Laying"),
			"fieldtype": "Data",
			"fieldname": "total_laying",
			"width": 100
		},
		{
		    "label": ("Paver Stock @Site"),
		    "fieldtype": "Data",
		    "fieldname": "paver_stock_site",
		    "width": 100
		},
	]
	return columns
