# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):

	columns = get_columns()

	from_date = filters.get("from_date")
	to_date = filters.get("to_date")

	doc = frappe.get_all("CW Manufacturing",{"molding_date":["between", (from_date, to_date)],"type":"Fencing Post","production_sqft":["!=",0],"docstatus":["!=",2]})
	
	data = []
	
	if doc:

		total_production_sqft = 0
		total_cost_per_sqft = 0
		labour_cost_per_sqft = 0
		operator_cost_per_sqft = 0
		strapping_cost_per_sqft = 0
		additional_cost_per_sqft = 0
		raw_material_cost_per_sqft = 0
		total_production_cost = 0
		report_total_cost_per_sqft = 0
		total_cost = 0

		sub_list = []
		sub_list.append("-")
		sub_list.append("-")
		sub_list.append("-")
		sub_list.append("-")
		sub_list.append("-")
		sub_list.append("-")
		sub_list.append("-")
		data.append(sub_list)

		sub_list = []
		sub_list.append(None)
		sub_list.append(None)
		sub_list.append(None)
		sub_list.append(None)
		sub_list.append(None)
		sub_list.append(None)
		sub_list.append(None)
		data.append(sub_list)

		for doc_name in doc:
			
			doc_details = frappe.get_doc("CW Manufacturing",doc_name.name)

			total_production_sqft += doc_details.production_sqft
			total_cost_per_sqft += doc_details.total_cost_per_sqft
			labour_cost_per_sqft += doc_details.labour_cost_per_sqft
			operator_cost_per_sqft += doc_details.operator_cost_per_sqft
			strapping_cost_per_sqft += doc_details.strapping_cost_per_sqft
			additional_cost_per_sqft += doc_details.additional_cost_per_sqft
			raw_material_cost_per_sqft += doc_details.raw_material_cost_per_sqft
			total_production_cost += doc_details.total_expence
			total_production_cost += doc_details.total_expense_for_unmolding
			total_production_cost += doc_details.labour_expense_for_curing

			if not data:

				for material in doc_details.items:

						sub_list = []
						
						sub_list.append(material.item_code)
						sub_list.append(round(material.qty, 2)),
						sub_list.append(0)
						sub_list.append(material.uom)
						sub_list.append(round(material.rate, 3))
						sub_list.append(0)
						sub_list.append(0)
						data.append(sub_list) 

			else:

				for material in doc_details.items:

					matched_item  = 0

					for item in	data:

						if item[0] == material.item_code:

							matched_item = 1
							item[1] += round(material.qty, 2)
							item[4] += round(material.rate, 3)

					if not matched_item:
						
						sub_list = []
						sub_list.append(material.item_code)
						sub_list.append(round(material.qty, 2))
						sub_list.append(0)
						sub_list.append(material.uom)
						sub_list.append(round(material.rate, 3))
						sub_list.append(0)
						sub_list.append(0)
						data.append(sub_list) 
		idx = 0
		for row in	data:
			if row[1] != "-" and row[1]:
				row[2] = round(row[1] / total_production_sqft, 3)
				row[4] = round(row[4] / len(doc), 2)
				row[5] = round(row[1] * row[4], 2)
				row[6] = round(row[5] / total_production_sqft, 2)
				report_total_cost_per_sqft += row[6]
			else:
				if idx == 0:
					idx = 1
					row[2] = f"<b>SQFT : {round(total_production_sqft,3)}</b>"
					row[3] = f"<b>Production Cost per SQFT : {round(total_cost_per_sqft / len(doc),3)}</b>"
					row[4] = f"<b>No of Days : </b>"
		
		sub_list = []
		sub_list.append(None)
		sub_list.append(None)
		sub_list.append(None)
		sub_list.append(None)
		sub_list.append("<b>Total Production Cost</b>")
		sub_list.append(f"<b>{round(total_production_cost, 2)}</b>")
		sub_list.append(f"<b>{round(report_total_cost_per_sqft, 2)}</b>")
		data.append(sub_list)
		total_cost += report_total_cost_per_sqft
		
		sub_list = []
		sub_list.append(None)
		sub_list.append(None)
		sub_list.append(None)
		sub_list.append(None)
		sub_list.append(None)
		sub_list.append("<b>Labour Cost Per Sqft</b>")
		sub_list.append(f"<b>{round((labour_cost_per_sqft / len(doc)), 2)}</b>")
		data.append(sub_list)
		total_cost += labour_cost_per_sqft / len(doc)

		sub_list = []
		sub_list.append(None)
		sub_list.append(None)
		sub_list.append(None)
		sub_list.append(None)
		sub_list.append(None)
		sub_list.append("<b>Operator Cost Per Sqft</b>")
		sub_list.append(f"<b>{round((operator_cost_per_sqft / len(doc)), 2)}</b>")
		data.append(sub_list)
		total_cost += operator_cost_per_sqft / len(doc)

		sub_list = []
		sub_list.append(None)
		sub_list.append(None)
		sub_list.append(None)
		sub_list.append(None)
		sub_list.append(None)
		sub_list.append("<b>Strapping Cost Per Sqft</b>")
		sub_list.append(f"<b>{round((strapping_cost_per_sqft / len(doc)), 2)}</b>")
		data.append(sub_list)
		total_cost += strapping_cost_per_sqft / len(doc)

		sub_list = []
		sub_list.append(None)
		sub_list.append(None)
		sub_list.append(None)
		sub_list.append(None)
		sub_list.append(None)
		sub_list.append("<b>Additional Cost Per Sqft</b>")
		sub_list.append(f"<b>{round((additional_cost_per_sqft / len(doc)), 2)}</b>")
		data.append(sub_list)
		total_cost += additional_cost_per_sqft / len(doc)

		sub_list = []
		sub_list.append(None)
		sub_list.append(None)
		sub_list.append(None)
		sub_list.append(None)
		sub_list.append(None)
		sub_list.append("<b>Raw Material Cost Per Sqft</b>")
		sub_list.append(f"<b>{round((raw_material_cost_per_sqft / len(doc)), 2)}</b>")
		data.append(sub_list)
		total_cost += raw_material_cost_per_sqft / len(doc)

		sub_list = []
		sub_list.append(None)
		sub_list.append(None)
		sub_list.append(None)
		sub_list.append(None)
		sub_list.append(None)
		sub_list.append("<b>Total Cost</b>")
		sub_list.append(f"<b>{round(total_cost, 2)}</b>")
		data.append(sub_list)

	return columns, data

def get_columns():

	columns = [
		_("Material") + ":Link/Item:250",
		_("Qty") + ":Data:80",
		_("Consumption") + ":Data:120",
		_("UOM") + ":Link/UOM:250",
		_("Rate") + ":Data:170",
		_("Amount") + ":Data:200",
		_("Cost Per SQFT") + ":Data:130"
	]

	return columns
	