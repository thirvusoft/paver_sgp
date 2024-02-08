# Copyright (c) 2023, Thirvusoft and contributors
# For license information, please see license.txt

from ganapathy_pavers.custom.py.workstation import make_custom_field, remove_custom_field, rename_custom_field_workstation
import frappe
from frappe.model.document import Document

type_doctypes = ["Journal Entry Account", "Stock Entry Detail", "GL Entry", "Purchase Invoice","Production Expense Table", "Vehicle Log", "Vehicle"]

class CompoundWallType(Document):
	def on_update(self):
		cw_types()
		make_custom_field(self=self, event=None, oldname=None, wrk_dt=type_doctypes, insert_after="production_details")

	def after_rename(self, oldname, newname, merge):
		rename_custom_field_workstation(self=self, event='after_rename', oldname=oldname, newname=newname, merge=merge, wrk_dt=type_doctypes, insert_after="production_details")

	def on_trash(self):
		remove_custom_field(self=self, event='on_trash', wrk_dt=type_doctypes)

def cw_types():
	doc=frappe.new_doc('Property Setter')
	cw_options = "Post\nSlab"
	other_cw_types = "\n".join(frappe.db.get_all("Compound Wall Type", {"name": ["not in", ["Post", "Slab", "Compound Wall"]]}, pluck="name", order_by="name"))
	if other_cw_types:
		cw_options = cw_options + '\n' + other_cw_types
	doc.update({
		"doctype_or_field": "DocField",
		"doc_type": "CW Manufacturing",
		"field_name": "type",
		"property": "options",
		"value": cw_options
	})
	doc.save()

	doc=frappe.new_doc('Property Setter')
	cw_options = "Post\nSlab\nCorner Post"
	other_cw_types = "\n".join(frappe.db.get_all("Compound Wall Type", {"name": ["not in", ["Post", "Slab", "Compound Wall", "Corner Post"]]}, pluck="name", order_by="name"))
	if other_cw_types:
		cw_options = cw_options + '\n' + other_cw_types
	doc.update({
		"doctype_or_field": "DocField",
		"doc_type": "Item",
		"field_name": "compound_wall_type",
		"property": "options",
		"value": cw_options
	})
	doc.save()