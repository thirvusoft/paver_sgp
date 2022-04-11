import frappe


@frappe.whitelist()
def get_item_value(doctype):
    res={
        'item_name':frappe.get_value('Item',doctype,'item_name'),
        'description':frappe.get_value('Item',doctype,'description'),
        'uom':frappe.get_value('Item',doctype,'sales_uom')
    }
    return res
    
@frappe.whitelist()
def create_site(self,action):
    return
    doc=frappe.new_doc('Project')
    
    
