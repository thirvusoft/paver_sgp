# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

import frappe
import json

from frappe.model.document import Document


class CWManufacturing(Document):
    pass


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
    stock_entry.append('items', dict(
        t_warehouse = target_warehouse, item_code=doc.get("item_to_manufacture"), qty=doc.get("produced_qty"), uom=default_nos, is_finished_item=1
    ))
    if doc.get("damaged_qty") > 0:
        stock_entry.append('items', dict(
            t_warehouse=default_scrap_warehouse, item_code=doc.get("item_to_manufacture"), qty=doc.get("damaged_qty"), uom=default_nos, is_process_loss=1
        ))
    stock_entry.append('additional_costs', dict(
        expense_account=expenses_included_in_valuation, amount=doc.get("total_expense"), description="Labour, Operator and Raw Material Cost Added"
    ))
    stock_entry.insert(ignore_mandatory=True, ignore_permissions=True)
    stock_entry.save()
    stock_entry.submit()
    frappe.msgprint("New Stock Entry Created "+stock_entry.name)
    return "Unmolding"



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
    if doc.get('post_chips_item_name') and doc.get('post_chips_qty') and doc.get("type") == "Post":
        row = {}
        row['item_code'], row['stock_uom'], row['uom'], row['rate'], row['validation_rate'] = frappe.get_value(
            "Item", doc['post_chips_item_name'], ['item_code', 'stock_uom', 'stock_uom', 'last_purchase_rate', 'valuation_rate'])
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
