# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry

class EmployeeBonus(Document):
	def on_submit(self):

			payment_doc=frappe.new_doc('Payment Entry')
			payment_doc.payment_type = 'Pay'
			payment_doc.party_type = 'Employee'
			payment_doc.party = self.employee
			company = frappe.get_doc('Company',self.company)
			abbr=company.abbr
			payment_doc.posting_date=self.bonus_payment_date
			payment_doc.paid_amount=self.bonus_amount
			payment_doc.received_amount=self.bonus_amount
			payment_doc.source_exchange_rate=1.0
			payment_doc.paid_from='Cash - '+abbr
			payment_doc.paid_from_account_currency=company.default_currency
			payment_doc.paid_to = 'Creditors - '+abbr
			payment_doc.submit()
