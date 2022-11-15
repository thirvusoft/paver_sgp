# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import pandas as pd

def execute(filters=None):
	columns = get_columns()

	from_date = filters.get("from_date")
	to_date = filters.get("to_date")

	doc = frappe.get_all("CW Manufacturing", {"molding_date":["between", (from_date, to_date)],"type":["!=","Fencing Post"],"production_sqft":["!=",0],"docstatus":["!=",2]}, order_by = 'molding_date')
	
	data = []
	
	if doc:
		for doc_name in doc:		
			doc_details = frappe.get_doc("CW Manufacturing",doc_name.name)
			
			if not data:
				for material in doc_details.item_details:

					sub_list = []
					sub_list.append(doc_details.molding_date.strftime("%B")),
					sub_list.append(material.item)
					sub_list.append(material.production_sqft)
					sub_list.append(None)
					sub_list.append(doc_details.raw_material_cost / doc_details.production_sqft)
					sub_list.append(doc_details.total_cost_per_sqft - (doc_details.raw_material_cost / doc_details.production_sqft))
					sub_list.append(doc_details.total_cost_per_sqft)
					sub_list.append(1)
					data.append(sub_list)

			else:

				for material in doc_details.item_details:
					matched_item  = 0

					for item in	data:
						
						if item[1] == material.item and item[0] == doc_details.molding_date.strftime("%B"):
							matched_item  = 1
							item[2] += material.production_sqft
							item[4] += doc_details.raw_material_cost / doc_details.production_sqft
							item[5] += doc_details.total_cost_per_sqft - (doc_details.raw_material_cost / doc_details.production_sqft)
							item[6] += doc_details.total_cost_per_sqft
							item[7] += 1

					if not matched_item:
						
						sub_list = []
						sub_list.append(doc_details.molding_date.strftime("%B")),
						sub_list.append(material.item)
						sub_list.append(material.production_sqft)
						sub_list.append(None)
						sub_list.append(doc_details.raw_material_cost / doc_details.production_sqft)
						sub_list.append(doc_details.total_cost_per_sqft - (doc_details.raw_material_cost / doc_details.production_sqft))
						sub_list.append(doc_details.total_cost_per_sqft)
						sub_list.append(1)
						data.append(sub_list)

		for row in data:
			row[4] = row[4] / row[7]
			row[5] = row[5] / row[7]
			row[6] = row[6] / row[7]

	return columns, data

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