# Copyright (c) 2023, Thirvusoft and contributors
# For license information, please see license.txt

import frappe
from ganapathy_pavers import uom_conversion
from frappe.model.document import Document

class ItemSizeRate(Document):
	pass

def get_item_size_price(item_size, item_code, posting_date, to_uom, filters = {}):
	args={
		'item_size': item_size,
		'posting_date': posting_date
       }
	conditions = """where item_size=%(item_size)s"""

	for field in filters:
		conditions += f""" and {field} = '{filters[field]}' """

	if args.get('posting_date'):
		conditions += """ and %(posting_date)s between
			ifnull(valid_from, '2000-01-01') and ifnull(valid_upto, '2500-12-31')"""

	rates = frappe.db.sql(""" select name, rate, uom
		from `tabItem Size Rate` {conditions}
		order by valid_from desc """.format(conditions=conditions), args, as_list=True)

	for rate in rates:
		if to_uom and item_code and rate[2]:
			rate[1] = uom_conversion(item=item_code, from_uom=to_uom, from_qty=rate[1], to_uom=rate[2])

	return rates
