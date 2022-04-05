import frappe
import json

@frappe.whitelist()
def item_details_fetching_pavers(item_code):
    value = frappe.get_doc("Item",item_code)
    item_price = value.__dict__["standard_rate"]
    area_bundle=value.__dict__["bundle_per_sqr_ft"]
    return area_bundle,item_price
	
@frappe.whitelist()
def item_details_fetching_compoundwall(item_code):
    value = frappe.get_doc("Item",item_code)
    item_price = value.__dict__["standard_rate"]
    area_bundle=value.__dict__["bundle_per_sqr_ft"]
    return area_bundle,item_price

@frappe.whitelist()
def add_total_amount(items):
    return sum([i['amount'] for i in json.loads(items)])
