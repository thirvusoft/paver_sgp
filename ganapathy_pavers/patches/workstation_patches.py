import frappe
from ganapathy_pavers.custom.py.workstation import rename_custom_field
from ganapathy_pavers.utils.py.workstation import workstation_item_customization

def execute():
    workstation_item_customization()

def rename():
    rename_custom_field(frappe.get_doc("Workstation", "Machine3 Day"), "after_rename", "Machine3", "Machine3 Day", 0)

# ganapathy_pavers.patches.workstation_patches.rename