import frappe

def execute():
    """
        Update cw manufacturing for cw type and cw sub type
    """
    cw = frappe.db.get_all("CW Manufacturing", {"type": ["in", ["Post", "Slab"]]}, ['name', 'type'])
    for r in cw:
        frappe.db.set_value('CW Manufacturing', r.name,'sub_type', r.type, update_modified=False)
        frappe.db.set_value('CW Manufacturing', r.name,'type', 'Compound Wall', update_modified=False)
