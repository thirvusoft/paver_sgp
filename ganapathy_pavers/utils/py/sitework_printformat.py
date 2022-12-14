import frappe
from ganapathy_pavers import get_valuation_rate, uom_conversion

def site_work(doc):
    doc=frappe.get_doc("Project",doc)
    items={}
    exp={}
    production_rate=[]
    nos=0
    supply_sqf=0
    sqf=doc.measurement_sqft or 0
    dn=frappe.get_all("Delivery Note", {"site_work": doc.name, "docstatus": 1}, pluck="name")
    si=frappe.get_all("Sales Invoice", {"site_work": doc.name, "docstatus": 1, "update_stock": 1}, pluck="name")
    for i in doc.delivery_detail:
        if i.item not in items:
            items[i.item]={
                "nos":0,"sqf":0,
            }
        items[i.item]["nos"]+=round(uom_conversion(i.item,i.stock_uom,i.delivered_stock_qty,'Nos'),2)
        nos+=uom_conversion(i.item,i.stock_uom,i.delivered_stock_qty,"Nos")
        items[i.item]["sqf"]+=round(uom_conversion(i.item,i.stock_uom,i.delivered_stock_qty,"SQF"),2)
        supply_sqf+=uom_conversion(i.item,i.stock_uom,i.delivered_stock_qty,"SQF")
    for row in doc.additional_cost:
        if row.description.lower().strip() not in exp:
            exp[row.description.lower().strip()]={"description": row.description, "nos": row.nos, "amount": row.amount, "sqft_amount": (row.amount or 0)/sqf if sqf else 0}
        else:
            exp[row.description.lower().strip()]["nos"]+=row.nos
            exp[row.description.lower().strip()]["amount"]+=row.amount
            exp[row.description.lower().strip()]["sqft_amount"]+=(row.amount or 0)/sqf if sqf else 0
    delivered_items=(items.keys())
    dn_items=frappe.get_all("Delivery Note Item", {"parenttype": "Delivery Note", "parent": ["in", dn], "item_code": ["in", delivered_items]}, ["creation", "item_code", "warehouse"])
    dn_items+=frappe.get_all("Sales Invoice Item", {"parenttype": "Sales Invoice", "parent": ["in", si], "item_code": ["in", delivered_items]}, ["creation", "item_code", "warehouse"])
    for item in dn_items:
        production_rate.append(get_production_rate(item["item_code"], item["warehouse"], item["creation"]))
    return {'items':items,'nos':round(nos,2),'sqf':round(sqf,2), 'expense': list(exp.values()), 'transporting_cost': doc.transporting_cost / sqf if sqf else 0,
     'total_job_worker_cost': doc.total_job_worker_cost / sqf if sqf else 0, 'total': doc.total / sqf if sqf else 0, 'supply_sqf': supply_sqf, 'production_rate': sum(production_rate)/len(production_rate) if len(production_rate) else 0}
    
def get_production_rate(item_code, warehouse, creation):
    production_rate=0
    item_doc=frappe.get_doc("Item", item_code)
    date=creation.date()
    if item_doc.item_group=="Pavers":
        paver_m=frappe.get_all("Material Manufacturing", filters={"docstatus": ["!=", 2], "from_time": ["<=", creation], "item_to_manufacture": item_code}, fields=["item_price", "name"], limit=1)
        if (paver_m and not paver_m[0]["item_price"]) or not paver_m:
            production_rate=get_valuation_rate(item_code, warehouse, creation)
        else:
            production_rate=paver_m[0]["item_price"]
    elif item_doc.item_group=="Compound Walls":
        filters=[
            ["CW Items", "item", "=", item_code],
            ["docstatus", "!=", 2],
            ["molding_date", "<=", date]
        ]
        cw_m=frappe.get_all("CW Manufacturing", filters=filters, fields=["total_cost_per_sqft", "name"], limit=1)
        if (cw_m and not cw_m[0]["total_cost_per_sqft"]) or not cw_m:
            production_rate=get_valuation_rate(item_code, warehouse, creation)
        else:
            production_rate=cw_m[0]["total_cost_per_sqft"]
    return production_rate