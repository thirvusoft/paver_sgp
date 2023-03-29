# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

from ganapathy_pavers.custom.py.journal_entry import get_production_details
from ganapathy_pavers.ganapathy_pavers.report.monthly_paver_production_report.monthly_paver_production_report import get_expense_data
from ganapathy_pavers.ganapathy_pavers.doctype.cw_manufacturing.cw_manufacturing import uom_conversion
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
            "width": 380
        },
        {
            "label": _("Sqft"),
            "fieldtype": "Float",
            "fieldname": "sqft",
            "width": 100
        },
         {
            "label": _("Pieces"),
            "fieldtype": "Float",
            "fieldname": "pieces",
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
            "label": _("Strapping Cost"),
            "fieldtype": "Float",
            "fieldname": "strapping_cost",
            "width": 100
        },
         {
            "label": _("Shot Blasting Cost"),
            "fieldtype": "Float",
            "fieldname": "shot_blasting_cost",
            "width": 100
        },
        {
            "label": _("Labour Operator Cost"),
            "fieldtype": "Float",
            "fieldname": "labour_operator_cost",
            "width": 160
        },
        {
            "label": _("Expense Cost"),
            "fieldtype": "Float",
            "fieldname": "expense_cost",
            "width": 150
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
    paver_filters={
        'from_time':['between',[filters.get('from_date'),filters.get('to_date')]],
    }
    if filters.get("machine"):
        paver_filters["work_station"]=["in", filters.get("machine")]
    paver=frappe.db.get_all("Material Manufacturing",  filters=paver_filters, fields=['item_to_manufacture','total_production_sqft as production_sqft','item_price','total_raw_material','from_time', 'strapping_cost_per_sqft', 'labour_cost_per_sqft'], order_by='from_time')
    for i in paver:
        if not i.production_sqft:
            continue
        f={"month":i.from_time.strftime("%B"),"item":i.item_to_manufacture,"sqft":i.production_sqft,"no_of_days":1}
        f["prod_cost"], f["labour_operator_cost"], f["strapping"], f["shot_blasting"]=get_production_cost(filters, i.item_to_manufacture)
        if f"{i.item_to_manufacture} {i.month}" not in data:
            data[f"{i.item_to_manufacture} {i.month}"] =f
        else:
            
            data[f"{i.item_to_manufacture} {i.month}"]['sqft']+=f["sqft"]
            data[f"{i.item_to_manufacture} {i.month}"]['no_of_days']+=1
        # data['pieces']=0
    data=list(data.values())
    prod_details=get_production_details(from_date=filters.get('from_date'), to_date=filters.get('to_date'), machines=(filters.get("machine", []) or []))
    expense_cost=get_sqft_expense(filters)
    for row in data:
        row["prod_cost"] = (row.get("prod_cost", 0) or 0) + (row.get("strapping", 0) or 0) + (row.get("shot_blasting", 0) or 0)
        row["strapping_cost"]=(row["strapping"] or 0)
        row["shot_blasting_cost"]=(row["shot_blasting"] or 0)
        row['pieces']=uom_conversion(item=row['item'], from_uom="SQF", from_qty=row['sqft'], to_uom="Nos")
        row["expense_cost"]=(expense_cost or 0) if not expense_cost else (expense_cost*(row['sqft'] or 0))/(prod_details.get("paver") or 1)/(prod_details.get("paver") or 1)
        row["expense_cost"]=(expense_cost or 0) if not expense_cost else (expense_cost)/(prod_details.get("paver") or 1)
        row["expense_cost"] = (row.get("expense_cost", 0) or 0) + (row.get("labour_operator_cost", 0) or 0)
        row["total_cost"]=(row["prod_cost"] or 0) + (row["expense_cost"] or 0)
   
    return data
	

def get_production_cost(filters, item):
    conditions=f"""
        WHERE mm.docstatus<2 
        AND mm.from_time BETWEEN '{filters.get('from_date')}' 
        AND '{frappe.utils.data.add_to_date(filters.get('to_date'), days=1)}'
        AND mm.item_to_manufacture='{item}'
    """
    if len((filters.get("machine", []) or []))>1:
        conditions+=f""" AND mm.work_station in {tuple(filters.get("machine"))}"""
    elif len((filters.get("machine", []) or []))==1:
        conditions+=f""" AND mm.work_station = '{filters.get("machine")[0]}'"""
    query=f"""
        SELECT 
            (
                SELECT AVG((lomm.operators_cost_in_manufacture+lomm.operators_cost_in_rack_shift))/AVG(lomm.total_production_sqft) + 
                AVG((lomm.labour_cost_manufacture+lomm.labour_cost_in_rack_shift+lomm.labour_expense))/AVG(lomm.total_production_sqft)
                FROM `tabMaterial Manufacturing` as lomm
                {conditions.replace("mm.", "lomm.").replace(F"AND lomm.item_to_manufacture='{item}'", " ")}
            ) as labour_operator_cost,
            ( 
                (
                    SELECT SUM(bi.amount) from `tabBOM Item` bi
                    WHERE bi.parent in (
                        SELECT mmm.name
                        from `tabMaterial Manufacturing` mmm
                        {conditions.replace("mm.", "mmm.") + " AND mmm.item_to_manufacture=mm.item_to_manufacture"}
                    )
                )/SUM(mm.total_production_sqft)
            ) as prod_cost,
        AVG(mm.strapping_cost_per_sqft) as strapping,
        AVG(mm.shot_blast_per_sqft) as shot_blasting

        FROM `tabMaterial Manufacturing` as mm
        {conditions} 
        GROUP BY mm.item_to_manufacture
        ORDER BY from_time
        """
    res=frappe.db.sql(query, as_dict=1)
    if res and res[0]:
        return res[0].get("prod_cost", 0), res[0].get("labour_operator_cost", 0),res[0].get("strapping", 0),res[0].get("shot_blasting", 0)
    return 0, 0, 0, 0


def get_sqft_expense(filters):
    exp=frappe.get_single("Expense Accounts")
    machine=None
    if ("Machine1" in (filters.get("machine", []) or []) or "Machine2" in (filters.get("machine", []) or [])) and "Machine3" in (filters.get("machine", []) or []):
        pass
    elif "Machine1" in (filters.get("machine", []) or []) or "Machine2" in (filters.get("machine", []) or []):
        machine="machine_12"
    elif (filters.get("machine", []) or []):
        machine="machine_3"
    paver_exp_tree=exp.tree_node(from_date=filters.get('from_date'), to_date=filters.get('to_date'), parent=exp.paver_group, machine=machine)
    total_sqf=0
    for i in paver_exp_tree:
        if i.get("child_nodes"):
            total_sqf+=get_expense_from_child(i['child_nodes'], 0)
        else:
            if i["balance"]:
                total_sqf+=i["balance"] or 0
    return total_sqf

def get_expense_from_child(account, total_sqf):
    for i in account:
        if i['child_nodes']:
            total_sqf+=(get_expense_from_child(i['child_nodes'], 0))
        elif i["balance"]:
            total_sqf+=i["balance"] or 0
    return total_sqf
