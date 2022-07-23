# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

# import frappe
import json
import frappe
from frappe.model.document import Document
from frappe.utils.data import time_diff_in_hours

class MaterialManufacturing(Document):
    def validate(doc):
        total_raw_material=[]
        total_cement = []
        total_cement_2a = []
        total_ggbs2 = []
        total_ggbs2_t = []
        for i in doc.raw_material_consumption:
            total_raw_material.append(i.total)
            total_cement.append(i.cm2_t)
            total_ggbs2.append(i.ggbs2_a)
            total_cement_2a.append(i.cm2_a)
            total_ggbs2_t.append(i.ggbs2_t)
        total_cm = sum(total_cement_2a) + sum(total_cement)
        total_ggbs = sum(total_ggbs2) + sum(total_ggbs2_t)
        avg_raw_material = sum(total_raw_material)/len(total_raw_material)
        avg_cement = total_cm/(len(total_cement)+len(total_cement_2a))
        avg_ggbs2 = total_ggbs/(len(total_ggbs2)+len(total_ggbs2_t))
        doc.total_no_of_raw_material = sum(total_raw_material)
        doc.total_no_of_cement = total_cm
        doc.total_no_of_ggbs2 = total_ggbs
        doc.average_of_raw_material = avg_raw_material
        doc.average_of_cement = avg_cement
        doc.average_of__ggbs2 = avg_ggbs2
        
    
    
    def before_submit(doc):
        if doc.total_completed_qty == 0 or doc.cement_item == '' or doc.ggbs_item == '':
            frappe.throw("Please Enter the Total Completed Qty, Cement Item and GGBS Item")
        expenses_included_in_valuation = frappe.get_cached_value("Company", doc.company, "expenses_included_in_valuation")
        stock_entry = frappe.new_doc("Stock Entry")
        stock_entry.stock_entry_type = doc.stock_entry_type
        stock_entry.company = doc.company
        stock_entry.form_bom = 1
        stock_entry.bom_no = doc.bom_no
        stock_entry.company = doc.company
        if doc.stock_entry_type=="Manufacture":
            for i in doc.items:
                stock_entry.append('items', dict(
                s_warehouse = doc.source_warehouse, item_code = i.item_code,qty = i.qty, uom = i.uom
                ))
            stock_entry.append('items', dict(
                t_warehouse = doc.target_warehouse, item_code = doc.item_to_manufacture	,qty = doc.total_completed_qty
                ))
            stock_entry.append('additional_costs', dict(
                	expense_account	 = expenses_included_in_valuation, amount = doc.total_expense,description = "Operating Cost as per Workstation"
                ))
            stock_entry.insert(ignore_mandatory=True, ignore_permissions=True)
            stock_entry.submit()

@frappe.whitelist()
def total_hrs(from_time = None,to = None):
    if(from_time and to):
        time_in_mins = time_diff_in_hours(to,from_time)
        return time_in_mins
@frappe.whitelist()
def total_expense(workstation):
    sum_of_wages, hour_rate=frappe.get_value("Workstation",workstation,["sum_of_wages_per_hours","hour_rate"])
    return sum_of_wages+hour_rate
@frappe.whitelist()
def add_item(bom_no,doc):
    items=[]
    doc=json.loads(doc)
    bom_doc = frappe.get_doc("BOM",bom_no)
    fields = ['item_code','qty', 'uom', 'stock_uom', 'rate', 'amount']
    for i in bom_doc.items:
        row = {field:i.__dict__[field] for field in fields}
        items.append(row)
    if doc.get('cement_item') and doc.get('total_no_of_cement'):
        row={}
        row['item_code'],row['stock_uom'],row['uom'],row['rate'] = frappe.get_value("Item",doc['cement_item'],['item_code','stock_uom','stock_uom','valuation_rate'])
        row['qty']=doc.get('total_no_of_cement')
        row['amount']=doc.get('total_no_of_cement')*row['rate']
        items.append(row)
    if doc.get('ggbs_item') and doc.get('total_no_of_cement'):
        row={}
        row['item_code'],row['stock_uom'],row['uom'],row['rate'] = frappe.get_value("Item",doc['ggbs_item'],['item_code','stock_uom','stock_uom','valuation_rate'])
        row['qty']=doc.get('total_no_of_ggbs2')
        row['amount']=doc.get('total_no_of_cement')*row['rate']
        items.append(row)
    return items

@frappe.whitelist()
def item_data(item_code):
    item_code,stock_uom,valuation_rate = frappe.get_value("Item",item_code,['item_code','stock_uom','valuation_rate'])
    return item_code,stock_uom,valuation_rate
