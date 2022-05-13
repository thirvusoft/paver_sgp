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

def before_save(doc, action):
    total1= 0
    total2 = 0
    total3 = 0
    total4 = 0
    for i in doc.additional_cost:
        total1 = total1+i.amount
    print(total1)
    doc.total = total1
    for i in doc.item_details:
        total2 = total2+i.amount
    doc.total_amount=total2
    for i in doc.job_worker:
        total3 = total3+i.amount
    doc.total_job_worker_cost=total3
    for i in doc.raw_material:
        total4 = total4+i.amount   
    doc.total_amount_of_raw_material=total4   
    total_costing=total1+total2+total3+total4
    doc.total_expense_amount=total_costing
		

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
        self.project_name+='-'+self.customer
    if(name):
        self.name=name
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
    