# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

import frappe
import json

from frappe.model.document import Document


class CWManufacturing(Document):
    def before_submit(doc):
        manufacture = frappe.get_all("Stock Entry",filters={"cw_usb":doc.get("name"),"stock_entry_type":"Manufacture"},pluck="name")
        repack = frappe.get_all("Stock Entry",filters={"cw_usb":doc.get("name"),"stock_entry_type":"Repack"},pluck="name")
        material = frappe.get_all("Stock Entry",filters={"cw_usb":doc.get("name"),"stock_entry_type":"Material Transfer"},pluck="name")
        if len(manufacture) == 0 or len(repack) == 0 or len(material) == 0:
            frappe.throw("Couldn't submit because the process is incomplete.")
        if(doc.status1 != "Completed"):
            frappe.throw(f"Please change the status to {frappe.bold('Completed')} before submitting.")

    def validate(doc):
        items={}
        type1=[]
        if(len(doc.item_details)>0):
            for row in doc.item_details:
                if(row.get('item')):
                    cw_type = frappe.get_value("Item", row.get('item'), 'compound_wall_type')
                    if(cw_type):
                        type1.append(cw_type)
            if(len(list(set(type1))) != 1 or type1[0] != doc.type):
                frappe.throw(f'Please enter Item with Compound Wall Type as {frappe.bold(doc.type)}')
            elif(type1[0] == "Slab"):
                doc.total_no_of_batche = len(doc.raw_material_consumption)
                    
        doc.abstractcalc()
    
    def abstractcalc(doc):
        labour_cost = float(doc.total_labour_wages or 0) + float(doc.labour_expense_for_curing or 0)
        operator_cost = float(doc.total_operator_wages or 0)
        additional_cost = float(doc.additional_cost_in_wages or 0) + float(doc.additional_cost_unmold or 0)

        item_sqft = {}
        total_sqft = 0
        for row in doc.item_details or []:
            if(row.item not in item_sqft):
                item_sqft[row.item] = 0
            item_sqft[row.item]+=row.ts_production_sqft
            total_sqft+=row.ts_production_sqft
        
        abstract = []
        for item in item_sqft:
            new_row = {}
            new_row['item'] = item
            new_row['item_cost_per_piece'] = (labour_cost / (total_sqft or 1) + operator_cost / (total_sqft or 1) + (doc.strapping_cost_per_sqft_unmold or 0) + additional_cost  / (total_sqft or 1) + (doc.raw_material_cost or 0)  / (total_sqft or 1)) / ( frappe.get_value('Item', item, 'pavers_per_sqft') or throw_error('Pieces Per Sqft', 'Item'))
            abstract.append(new_row)
        doc.update({
            "cw_abstract" : abstract,
            "labour_cost_per_sqft": labour_cost / (total_sqft or 1),
            "operator_cost_per_sqft": operator_cost / (total_sqft or 1),
            "strapping_cost_per_sqft": (doc.strapping_cost_per_sqft_unmold or 0),
            "additional_cost_per_sqft": additional_cost  / (total_sqft or 1),
            "raw_material_cost_per_sqft": (doc.raw_material_cost or 0)  / (total_sqft or 1),
            "total_cost_per_sqft": labour_cost / (total_sqft or 1) + operator_cost / (total_sqft or 1) + (doc.strapping_cost_per_sqft_unmold or 0) + additional_cost  / (total_sqft or 1) + (doc.raw_material_cost or 0)  / (total_sqft or 1)
        })


def throw_error(field, doctype = "Cw Settings"):
    frappe.throw(f"Please enter value for {frappe.bold(field)} in {frappe.bold(doctype)}")


@frappe.whitelist()
def make_stock_entry_for_molding(doc):
    doc = json.loads(doc)
    if(not doc.get('molding_date')):
        frappe.throw("Please Enter Manufacturing Date")
    valid = frappe.get_all("Stock Entry", filters={"cw_usb": doc.get(
            "name"), "stock_entry_type": "Manufacture", "docstatus": ["!=", 2]}, pluck="name")
        
    if len(valid) >= 1:
        frappe.throw("Already Stock Entry Created For Manufacturing: <ul>" + frappe.bold(''.join(["<li>"+frappe.utils.csvutils.getlink('Stock Entry', i)+"</li>" for i in valid]))+ "</ul>")

    stock_entries = []
    default_scrap_warehouse = frappe.db.get_singles_value(
        "CW Settings", "scrap_warehouse") or throw_error("Scrap Warehouse")
    expenses_included_in_valuation = frappe.get_cached_value(
        "Company", doc.get("company"), "expenses_included_in_valuation") or throw_error('Expenses Included In Valuation', doc.get('company'))
    source_warehouse = frappe.db.get_singles_value(
        "CW Settings", "default_molding_source_warehouse") or throw_error('Molding Source Warehouse')
    target_warehouse = frappe.db.get_singles_value(
        "CW Settings", "default_molding_target_warehouse") or throw_error('Molding Target Warehouse')
    
    
    
    default_nos = frappe.db.get_singles_value(
        "CW Settings", "default_molding_uom") or throw_error('Molding UOM')


    for item in doc.get("item_details") or []:
        stock_entry = frappe.new_doc("Stock Entry")
        stock_entry.company = doc.get("company")
        stock_entry.from_bom = 1
        
        stock_entry.cw_usb = doc.get("name")
        stock_entry.set_posting_time = 1
        stock_entry.posting_date = doc.get('molding_date')
        stock_entry.stock_entry_type = "Manufacture"
        stock_entry.bom_no = item.get("bom")

        if (item.get("item")):
            if (not frappe.get_value('Item', item.get("item"), 'has_batch_no')):
                frappe.throw(
                    f'Please choose {frappe.bold("Has Batch No")} for an item {item.get("item")}')
        
    
        if (doc.get("items")):
            for i in doc.get("items"):
                stock_entry.append('items', dict(
                    s_warehouse=(i.get("source_warehouse") or source_warehouse), item_code=i["item_code"], qty=i["qty"]*(item.get("ts_production_sqft")/doc.get("ts_production_sqft")), uom=i["uom"],
                    basic_rate=i['rate'],
                     basic_rate_hidden=i['rate'],
                   
                ))
        else:
            frappe.throw("Kindly Enter Raw Materials")
        manufactue_qty = uom_conversion(item.get("item"), 'Nos', item.get("produced_qty"), default_nos)
        
        stock_entry.append('items', dict(
            t_warehouse = target_warehouse, item_code=item.get("item"), qty= manufactue_qty, uom=default_nos, is_finished_item=1,
                basic_rate=uom_conversion_for_rate(item.get("item"),"SQF",doc.get('total_cost_per_sqft'),default_nos),
                basic_rate_hidden=uom_conversion_for_rate(item.get("item"),"SQF",doc.get('total_cost_per_sqft'),default_nos),
 
        ))
        if item.get("damaged_qty") > 0:
            scrap_qty = uom_conversion(item.get("item"), 'Nos', item.get("damaged_qty"), default_nos)
            stock_entry.append('items', dict(
                t_warehouse=default_scrap_warehouse, item_code=item.get("item"), qty=scrap_qty, uom=default_nos, is_process_loss=1,

            ))
        stock_entry.append('additional_costs', dict(
            expense_account=expenses_included_in_valuation, amount=doc.get("total_expence")*(item.get("ts_production_sqft")/doc.get("ts_production_sqft")), description="It includes labours cost, operators cost and additional cost."
        ))
        stock_entry.insert(ignore_mandatory=True, ignore_permissions=True)
        stock_entry.save()
        stock_entry.submit()
        stock_entries.append(stock_entry.name)
    frappe.msgprint("New Stock Entry Created: <ul>" + frappe.bold(''.join(["<li>"+frappe.utils.csvutils.getlink('Stock Entry', i)+"</li>" for i in stock_entries]))+ "</ul>")
    return "Unmolding"

@frappe.whitelist()
def make_stock_entry_for_bundling(doc):
    doc = json.loads(doc)
    valid = frappe.get_all("Stock Entry", filters={"cw_usb": doc.get(
            "name"), "stock_entry_type": "Manufacture", "docstatus": ["!=", 2]}, pluck="name")
        
    if len(valid) < 1:
        frappe.throw("Please Create Stock Entry For Manufacturing before Unmolding.")
    if(not doc.get('unmolding_date')):
        frappe.throw("Please Enter Unmolding Date")
    valid = frappe.get_all("Stock Entry", filters={"cw_usb": doc.get(
            "name"), "stock_entry_type": "Repack", "docstatus": ["!=", 2]}, pluck="name")
    stock_entries = []
    if len(valid) >= 1:
        frappe.throw("Already Stock Entry Created For Unmolding: <ul>" + frappe.bold(''.join(["<li>"+frappe.utils.csvutils.getlink('Stock Entry', i)+"</li>" for i in valid]))+ "</ul>")

 
    expenses_included_in_valuation = frappe.get_cached_value(
        "Company", doc.get("company"), "expenses_included_in_valuation") or throw_error('Expenses Included In Valuation', doc.get('company'))
    source_warehouse = frappe.db.get_singles_value(
        "CW Settings", "default_unmolding_source_warehouse") or throw_error('Unmolding Source Warehouse')
    target_warehouse = frappe.db.get_singles_value(
        "CW Settings", "default_unmolding_target_warehouse") or throw_error('Unmolding Target Warehouse')
    default_nos = frappe.db.get_singles_value(
            "CW Settings", "default_unmolding_and_bundling_uom") or throw_error('Default Unmolding and Bundling UOM')



    for item in doc.get("cw_manufacturing_batch_details") or []:
        if (item.get("item_code")):
            if (not frappe.get_value('Item', item.get("item_code"), 'has_batch_no')):
                frappe.throw(
                    f'Please choose {frappe.bold("Has Batch No")} for an item {item.get("item_code")}')
        
        
        stock_entry = frappe.new_doc("Stock Entry")
        stock_entry.company = doc.get("company")
        stock_entry.cw_usb = doc.get("name")
        stock_entry.stock_entry_type = "Repack"
        
        
        stock_entry.set_posting_time = 1
        stock_entry.posting_date = doc.get("unmolding_date")
        converted_qty = uom_conversion(item.get('item_code'), item.get("uom"),  item.get('qty') , default_nos)
        
        sqft_qty = uom_conversion(item.get('item_code'), item.get("uom"),  item.get('qty') , "SQF")

        stock_entry.append('items', dict(
            s_warehouse = source_warehouse, item_code = item.get('item_code'), qty = item.get('qty') ,uom = item.get('uom') ,batch_no = item.get("batch"),
             basic_rate=uom_conversion_for_rate(item.get("item_code"),"SQF",doc.get('total_cost_per_sqft'), item.get('uom')),
                  basic_rate_hidden=uom_conversion_for_rate(item.get("item_code"),"SQF",doc.get('total_cost_per_sqft'), item.get('uom')),
            )) 
        stock_entry.append('items', dict(
            t_warehouse = target_warehouse, item_code = item.get('item_code'), qty = converted_qty,uom = default_nos,
                  basic_rate=uom_conversion_for_rate(item.get("item_code"),"SQF",doc.get('total_cost_per_sqft'),default_nos),
                  basic_rate_hidden=uom_conversion_for_rate(item.get("item_code"),"SQF",doc.get('total_cost_per_sqft'),default_nos),
            ))
        stock_entry.append('additional_costs', dict(
                expense_account	 = expenses_included_in_valuation, amount = doc.get("total_expense_for_unmolding") * (sqft_qty/doc.get("ts_production_sqft")), description = "It includes strapping cost and additional cost."
            ))
        stock_entry.insert(ignore_mandatory=True, ignore_permissions=True)
        stock_entry.save()
        stock_entry.submit()
        stock_entries.append(stock_entry.name)
    frappe.msgprint("New Stock Entry Created: <ul>" + frappe.bold(''.join(["<li>"+frappe.utils.csvutils.getlink('Stock Entry', i)+"</li>" for i in stock_entries]))+ "</ul>")
    return "Curing"


@frappe.whitelist()
def make_stock_entry_for_curing(doc):
    doc = json.loads(doc)
    valid = frappe.get_all("Stock Entry", filters={"cw_usb": doc.get(
            "name"), "stock_entry_type": "Repack", "docstatus": ["!=", 2]}, pluck="name")
        
    if len(valid) < 1:
        frappe.throw("Please Create Stock Entry For Unmolding before Curing.")
    if(not doc.get('curing_date')):
        frappe.throw("Please Enter Curing Date")
    valid = frappe.get_all("Stock Entry", filters={"cw_usb": doc.get(
            "name"), "stock_entry_type": "Material Transfer", "docstatus": ["!=", 2]}, pluck="name")
    stock_entries = []
    if len(valid) >= 1:
        frappe.throw("Already Stock Entry Created For Curing: <ul>" + frappe.bold(''.join(["<li>"+frappe.utils.csvutils.getlink('Stock Entry', i)+"</li>" for i in valid]))+ "</ul>")

    expenses_included_in_valuation = frappe.get_cached_value(
        "Company", doc.get("company"), "expenses_included_in_valuation") or throw_error('Expenses Included In Valuation', doc.get('company'))
    source_warehouse = frappe.db.get_singles_value(
        "CW Settings", "default_curing_source_warehouse") or throw_error('Curing Source Warehouse')
    target_warehouse = frappe.db.get_singles_value(
        "CW Settings", "default_curing_target_warehouse") or throw_error('Curing Target Warehouse')
    
   

    for item in doc.get("cw_unmolding_batch_details") or []:
        stock_entry = frappe.new_doc("Stock Entry")
        stock_entry.company = doc.get("company")
        stock_entry.cw_usb = doc.get("name")
        stock_entry.stock_entry_type = "Material Transfer"
        stock_entry.set_posting_time = 1
        stock_entry.posting_date = doc.get("curing_date")
        if (item.get("item_code")):
            if (not frappe.get_value('Item', item.get("item_code"), 'has_batch_no')):
                frappe.throw(
                    f'Please choose {frappe.bold("Has Batch No")} for an item {item.get("item_code")}')

        sqft_qty = uom_conversion(item.get('item_code'), item.get("uom"),  item.get('qty') , "SQF")
        stock_entry.append('items', dict(
            s_warehouse = source_warehouse, item_code = item.get("item_code"),qty = item.get('qty') ,uom = item.get('uom') ,batch_no = item.get("batch"),
            t_warehouse = target_warehouse,
                   basic_rate=uom_conversion_for_rate(item.get("item_code"),"SQF",doc.get('total_cost_per_sqft'),item.get("uom")),
                    basic_rate_hidden=uom_conversion_for_rate(item.get("item_code"),"SQF",doc.get('total_cost_per_sqft'),item.get("uom")),
            ))
        stock_entry.append('additional_costs', dict(
                expense_account	 = expenses_included_in_valuation, amount = doc.get("labour_expense_for_curing") * (sqft_qty/doc.get("ts_production_sqft")),description = "It includes labours cost."
            ))
        stock_entry.insert(ignore_mandatory=True, ignore_permissions=True)
        stock_entry.save()
        stock_entry.submit()
        stock_entries.append(stock_entry.name)
    frappe.msgprint("New Stock Entry Created: <ul>" + frappe.bold(''.join(["<li>"+frappe.utils.csvutils.getlink('Stock Entry', i)+"</li>" for i in stock_entries]))+ "</ul>")
    return "Completed"


def get_valuation_rate(item_code):
    warehouse =  frappe.db.get_singles_value(
        "CW Settings", "default_molding_source_warehouse") or throw_error('Molding Source Warehouse')
    rate = frappe.get_all('Bin', {'item_code': item_code, 'warehouse': warehouse}, pluck= 'valuation_rate')
    if rate:
        return rate[0]
    else:
        return 0


@frappe.whitelist()
def std_item(doc):
    items = {}
    doc = json.loads(doc)
    if doc.get('cement_item_name') and doc.get('cement_qty'):
        row = {}
        row['item_code'], row['stock_uom'], row['uom'], row['rate'], row['validation_rate'] = frappe.get_value(
            "Item", doc['cement_item_name'], ['item_code', 'stock_uom', 'stock_uom', 'last_purchase_rate', 'valuation_rate'])
        row['qty'] = doc.get('cement_qty')
        row['validation_rate'] = get_valuation_rate(row['item_code'])
        row['amount'] = doc.get('cement_qty') * (row['rate'] or row['validation_rate'])
        items[row['item_code']] = row
    if doc.get('ggbs_item_name') and doc.get('cement_qty'):
        row = {}
        row['item_code'], row['stock_uom'], row['uom'], row['rate'], row['validation_rate'] = frappe.get_value(
            "Item", doc['ggbs_item_name'], ['item_code', 'stock_uom', 'stock_uom', 'last_purchase_rate', 'valuation_rate'])
        row['qty'] = doc.get('ggbs_qty')
        row['validation_rate'] = get_valuation_rate(row['item_code'])
        row['amount'] = doc.get('ggbs_qty') * (row['rate'] or row['validation_rate'])
        items[row['item_code']] = row
    if doc.get('post_chips') and doc.get('post_chips_qty'):
        row = {}
        row['item_code'], row['stock_uom'], row['uom'], row['rate'], row['validation_rate'] = frappe.get_value(
            "Item", doc['post_chips'], ['item_code', 'stock_uom', 'stock_uom', 'last_purchase_rate', 'valuation_rate'])
        row['qty'] = doc.get('post_chips_qty')
        row['validation_rate'] = get_valuation_rate(row['item_code'])
        row['amount'] = doc.get('post_chips_qty') * (row['rate'] or row['validation_rate'])
        items[row['item_code']] = row
    if doc.get('slab_chips_item_name') and doc.get('slab_chips_qty'):
        row = {}
        row['item_code'], row['stock_uom'], row['uom'], row['rate'], row['validation_rate'] = frappe.get_value(
            "Item", doc['slab_chips_item_name'], ['item_code', 'stock_uom', 'stock_uom', 'last_purchase_rate', 'valuation_rate'])
        row['qty'] = doc.get('slab_chips_qty')
        row['validation_rate'] = get_valuation_rate(row['item_code'])
        row['amount'] = doc.get('slab_chips_qty') * (row['rate'] or row['validation_rate'])
        items[row['item_code']] = row
    if doc.get('m_sand_item_name') and doc.get('m_sand_qty'):
        row = {}
        row['item_code'], row['stock_uom'], row['uom'], row['rate'], row['validation_rate'] = frappe.get_value(
            "Item", doc['m_sand_item_name'], ['item_code', 'stock_uom', 'stock_uom', 'last_purchase_rate', 'valuation_rate'])
        row['qty'] = doc.get('m_sand_qty')
        row['validation_rate'] = get_valuation_rate(row['item_code'])
        row['amount'] = doc.get('m_sand_qty') * (row['rate'] or row['validation_rate'])
        items[row['item_code']] = row
    bom_list = []
    for row in doc.get('item_details') or  []:
        if(row.get('bom') and row.get('bom') not in bom_list):
            bom_list.append(row.get('bom'))
    for bom in bom_list:
        bom_doc = frappe.get_doc("BOM", bom)
        for item in bom_doc.items:
            if(item.is_usb_item and item.item_code in items):
                if item.qty:
                    items[item.item_code]['ts_qty'] = item.qty
                if 'ts_qty' not in items[item.item_code]:
                    items[item.item_code]['ts_qty']=0
                if item.source_warehouse:
                    items[item.item_code]['source_warehouse'] = item.source_warehouse
                if 'source_warehouse' not in items[item.item_code]:
                    items[item.item_code]['source_warehouse']=''
    for row in doc.get('item_details') or  []:
        if row.get('workstation'):
            for item in items:            
                ws_warehouse=get_items_warehosue_from_workstation(items[item]['item_code'], 1, row.get('workstation'))
                if ws_warehouse:
                    items[item]['source_warehouse']=ws_warehouse
    return list(items.values())



@frappe.whitelist()
def find_batch(name):
    manufacture_batch_list = []
    unmolding_batch_list = []
    curing_batch_list = []
    if name:
        stock = frappe.get_all("Stock Entry",filters={"cw_usb":name,"docstatus":1},fields=['name','stock_entry_type'])
        for i in stock:
            if i.stock_entry_type == "Manufacture":
                batch = frappe.get_doc("Stock Entry",i.name)
                for j in batch.items:
                    if j.t_warehouse and j.is_finished_item and not j.is_process_loss:
                        manufacture_batch_list.append({'item_code': j.item_code, 'batch': j.batch_no, 'qty': j.qty, 'uom': j.uom})
                        
            elif i.stock_entry_type == "Repack":
                batch = frappe.get_doc("Stock Entry",i.name)
                for j in batch.items:
                    if j.t_warehouse and j.is_finished_item and not j.is_process_loss:
                        unmolding_batch_list.append({'item_code': j.item_code, 'batch': j.batch_no, 'qty': j.qty, 'uom': j.uom})
            elif i.stock_entry_type == "Material Transfer":
                batch = frappe.get_doc("Stock Entry",i.name)
                for j in batch.items:
                    if j.t_warehouse and j.s_warehouse:
                        curing_batch_list.append({'item_code': j.item_code, 'batch': j.batch_no, 'qty': j.qty, 'uom': j.uom})
    return manufacture_batch_list, unmolding_batch_list, curing_batch_list

@frappe.whitelist()
def uom_conversion(item, from_uom='', from_qty=0, to_uom=''):
    if(not from_uom):
        from_uom = frappe.get_value('Item', item, 'stock_uom')
    item_doc = frappe.get_doc('Item', item)
    from_conv = 0
    to_conv = 0
    for row in item_doc.uoms:
        if(row.uom == from_uom):
            from_conv = row.conversion_factor
        if(row.uom == to_uom):
            to_conv = row.conversion_factor
    if(not from_conv):
        throw_error(from_uom + " Conversion", item)
    if(not to_conv):
        throw_error(to_uom + " Conversion", item)
    
    return (float(from_qty) * from_conv) / to_conv


def uom_conversion_for_rate(item, from_uom, price, to_uom):
    item_doc = frappe.get_doc('Item', item)
    from_conv = 0
    to_conv = 0
    for row in item_doc.uoms:
        if(row.uom == from_uom):
            from_conv = row.conversion_factor
        if(row.uom == to_uom):
            to_conv = row.conversion_factor
    if(not from_conv):
        throw_error(from_uom + " Bundle Conversion", "Item")
    if(not to_conv):
        throw_error(to_uom + " Bundle Conversion", 'Item')
 
    return (float(price) * from_conv) * to_conv

@frappe.whitelist()
def get_operators(doc, item_count=1):
    item_count = int(item_count)
    doc = json.loads(doc)
    op_table=[]
    op_list=[]
    if(len(doc)>0):
        for i in doc:
            op_cost= frappe.get_doc("Workstation",i.get('workstation'))
            for j in op_cost.ts_operators_table:
                if(j.ts_operator_name not in op_list):
                    op_list.append(j.ts_operator_name)
                    op_table.append({"employee":j.ts_operator_name,"operator_name":j.ts_operator_full_name,"salary":j.ts_operator_wages, "division_salary":(j.ts_operator_wages/item_count)})
                else:
                    for k in op_table:
                        if k['employee'] == j.ts_operator_name:
                            k['salary'] = j.ts_operator_wages
                            k["division_salary"] = (j.ts_operator_wages/item_count)
    return(op_table)


@frappe.whitelist()
def get_working_hrs(attendance_date, machine):
    attn = frappe.get_all("Attendance", { "attendance_date": attendance_date, "machine": machine, "docstatus": 1},
                     pluck="working_hours")
    attn = [float(att) if(att) else 0 for att in attn]
    return {'hours':sum(attn), 'labours': len(attn)}


@frappe.whitelist()
def add_item(doc, batches = 1):
    items={}
    type1=[]
    doc=json.loads(doc)
    item_table_len = 0
    if(len(doc)>0):
        for row in doc:
            if(row.get('bom')):
                item_table_len += 1
            if(row.get('item')):
                cw_type = frappe.get_value("Item", row.get('item'), 'compound_wall_type')
                if(cw_type):
                    type1.append(cw_type)
        if(len(list(set(type1))) != 1):
            frappe.throw('Please enter either Post or Slab.')
        else:
            type1 = type1[0]
        for k in doc:
            no_of_batches = (k.get('no_of_batches') or 0) if(type1 == 'Post') else float(batches)/item_table_len
            if(k.get('bom')):
                bom_doc = frappe.get_doc("BOM",k.get('bom'))
                fields = ['item_code','qty', 'uom', 'stock_uom', 'rate', 'amount', 'source_warehouse']
                for i in bom_doc.items:
                    if(i.is_usb_item == 0):
                        if(i.item_code not in items):
                            row = {field:i.__dict__[field] for field in fields}
                            row['ts_qty'] = row['qty']
                            row['qty'] *= no_of_batches
                            row['amount'] *= no_of_batches
                            items.update({i.item_code: row})
                        else:
                            items[i.item_code]['qty'] += (no_of_batches * i.qty)
                            items[i.item_code]['amount'] += (no_of_batches * i.amount)
        for k in doc:
            if k.get('workstation'):
                for row in list(items.values()):
                    ws_warehouse=get_items_warehosue_from_workstation(row['item_code'], 0, k.get('workstation'))
                    if ws_warehouse:
                        row['source_warehouse']=ws_warehouse           
        
    return list(items.values())
           
def get_items_warehosue_from_workstation(item_code : str, is_usb_item : int, workstation : str) -> str:
   ws=frappe.get_doc("Workstation", workstation)
   for row in ws.raw_material_warehouse:
      if row.is_usb_item!=(is_usb_item or 0):
         continue
      if row.item_code==item_code:
         return row.source_warehouse
