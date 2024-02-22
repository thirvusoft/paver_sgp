# Copyright (c) 2023, Thirvusoft and contributors
# For license information, please see license.txt

from ganapathy_pavers.custom.py.workstation import make_custom_field, remove_custom_field, rename_custom_field_workstation
import frappe
from frappe.model.document import Document
from frappe.model.rename_doc import rename_doc

type_doctypes = ["Journal Entry Account", "Stock Entry Detail", "GL Entry", "Purchase Invoice","Production Expense Table", "Vehicle Log", "Vehicle"]

class CompoundWallType(Document):
	def on_update(self):
		make_custom_field(self=self, event=None, oldname=None, wrk_dt=type_doctypes, insert_after="production_details")

	def on_trash(self):
		if self.name in ['Compound Wall', 'Lego Block', 'Fencing Post']:
			frappe.throw("Root type can't be deleted.")
		
		remove_custom_field(self=self, event='on_trash', wrk_dt=type_doctypes)

	def after_insert(self):
		name = {'Paver': 'Pavers'}
		d = frappe.new_doc("Types")
		d.update({
			"type": (name.get(self.name) or self.name)
		})
		d.save()
	
	def after_delete(self):
		name = {'Paver': 'Pavers'}
		d = frappe.get_doc("Types", (name.get(self.name) or self.name))
		d.delete()
	
	def after_rename(self, olddn, newdn, merge=False):
		rename_custom_field_workstation(self=self, event='after_rename', oldname=olddn, newname=newdn, merge=merge, wrk_dt=type_doctypes, insert_after="production_details")
		rename_doc(
			doctype="Types",
			old=olddn,
			new=newdn,
			ignore_permissions=True
		)

def get_paver_and_compound_wall_types():
	cw = [frappe.scrub(i) for i in frappe.db.get_all("Compound Wall Type", {'used_in_expense_splitup': 1}, pluck="name")]
	paver = [frappe.scrub(i) for i in frappe.db.get_all("Paver Type", {'used_in_expense_splitup': 1}, pluck="name")]
	fields = list(set(paver + cw + ["paver", "is_shot_blast", "compound_wall", "fencing_post", "lego_block"]))
	return fields

