# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class AttendanceToolSettings(Document):
	pass

@frappe.whitelist()
def after_save():
	frappe.publish_realtime('ts_update_settings')

@frappe.whitelist()
def clear_dialogs():
	frappe.publish_realtime('ts_clear_dialogs')