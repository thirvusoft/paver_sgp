# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Maintenancetype(Document):
	def onload(self):
		self.set_onload("vl_fields", sorted(get_doc_fields("Vehicle Log"), key=lambda x: x.get("parent", "")))

	def validate(self):
		if self.expense_calculation_per_vehicle_log and self.expense_calculation_per_km and self.expense_calculation_per_day and self.expense_calculation_based_on_field:
			frappe.throw(f"You have to choose anyone calculation method for <b>{self.name}</b>")
		if not self.expense_calculation_per_km:
			self.vehicle_log_purpose_per_km=[]
		if not self.expense_calculation_per_vehicle_log:
			self.vehicle_log_purpose_per_log=[]
		if not self.expense_calculation_per_day:
			self.vehicle_log_purpose_per_day=[]
		if not self.expense_calculation_based_on_field:
			self.vl_fieldname=""
			self.vl_doctype=""

	def on_update(self):
		self.update_maintenance_desc()

	def update_maintenance_desc(self):
		frappe.db.sql(f"""
			UPDATE `tabMaintenance Details`
			SET default_expense_account = '{self.expense_account or ""}'
			WHERE maintenance='{self.name}'
		""")
		fields=[
			"expense_calculation_per_km",
			"expense_calculation_per_vehicle_log", 
			"expense_calculation_per_day",
			"expense_calculation_based_on_field"
		]
		for field in fields:
			frappe.db.sql(f"""
				UPDATE `tabMaintenance Details`
				SET {field} = {self.get(field) or 0}
				WHERE maintenance='{self.name}'
			""")

		purpose_desc={
			"vehicle_log_purpose_per_log": "",
			"vehicle_log_purpose_per_km": "",
			"vehicle_log_purpose_per_day": "",
			}
		for field in purpose_desc:
			purpose_desc[field]=frappe.db.sql(f"""
				SELECT 
					GROUP_CONCAT(
						IF(
							parent='{self.name}' and parentfield="{field}"
							, select_purpose
							, NULL
						) 
						SEPARATOR ', '
					) 
				FROM `tabVehicle Log Purpose`;
			""")
		for field in purpose_desc:
			frappe.db.sql(f"""
				UPDATE `tabMaintenance Details`
				SET {field} = '{purpose_desc[field][0][0] or ""}'
				WHERE maintenance='{self.name}'
			""")
		frappe.db.sql(f"""
				UPDATE `tabMaintenance Details`
				SET doctype_and_field = "{f'''<b>Doctype:</b> {self.vl_doctype}<br><b>Fieldname:</b> {self.vl_fieldname}''' if self.vl_fieldname or self.vl_doctype else ""}"
				WHERE maintenance='{self.name}'
			""")


def update_select_purpose(self, event=None):
	for maintenance in list(set([i.maintenance for i in self.maintanence_details_])):
		if maintenance:
			doc=frappe.get_doc("Maintenance type", maintenance)
			doc.update_maintenance_desc()

def get_doc_fields(doctype):
	child_doctypes = []
	is_hidden_section = 0
	fields = []
	for field in frappe.get_meta(doctype).fields:
		if (field.fieldtype in ["Section Break", "Column Break", "Tab Break"]):
			is_hidden_section = field.hidden
		
		if (field.fieldtype == "Table" and field.hidden == 0 and not is_hidden_section):
			child_doctypes.append(field.options.strip())
		
		if (field.fieldtype in ["Int", "Float", "Currency"] and field.hidden == 0):
			fields.append(field)
	for child in child_doctypes:
		res=get_doc_fields(child)
		for field in res:
			fields.append(field)

	return fields
	