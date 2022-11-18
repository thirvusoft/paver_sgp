# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	columns = get_columns()

	from_date = filters.get("from_date")
	to_date = filters.get("to_date")

	doc = frappe.get_all("CW Manufacturing", {"molding_date":["between", (from_date, to_date)],"type":["!=","Fencing Post"],"production_sqft":["!=",0],"docstatus":["!=",2]}, order_by = 'molding_date')
	
	data = []
	final_data = []

	if doc:
		for doc_name in doc:		
			doc_details = frappe.get_doc("CW Manufacturing",doc_name.name)
			
			if not data:
				for material in doc_details.item_details:
					
					matched_item  = 0

					for item in	data:

						if item["item"] == material.item and item["month"] == doc_details.molding_date.strftime("%B"):
							matched_item  = 1
							item["production_sqft"] += material.production_sqft
							item["production_cost"] += doc_details.raw_material_cost / doc_details.production_sqft
							item["expense"] += doc_details.total_cost_per_sqft - (doc_details.raw_material_cost / doc_details.production_sqft)
							item["total_cost_per_sqft"] += doc_details.total_cost_per_sqft
							item["total_item_count"] += 1

					if not matched_item:
						
						data.append({
						"month":doc_details.molding_date.strftime("%B"),
						"item":material.item,
						"production_sqft":material.production_sqft,
						"days":None,
						"production_cost":doc_details.raw_material_cost / doc_details.production_sqft,
						"expense":doc_details.total_cost_per_sqft - (doc_details.raw_material_cost / doc_details.production_sqft),
						"total_cost_per_sqft":doc_details.total_cost_per_sqft,
						"total_item_count":1
					})

			else:

				for material in doc_details.item_details:
					matched_item  = 0

					for item in	data:

						if item["item"] == material.item and item["month"] == doc_details.molding_date.strftime("%B"):
							matched_item  = 1
							item["production_sqft"] += material.production_sqft
							item["production_cost"] += doc_details.raw_material_cost / doc_details.production_sqft
							item["expense"] += doc_details.total_cost_per_sqft - (doc_details.raw_material_cost / doc_details.production_sqft)
							item["total_cost_per_sqft"] += doc_details.total_cost_per_sqft
							item["total_item_count"] += 1

					if not matched_item:
						
						data.append({
						"month":doc_details.molding_date.strftime("%B"),
						"item":material.item,
						"production_sqft":material.production_sqft,
						"days":None,
						"production_cost":doc_details.raw_material_cost / doc_details.production_sqft,
						"expense":doc_details.total_cost_per_sqft - (doc_details.raw_material_cost / doc_details.production_sqft),
						"total_cost_per_sqft":doc_details.total_cost_per_sqft,
						"total_item_count":1
					})

		for row in data:
			
			row["production_cost"] = row["production_cost"] / row["total_item_count"]
			row["expense"] = row["expense"] / row["total_item_count"]
			row["total_cost_per_sqft"] = row["total_cost_per_sqft"] / row["total_item_count"]
			
			final_data.append(list(row.values()))

	return columns, final_data

def get_columns():

	columns = [
		_("Month") + ":Data:100",
		_("Item") + ":Link/Item:250",
		_("Sqft") + ":Float:100",
		{
			"fieldname":"no_of_days",
			"label":"No Of Days",
			"width":100,
			"hidden":1,
			"fieldtype":"Int"
		},
		_("Prod Cost") + ":Currency:100",
		_("Expense Cost") + ":Currency:150",
		_("Total Cost") + ":Currency:100"
	]

	return columns