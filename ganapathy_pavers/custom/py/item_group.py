import frappe


def item_group():
    doc = frappe.new_doc("Item Group")
    doc.update({
        'item_group_name' : "Pavers"
    })
    doc.insert(ignore_permissions=True)
    
    doc1 = frappe.new_doc("Item Group")
    doc1.update({
        'item_group_name' : "Compound Walls"
    })
    doc1.insert(ignore_permissions=True)
    
    