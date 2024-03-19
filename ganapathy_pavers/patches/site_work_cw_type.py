import frappe

def execute():
    """
        Update site work compound wall items for cw type and cw sub type
    """
    items = frappe.db.get_all("Compound Wall", {"compound_wall_type": ["in", ["Post", "Slab"]]}, ['name', 'compound_wall_type'])
    for r in items:
        frappe.db.set_value('Compound Wall', r.name,'compound_wall_sub_type', r.compound_wall_type, update_modified=False)
        frappe.db.set_value('Compound Wall', r.name,'compound_wall_type', 'Compound Wall', update_modified=False)
