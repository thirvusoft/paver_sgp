import frappe
from ganapathy_pavers.__init__ import uom_conversion
def site_work(doc):
    doc=frappe.get_doc("Project",doc)
    items={}
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
    return {'items':items,'nos':round(nos,2),'sqf':round(sqf,2)}
    






