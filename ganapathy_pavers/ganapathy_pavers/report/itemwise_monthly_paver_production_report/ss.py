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
            "fieldname": "item_to_manufacture",
            "options":"Item",
            "width": 150#380
        },
        {
            "label": _("Sqft"),
            "fieldtype": "Float",
            "fieldname": "production_sqft",
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
            "fieldname": "item_price",
            "width": 100
        }
      
      
        ]
    return columns

def get_data(filters):
    data={}
    conditions=f"""
        WHERE mm.docstatus<2 
        AND mm.from_time BETWEEN '{filters.get('from_date')}' 
        AND '{frappe.utils.data.add_to_date(filters.get('to_date'), days=1)}'
    """
    if len(filters.get("machine", []))>1:
        conditions+=f""" AND mm.work_station in {tuple(filters.get("machine"))}"""
    elif len(filters.get("machine", []))==1:
        conditions+=f""" AND mm.work_station = '{filters.get("machine")[0]}'"""
    paver=frappe.db.get_all("Material Manufacturing",  filters={'from_time':['between',[filters.get('from_date'),filters.get('to_date')]]}, fields=['item_to_manufacture','production_sqft','item_price','total_raw_material','from_time', 'strapping_cost_per_sqft', 'labour_cost_per_sqft'], order_by='from_time')
    query=f"""
        SELECT 
            mm.item_to_manufacture, 
            SUM(mm.production_sqft/(
                SELECT COUNT(*) from `tabBOM Item` bi
                WHERE bi.parent=mm.name
                )
            ) as production_sqft,
            COUNT(DISTINCT(mm.name)) as no_of_days,
            MONTHNAME(mm.from_time) as month,
            (
                AVG(mm.strapping_cost_per_sqft) +
                AVG(mm.shot_blast_per_sqft) + 
                AVG((mm.operators_cost_in_manufacture+mm.operators_cost_in_rack_shift)/mm.production_sqft) + 
                AVG((mm.labour_cost_manufacture+mm.labour_cost_in_rack_shift+mm.labour_expense)/mm.production_sqft) + 
                (
                    SELECT SUM(bi.amount) from `tabBOM Item` bi
                    WHERE bi.parent in (
                        SELECT mmm.name
                        from `tabMaterial Manufacturing` mmm
                        {conditions.replace("mm", "mmm") + " AND mmm.item_to_manufacture=mm.item_to_manufacture"}
                    )
                )/SUM(mm.production_sqft/(
                        SELECT COUNT(*) from `tabBOM Item` bi
                        WHERE bi.parent=mm.name
                        )
                )
            ) as prod_cost
        FROM `tabMaterial Manufacturing` as mm
        LEFT OUTER JOIN `tabBOM Item` as bom
        ON bom.parent=mm.name
        {conditions} 
        GROUP BY mm.item_to_manufacture
        ORDER BY from_time
        """
    paver=frappe.db.sql(query, as_dict=1)
    return paver
    for i in paver:
        if not i.production_sqft:
            continue
        production_cost=(i.total_raw_material/i.production_sqft) + i.strapping_cost_per_sqft + i.labour_cost_per_sqft
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
	

"""

"""