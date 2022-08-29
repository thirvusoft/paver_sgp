# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

from erpnext.stock.doctype import manufacturer
import frappe
import json

from frappe.model.document import Document


class CWManufacturing(Document):
    def before_submit(doc):
        manufacture = frappe.get_all("Stock Entry",filters={"cw_usb":doc.get("name"),"stock_entry_type":"Manufacture"},pluck="name")
        repack = frappe.get_all("Stock Entry",filters={"cw_usb":doc.get("name"),"stock_entry_type":"Repack"},pluck="name")
        material = frappe.get_all("Stock Entry",filters={"cw_usb":doc.get("name"),"stock_entry_type":"Material Transfer"},pluck="name")
        if len(manufacture) == 0 or len(repack) == 0 or len(material) == 0:
            frappe.throw("Process Incomplete. Create Stock Entry To Submit")
        if(doc.status1 != "Completed"):
            frappe.throw(f"Please change the status to {frappe.bold('Completed')} before submitting.")


def throw_error(field, doctype = "Cw Settings"):
    frappe.throw(f"Please enter value for {frappe.bold(field)} in {frappe.bold(doctype)}")

@frappe.whitelist()
def make_stock_entry_for_molding(doc):
    doc = json.loads(doc)
    if (doc.get("item_to_manufacture")):
        if (not frappe.get_value('Item', doc.get("item_to_manufacture"), 'has_batch_no')):
            frappe.throw(
                f'Please choose {frappe.bold("Has Batch No")} for an item {doc.get("item_to_manufacture")}')

    default_scrap_warehouse = frappe.db.get_singles_value(
        "CW Settings", "scrap_warehouse") or throw_error("Scrap Warehouse")
    expenses_included_in_valuation = frappe.get_cached_value(
        "Company", doc.get("company"), "expenses_included_in_valuation") or throw_error('Expenses Included In Valuation', doc.get('company'))
    source_warehouse = frappe.db.get_singles_value(
        "CW Settings", "default_molding_source_warehouse") or throw_error('Molding Source Warehouse')
    target_warehouse = frappe.db.get_singles_value(
        "CW Settings", "default_molding_target_warehouse") or throw_error('Molding Target Warehouse')
    stock_entry = frappe.new_doc("Stock Entry")
    stock_entry.company = doc.get("company")
    stock_entry.from_bom = 1
    stock_entry.bom_no = doc.get("bom")
    stock_entry.cw_usb = doc.get("name")
    default_nos = frappe.db.get_singles_value(
        "CW Settings", "default_molding_uom") or throw_error('Molding UOM')
    valid = frappe.get_all("Stock Entry", filters={"cw_usb": doc.get(
        "name"), "stock_entry_type": "Manufacture", "docstatus": ["!=", 2]}, pluck="name")
    stock_entry.set_posting_time = 1
    stock_entry.posting_date = doc.get('molding_date')
    if len(valid) >= 1:
        frappe.throw(
            "Already Stock Entry ("+valid[0]+") Created For Molding")
    stock_entry.stock_entry_type = "Manufacture"
    if (doc.get("items")):
        for i in doc.get("items"):
            stock_entry.append('items', dict(
                s_warehouse=(doc.get("source_warehouse") or source_warehouse), item_code=i["item_code"], qty=i["qty"], uom=i["uom"],
                basic_rate=i["rate"]
            ))
    else:
        frappe.throw("Kindly Enter Raw Materials")
    manufactue_qty = uom_conversion(doc.get('item_to_manufacture'), 'Nos', doc.get("produced_qty"), default_nos)
    
    stock_entry.append('items', dict(
        t_warehouse = target_warehouse, item_code=doc.get("item_to_manufacture"), qty= manufactue_qty, uom=default_nos, is_finished_item=1
    ))
    if doc.get("damaged_qty") > 0:
        scrap_qty = uom_conversion(doc.get('item_to_manufacture'), 'Nos', doc.get("damaged_qty"), default_nos)
        stock_entry.append('items', dict(
            t_warehouse=default_scrap_warehouse, item_code=doc.get("item_to_manufacture"), qty=scrap_qty, uom=default_nos, is_process_loss=1
        ))
    stock_entry.append('additional_costs', dict(
        expense_account=expenses_included_in_valuation, amount=doc.get("total_expense"), description="It includes labours cost, operators cost and additional cost."
    ))
    stock_entry.insert(ignore_mandatory=True, ignore_permissions=True)
    stock_entry.save()
    stock_entry.submit()
    frappe.msgprint("New Stock Entry Created "+stock_entry.name)
    return "Unmolding"

@frappe.whitelist()
def make_stock_entry_for_bundling(doc):
    doc = json.loads(doc)
    
    if (doc.get("item_to_manufacture")):
        if (not frappe.get_value('Item', doc.get("item_to_manufacture"), 'has_batch_no')):
            frappe.throw(
                f'Please choose {frappe.bold("Has Batch No")} for an item {doc.get("item_to_manufacture")}')
    rem_qty = remaining_qty(doc.get('item_to_manufacture'), doc.get('type'), doc.get('remaining_qty_from_bundles') or 0) or 0

    default_scrap_warehouse = frappe.db.get_singles_value(
        "CW Settings", "scrap_warehouse") or throw_error("Scrap Warehouse")
    expenses_included_in_valuation = frappe.get_cached_value(
        "Company", doc.get("company"), "expenses_included_in_valuation") or throw_error('Expenses Included In Valuation', doc.get('company'))
    source_warehouse = frappe.db.get_singles_value(
        "CW Settings", "default_unmolding_source_warehouse") or throw_error('Unmolding Source Warehouse')
    target_warehouse = frappe.db.get_singles_value(
        "CW Settings", "default_unmolding_target_warehouse") or throw_error('Unmolding Target Warehouse')
    stock_entry = frappe.new_doc("Stock Entry")
    stock_entry.company = doc.get("company")
    stock_entry.cw_usb = doc.get("name")
    stock_entry.stock_entry_type = "Repack"
    default_nos = frappe.db.get_singles_value(
        "CW Settings", "default_unmolding_and_bundling_uom") or throw_error('Default Unmolding and Bundling UOM')
    manufacture_uom = frappe.db.get_singles_value(
        "CW Settings", "default_molding_uom") or throw_error('Molding UOM')
    valid = frappe.get_all("Stock Entry", filters={"cw_usb": doc.get(
        "name"), "stock_entry_type": "Repack", "docstatus": 1}, pluck="name")
    if len(valid) >= 1:
            frappe.throw("Already Stock Entry ("+valid[0]+") Created For Repack.")
    stock_entry.set_posting_time = 1
    stock_entry.posting_date = doc.get("unmolding_date")
    manufacture_qty = (doc.get('no_of_bundle_unmold') + (rem_qty or 0)) * (frappe.get_value('Item', doc.get('item_to_manufacture'), 'pavers_per_bundle') or throw_error('Pieces Per Bundle', doc.get('item_to_manufacture')))
    manufacture_qty = uom_conversion(doc.get('item_to_manufacture'), 'Nos', manufacture_qty, manufacture_uom)
    converted_qty = uom_conversion(doc.get('item_to_manufacture'), manufacture_uom, manufacture_qty, default_nos)
    stock_entry.append('items', dict(
        s_warehouse = source_warehouse, item_code = doc.get("item_to_manufacture"),qty = manufacture_qty ,uom = manufacture_uom ,batch_no = doc.get("molding_batch")
        )) 
    stock_entry.append('items', dict(
        t_warehouse = target_warehouse, item_code = doc.get("item_to_manufacture"),qty = converted_qty,uom = default_nos
        ))
    if doc.get("damaged_qty_at_bundling") > 0:
        scrap_qty = uom_conversion(doc.get('item_to_manufacture'), "Nos", doc.get("damaged_qty_at_bundling"), default_nos)
        stock_entry.append('items', dict(
            t_warehouse = default_scrap_warehouse, item_code = doc.get("item_to_manufacture"),qty =  scrap_qty ,uom = default_nos,  is_process_loss = 1
            ))
    stock_entry.append('additional_costs', dict(
            expense_account	 = expenses_included_in_valuation, amount = doc.get("total_expense_for_unmolding"),description = "It includes labours cost, operators cost and additional cost."
        ))
    stock_entry.insert(ignore_mandatory=True, ignore_permissions=True)
    stock_entry.save()
    stock_entry.submit()
    frappe.msgprint("New Stock Entry Created "+stock_entry.name)
    return "Curing"


@frappe.whitelist()
def make_stock_entry_for_curing(doc):
    doc = json.loads(doc)
    
    if (doc.get("item_to_manufacture")):
        if (not frappe.get_value('Item', doc.get("item_to_manufacture"), 'has_batch_no')):
            frappe.throw(
                f'Please choose {frappe.bold("Has Batch No")} for an item {doc.get("item_to_manufacture")}')

    expenses_included_in_valuation = frappe.get_cached_value(
        "Company", doc.get("company"), "expenses_included_in_valuation") or throw_error('Expenses Included In Valuation', doc.get('company'))
    source_warehouse = frappe.db.get_singles_value(
        "CW Settings", "default_curing_source_warehouse") or throw_error('Curing Source Warehouse')
    target_warehouse = frappe.db.get_singles_value(
        "CW Settings", "default_curing_target_warehouse") or throw_error('Curing Target Warehouse')
    stock_entry = frappe.new_doc("Stock Entry")
    stock_entry.company = doc.get("company")
    stock_entry.cw_usb = doc.get("name")
    stock_entry.stock_entry_type = "Material Transfer"
    stock_entry.set_posting_time = 1
    stock_entry.posting_date = doc.get("curing_date")
    default_nos = frappe.db.get_singles_value(
        "CW Settings", "default_unmolding_and_bundling_uom") or throw_error('Default Unmolding and Bundling UOM')
    valid = frappe.get_all("Stock Entry", filters={"cw_usb": doc.get(
        "name"), "stock_entry_type": "Material Transfer", "docstatus": 1}, pluck="name")
    if len(valid) >= 1:
            frappe.throw("Already Stock Entry ("+valid[0]+") Created For Curing.")
    manufacture_qty = doc.get('no_of_bundle_curing')  * (frappe.get_value('Item', doc.get('item_to_manufacture'), 'pavers_per_bundle') or throw_error('Pieces Per Bundle', doc.get('item_to_manufacture')))
    manufacture_qty = uom_conversion(doc.get('item_to_manufacture'), 'Nos', manufacture_qty, default_nos)
    stock_entry.append('items', dict(
        s_warehouse = source_warehouse, item_code = doc.get("item_to_manufacture"),qty = manufacture_qty ,uom = default_nos ,batch_no = doc.get("unmolding_batch"),
        t_warehouse = target_warehouse, 
        ))
    stock_entry.append('additional_costs', dict(
            expense_account	 = expenses_included_in_valuation, amount = doc.get("labour_expense_for_curing"),description = "It includes labours cost."
        ))
    stock_entry.insert(ignore_mandatory=True, ignore_permissions=True)
    stock_entry.save()
    stock_entry.submit()
    frappe.msgprint("New Stock Entry Created "+stock_entry.name)
    return "Completed"

@frappe.whitelist()
def std_item(doc):
    items = []
    doc = json.loads(doc)
    if doc.get('cement_item_name') and doc.get('cement_qty'):
        row = {}
        row['item_code'], row['stock_uom'], row['uom'], row['rate'], row['validation_rate'] = frappe.get_value(
            "Item", doc['cement_item_name'], ['item_code', 'stock_uom', 'stock_uom', 'last_purchase_rate', 'valuation_rate'])
        row['qty'] = doc.get('cement_qty')
        row['amount'] = doc.get('cement_qty') * \
            (row['rate'] or row['validation_rate'])
        items.append(row)
    if doc.get('ggbs_item_name') and doc.get('cement_qty'):
        row = {}
        row['item_code'], row['stock_uom'], row['uom'], row['rate'], row['validation_rate'] = frappe.get_value(
            "Item", doc['ggbs_item_name'], ['item_code', 'stock_uom', 'stock_uom', 'last_purchase_rate', 'valuation_rate'])
        row['qty'] = doc.get('ggbs_qty')
        row['amount'] = doc.get('ggbs_qty') * \
            (row['rate'] or row['validation_rate'])
        items.append(row)
    if doc.get('post_chips') and doc.get('post_chips_qty') and doc.get("type") == "Post":
        row = {}
        row['item_code'], row['stock_uom'], row['uom'], row['rate'], row['validation_rate'] = frappe.get_value(
            "Item", doc['post_chips'], ['item_code', 'stock_uom', 'stock_uom', 'last_purchase_rate', 'valuation_rate'])
        row['qty'] = doc.get('post_chips_qty')
        row['amount'] = doc.get('post_chips_qty') * \
            (row['rate'] or row['validation_rate'])
        items.append(row)
    if doc.get('slab_chips_item_name') and doc.get('slab_chips_qty') and doc.get("type") == "Slab":
        row = {}
        row['item_code'], row['stock_uom'], row['uom'], row['rate'], row['validation_rate'] = frappe.get_value(
            "Item", doc['slab_chips_item_name'], ['item_code', 'stock_uom', 'stock_uom', 'last_purchase_rate', 'valuation_rate'])
        row['qty'] = doc.get('slab_chips_qty')
        row['amount'] = doc.get('slab_chips_qty') * \
            (row['rate'] or row['validation_rate'])
        items.append(row)
    if doc.get('m_sand_item_name') and doc.get('m_sand_qty'):
        row = {}
        row['item_code'], row['stock_uom'], row['uom'], row['rate'], row['validation_rate'] = frappe.get_value(
            "Item", doc['m_sand_item_name'], ['item_code', 'stock_uom', 'stock_uom', 'last_purchase_rate', 'valuation_rate'])
        row['qty'] = doc.get('m_sand_qty')
        row['amount'] = doc.get('m_sand_qty') * \
            (row['rate'] or row['validation_rate'])
        items.append(row)
    return items


def remaining_qty(item, type1, qty):
    if(item):
        bundle_qty = frappe.get_value("Item", item, "pavers_per_bundle") or throw_error('Pieces Per Bundle', 'Item')
        conv_bundle = 0
        rem_doc = frappe.get_single("CW Remaining Qty Details")
        catch1 = 0
        for row in range(len(rem_doc.item_details)):
            if(rem_doc.item_details[row].item == item):
                catch1 = 1
                qty1= round(rem_doc.item_details[row].qty + qty)
                if(qty1 >= bundle_qty):
                    conv_bundle = qty1 // bundle_qty
                    
                    rem_doc.item_details[row].qty = (qty1 % bundle_qty)
                else:
                    rem_doc.item_details[row].qty = qty1
        if(not catch1):
            rem_doc.update({
                'item_details': rem_doc.item_details + [{'item': item, 'type': type1, 'qty': qty}]
            })
        rem_doc.ignore_permissions = True
        rem_doc.ignore_mandatory = True
        rem_doc.save()
        return conv_bundle

@frappe.whitelist()
def find_batch(name):
    manufacture=""
    repack=""
    transfer=""
    if name:
        stock = frappe.get_all("Stock Entry",filters={"cw_usb":name,"docstatus":1},fields=['name','stock_entry_type'])
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

def uom_conversion(item, from_uom, from_qty, to_uom):
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
        throw_error(to_conv + " Bundle Conversion", 'Item')
    
    return (float(from_qty) * from_conv) / to_conv
