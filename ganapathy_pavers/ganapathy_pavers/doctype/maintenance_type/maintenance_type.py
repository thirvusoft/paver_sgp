# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Maintenancetype(Document):
	def validate(self):
		if self.expense_calculation_per_vehicle_log and self.expense_calculation_per_km:
			frappe.throw(f"You can't choose both calculations for <b>{self.name}</b>")
		if not self.expense_calculation_per_km:
			self.vehicle_log_purpose_per_km=[]
		if not self.expense_calculation_per_vehicle_log:
			self.vehicle_log_purpose_per_log=[]

	def on_update(self):
		frappe.db.sql(f"""
			UPDATE `tabMaintenance Details`
			SET expense_calculation_per_km = {self.expense_calculation_per_km or 0}
			WHERE maintenance='{self.name}'
		""")
		frappe.db.sql(f"""
			UPDATE `tabMaintenance Details`
			SET expense_calculation_per_vehicle_log = {self.expense_calculation_per_vehicle_log or 0}
			WHERE maintenance='{self.name}'
		""")
		per_log_str=frappe.db.sql(f"""
			SELECT 
				GROUP_CONCAT(
					IF(
						parent='{self.name}' and parentfield="vehicle_log_purpose_per_log"
						, select_purpose
						, NULL
					) 
					SEPARATOR ', '
				) 
			FROM `tabVehicle Log Purpose`;
		""")
		frappe.db.sql(f"""
			UPDATE `tabMaintenance Details`
			SET vehicle_log_purpose_per_log = '{per_log_str[0][0] or ""}'
			WHERE maintenance='{self.name}'
		""")


		frappe.db.sql(f"""
			UPDATE `tabMaintenance Details`
			SET default_expense_account = '{self.expense_account or ""}'
			WHERE maintenance='{self.name}'
		""")
		per_km_str=frappe.db.sql(f"""
			SELECT 
				GROUP_CONCAT(
					IF(
						parent='{self.name}' and parentfield="vehicle_log_purpose_per_km"
						, select_purpose
						, NULL
					) 
					SEPARATOR ', '
				) 
			FROM `tabVehicle Log Purpose`;
		""")
		frappe.db.sql(f"""
			UPDATE `tabMaintenance Details`
			SET vehicle_log_purpose_per_km = '{per_km_str[0][0] or ""}'
			WHERE maintenance='{self.name}'
		""")


def update_select_purpose(self, event=None):
	for maintenance in list(set([i.maintenance for i in self.maintanence_details_])):
		if maintenance:
			doc=frappe.get_doc("Maintenance type", maintenance)
			doc.on_update()