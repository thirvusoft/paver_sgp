import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter
def batch_property_setter():               
    make_property_setter("Purchase Invoice", "sec_warehouse", "hidden", "0", "Check")
    make_property_setter("Purchase Invoice", "set_from_warehouse", "hidden", "1", "Check")
    make_property_setter("Purchase Invoice", "supplier_warehouse", "hidden", "1", "Check")
    make_property_setter("Purchase Invoice", "is_subcontracted", "hidden", "1", "Check") 