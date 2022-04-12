import frappe
import json

@frappe.whitelist()
def get_item_value(doctype):
    res={
        'item_name':frappe.get_value('Item',doctype,'item_name'),
        'description':frappe.get_value('Item',doctype,'description'),
        'uom':frappe.get_value('Item',doctype,'sales_uom')
    }
    return res
    
@frappe.whitelist()
def create_site(self):
    return
    frappe.errprint(self)
    self=json.loads(self)
    doc=dict(
        doctype='Project',
        project_type=self['type'],
        project_name=self['site_work'],
        # item_details=self['pavers'],
        # sales_order=self['name']
    )
    frappe.errprint(doc)
    return doc
    
    
    
