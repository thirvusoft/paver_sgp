# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

# import frappe
import json
import frappe
from frappe.model.document import Document
from erpnext.controllers.queries import get_fields

class ShotBlastCosting(Document):
    def before_submit(doc):
        material = frappe.get_all("Stock Entry",filters={"shot_blast":doc.get("name"),"stock_entry_type":"Material Transfer"},pluck="name")
        if len(material) == 0:
            frappe.throw("Process Incomplete. Create Stock Entry To Submit")
    def on_update(doc):
        if doc.docstatus<=1:
            sbc=frappe.db.sql("""
                select material_manufacturing, sum(bundle_taken) as bundle_taken from `tabShot Blast Items` where parent in (select name from `tabShot Blast Costing` where docstatus!=2) group by material_manufacturing;
            """, as_dict=True)
            mm = [i['material_manufacturing'] for i in sbc]
            other_mms = frappe.get_all("Material Manufacturing", filters = {"is_shot_blasting": 1, "name": ["not in", mm]}, fields = ["name as material_manufacturing"])
            for mm in other_mms:
                mm["bundle_taken"] = 0

            for i in sbc + other_mms:
                Bdl=(frappe.db.get_value("Material Manufacturing", i['material_manufacturing'], 'no_of_bundle') or 0)
                frappe.db.set_value("Material Manufacturing",i['material_manufacturing'],'shot_blasted_bundle', Bdl-(i['bundle_taken'] or 0))
                if Bdl-(i['bundle_taken'] or 0) <= 0:
                    frappe.db.set_value("Material Manufacturing",i['material_manufacturing'],'status1', "Completed")
                else:
                    frappe.db.set_value("Material Manufacturing",i['material_manufacturing'],'status1', "Shot Blast")
       

    def on_trash(doc):
        sbc=frappe.db.sql(f"""
            select material_manufacturing, sum(bundle_taken) as bundle_taken from `tabShot Blast Items` where parent in (select name from `tabShot Blast Costing` where docstatus!=2 and name!='{doc.name}') group by material_manufacturing;
        """, as_dict=True)
        # and name!= '{doc.name}'
        mm=frappe.db.sql(f"""
            select material_manufacturing, sum(bundle_taken) as bundle_taken from `tabShot Blast Items` where parent in (select name from `tabShot Blast Costing` where docstatus!=2 and name='{doc.name}') group by material_manufacturing;
        """)
        for mm_doc in mm:
            mm1=frappe.db.sql(f"""
                select name from `tabShot Blast Items` where parent!='{doc.name}' and material_manufacturing='{mm_doc[0]}'
            """)
            if not mm1:
                sbc+=({'material_manufacturing': mm_doc[0], "bundle_taken": 0},)
        mm = [i['material_manufacturing'] for i in sbc]
        other_mms = frappe.get_all("Material Manufacturing", filters = {"is_shot_blasting": 1, "name": ["not in", mm]}, fields = ["name as material_manufacturing"])
        for mm in other_mms:
            mm["bundle_taken"] = 0

        for i in sbc + other_mms:
            Bdl=(frappe.db.get_value("Material Manufacturing", i['material_manufacturing'], 'no_of_bundle') or 0)
            frappe.db.set_value("Material Manufacturing",i['material_manufacturing'],'shot_blasted_bundle', Bdl-(i['bundle_taken'] or 0))
            if Bdl-(i['bundle_taken'] or 0) <= 0:
                frappe.db.set_value("Material Manufacturing",i['material_manufacturing'],'status1', "Completed")
            else:
                frappe.db.set_value("Material Manufacturing",i['material_manufacturing'],'status1', "Shot Blast")

    def on_cancel(doc):
        doc.on_trash()

@frappe.whitelist()
def make_stock_entry(doc):
    doc=json.loads(doc)
    if doc.get("total_cost") == 0:
        frappe.throw("Please Enter Total Expense Cost")
    if doc.get("total_bundle") == 0 :
        frappe.throw("Please Enter Total Bundle")
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
                s_warehouse = doc.get("source_warehouse"),t_warehouse = default_scrap_warehouse, item_code = i["item_name"]	,qty = i["damages_in_nos"], uom = default_nos, is_process_loss = 1,batch_no = i["batch"]
                ))
    stock_entry.append('additional_costs', dict(
            expense_account	 = expenses_included_in_valuation, amount = doc.get("total_cost"),description = "In Shot Blast, Cost of Labour and Additional"
        ))
    stock_entry.insert(ignore_mandatory=True, ignore_permissions=True)
    stock_entry.save()
    stock_entry.submit()
    frappe.msgprint("New Stock Entry Created "+stock_entry.name)

@frappe.whitelist()
def uom_conversion(mm, batch=None):
    if batch:
        batch_qty = frappe.get_value('Material Manufacturing', mm, 'shot_blasted_bundle')
        return batch_qty
    else:
        return 0

@frappe.whitelist()
def batch_query(doctype, txt, searchfield, start, page_len, filters, as_dict=False):
    searchfield = frappe.get_meta(doctype).get_search_fields()
    searchfield = "(" +"or ".join(field + " like %(txt)s" for field in searchfield)
    if filters and filters.get('material_manufacturing'):
        searchfield+=f""") and name='{frappe.get_value("Material Manufacturing", filters.get("material_manufacturing"), "batch_no_curing")}' """
    fields = ', '.join(get_fields(doctype))
    res = frappe.db.sql(
        f"""SELECT 
                {fields} 
            FROM 
                `tab{doctype}` 
            WHERE
                ({searchfield})
            ORDER BY
                (case when locate(%(_txt)s, name) > 0 then locate(%(_txt)s, name) else 99999 end),
                idx desc,
                name
            LIMIT
                {page_len} offset {start}
        """,
        {"txt": "%%%s%%" % txt, "_txt": txt.replace("%", ""), "start": start, "page_len": page_len},
    )
    return res