# Copyright (c) 2023, Thirvusoft and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	customer = filters.get("customer")
	sitework= filters.get("site_name")
	type=filters.get("type")
	status=filters.get("status")
	filters={"type":type,"status":status}
	data=[]
	if customer:
		filters.update({"customer":customer})
	if sitework:
		filters.update({"project_name":sitework})
	

	if type == "Pavers":
		paver_list=frappe.get_all("Project",filters=filters)
	
		for i in paver_list:
	
			paver=frappe.db.sql("""
			select 
				sw.name as site_name,
				(
				SELECT 
					GROUP_CONCAT(
					IF(
						parent='{0}'
						, item
						, NULL
					) 
					SEPARATOR ', '
					) 
				FROM `tabPavers`
				) as paver_design, 
			
				
				(select sum(ps.required_area) from `tabPavers` as ps where ps.parent='{0}') as po_qty,
				(select sum(ds.delivered_stock_qty) from `tabDelivery Status` as ds where ds.parent='{0}') as total_paver_delivery,
				(select sum(jw.sqft_allocated) from `tabTS Job Worker Details` as jw where jw.parent='{0}') as total_lying,
				((select sum(ds.delivered_stock_qty) from `tabDelivery Status` as ds where ds.parent='{0}') - (select sum(jw.sqft_allocated) from `tabTS Job Worker Details` as jw where jw.parent='{0}')) as paver_stock_site 
			from `tabProject` as sw 
			where sw.name='{0}' """.format(i.name),as_dict=1)
			raw_material=frappe.db.sql("""select rw.item as raw_material,rw.qty as raw_material_fixed,rw.delivered_quantity as raw_material_delivered from `tabRaw Materials` as rw where rw.parent='{0}' 
			""".format(i.name),as_dict=1)

			if raw_material:
				for i in range(0,len(raw_material),1):
					if i==0:
						paver[0].update(raw_material[0])
					else:
						paver.append(raw_material[i])

			
			for j in paver:
				
				data.append(j)
	if type == "Compound Wall":
		paver_list=frappe.get_all("Project",filters=filters)
	
		for i in paver_list:
		
			paver=frappe.db.sql("""
			select 
				sw.name as site_name,
				(
				SELECT 
						GROUP_CONCAT(
						IF(
							parent='{0}'
							, item
							, NULL
						) 
						SEPARATOR ', '
						) 
					FROM `tabCompound Wall`
				) as paver_design, 
				(select sum(cw.allocated_ft) from `tabCompound Wall` as cw where cw.parent='{0}') as po_qty,	
				(select sum(ds.delivered_stock_qty) from `tabDelivery Status` as ds where ds.parent='{0}') as total_paver_delivery,
				(select sum(jw.sqft_allocated) from `tabTS Job Worker Details` as jw where jw.parent='{0}') as total_lying,
				((select sum(ds.delivered_stock_qty) from `tabDelivery Status` as ds where ds.parent='{0}') - (select sum(jw.sqft_allocated) from `tabTS Job Worker Details` as jw where jw.parent='{0}')) as paver_stock_site 
			from `tabProject` as sw  where sw.name='{0}' """.format(i.name),as_dict=1)
			raw_material=frappe.db.sql("""select rw.item as raw_material,rw.qty as raw_material_fixed,rw.delivered_quantity as raw_material_delivered from `tabRaw Materials` as rw where rw.parent='{0}' 
			""".format(i.name),as_dict=1)
			if raw_material:
				for i in range(0,len(raw_material),1):
					if i==0:
						paver[0].update(raw_material[0])
					else:
						paver.append(raw_material[i])
			for j in paver:
				data.append(j)

	
	columns=get_columns()
	return columns,data
	
def get_columns():
	
	columns = [
		{
			"label": ("Site Name"),
			"fieldtype": "Link",
			"fieldname": "site_name",
			"options":"Project",
			"width": 380
		},
		{
			"label": ("Paver Design"),
			"fieldtype": "Data",
			"fieldname": "paver_design",
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
			"width": 110
		},
		{
			"label": ("Raw Material"),
			"fieldtype": "Data",
			"fieldname": "raw_material",
			"width": 110
		},
		{
			"label": ("Raw Material Fixed"),
			"fieldtype": "Data",
			"fieldname": "raw_material_fixed",
			"width": 110
		},
		{
			"label": ("Raw Material Delivered"),
			"fieldtype": "Data",
			"fieldname": "raw_material_delivered",
			"width": 120
		},
		{
			"label": ("Total Lying"),
			"fieldtype": "Data",
			"fieldname": "total_lying",
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

