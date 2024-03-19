# Copyright (c) 2023, Thirvusoft and contributors
# For license information, please see license.txt

import frappe
from ganapathy_pavers.ganapathy_pavers.doctype.compound_wall_type.compound_wall_type import CompoundWallType


class PaverType(CompoundWallType):
	def on_trash(self):
		if self.name in ['Paver', 'Pavers']:
			frappe.throw("Root type can't be deleted.")
		return super().on_trash()
