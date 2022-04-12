import frappe
import json
from frappe.model.mapper import get_mapped_doc


@frappe.whitelist()
def get_item_value(doctype):
    res={
        'item_name':frappe.get_value('Item',doctype,'item_name'),
        'description':frappe.get_value('Item',doctype,'description'),
        'uom':frappe.get_value('Item',doctype,'sales_uom')
    }
    return res
    
# @frappe.whitelist()
# def create_site(source_name):
#     target_doc = get_mapped_doc("Sales Order", source_name, {
# 		"Sales Order": {
# 			"doctype": "Project",
			
# 		},
# 		"Item Detail Pavers": {
# 			"doctype": "Item Detail Pavers",
			
			
# 		}
# 	})
#     return doclist
    
    
    
