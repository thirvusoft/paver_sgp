import frappe


def item_group():
    if not frappe.db.exists("Item Group", "Pavers"):
        doc = frappe.new_doc("Item Group")
        doc.update({
            'item_group_name' : "Pavers"
        })
        doc.insert(ignore_permissions=True)
    if not frappe.db.exists("Item Group", "Compound Walls"):
        doc1 = frappe.new_doc("Item Group")
        doc1.update({
            'item_group_name' : "Compound Walls"
        })
        doc1.insert(ignore_permissions=True)
    
    