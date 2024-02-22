import frappe

def execute():
    """
        Update items table for cw type and cw sub type
    """
    soi = frappe.db.get_all("Sales Order Item", {"compound_wall_type": ["in", ["Post", "Slab"]]}, ['name', 'compound_wall_type'])
    for r in soi:
        frappe.db.set_value('Sales Order Item', r.name,'compound_wall_sub_type', r.compound_wall_type, update_modified=False)
        frappe.db.set_value('Sales Order Item', r.name,'compound_wall_type', 'Compound Wall', update_modified=False)
