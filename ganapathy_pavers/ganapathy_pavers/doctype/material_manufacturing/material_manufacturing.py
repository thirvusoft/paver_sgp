# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

# import frappe
from email.policy import default
import json
import frappe
from frappe.model.document import Document
from ganapathy_pavers.ganapathy_pavers.doctype.cw_manufacturing.cw_manufacturing import uom_conversion_for_rate
from ganapathy_pavers.ganapathy_pavers.doctype.cw_manufacturing.cw_manufacturing import uom_conversion
from frappe.utils.data import time_diff_in_hours

class MaterialManufacturing(Document):
    def validate(doc):
        doc.get_bin_items()
        for row in doc.items:
            row.amount = (row.rate or 0) * (row.qty or 0)
            
    def get_bin_items(doc):
        bin_items = []
        total_raw_material=[]
        for row in doc.bin_items:
            row.total_qty=0
            row.average_qty=0
            if frappe.scrub(row.bin) in bin_items:
                frappe.throw(f"""Bin <b>{row.bin}</b> is repeating more than once in <b>Bin Item Mapping</b>""")
            bin_items.append(frappe.scrub(row.bin))

        for row in doc.raw_material_consumption:
            total_raw_material.append(row.total or 0)
            for bin in doc.bin_items:
                if not bin.total_qty:
                    bin.total_qty=0
                bin.total_qty+=row.get(frappe.scrub(bin.bin), 0)
                if not bin.average_qty:
                    bin.average_qty=0
                bin.average_qty+=(row.get(frappe.scrub(bin.bin), 0)/len(doc.raw_material_consumption))
        
        if len(total_raw_material) == 0:
            doc.total_no_of_raw_material = 0
            doc.average_of_raw_material = 0
        else:
            avg_raw_material = sum(total_raw_material)/len(total_raw_material)
            doc.total_no_of_raw_material = sum(total_raw_material)
            doc.average_of_raw_material = avg_raw_material

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
       return time_in_mins

@frappe.whitelist()
def total_expense(workstation,operators_cost,labour_cost,tot_work_hrs,tot_item,tot_hrs):
   sum_of_wages, hour_rate=frappe.get_value("Workstation",workstation,["sum_of_wages_per_hours","hour_rate"])
   amount_split = operators_cost
   if float(tot_item) > 1:
       if float(tot_hrs) > 0:
           tot_mins = float(tot_hrs)*60
           tot_work_mins = float(tot_work_hrs)*60
           shared_mins = (tot_work_mins/tot_mins)*100
           amount_split = (float(operators_cost)/100)*shared_mins
       else:
           frappe.throw("Kindly Enter Total Working Hrs")
   return hour_rate+float(labour_cost),float(amount_split)

@frappe.whitelist()
def add_item(bom_no,doc):
   items=[]
   doc=json.loads(doc)
   bom_doc = frappe.get_doc("BOM",bom_no)
   fields = ['item_code','qty', 'layer_type', 'uom', 'stock_uom', 'rate', 'amount', 'source_warehouse']
   for i in bom_doc.items:
       if i.layer_type=="Top Layer":
         row = {field:i.__dict__[field] for field in fields}
         row['ts_qty'] = row.get('qty') or 0
         ws_warehosue=get_items_warehosue_from_workstation(i.item_code, i.layer_type, doc.get("work_station"))
         if ws_warehosue:
            row['source_warehouse']=ws_warehosue
         items.append(row)
   return items

@frappe.whitelist()
def std_item(doc):
    items=[]
    doc=json.loads(doc)
    bin_items={}
    for bin in doc.get("bin_items"):
        if bin.get('item_code') not in bin_items:
            bin_items[bin.get("item_code")]={
                "total_qty": 0,
                "average_qty": 0,
                "item_code": bin.get("item_code"),
            }
        bin_items[bin.get("item_code")]["total_qty"]+=bin.get("total_qty", 0)
        bin_items[bin.get("item_code")]["average_qty"]+=bin.get("average_qty", 0)

    for bin in list(bin_items.values()):
        row={}
        row['item_code'],row['stock_uom'],row['uom'],row['rate'],row['validation_rate'] = frappe.get_value("Item", bin.get("item_code"), ['item_code', 'stock_uom', 'stock_uom', 'last_purchase_rate', 'valuation_rate'])
        row['qty']=bin.get('total_qty')
        row['average_consumption'] = bin.get('average_qty')
        row['layer_type'] = 'Panmix'
        row['amount']=bin.get('total_qty')*(row['rate'] or row['validation_rate'])
        items.append(row)

    if doc.get('setting_oil_item_name') and doc.get('total_setting_oil_qty'):
        row={}
        row['item_code'],row['stock_uom'],row['uom'],row['rate'],row['validation_rate'] = frappe.get_value("Item",doc['setting_oil_item_name'],['item_code','stock_uom','stock_uom','last_purchase_rate','valuation_rate'])
        row['qty']=doc.get('total_setting_oil_qty')
        row['average_consumption'] = (doc.get('setting_oil_qty') or 0)/1000
        row['layer_type'] = 'Panmix'
        row['amount']=doc.get('total_setting_oil_qty')*(row['rate'] or row['validation_rate'])
        items.append(row)
    bom_qty = {}
    if(doc.get('bom_no')):
        bom_doc = frappe.get_doc('BOM', doc.get('bom_no'))
        for row in bom_doc.items:
            if(row.layer_type == 'Panmix'):
                if(row.item_code not in bom_qty):
                    bom_qty[row.item_code] = 0
                bom_qty[row.item_code] += row.qty
                for item in items:
                        if(item["item_code"]==row.item_code and row.source_warehouse):
                            item['source_warehouse']=row.source_warehouse
                        if 'source_warehouse' not in item:
                            item['source_warehouse']=''
    if(doc.get('work_station')):
        for item in items:
            ws_warehosue=get_items_warehosue_from_workstation(item["item_code"], item["layer_type"], doc.get("work_station"))
            if ws_warehosue:
                item['source_warehouse']=ws_warehosue
    return {'items': items, 'bom_qty': bom_qty}

def get_items_warehosue_from_workstation(item_code : str, layer_type : str, workstation : str) -> str:
   ws=frappe.get_doc("Workstation", workstation)
   for row in ws.raw_material_warehouse:
      if row.layer_type and row.layer_type!=layer_type:
         continue
      if row.item_code==item_code:
         return row.source_warehouse

@frappe.whitelist()
def item_data(item_code):
   if(item_code):
       item_code,stock_uom,last_purchase_rate,valuation_rate = frappe.get_value("Item",item_code,['item_code','stock_uom','last_purchase_rate','valuation_rate'])
       return item_code,stock_uom,last_purchase_rate or valuation_rate

@frappe.whitelist()
def make_stock_entry(doc,type1):
   doc=json.loads(doc)
   if(doc.get("item_to_manufacture")):
       if(not frappe.get_value('Item', doc.get("item_to_manufacture"), 'has_batch_no')):
           frappe.throw(f'Please choose {frappe.bold("Has Batch No")} for an item {doc.get("item_to_manufacture")}')

   if doc.get("total_completed_qty") == 0 or doc.get("cement_item") == '' or doc.get("ggbs_item") == '' or doc.get("total_expense") == 0:
           frappe.throw("Please Enter the Produced Qty and From Time - To Time in Manufacture Section and Save This Form")
   default_scrap_warehouse = frappe.db.get_singles_value("USB Setting", "scrap_warehouse")
   expenses_included_in_valuation = frappe.get_cached_value("Company", doc.get("company"), "expenses_included_in_valuation")
   stock_entry = frappe.new_doc("Stock Entry")
   stock_entry.company = doc.get("company")
   stock_entry.from_bom = 1
   stock_entry.bom_no = doc.get("bom_no")
   stock_entry.usb = doc.get("name")
   default_nos = frappe.db.get_singles_value("USB Setting", "default_manufacture_uom")
   default_bundle = frappe.db.get_singles_value("USB Setting", "default_rack_shift_uom")
   if doc.get("stock_entry_type")=="Manufacture" and type1 == "create_stock_entry":
       valid = frappe.get_all("Stock Entry",filters={"usb":doc.get("name"),"stock_entry_type":"Manufacture","docstatus":["!=",2]},pluck="name")
       stock_entry.set_posting_time = 1
       stock_entry.posting_date = frappe.utils.formatdate(doc.get("to"), "yyyy-MM-dd")
       stock_entry.posting_time=frappe.utils.get_datetime(doc.get("from_time")).time()
       if len(valid) >= 1:
           frappe.throw("Already Stock Entry("+valid[0]+") Created For Manufacture")
       stock_entry.stock_entry_type = doc.get("stock_entry_type")
       if(doc.get("items")):
           for i in doc.get("items"):
               stock_entry.append('items', dict(
               s_warehouse = i.get("source_warehouse") or doc.get("source_warehouse"), item_code = i["item_code"],qty = i["qty"], uom = i["uom"],
               basic_rate_hidden = i["rate"],
               basic_rate = i["rate"]
               ))
       else:
           frappe.throw("Kindly Save this Form")
       stock_entry.append('items', dict(
           t_warehouse = doc.get("target_warehouse"), item_code = doc.get("item_to_manufacture"), qty = uom_conversion(doc.get("item_to_manufacture"), 'Nos', doc.get("total_completed_qty"), default_nos), uom = default_nos,is_finished_item = 1,
           basic_rate=uom_conversion_for_rate(doc.get("item_to_manufacture"),"SQF",doc.get("item_price"),default_nos),
           basic_rate_hidden = uom_conversion_for_rate(doc.get("item_to_manufacture"),"SQF",doc.get("item_price"),default_nos)
           ))
       if doc.get("damage_qty") > 0:
           if default_scrap_warehouse:
               stock_entry.append('items', dict(
                   t_warehouse = default_scrap_warehouse, item_code = doc.get("item_to_manufacture")   ,qty = uom_conversion(doc.get("item_to_manufacture"), 'Nos', doc.get("damage_qty"), default_nos), uom = default_nos, is_process_loss = 1,

                   ))
           else:
               frappe.throw("Set Scrap Warehouse in USB Setting")
       stock_entry.append('additional_costs', dict(
               expense_account  = expenses_included_in_valuation, amount = doc.get("total_expense"),description = "In This Labour, operator, Raw Material Cost Added"
           ))
       stock_entry.insert(ignore_mandatory=True, ignore_permissions=True)
       stock_entry.save()
       stock_entry.submit()
       frappe.msgprint("New Stock Entry Created "+stock_entry.name)
   elif doc.get("stock_entry_rack_shift")=="Repack" and type1 == "create_rack_shiftingstock_entry":
       if doc.get("total_rack_shift_expense") == 0:
           frappe.throw("Please Enter From Time - To Time in Rack Shifting Section and Save This Form as Rack Shifting expense is empty")
       valid = frappe.get_all("Stock Entry",filters={"usb":doc.get("name"),"stock_entry_type":"Repack","docstatus":["!=",2]},pluck="name")
       stock_entry.set_posting_time = 1
       stock_entry.posting_date = frappe.utils.formatdate(doc.get("to_time_rack"), "yyyy-MM-dd")
       stock_entry.posting_time=frappe.utils.get_datetime(doc.get("to_time_rack")).time()
       if len(valid) >= 1:
           frappe.throw("Already Stock Entry("+valid[0]+") Created For Repack")
       if doc.get("batch_no_manufacture"):
           pass
       else:
           frappe.throw("Kindly Submit Manufacture Stock Entry")
       stock_entry.stock_entry_type = doc.get("stock_entry_rack_shift")
       if doc.get("total_no_of_produced_qty") == 0:
           frappe.throw("Please Enter the Total No of Bundle")
       r_qty,emp_bundle,r_total_qty = remaining_qty(doc.get("item_to_manufacture"),default_bundle,default_nos,doc.get("name"))
       for i in emp_bundle:
           stock_entry.append('items', dict(
               s_warehouse = doc.get("rack_shift_source_warehouse"), item_code = doc.get("item_to_manufacture"),qty = frappe.get_value("Batch",i,"batch_qty"),uom = frappe.get_value("Batch",i,"stock_uom") ,batch_no = i
           ))
       qty = doc.get("total_no_of_bundle") + r_qty
       stock_entry.append('items', dict(
       s_warehouse = doc.get("rack_shift_source_warehouse"), item_code = doc.get("item_to_manufacture"),qty = uom_conversion(doc.get("item_to_manufacture"), "Nos", (doc.get("total_no_of_produced_qty")+doc.get("rack_shift_damage_qty"))-(int(r_total_qty) or doc.get("remaining_qty")), default_nos),uom = default_nos ,batch_no = doc.get("batch_no_manufacture"),
       basic_rate=uom_conversion_for_rate(doc.get("item_to_manufacture"),"SQF",doc.get("item_price"),default_nos),
        basic_rate_hidden = uom_conversion_for_rate(doc.get("item_to_manufacture"),"SQF",doc.get("item_price"),default_nos)
       ))
       stock_entry.append('items', dict(
           t_warehouse = doc.get("rack_shift_target_warehouse"), item_code = doc.get("item_to_manufacture"),qty = uom_conversion(doc.get("item_to_manufacture"), "Bdl",qty, default_bundle),uom = default_bundle,
           basic_rate=uom_conversion_for_rate(doc.get("item_to_manufacture"),"SQF",doc.get("item_price"),default_bundle),
            basic_rate_hidden = uom_conversion_for_rate(doc.get("item_to_manufacture"),"SQF",doc.get("item_price"),default_bundle)
           ))
       if doc.get("rack_shift_damage_qty") > 0:
           stock_entry.append('items', dict(
               t_warehouse = default_scrap_warehouse, item_code = doc.get("item_to_manufacture"),qty = uom_conversion(doc.get("item_to_manufacture"), "Nos",doc.get("rack_shift_damage_qty"), default_nos),uom = default_nos,  is_process_loss = 1,

               ))
       stock_entry.append('additional_costs', dict(
               expense_account  = expenses_included_in_valuation, amount = doc.get("rack_shifting_total_expense1"),description = "In This Labour Cost Added"
           ))
       stock_entry.insert(ignore_mandatory=True, ignore_permissions=True)
       stock_entry.save()
       stock_entry.submit()
       frappe.msgprint("New Stock Entry Created "+stock_entry.name)
   elif doc.get("curing_stock_entry_type")=="Material Transfer" and type1 == "curing_stock_entry":
       valid = frappe.get_all("Stock Entry",filters={"usb":doc.get("name"),"stock_entry_type":"Material Transfer","docstatus":["!=",2]},pluck="name")
       stock_entry.set_posting_time = 1
       stock_entry.posting_date = frappe.utils.formatdate(doc.get("to_time_rack"), "yyyy-MM-dd")
       stock_entry.posting_time=frappe.utils.get_datetime(doc.get("to_time_rack")).time()
       if len(valid) >= 1:
           frappe.throw("Already Stock Entry("+valid[0]+") Created For Material Transfer")
       if doc.get("batch_no_rack_shifting"):
           pass
       else:
           frappe.throw("Kindly Submit Repack Stock Entry")
       stock_entry.stock_entry_type = doc.get("curing_stock_entry_type")
       if doc.get("no_of_bundle") == 0:
           frappe.throw("Please Enter No of Bundle")
       stock_entry.append('items', dict(
       s_warehouse = doc.get("curing_source_warehouse"),t_warehouse = doc.get("curing_target_warehouse"), item_code = doc.get("item_to_manufacture"),qty = uom_conversion(doc.get("item_to_manufacture"), 'Bdl', doc.get("no_of_bundle"), default_bundle), uom = default_bundle,batch_no = doc.get("batch_no_rack_shifting"),
       basic_rate=uom_conversion_for_rate(doc.get("item_to_manufacture"),"SQF",doc.get("item_price"),default_bundle),
        basic_rate_hidden = uom_conversion_for_rate(doc.get("item_to_manufacture"),"SQF",doc.get("item_price"),default_bundle)
       ))
       if doc.get("curing_damaged_qty") > 0:
           stock_entry.append('items', dict(
               t_warehouse = default_scrap_warehouse, item_code = doc.get("item_to_manufacture")   ,qty = uom_conversion(doc.get("item_to_manufacture"), 'Nos', doc.get("curing_damaged_qty"), default_nos), uom = default_nos, is_process_loss = 1,
              basic_rate=uom_conversion_for_rate(doc.get("item_to_manufacture"),"SQF",doc.get("item_price"),default_nos),
               basic_rate_hidden = uom_conversion_for_rate(doc.get("item_to_manufacture"),"SQF",doc.get("item_price"),default_nos)
               ))
       stock_entry.append('additional_costs', dict(
               expense_account  = expenses_included_in_valuation, amount = doc.get("labour_cost"),description = "In This Labour Cost Added"
           ))
       stock_entry.insert(ignore_mandatory=True, ignore_permissions=True)
       stock_entry.save()
       stock_entry.submit()
       frappe.msgprint("New Stock Entry Created "+stock_entry.name)
   if doc.get("status1") == "Manufacture":
       return "Rack Shifting"
   elif doc.get("status1") == "Rack Shifting":
       return "Curing"
   elif doc.get("status1") == "Curing":
       if doc.get("is_shot_blasting") ==1:
           return "Shot Blast"
       else:
           return "Completed"
   elif doc.get("status1") == "Shot Blast":
       return "Completed"

def remaining_qty(item_code,default_bundle,default_nos,cur_doc):
   emp_batch=[]
   uom =frappe.get_doc("Item",item_code)
   uom_qty = 0
   uom_nos = 0
   for i in uom.uoms:
       if(default_bundle == i.uom):
           uom_qty=i.conversion_factor
       if(default_nos == i.uom):
           uom_nos=i.conversion_factor
   total_qty=0
   remaining_qty = frappe.get_all("Material Manufacturing",fields=['name','remaining_qty',"batch_no_manufacture"],filters={"item_to_manufacture" : item_code})
   for j in remaining_qty:
       total_qty = total_qty+(j.remaining_qty*uom_nos)
   set_qty = 0
   while(int(total_qty) > int(uom_qty)):
       total_qty = total_qty - uom_qty
       set_qty = set_qty+1
   total_qty=(total_qty/uom_nos if uom_nos else 0)
   if set_qty:
       for j in range (len(remaining_qty)):
           if remaining_qty[j].name == cur_doc:
               frappe.db.set_value("Material Manufacturing",remaining_qty[j].name,'remaining_qty', total_qty)
           else:
               frappe.db.set_value("Material Manufacturing",remaining_qty[j].name,'remaining_qty', 0)
               # frappe.db.set_value("Batch",remaining_qty[j].batch_no_manufacture,'batch_qty', 0)
               if remaining_qty[j].remaining_qty:
                  emp_batch.append(remaining_qty[j].batch_no_manufacture)
    #    frappe.db.commit()
       return set_qty,emp_batch,total_qty
   return 0,[],0

@frappe.whitelist()
def find_batch(name):
   manufacture=""
   repack=""
   transfer=""
   if name:
       stock = frappe.get_all("Stock Entry",filters={"usb":name,"docstatus":1},fields=['name','stock_entry_type'])
       for i in stock:
           if i.stock_entry_type == "Manufacture":
               batch = frappe.get_doc("Stock Entry",i.name)
               for j in batch.items:
                   if j.t_warehouse and j.is_finished_item and not j.is_process_loss:
                       manufacture=j.batch_no
           elif i.stock_entry_type == "Repack":
               batch = frappe.get_doc("Stock Entry",i.name)
               for j in batch.items:
                   if j.t_warehouse and j.is_finished_item and not j.is_process_loss:
                       repack=j.batch_no
           elif i.stock_entry_type == "Material Transfer":
               batch = frappe.get_doc("Stock Entry",i.name)
               for j in batch.items:
                   if j.t_warehouse and j.s_warehouse:
                       transfer=j.batch_no
   return manufacture,repack,transfer

