import frappe
import erpnext
from frappe import _
def validate_phone(doc,action):
   cell_number = doc.cell_number
   if cell_number:
       if not cell_number.isdigit() or len(cell_number) != 10:
           frappe.throw(frappe._("{0} is not a valid Phone Number.").format(cell_number), frappe.InvalidPhoneNumberError) 