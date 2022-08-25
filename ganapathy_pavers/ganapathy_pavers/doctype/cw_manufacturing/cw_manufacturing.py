# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

import frappe
import json

from frappe.model.document import Document


class CWManufacturing(Document):
    pass


@frappe.whitelist()
def make_stock_entry(doc, type1):
    doc = json.loads(doc)
    if (doc.get("item_to_manufacture")):
        if (not frappe.get_value('Item', doc.get("item_to_manufacture"), 'has_batch_no')):
            frappe.throw(
                f'Please choose {frappe.bold("Has Batch No")} for an item {doc.get("item_to_manufacture")}')

    if doc.get("total_completed_qty") == 0 or doc.get("cement_item") == '' or doc.get("ggbs_item") == '' or doc.get("total_expense") == 0:
        frappe.throw(
            "Please Enter the Produced Qty and From Time - To Time in Manufacture Section and Save This Form")
    default_scrap_warehouse = frappe.db.get_singles_value(
        "USB Setting", "scrap_warehouse")
    expenses_included_in_valuation = frappe.get_cached_value(
        "Company", doc.get("company"), "expenses_included_in_valuation")
    stock_entry = frappe.new_doc("Stock Entry")
    stock_entry.company = doc.get("company")
    stock_entry.form_bom = 1
    stock_entry.bom_no = doc.get("bom_no")
    stock_entry.usb = doc.get("name")
    default_nos = frappe.db.get_singles_value(
        "USB Setting", "default_manufacture_uom")
    default_bundle = frappe.db.get_singles_value(
        "USB Setting", "default_rack_shift_uom")
    if doc.get("stock_entry_type") == "Manufacture" and type1 == "create_stock_entry":
        valid = frappe.get_all("Stock Entry", filters={"usb": doc.get(
            "name"), "stock_entry_type": "Manufacture", "docstatus": ["!=", 2]}, pluck="name")
        stock_entry.set_posting_time = 1
        stock_entry.posting_date = frappe.utils.formatdate(
            doc.get("to"), "yyyy-MM-dd")
        if len(valid) >= 1:
            frappe.throw(
                "Already Stock Entry("+valid[0]+") Created For Manufacture")
        stock_entry.stock_entry_type = doc.get("stock_entry_type")
        if (doc.get("items")):
            for i in doc.get("items"):
                stock_entry.append('items', dict(
                    s_warehouse=doc.get("source_warehouse"), item_code=i["item_code"], qty=i["qty"], uom=i["uom"],
                    basic_rate=i["rate"]
                ))
        else:
            frappe.throw("Kindly Save this Form")
        stock_entry.append('items', dict(
            t_warehouse=doc.get("target_warehouse"), item_code=doc.get("item_to_manufacture"), qty=doc.get("total_completed_qty"), uom=default_nos, is_finished_item=1
        ))
        if doc.get("damage_qty") > 0:
            if default_scrap_warehouse:
                stock_entry.append('items', dict(
                    t_warehouse=default_scrap_warehouse, item_code=doc.get("item_to_manufacture"), qty=doc.get("damage_qty"), uom=default_nos, is_process_loss=1
                ))
            else:
                frappe.throw("Set Scrap Warehouse in USB Setting")
        stock_entry.append('additional_costs', dict(
            expense_account=expenses_included_in_valuation, amount=doc.get("total_expense"), description="In This Labour, operator, Raw Material Cost Added"
        ))
        stock_entry.insert(ignore_mandatory=True, ignore_permissions=True)
        stock_entry.save()
        stock_entry.submit()
        frappe.msgprint("New Stock Entry Created "+stock_entry.name)
