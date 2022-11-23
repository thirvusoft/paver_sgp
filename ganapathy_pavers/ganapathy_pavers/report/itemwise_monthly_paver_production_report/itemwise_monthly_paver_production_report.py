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
            "label": _("Month"),
            "fieldtype": "Data",
            "fieldname": "month",
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
            "label": _("Sqft"),
            "fieldtype": "Float",
            "fieldname": "sqft",
            "width": 100
        },
        {
            "label": _("No of Days"),
            "fieldtype": "Int",
            "fieldname": "no_of_days",
            "width": 100
        },
         {
            "label": _("Prod Cost"),
            "fieldtype": "Float",
            "fieldname": "prod_cost",
            "width": 100
        },
        {
            "label": _("Expense Cost"),
            "fieldtype": "Float",
            "fieldname": "expense_cost",
            "width": 100
        },
        {
            "label": _("Total Cost"),
            "fieldtype": "Float",
            "fieldname": "total_cost",
            "width": 100
        }
      
      
        ]
    return columns

def get_data(filters):
    data={}
    paver=frappe.db.get_all("Material Manufacturing",  filters={'from_time':['between',[filters.get('from_date'),filters.get('to_date')]]}, fields=['item_to_manufacture','production_sqft','item_price','total_raw_material','from_time'], order_by='from_time')
    for i in paver:
        production_cost=i.total_raw_material/i.production_sqft
        expense=i.item_price-production_cost
        f={"month":i.from_time.strftime("%B"),"item":i.item_to_manufacture,"sqft":i.production_sqft,"prod_cost":production_cost,"expense_cost":expense,"total_cost":i.item_price,"no_of_days":1}
        if f"{i.item_to_manufacture} {i.month}" not in data:
            data[f"{i.item_to_manufacture} {i.month}"] =f
        else:
            data[f"{i.item_to_manufacture} {i.month}"]['sqft']+=f["sqft"]
            data[f"{i.item_to_manufacture} {i.month}"]['prod_cost']+=f["prod_cost"]
            data[f"{i.item_to_manufacture} {i.month}"]['expense_cost']+=f["expense_cost"]
            data[f"{i.item_to_manufacture} {i.month}"]['total_cost']+=f["total_cost"]
            data[f"{i.item_to_manufacture} {i.month}"]['no_of_days']+=1
    for i in data:
        # data [i]['sqft']/=data[i]["count"]
        data [i]['prod_cost']/=data[i]["no_of_days"]
        data [i]['expense_cost']/=data[i]["no_of_days"]
        data [i]['total_cost']/=data[i]["no_of_days"]
    
    return list(data.values())
	

