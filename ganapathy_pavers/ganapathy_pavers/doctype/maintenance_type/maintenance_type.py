# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Maintenancetype(Document):
	def validate(self):
		frappe.db.sql(f"""
			UPDATE `tabMaintenance Details`
			SET expense_calculation_per_sqft = {self.expense_calculation_per_sqft}
			WHERE maintenance='{self.name}'
		""")
