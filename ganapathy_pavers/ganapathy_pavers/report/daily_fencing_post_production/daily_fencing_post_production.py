# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from datetime import timedelta
from frappe.utils import getdate,add_days

def execute(filters=None):
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	date_list = date_range_list(getdate(from_date),getdate(to_date))
	data = []
	cw_list = frappe.db.get_list("CW Manufacturing",filters={'molding_date':["between",[from_date,to_date]],'type':["in",["Fencing Post"]]},pluck="name")
	print(cw_list)
	cw_items = []
	if cw_list:
		cw_items = frappe.db.get_list("CW Items",filters={'parent':['in',cw_list]},fields=["item",'sum(produced_qty) as produced_qty','sum(production_sqft) as production_sqft'],group_by="item",order_by="item")
		
		for date in date_list:
			test_data = frappe._dict()
			test_data.update({'date':date})
			produced_qty = frappe.db.sql(""" select child.item as item,sum(child.produced_qty) as produced_qty from `tabCW Manufacturing` as parent left outer join `tabCW Items` as child on child.parent = parent.name  where parent.molding_date = '{0}' group by child.item order by child.item asc""".format(date),as_dict= True)
			for qty in produced_qty:
				test_data.update({
					qty['item']:int(qty['produced_qty'])
				})
			data.append(test_data)
		total_data = ["<b>Total</b>"]
		total_sqft = ["<b>Total SQFT</b>"]
		for qty in cw_items:
			total_data.append(qty['produced_qty'])
			total_sqft.append(qty['production_sqft'])

		data.append(total_data)
		data.append(total_sqft)
	columns = get_columns(cw_items)
	return columns, data
 
def get_columns(cw_items):
	columns = [{
		"fieldtype":"Data",
		"fieldname":"date",
		"label":"<b>Date</b>",
		"width":100
		}]
	for cw_item in cw_items:
		columns.append({
			"fieldtype":"Float",
			"fieldname":cw_item['item'],
			"label":f"<b>{cw_item['item']}</b>",
			"width":200
		})

	return columns


def date_range_list(start_date, end_date):
    # Return list of datetime.date objects between start_date and end_date (inclusive).
    date_list = []
    curr_date = start_date
    while curr_date <= end_date:
        date_list.append(curr_date)
        curr_date += timedelta(days=1)
    return date_list
