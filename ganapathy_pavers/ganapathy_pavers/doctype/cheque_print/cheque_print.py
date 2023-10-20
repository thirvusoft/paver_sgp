# Copyright (c) 2023, Thirvusoft and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import money_in_words, get_defaults
from frappe.model.document import Document

class ChequePrint(Document):
	pass

@frappe.whitelist()
def aount_in_words(amount = 0):
	money = money_in_words(amount)
	d = get_defaults()
	currency = d.get('currency', 'INR')
	if money.find(f"{currency} ") == 0:
		money = money.replace(f"{currency} ", "", 1)
	
	return money
