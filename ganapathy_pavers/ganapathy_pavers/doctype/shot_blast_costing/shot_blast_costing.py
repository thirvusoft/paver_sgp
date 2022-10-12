# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

# import frappe
import json
import frappe
from frappe.model.document import Document
from erpnext.stock.doctype.batch.batch import get_batch_qty

class ShotBlastCosting(Document):
    def before_submit(doc):
        material = frappe.get_all("Stock Entry",filters={"shot_blast":doc.get("name"),"stock_entry_type":"Material Transfer"},pluck="name")
        if len(material) == 0:
            frappe.throw("Process Incomplete. Create Stock Entry To Submit")
        for i in doc.items:
            frappe.db.set_value("Material Manufacturing",i.material_manufacturing,'shot_blasted_bundle', i.bundle-i.bundle_taken)
            if i.bundle-i.bundle_taken == 0:
                frappe.db.set_value("Material Manufacturing",i.material_manufacturing,'status1', "Completed")
@frappe.whitelist()
def make_stock_entry(doc):
    doc=json.loads(doc)
    if doc.get("total_cost") == 0 or doc.get("total_bundle") == 0 :
            frappe.throw("Please Enter All Fields")
    valid = frappe.get_all("Stock Entry",filters={"shot_blast":doc.get("name"),"stock_entry_type":"Material Transfer","docstatus":["!=",2]},pluck="name")
    if len(valid) >= 1:
        frappe.throw("Already Stock Entry("+valid[0]+") Created")
    default_scrap_warehouse = frappe.db.get_singles_value("USB Setting", "scrap_warehouse")
    expenses_included_in_valuation = frappe.get_cached_value("Company", doc.get("company"), "expenses_included_in_valuation")
    stock_entry = frappe.new_doc("Stock Entry")
    stock_entry.company = doc.get("company")
    stock_entry.shot_blast = doc.get("name")
    stock_entry.set_posting_time = 1
    stock_entry.posting_date = frappe.utils.formatdate(doc.get("to_time"), "yyyy-MM-dd")
    default_nos = frappe.db.get_singles_value("USB Setting", "default_manufacture_uom")
    default_bundle = frappe.db.get_singles_value("USB Setting", "default_rack_shift_uom")
    stock_entry.stock_entry_type = "Material Transfer"
    for i in doc.get("items"):
        stock_entry.append('items', dict(
        s_warehouse = doc.get("source_warehouse"),t_warehouse = doc.get("warehouse"), item_code = i["item_name"],qty = i["sqft"]-i["damages_in_sqft"], uom = frappe.db.get_value("Item", i["item_name"], "stock_uom"),batch_no = i["batch"]
        ))
        if i["damages_in_nos"] > 0:
            stock_entry.append('items', dict(
                s_warehouse = doc.get("source_warehouse"),t_warehouse = default_scrap_warehouse, item_code = i["item_name"]	,qty = i["damages_in_nos"], uom = default_nos, is_process_loss = 1
                ))
    stock_entry.append('additional_costs', dict(
            expense_account	 = expenses_included_in_valuation, amount = doc.get("total_cost"),description = "In Shot Blast, Cost of Labour and Additional"
        ))
    stock_entry.insert(ignore_mandatory=True, ignore_permissions=True)
    stock_entry.save()
    stock_entry.submit()
    frappe.msgprint("New Stock Entry Created "+stock_entry.name)

@frappe.whitelist()
def uom_conversion(item, batch=None, to_uom=None, mm=None):
    if(not mm):
        warehouse=frappe.db.get_single_value("USB Setting", 'default_curing_target_warehouse_for_setting')
    else:
        warehouse=frappe.get_value('Material Manufacturing', mm, 'curing_target_warehouse')
    if batch:
        batch_qty = get_batch_qty(batch_no=batch, warehouse=warehouse ) or 0
        from_uom = frappe.get_value("Batch", batch, "stock_uom")
        if batch_qty:
            from_qty = batch_qty
        item_doc = frappe.get_doc('Item', item)
        from_conv = 0
        to_conv = 0
        for row in item_doc.uoms:
            if(row.uom == from_uom):
                from_conv = row.conversion_factor
            if(row.uom == to_uom):
                to_conv = row.conversion_factor

        if(not from_conv):
            frappe.msgprint(f"Assign {from_uom} conversion factor for {item}")
        if(not to_conv):
            frappe.msgprint(f"Assign {to_uom} conversion factor for {item}")
        
        if from_conv and to_conv:
            return (float(from_qty) * from_conv) / to_conv
        else:
            return 0
    else:
        return 0