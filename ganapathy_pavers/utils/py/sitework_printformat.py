import frappe
from ganapathy_pavers.__init__ import uom_conversion
def site_work(doc):
    doc=frappe.get_doc("Project",doc)
    items={}
    exp={}
    nos=0
    sqf=0
    for i in doc.delivery_detail:
        if i.item not in items:
            items[i.item]={
                "nos":0,"sqf":0,
            }
        items[i.item]["nos"]+=round(uom_conversion(i.item,i.stock_uom,i.delivered_stock_qty,'Nos'),2)
        nos+=uom_conversion(i.item,i.stock_uom,i.delivered_stock_qty,"Nos")
        items[i.item]["sqf"]+=round(uom_conversion(i.item,i.stock_uom,i.delivered_stock_qty,"SQF"),2)
        sqf+=uom_conversion(i.item,i.stock_uom,i.delivered_stock_qty,"SQF")
    for row in doc.additional_cost:
        if row.description.lower().strip() not in exp:
            exp[row.description.lower().strip()]={"description": row.description, "nos": row.nos, "amount": row.amount, "sqft_amount": (row.amount or 0)/sqf}
        else:
            exp[row.description.lower().strip()]["nos"]+=row.nos
            exp[row.description.lower().strip()]["amount"]+=row.amount
            exp[row.description.lower().strip()]["sqft_amount"]+=(row.amount or 0)/sqf
    return {'items':items,'nos':round(nos,2),'sqf':round(sqf,2), 'expense': list(exp.values())}
    






