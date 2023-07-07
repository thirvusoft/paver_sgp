# Copyright (c) 2023, Thirvusoft and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ItemSizeRate(Document):
	pass

def get_item_size_price(item_size, posting_date):
	args={
		'item_size': item_size,
		'posting_date': posting_date
       }
	conditions = """where item_size=%(item_size)s"""

	if args.get('posting_date'):
		conditions += """ and %(posting_date)s between
			ifnull(valid_from, '2000-01-01') and ifnull(valid_upto, '2500-12-31')"""

	return frappe.db.sql(""" select name, rate
		from `tabItem Size Rate` {conditions}
		order by valid_from desc """.format(conditions=conditions), args)