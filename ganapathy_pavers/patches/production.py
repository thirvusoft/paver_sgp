import frappe
from ganapathy_pavers.ganapathy_pavers.doctype.compound_wall_type.compound_wall_type import cw_types

def execute():
    for i in ["Fencing Post", "Lego Block", "Compound Wall", "U Drain"]:
        frappe.get_doc({"doctype": "Compound Wall Type", "compound_wall_type": i, "used_in_expense_splitup": 1}).save()

    for i in frappe.db.get_all("Item", {"compound_wall_type": "U Drain Post"}):
        frappe.db.set_value("Item", i.name, "compound_wall_type", "U Drain")
    cw_types()