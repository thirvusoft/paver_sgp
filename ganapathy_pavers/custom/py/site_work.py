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
    if(not self.project_name):
        frappe.throw('Please Enter Site Work Name')
    else:
        name= self.project_name
    if(not self.is_multi_customer and not self.customer):
        frappe.throw("Please Enter Customer's Name")
    elif(not self.is_multi_customer):
        name+= '-' + self.customer
    if(name):
        self.name=name
        frappe.errprint(self.name)
    else:
        pass
        
def create_status():
    print('Creating Property Setter for Site Work Status')
    doc=frappe.new_doc('Property Setter')
    doc.update({
        "doctype_or_field": "DocField",
        "doc_type":"Project",
        "field_name":"status",
        "property":"options",
        "value":"\nOpen\nCompleted\nCancelled\nStock Pending at Site"
    })
    doc.save()
    frappe.db.commit()
    