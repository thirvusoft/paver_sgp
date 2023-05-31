# Copyright (c) 2023, Thirvusoft and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	columns, data = get_columns(filters), get_data(filters)
	return columns, data

def get_data(filters):
	conditions = ""
	operator_conditions = ""
	if filters.get("item_code"):
		conditions += f""" and sbi.item_name = '{filters.get("item_code")}' """
		operator_conditions += f"""  and opr_sbi.item_name = '{filters.get("item_code")}' """

	if filters.get("material_manufacturing"):
		conditions += f""" and sbi.material_manufacturing = '{filters.get("material_manufacturing")}' """
		operator_conditions += f""" and opr_sbi.material_manufacturing = '{filters.get("material_manufacturing")}' """

	if filters.get("from_date"):
		conditions += f""" and DATE(sbc.to_time) >= '{filters.get("from_date")}' """
		operator_conditions += f""" and DATE(opr_sbc.to_time) >= '{filters.get("from_date")}' """

	if filters.get("to_date"):
		conditions += f""" and DATE(sbc.to_time) <= '{filters.get("to_date")}' """
		operator_conditions += f""" and DATE(opr_sbc.to_time) <= '{filters.get("to_date")}' """

	query = f"""
		SELECT
			DATE(sbc.to_time) as date,
			sbi.item_name as item_code,
			SUM(sbi.bundle_taken) as bundle_taken,
			SUM(sbi.sqft - sbi.damages_in_sqft) as sqft,
			SUM(sbi.damages_in_nos) as damages_in_nos,
			SUM(sbi.damages_in_sqft) as damages_in_sqft,
			SUM(sbi.damages_in_sqft) * 100 / SUM(sbi.sqft) as damage_percent,
			SUM(sbi.damage_cost) as damage_cost,
			SUM(sbc.no_of_labour * (sbi.sqft / sbc.total_sqft)) as no_of_labour,
			SUM(sbc.total_hrs * (sbi.sqft / sbc.total_sqft)) as total_hrs,
			SUM(sbc.labour_cost * (sbi.sqft / sbc.total_sqft)) as labour_cost,
			(
				SELECT 
					GROUP_CONCAT(DISTINCT opr.operator_name SEPARATOR ', ') 
                FROM `tabCW Operator Details` opr
				WHERE 
					opr.parenttype = "Shot Blast Costing" and
					opr.parent in (
						SELECT 
							opr_sbc.name
						FROM `tabShot Blast Items` opr_sbi
						INNER JOIN `tabShot Blast Costing` opr_sbc
						ON opr_sbi.parent = opr_sbc.name
						WHERE
							opr_sbc.docstatus != 2 and
							DATE(opr_sbc.to_time) = DATE(sbc.to_time) and
							opr_sbi.item_name = sbi.item_name
							{operator_conditions}
					)
			) as operator,
			SUM(sbc.total_operator_wages * (sbi.sqft / sbc.total_sqft)) as operator_salary,
			SUM(sbc.additional_cost * (sbi.sqft / sbc.total_sqft)) as additional_cost,
			SUM(sbc.total_cost * (sbi.sqft / sbc.total_sqft)) as total_cost
		FROM `tabShot Blast Items` sbi
		INNER JOIN `tabShot Blast Costing` sbc
		ON sbi.parent = sbc.name
		WHERE
			sbc.docstatus != 2
			{conditions}
		GROUP BY {"DATE(sbc.to_time), sbi.item_name" if filters.get("group_by") == "Date" else "sbi.item_name, DATE(sbc.to_time)"}
	"""

	data = frappe.db.sql(query, as_dict=True)
	try:
		return add_group_total(data, "date" if filters.get("group_by") == "Date" else "item_code")
	except:
		frappe.log_error("SHOT BLAST COSTING REPORT", frappe.get_traceback())
		return data

def add_group_total(data, group_by, gt_column = "item_code"):
	res = []
	current_group = data[0].get(group_by) if data else False
	group=[]
	group_total = {}
	total = {}

	for row in data:
		if group and row.get(group_by) != current_group:
			res += group
			group_total[gt_column] = "Group Total"
			group_total["damage_percent"] = sum(group_total.get("damage_percent") or []) / (len(group_total.get("damage_percent") or []) or 1)
			res.append(group_total)
			res.append({})
			group=[]
			group_total = {} 
			current_group = row.get(group_by)

		group.append(row)
		for col in row:
			if col=="damage_percent":
				if row[col]:
					group_total[col] = (group_total.get(col) or []) + [row[col] or 0]
					total[col] = (total.get(col) or []) + [row[col] or 0]
					
			elif (col not in group_total and (isinstance(row[col], int) or isinstance(row[col], float))):
				group_total[col] = (group_total.get(col) or 0) + row[col]
				total[col] = (total.get(col) or 0) + row[col]
				
			elif (isinstance(row[col], int) or isinstance(row[col], float)):
				group_total[col] = (group_total.get(col) or 0) + row[col]
				total[col] = (total.get(col) or 0) + row[col]

	if group:
		res += group
		group_total[gt_column] = "Group Total"
		group_total["damage_percent"] = sum(group_total.get("damage_percent") or []) / (len(group_total.get("damage_percent") or []) or 1)
		res.append(group_total)
		group=[]
		group_total = {} 
		current_group = row.get(group_by)
	
	if res:
		total[gt_column] = "Total"
		total["damage_percent"] = sum(total.get("damage_percent") or []) / (len(total.get("damage_percent") or []) or 1)
		res.append(total)

	return res

def get_columns(filters):
	columns = [
		{
			"fieldname": "date",
			"label": "Date",
			"fieldtype": "Date",
			"width": 100,
		},
		{
			"fieldname": "item_code",
			"label": "Item Code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 300,
		},
		{
			"fieldname": "bundle_taken",
			"label": "Taken Bundle",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"fieldname": "sqft",
			"label": "SQFT",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"fieldname": "damages_in_nos",
			"label": "Damage Nos",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"fieldname": "damages_in_sqft",
			"label": "Damage Sqft",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"fieldname": "damage_percent",
			"label": "Damage Percent",
			"fieldtype": "Percent",
			"width": 100,
		},
		{
			"fieldname": "damage_cost",
			"label": "Damage Cost",
			"fieldtype": "Currency",
			"width": 100,
		},
		{
			"fieldname": "no_of_labour",
			"label": "No of Labours",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"fieldname": "total_hrs",
			"label": "Total Working Hour",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"fieldname": "labour_cost",
			"label": "Labour Salary",
			"fieldtype": "Currency",
			"width": 100,
		},
		{
			"fieldname": "operator",
			"label": "Operator",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 100,
		},
		{
			"fieldname": "operator_salary",
			"label": "Operator Salary",
			"fieldtype": "Currency",
			"width": 100,
		},
		{
			"fieldname": "additional_cost",
			"label": "Additional Cost",
			"fieldtype": "Currency",
			"width": 100,
		},
		{
			"fieldname": "total_cost",
			"label": "Total Cost",
			"fieldtype": "Currency",
			"width": 100,
		}
	]

	return columns
