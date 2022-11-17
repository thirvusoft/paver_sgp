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
		
		data.append({
			"material": "-",
			"qty": "-",
			"consumption": "-",
			"uom": "-",
			"rate": "-",
			"amount": "-",
			"cost_per_sqft": "-"
		})	

		data.append({
			"material": None,
			"qty": None,
			"consumption": None,
			"uom": None,
			"rate": None,
			"amount": None,
			"cost_per_sqft": None
		})	

		for doc_name in doc:
			
			doc_details = frappe.get_doc("CW Manufacturing",doc_name.name)
			
			if doc_details.production_sqft:

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

							data.append({
								"material": material.item_code,
								"qty": material.qty,
								"consumption": 0,
								"uom": material.uom,
								"rate": material.rate,
								"amount": 0,
								"cost_per_sqft": 0
							})

				else:
					for material in doc_details.items:
						matched_item  = 0

						for item in	data:
							if item["material"] == material.item_code:

								matched_item = 1
								item["qty"] += material.qty
								item["rate"] += material.rate

						if not matched_item:
							data.append({
								"material": material.item_code,
								"qty": material.qty,
								"consumption": 0,
								"uom": material.uom,
								"rate": material.rate,
								"amount": 0,
								"cost_per_sqft": 0
							})

		idx = 0
		for row in	data:
			
			if row["qty"] != "-" and row["qty"]:
				row["consumption"] = round(row["qty"] / total_production_sqft, 3)
				row["rate"] = round(row["rate"] / len(doc), 2)
				row["amount"] = round(row["qty"] * row["rate"], 2)
				row["cost_per_sqft"] = round(row["amount"] / total_production_sqft, 2)
				report_total_cost_per_sqft += row["cost_per_sqft"]
			else:
				if idx == 0:
					idx = 1
					row["consumption"] = f"<b>SQFT : {round(total_production_sqft,3)}</b>"
					row["uom"] = f"<b>Production Cost per SQFT : {round(total_cost_per_sqft / len(doc),3)}</b>"
					row["rate"] = f"<b>No of Days : </b>"

		data.append({
			"material": None,
			"qty": None,
			"consumption": None,
			"uom": None,
			"rate": "<b>Total Production Cost</b>",
			"amount": f"<b>{round(total_production_cost, 2)}</b>",
			"cost_per_sqft": f"<b>{round(report_total_cost_per_sqft, 2)}</b>"
		})
		total_cost += report_total_cost_per_sqft
		
		data.append({
			"material": None,
			"qty": None,
			"consumption": None,
			"uom": None,
			"rate": None,
			"amount": "<b>Labour Cost Per Sqft</b>",
			"cost_per_sqft": f"<b>{round((labour_cost_per_sqft / len(doc)), 2)}</b>"
		})
		total_cost += labour_cost_per_sqft / len(doc)

		data.append({
			"material": None,
			"qty": None,
			"consumption": None,
			"uom": None,
			"rate": None,
			"amount": "<b>Operator Cost Per Sqft</b>",
			"cost_per_sqft": f"<b>{round((operator_cost_per_sqft / len(doc)), 2)}</b>"
		})
		total_cost += operator_cost_per_sqft / len(doc)

		data.append({
			"material": None,
			"qty": None,
			"consumption": None,
			"uom": None,
			"rate": None,
			"amount": "<b>Strapping Cost Per Sqft</b>",
			"cost_per_sqft": f"<b>{round((strapping_cost_per_sqft / len(doc)), 2)}</b>"
		})
		total_cost += strapping_cost_per_sqft / len(doc)

		data.append({
			"material": None,
			"qty": None,
			"consumption": None,
			"uom": None,
			"rate": None,
			"amount": "<b>Additional Cost Per Sqft</b>",
			"cost_per_sqft": f"<b>{round((additional_cost_per_sqft / len(doc)), 2)}</b>"
		})
		total_cost += additional_cost_per_sqft / len(doc)

		data.append({
			"material": None,
			"qty": None,
			"consumption": None,
			"uom": None,
			"rate": None,
			"amount": "<b>Raw Material Cost Per Sqft</b>",
			"cost_per_sqft": f"<b>{round((raw_material_cost_per_sqft / len(doc)), 2)}</b>"
		})
		total_cost += raw_material_cost_per_sqft / len(doc)

		data.append({
			"material": None,
			"qty": None,
			"consumption": None,
			"uom": None,
			"rate": None,
			"amount": "<b>Total Cost</b>",
			"cost_per_sqft": f"<b>{round(total_cost, 2)}</b>"
		})

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
	