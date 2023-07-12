# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

import frappe
from frappe import _



def execute(filters=None):
    columns, data = [], [{}]
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data
def get_columns(filters):
    columns = [
        {
            "label": _("Paver Prod. No"),
            "fieldtype": "Data",
            "fieldname": "paver_prod_no",
            "width": 100
        },
        {
            "label": _("Date"),
            "fieldtype": "Date",
            "fieldname": "date",
            "width": 100
        },
        {
			"label": _("Item"),
            "fieldtype": "Link",
            "fieldname": "item",
            "options":"Item",
            "width": 150
		},
        {
            "label": _("Machine"),
            "fieldtype": "Data",
            "fieldname": "machine",
            "width": 100
        },
        {
            "label": _("Area Conv"),
            "fieldtype": "Float",
            "fieldname": "area_conv",
            "width": 100
        },
        {
            "label": _("No of Rack"),
            "fieldtype": "Int",
            "fieldname": "no_of_rack",
            "width": 100
        },
        {
            "label": _("Sqft"),
            "fieldtype": "Data",
            "fieldname": "sqft",
            "width": 100
        },
       
        ]
    return columns

def get_data(filters):
    data=[]
    _filters={
            'from_time': ['between',[filters.get('from_date'),filters.get('to_date')]],
            'is_sample': 0
        }
    if filters.get('item'):
        _filters["item_to_manufacture"]=filters.get('item')
    if filters.get('machine'):
        _filters["work_station"]=["in", filters.get('machine')]
    daily_paver=frappe.db.get_all("Material Manufacturing", filters=_filters,fields=["name","item_to_manufacture","work_station","from_time","total_production_sqft as production_sqft","no_of_racks"], order_by="item_to_manufacture")

    
    grand_total=0
        
    for i in range(len(daily_paver)):
        item_doc=frappe.get_doc("Item",daily_paver[i].item_to_manufacture)
        square_ft=0
        nos=0
        for row in item_doc.uoms:
            if row.uom == 'SQF':
                square_ft=row.conversion_factor
            if row.uom == 'Nos':
                nos=row.conversion_factor
        if not square_ft:
            frappe.throw("Please Select SQF Conversion of the item " f"{daily_paver[i].item_to_manufacture}")
        if not nos:
            frappe.throw("Please Select Nos Conversion of the item " f"{daily_paver[i].item_to_manufacture}")
        area_conv=square_ft/nos
        f=frappe._dict()
        f.update({"paver_prod_no":daily_paver[i].name,"date":daily_paver[i].from_time,"item":daily_paver[i].item_to_manufacture,"machine":daily_paver[i].work_station,"area_conv":area_conv,"no_of_rack":daily_paver[i].no_of_racks,"sqft":daily_paver[i].production_sqft or 0})
        data.append(f)
        grand_total+=float(f["sqft"] or 0)
        if i+1== len(daily_paver) or daily_paver[i].item_to_manufacture != daily_paver[i+1].item_to_manufacture :
            data.append({"item":"<b>Group Total</b>","sqft":f"<b>{'%.2f'%(grand_total or 0)}</b>"})
            grand_total=0
        
    return data 