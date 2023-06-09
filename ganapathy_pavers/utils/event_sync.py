import frappe, json
from frappe.desk.form.load import getdoc
from frappe.event_streaming.doctype.event_producer.event_producer import resync
from frappe.model import default_fields
import re

# from ganapathy_pavers.utils.event_sync import resynccall
# from ganapathy_pavers.utils.event_sync import checkitems

def resynccall():
    frappe.session.siteName = "sgpprime"
    all = frappe.get_all("Event Sync Log", {
        "status": "Failed", 
        "ref_doctype": "Sales Invoice", 
        "issue_fixed": 0
        }, order_by="creation", pluck="name")
    total = len(all)
    success, failed = 0, 0
    print("TOTAL", total)
    for i in all:
        data = frappe.db.get_value("Event Sync Log", i, "data")
        

        data = re.sub(r'"so_detail": "[^"]+",', '', data)
        data = re.sub(r'"dn_detail": "[^"]+",', '', data)
        data = re.sub(r'"sales_order": "[^"]+",', '', data)
        data = re.sub(r'"delivery_note": "[^"]+",', '', data)
        data = re.sub(r'"batch_no": "[^"]+",', '', data)
        data = re.sub(r'"update_stock": 1,', '"update_stock": 0,', data)

        frappe.db.set_value("Event Sync Log", i, "data", data, update_modified=False)

        frappe.response.docs = []
        getdoc("Event Sync Log", i)
        d=json.dumps(frappe.response.docs[0].__dict__, indent=4, sort_keys=True, default=str)
        res = resync(d)
        print(res)
        if res == "Failed":
            failed += 1
        else:
            success += 1
        
        print(total, success, failed)
        frappe.db.set_value("Event Sync Log", i, 'status', res)



def checkitems():
    all = frappe.get_all("Item", {"name": "100*100*70MM -16 CAVITY-SHOT BLAST-BLACK"})
    print(len(all))
    wrong=0
    run=0
    for item in all:
        run+=1
        item = frappe.get_doc("Item", item.name)
        if checkuom(item):
            wrong+=1
            # print(len(all), run, wrong)
            # continue
        
        if checkitemdefaults(item):
            wrong+=1
            # print(len(all), run, wrong)
            # continue
        
        if checktaxes(item):
            wrong+=1
        
        checkItemAttribute(item)
            # print(len(all), run, wrong)
            # continue

        print(len(all), run, wrong, item.name)
        item.save()
        

def checkuom(item):
    itemsuoms = {}
    for row in item.uoms:
        row = row.__dict__
        for fieldname in default_fields:
            if fieldname in row:
                del row[fieldname]
        itemsuoms[row.get("uom")] = row


    item.update({
        "uoms": list(itemsuoms.values())
    })

    itemsuoms = list(itemsuoms.values())
    uoms = {}
    for row in item.uoms:
        uoms[row.uom] = (uoms.get(row.uom) or 0) + 1

    for i in uoms:
        if (uoms.get(i) or 0) > 1:
            if item.stock_uom == "SQF" and i in ["SQF", "Nos", "Bdl"]:
                crt = []
                for j in itemsuoms:
                    if j.get("uom") != i:
                        crt.append(j)
                itemsuoms = crt
                itemsuoms.append({"uom": i, "conversion_factor": {"SQF": 1, "Nos": 1/item.pavers_per_sqft, "Bdl": item.bundle_per_sqr_ft}[i]})
                        
    item.update({
        "uoms": itemsuoms
    })    

def checkitemdefaults(item):
    defs = {}
    itemsdefs={}
    for row in item.item_defaults:
        _row = row
        row = row.__dict__
        for fieldname in default_fields:
            if fieldname in row:
                del row[fieldname]

        itemsdefs[row.get("idx")] = row
        defs[json.dumps(row, sort_keys=True, default=str)] = (defs.get(json.dumps(row, sort_keys=True, default=str)) or 0) + 1
    
    item.update({
        "item_defaults": list(itemsdefs.values())
    })
    
    

def checktaxes(item):
    tax= {}
    taxes = {}
    for row in item.taxes:
        _row = row
        row = row.__dict__
        for fieldname in default_fields:
            if fieldname in row:
                del row[fieldname]
        taxes[row.get("idx")] = row
        tax[json.dumps(row, sort_keys=True, default=str)] = (tax.get(json.dumps(row, sort_keys=True, default=str)) or 0) + 1
    
    item.update({
        "taxes": list(taxes.values())
    })

def checkItemAttribute(item):
    itemattr = {}
    for row in item.attributes:
        _row = row
        row = row.__dict__
        for fieldname in default_fields:
            if fieldname in row:
                del row[fieldname]
        itemattr[f"""{(row.get("variant_of") or "")} {(row.get("attribute") or "")}"""] = row
    
    item.update({
        "attributes": list(itemattr.values())
    })


def validate_prime_item(self, event=None):
    siteName = ""
    try:
        siteName = (frappe.local.site).split('.')[0]
    except:
        pass
    if siteName == "sgpprime":
        checkuom(self)
        checkitemdefaults(self)
        checktaxes(self)
        checkItemAttribute(self)

        
        
