# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

# import frappe
from dataclasses import field
import json
from wsgiref import validate
import frappe
from frappe.model.document import Document
from frappe.utils.data import time_diff_in_hours

class MaterialManufacturing(Document):
    def validate(doc):
        total_raw_material=[]
        total_cement_2a = []
        total_ggbs2_a = []
        total_dust_a = []
        total_chips_a =[]
        for i in doc.raw_material_consumption:
            if i.total == None or i.cm2_t == None or i.cm2_a == None or i.ggbs2_a == None or i.ggbs2_t == None:
                frappe.throw("Kindly Fill The Raw Material Consumption Table Completely")
            total_raw_material.append(i.total)
            total_cement_2a.append(i.cm2_a)
            total_ggbs2_a.append(i.ggbs2_a)
            total_chips_a.append(i.bin1_a + i.bin2_a)
            total_dust_a.append(i.bin3_a + i.bin4_a)
        if len(total_raw_material) == 0:
            doc.total_no_of_raw_material = 0
            doc.total_no_of_dust=0
            doc.total_no_of_chips=0
            doc.total_no_of_cement = 0
            doc.total_no_of_ggbs2 = 0
            doc.average_of_raw_material = 0
            doc.average_of_cement = 0
            doc.average_of__ggbs2 = 0
            doc.average_of_chips=0
            doc.average_of_dust=0
        else:
            avg_raw_material = sum(total_raw_material)/len(total_raw_material)
            doc.total_no_of_raw_material = sum(total_raw_material)
            doc.total_no_of_dust = sum(total_dust_a)
            doc.total_no_of_chips = sum(total_chips_a)
            doc.total_no_of_cement = sum(total_cement_2a)
            doc.total_no_of_ggbs2 = sum(total_ggbs2_a)
            doc.average_of_raw_material = avg_raw_material
            doc.average_of_cement = sum(total_cement_2a)/len(total_cement_2a)
            doc.average_of__ggbs2 = sum(total_ggbs2_a)/len(total_ggbs2_a)   
            doc.average_of_chips = sum(total_chips_a)/len(total_chips_a)   
            doc.average_of_dust = sum(total_dust_a)/len(total_dust_a)
    def before_submit(doc):
        manufacture = frappe.get_all("Stock Entry",filters={"usb":doc.get("name"),"stock_entry_type":"Manufacture"},pluck="name")
        repack = frappe.get_all("Stock Entry",filters={"usb":doc.get("name"),"stock_entry_type":"Manufacture"},pluck="name")
        material = frappe.get_all("Stock Entry",filters={"usb":doc.get("name"),"stock_entry_type":"Material Transfer"},pluck="name")
        if len(manufacture) == 0 or len(repack) == 0 or len(material) == 0:
            frappe.throw("Process Incomplete. Create Stock Entry To Submit")

@frappe.whitelist()
def total_hrs(from_time = None,to = None):
    if(from_time and to):
        time_in_mins = time_diff_in_hours(to,from_time)
        return time_in_mins-1
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
    return items
@frappe.whitelist()
def std_item(doc):
    items=[]
    doc=json.loads(doc)
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
    if doc.get('chips_item_name') and doc.get('total_no_of_chips'):
        row={}
        row['item_code'],row['stock_uom'],row['uom'],row['rate'] = frappe.get_value("Item",doc['chips_item_name'],['item_code','stock_uom','stock_uom','valuation_rate'])
        row['qty']=doc.get('total_no_of_chips')
        row['amount']=doc.get('total_no_of_chips')*row['rate']
        items.append(row)
    if doc.get('dust_item_name') and doc.get('total_no_of_dust'):
        row={}
        row['item_code'],row['stock_uom'],row['uom'],row['rate'] = frappe.get_value("Item",doc['dust_item_name'],['item_code','stock_uom','stock_uom','valuation_rate'])
        row['qty']=doc.get('total_no_of_dust')
        row['amount']=doc.get('total_no_of_dust')*row['rate']
        items.append(row)
    return items

@frappe.whitelist()
def item_data(item_code):
    item_code,stock_uom,valuation_rate = frappe.get_value("Item",item_code,['item_code','stock_uom','valuation_rate'])
    return item_code,stock_uom,valuation_rate
@frappe.whitelist()
def make_stock_entry(doc,type):
    doc=json.loads(doc)
    if doc.get("total_completed_qty") == 0 or doc.get("cement_item") == '' or doc.get("ggbs_item") == '' or doc.get("total_expense") == 0:
            frappe.throw("Please Enter the Produced Qty and From Time - To Time in Manufacture Section and Save This Form")
    default_scrap_warehouse = frappe.db.get_singles_value("USB Setting", "scrap_warehouse")
    expenses_included_in_valuation = frappe.get_cached_value("Company", doc.get("company"), "expenses_included_in_valuation")
    stock_entry = frappe.new_doc("Stock Entry")
    stock_entry.company = doc.get("company")
    stock_entry.form_bom = 1
    stock_entry.bom_no = doc.get("bom_no")
    stock_entry.usb = doc.get("name")
    default_nos = frappe.db.get_singles_value("USB Setting", "default_manufacture_uom")
    default_bundle = frappe.db.get_singles_value("USB Setting", "default_rack_shift_uom")
    if doc.get("stock_entry_type")=="Manufacture" and type == "create_stock_entry":
        valid = frappe.get_all("Stock Entry",filters={"usb":doc.get("name"),"stock_entry_type":"Manufacture","docstatus":["!=",2]},pluck="name")
        if len(valid) >= 1:
            frappe.throw("Already Stock Entry("+valid[0]+") Created For Manufacture")
        stock_entry.stock_entry_type = doc.get("stock_entry_type")
        if(doc.get("items")):  
            for i in doc.get("items"):
                stock_entry.append('items', dict(
                s_warehouse = doc.get("source_warehouse"), item_code = i["item_code"],qty = i["qty"], uom = i["uom"]
                ))
        else:
            frappe.throw("Kindly Save this Form")
        stock_entry.append('items', dict(
            t_warehouse = doc.get("target_warehouse"), item_code = doc.get("item_to_manufacture"), qty = doc.get("total_completed_qty"), uom = default_nos
            ))
        if doc.get("damage_qty") > 0:
            if default_scrap_warehouse:
                stock_entry.append('items', dict(
                    t_warehouse = default_scrap_warehouse, item_code = doc.get("item_to_manufacture")	,qty = doc.get("damage_qty"), uom = default_nos, is_process_loss = 1
                    ))
            else:
                frappe.throw("Set Scrap Warehouse in USB Setting")
        stock_entry.append('additional_costs', dict(
                expense_account	 = expenses_included_in_valuation, amount = doc.get("total_expense"),description = "Operating Cost as per Workstation"
            ))
        stock_entry.insert(ignore_mandatory=True, ignore_permissions=True)
        stock_entry.save()
        frappe.msgprint("New Stock Entry Created "+stock_entry.name)
    elif doc.get("stock_entry_rack_shift")=="Repack" and type == "create_rack_shiftingstock_entry":
        if doc.get("total_rack_shift_expense") == 0:
            frappe.throw("Please Enter From Time - To Time in Rack Shifting Section and Save This Form")
        valid = frappe.get_all("Stock Entry",filters={"usb":doc.get("name"),"stock_entry_type":"Repack","docstatus":["!=",2]},pluck="name")
        if len(valid) >= 1:
            frappe.throw("Already Stock Entry("+valid[0]+") Created For Repack")
        stock_entry.stock_entry_type = doc.get("stock_entry_rack_shift")
        if doc.get("total_no_of_produced_qty") == 0:
            frappe.throw("Please Enter the Total No of Bundle")
        stock_entry.append('items', dict(
        s_warehouse = doc.get("rack_shift_source_warehouse"), item_code = doc.get("item_to_manufacture"),qty = doc.get("total_no_of_produced_qty"),uom = default_nos
        ))
        qty = doc.get("total_no_of_bundle") + remaining_qty(doc.get("item_to_manufacture"),default_bundle,doc.get("name"))
        stock_entry.append('items', dict(
            t_warehouse = doc.get("rack_shift_target_warehouse"), item_code = doc.get("item_to_manufacture"),qty = qty,uom = default_bundle
            ))
        if doc.get("rack_shift_damage_qty") > 0:
            stock_entry.append('items', dict(
                t_warehouse = default_scrap_warehouse, item_code = doc.get("item_to_manufacture"),qty = doc.get("rack_shift_damage_qty"),uom = default_nos,  is_process_loss = 1
                ))
        stock_entry.append('additional_costs', dict(
                expense_account	 = expenses_included_in_valuation, amount = doc.get("rack_shifting_total_expense"),description = "Operating Cost as per Workstation"
            ))
        stock_entry.insert(ignore_mandatory=True, ignore_permissions=True)
        stock_entry.save()
        frappe.msgprint("New Stock Entry Created "+stock_entry.name)
    elif doc.get("curing_stock_entry_type")=="Material Transfer" and type == "curing_stock_entry":
        valid = frappe.get_all("Stock Entry",filters={"usb":doc.get("name"),"stock_entry_type":"Material Transfer","docstatus":["!=",2]},pluck="name")
        if len(valid) >= 1:
            frappe.throw("Already Stock Entry("+valid[0]+") Created For Material Transfer")
        stock_entry.stock_entry_type = doc.get("curing_stock_entry_type")
        if doc.get("no_of_bundle") == 0:
            frappe.throw("Please Enter No of Bundle")
        stock_entry.append('items', dict(
        s_warehouse = doc.get("curing_source_warehouse"),t_warehouse = doc.get("curing_target_warehouse"), item_code = doc.get("item_to_manufacture"),qty = doc.get("no_of_bundle"), uom = default_bundle
        ))
        if doc.get("curing_damaged_qty") > 0:
            stock_entry.append('items', dict(
                t_warehouse = default_scrap_warehouse, item_code = doc.get("item_to_manufacture")	,qty = doc.get("curing_damaged_qty"), uom = default_nos, is_process_loss = 1
                ))
        stock_entry.append('additional_costs', dict(
                expense_account	 = expenses_included_in_valuation, amount = doc.get("labour_cost"),description = "Operating Cost as per Labour Cost"
            ))
        stock_entry.insert(ignore_mandatory=True, ignore_permissions=True)
        stock_entry.save()
        frappe.msgprint("New Stock Entry Created "+stock_entry.name)
    if doc.get("status") == "Manufacture":
        return "Rack Shifting"
    elif doc.get("status") == "Rack Shifting":
        return "Curing"
    elif doc.get("status") == "Curing":
        return "Completed"
def remaining_qty(item_code,default_bundle,cur_doc):
    uom =frappe.get_doc("Item",item_code)
    uom_qty = 0
    for i in uom.uoms:
        if(default_bundle == i.uom):
            uom_qty=i.conversion_factor	
    total_qty=0
    remaining_qty = frappe.get_all("Material Manufacturing",fields=['name','remaining_qty'],filters={"item_to_manufacture" : item_code})
    for j in remaining_qty:
        total_qty = total_qty+j.remaining_qty
    set_qty = 0
    while(int(total_qty) > int(uom_qty)):
        total_qty = total_qty - uom_qty
        set_qty = set_qty+1
    if set_qty:
        for j in range (len(remaining_qty)):
            if remaining_qty[j].name == cur_doc:
                frappe.db.set_value("Material Manufacturing",remaining_qty[j].name,'remaining_qty', total_qty)
            else:
                frappe.db.set_value("Material Manufacturing",remaining_qty[j].name,'remaining_qty', 0)
        frappe.db.commit()
        return set_qty
    return 0
            
