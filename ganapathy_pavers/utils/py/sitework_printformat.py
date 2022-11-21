import frappe
from ganapathy_pavers.__init__ import uom_conversion
from ganapathy_pavers import get_valuation_rate

def site_work(doc):
    doc=frappe.get_doc("Project",doc)
    items={}
    exp={}
    prod_rate={}
    nos=0
    supply_sqf=0
    sqf=doc.measurement_sqft or 0
    for item in doc.item_details:
        prod_rate[item.item]=get_valuation_rate(item_code=item.item, warehouse=item.warehouse, posting_date=frappe.utils.get_date_str(doc.creation))
    for item in doc.item_details_compound_wall:
        prod_rate[item.item]=get_valuation_rate(item_code=item.item, warehouse=item.warehouse, posting_date=frappe.utils.get_date_str(doc.creation))
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
    return {'items':items,'nos':round(nos,2),'sqf':round(sqf,2), 'expense': list(exp.values()), 'transporting_cost': doc.transporting_cost / sqf if sqf else 0,
     'total_job_worker_cost': doc.total_job_worker_cost / sqf if sqf else 0, 'total': doc.total / sqf if sqf else 0, 'prod_rate': prod_rate, 'supply_sqf': supply_sqf}
    






