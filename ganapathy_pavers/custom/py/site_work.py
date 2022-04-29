import frappe
import json

@frappe.whitelist()
def item_details_fetching_pavers(item_code):
    if item_code:
        doc = frappe.get_doc("Item",item_code)
        item_price = doc.standard_rate
        area_bundle= doc.bundle_per_sqr_ft
        return area_bundle,item_price
	
@frappe.whitelist()
def item_details_fetching_compoundwall(item_code):
    if item_code:
        doc = frappe.get_doc("Item",item_code)
        item_price = doc.standard_rate
        area_bundle= doc.bundle_per_sqr_ft
        return area_bundle,item_price

@frappe.whitelist()
def add_total_amount(items):
    if items:
        return sum([i['amount'] for i in json.loads(items)])


def autoname(self, event):
    name= (self.project_name or '') + (self.customer or '')
    if(name):
        self.name=name
    else:
        pass