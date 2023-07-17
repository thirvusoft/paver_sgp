# Copyright (c) 2023, Thirvusoft and contributors
# For license information, please see license.txt

from ganapathy_pavers.custom.py.workstation import make_custom_field, remove_custom_field, rename_custom_field_workstation
import frappe
from frappe.model.document import Document

type_doctypes = ["Journal Entry Account", "Stock Entry Detail", "GL Entry", "Purchase Invoice","Production Expense Table", "Vehicle Log", "Vehicle"]

class PaverType(Document):
	def on_update(self):
		make_custom_field(self=self, event=None, oldname=None, wrk_dt=type_doctypes, insert_after="production_details")

	def after_rename(self, oldname, newname, merge):
		rename_custom_field_workstation(self=self, event='after_rename', oldname=oldname, newname=newname, merge=merge, wrk_dt=type_doctypes, insert_after="production_details")

	def on_trash(self):
		remove_custom_field(self=self, event='on_trash', wrk_dt=type_doctypes)