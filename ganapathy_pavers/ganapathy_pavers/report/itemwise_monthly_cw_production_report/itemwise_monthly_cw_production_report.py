# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from ganapathy_pavers.ganapathy_pavers.doctype.cw_manufacturing.cw_manufacturing import uom_conversion


def execute(filters=None, _type=["Post", "Slab"]):
	columns = get_columns()

	from_date = filters.get("from_date")
	to_date = filters.get("to_date")

	doc = frappe.get_all("CW Manufacturing", {"molding_date":["between", (from_date, to_date)],"type":["in",_type],"production_sqft":["!=",0],"docstatus":["!=",2]}, order_by = 'molding_date')
	days_count = {}
	data = {}

	if doc:
		for doc_name in doc:		
			doc_details = frappe.get_doc("CW Manufacturing",doc_name.name)
			for material in doc_details.item_details:
				
				if(f'{doc_details.molding_date.strftime("%B")}{material.item}.+.+.+.{material.parent}' not in days_count):days_count[f'{doc_details.molding_date.strftime("%B")}{material.item}.+.+.+.{material.parent}'] = 1
				else:days_count[f'{doc_details.molding_date.strftime("%B")}{material.item}.+.+.+.{material.parent}'] += 1
				data_key=f"""{material.item}----{doc_details.molding_date.strftime("%B")}"""
				if data_key not in data:
					data[data_key]={
						"month":doc_details.molding_date.strftime("%B"),
						"item":material.item,
						"production_sqft":material.production_sqft,
						"pieces":0,
						"no_of_days":None,
						"production_cost":((doc_details.raw_material_cost / doc_details.production_sqft) + doc_details.strapping_cost_per_sqft + doc_details.labour_cost_per_sqft_curing),
						"expense":doc_details.total_cost_per_sqft - ((doc_details.raw_material_cost / doc_details.production_sqft) + doc_details.strapping_cost_per_sqft + doc_details.labour_cost_per_sqft_curing),
						"total_cost_per_sqft":doc_details.total_cost_per_sqft,
						"total_item_count":1
					}
				else:
					data[data_key]["production_sqft"] += material.production_sqft
					data[data_key]["production_cost"] += ((doc_details.raw_material_cost / doc_details.production_sqft) + doc_details.strapping_cost_per_sqft + doc_details.labour_cost_per_sqft_curing)
					data[data_key]["expense"] += doc_details.total_cost_per_sqft - ((doc_details.raw_material_cost / doc_details.production_sqft) + doc_details.strapping_cost_per_sqft + doc_details.labour_cost_per_sqft_curing)
					data[data_key]["total_cost_per_sqft"] += doc_details.total_cost_per_sqft
					data[data_key]["total_item_count"] += 1

		data=list(data.values())
		for row in data:
			row['pieces']=uom_conversion(item=row['item'], from_uom="SQF", from_qty=row['production_sqft'], to_uom="Nos")
			row["production_cost"] = row["production_cost"] / row["total_item_count"]
			row["expense"] = row["expense"] / row["total_item_count"]
			row["total_cost_per_sqft"] = row["total_cost_per_sqft"] / row["total_item_count"]
			
	days_count=sorted(days_count, key=lambda x:x)
	key = {i.split('.+.+.+.')[0]:0 for i in days_count}
	for i in days_count:
		key[i.split('.+.+.+.')[0]] += 1
	for i in data:
		i["no_of_days"] = key[i["month"]+i["item"]]
	print(columns)
	print(data)
	return columns, data

def get_columns():

	columns = [
		_("Month") + ":Data:100",
		_("Item") + ":Link/Item:250",
		{
			"fieldname":"production_sqft",
			"label":"Sqft",
			"width":100,
			"fieldtype":"Float"
		},
		_("pieces") + ":Float:100",
		{
			"fieldname":"no_of_days",
			"label":"No Of Days",
			"width":100,
			"fieldtype":"Int"
		},
		{
			"fieldname":"production_cost",
			"label":_("Prod Cost"),
			"width":100,
			"fieldtype":"Currency"
		},
		_("Expense") + ":Currency:150",
		{
			"fieldname":"total_cost_per_sqft",
			"label":_("Total Cost"),
			"width":100,
			"fieldtype":"Currency"
		}
	]

	return columns