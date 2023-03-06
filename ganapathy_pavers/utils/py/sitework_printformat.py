from ganapathy_pavers.ganapathy_pavers.report.itemwise_monthly_cw_production_report.itemwise_monthly_cw_production_report import get_cw_cost
from ganapathy_pavers.ganapathy_pavers.report.itemwise_monthly_paver_production_report.itemwise_monthly_paver_production_report import get_production_cost
import frappe
from frappe.utils import nowdate, get_first_day, get_last_day
from ganapathy_pavers import get_valuation_rate, uom_conversion

DATE_FORMAT = "%Y-%m-%d"

def site_work(doc):
    doc=frappe.get_doc("Project",doc)
    items={}
    exp={}
    production_rate={}
    nos=0
    supply_sqf=0
    sqf=doc.measurement_sqft or 0
    dn=frappe.get_all("Delivery Note", {"site_work": doc.name, "docstatus": 1}, pluck="name")
    si=frappe.get_all("Sales Invoice", {"site_work": doc.name, "docstatus": 1, "update_stock": 1}, pluck="name")
    for i in doc.delivery_detail:
        rate=0
        for item_row in (doc.item_details or []) + (doc.item_details_compound_wall or []) + (doc.raw_material or []):
            if item_row.get("item")==i.item:
                rate=item_row.get('rate', 0)
        if not rate:
            rate_list=frappe.db.sql(f"""
                select dni.rate
                from `tabDelivery Note Item` as dni left outer join `tabDelivery Note` as dn
                    on dni.parent = dn.name
                where dn.site_work='{doc.name}' and dni.item_code='{i.item}'
            """)
            if rate_list and rate_list[0] and rate_list[0][0]:
                rate=rate_list[0][0]
        if i.item not in items:
            items[i.item]={
                "nos":0,"sqf":0,"rate": rate,
            }
        items[i.item]["nos"]+=round(uom_conversion(i.item,i.stock_uom,i.delivered_stock_qty,'Nos'),2)
        nos+=uom_conversion(i.item,i.stock_uom,i.delivered_stock_qty,"Nos")
        items[i.item]["sqf"]+=round(uom_conversion(i.item,i.stock_uom,i.delivered_stock_qty,"SQF"),2)
        supply_sqf+=uom_conversion(i.item,i.stock_uom,i.delivered_stock_qty,"SQF")
    for row in doc.additional_cost:
        if row.description.lower().strip() not in exp:
            exp[row.description.lower().strip()]={"description": row.description, "nos": row.nos, "amount": row.amount, "sqft_amount": (row.amount or 0)/sqf if sqf else 0, "supply_sqft_amount": (row.amount or 0)/supply_sqf if supply_sqf else 0}
        else:
            exp[row.description.lower().strip()]["nos"]+=row.nos
            exp[row.description.lower().strip()]["amount"]+=row.amount
            exp[row.description.lower().strip()]["sqft_amount"]+=(row.amount or 0)/sqf if sqf else 0
            exp[row.description.lower().strip()]["supply_sqft_amount"]+=(row.amount or 0)/supply_sqf if supply_sqf else 0
    
    delivered_items=(items.keys())
    dn_items=frappe.get_all("Delivery Note Item", {"parenttype": "Delivery Note", "parent": ["in", dn], "item_code": ["in", delivered_items]}, ["creation", "item_code", "warehouse"])
    dn_items+=frappe.get_all("Sales Invoice Item", {"parenttype": "Sales Invoice", "parent": ["in", si], "item_code": ["in", delivered_items]}, ["creation", "item_code", "warehouse"])
    
    paver_prod_details = []
    cw_types={}
    for item in dn_items:
        if frappe.db.get_value("Item", item['item_code'], "item_group") == "Pavers":
            if item['item_code'] not in production_rate:
                production_rate[item['item_code']] = []
            
            if [item["item_code"], get_first_day(item["creation"])] not in paver_prod_details:
                prod_cost=get_paver_production_rate(item["item_code"], item["creation"])
                paver_prod_details.append([item["item_code"], get_first_day(item["creation"])])
                if prod_cost:
                    production_rate[item['item_code']].append(prod_cost)
        
        if frappe.db.get_value("Item", item['item_code'], "item_group") == "Compound Walls":
            _type = frappe.db.get_value("Item", item['item_code'], "compound_wall_type")
            if item['item_code'] not in production_rate:
                production_rate[item['item_code']] = 0
            
            month = get_first_day(item["creation"])

            if month not in cw_types:
                cw_types[month]=[]

            if _type not in cw_types[month]:
                cw_types[month].append(_type)
    
    prod_cost = []
    for i in cw_types:
        cost = get_cw_production_rate(_type=cw_types[i], date = i)
        if cost:
            prod_cost.append(cost)
    
    prod_cost = (sum(prod_cost) / len(prod_cost)) if prod_cost else 0
    
    for item in dn_items:
        if frappe.db.get_value("Item", item['item_code'], "item_group") == "Compound Walls":
            production_rate[item['item_code']] = prod_cost

    for item in production_rate:
        if isinstance(production_rate[item], list):
            if len(list(set(production_rate[item]))):
                production_rate[item]= sum(list(set(production_rate[item])))/len(list(set(production_rate[item])))
    return {
            'items':items,
            'nos':round(nos,2),
            'sqf':round(sqf,2), 
            'expense': list(exp.values()), 
            'transporting_cost': doc.transporting_cost / sqf if sqf else 0,
            'total_job_worker_cost': doc.total_job_worker_cost / sqf if sqf else 0, 
            'total': doc.total / sqf if sqf else 0, 
            'supply_total': doc.total / supply_sqf if supply_sqf else 0,
            'supply_sqf': supply_sqf, 
            'production_rate': production_rate
        }
    

def site_completion_delivery_uom(site_work, item):
    query=f"""
        SELECT 
            SUM(dni.qty) as qty,
            dni.uom
        FROM `tabDelivery Note Item` dni
        LEFT OUTER JOIN `tabDelivery Note` dn
        ON dn.name=dni.parent AND dni.parenttype="Delivery Note"
        WHERE
            dni.item_code = '{item}'
            AND dn.site_work='{site_work}'
            AND dn.docstatus=1
        GROUP BY dni.uom
    """
    return frappe.db.sql(query, as_dict=True)

def get_paver_production_rate(item, date=None):
    def get_paver_production_date(filters, item):
        if frappe.get_all("Material Manufacturing", {
            "item_to_manufacture": item,
            "docstatus": ["!=", 2],
            "from_time": ["between", [filters.get('from_date'), filters.get('to_date')]]
            }):
            return filters
        
        date = frappe.get_all("Material Manufacturing",{
            "item_to_manufacture": item,
            "docstatus": ["!=", 2],
            "from_time": ["<=", filters.get('to_date'),]
            }, order_by="from_time desc", pluck="from_time", limit=1)

        if not date:
            date = frappe.get_all("Material Manufacturing",{
            "item_to_manufacture": item,
            "docstatus": ["!=", 2],
            }, order_by="from_time desc", pluck="from_time", limit=1)
        
        if not date:
            return filters
    
        filters["from_date"] = get_first_day(date[0]).strftime(DATE_FORMAT)
        filters["last_date"] = get_last_day(date[0]).strftime(DATE_FORMAT)
        return filters
    

    if not date:
        date=nowdate()
    
    filters = {
        "from_date": get_first_day(date).strftime(DATE_FORMAT),
        "to_date": get_last_day(date).strftime(DATE_FORMAT),
        "machine": []
    }
    filters = get_paver_production_date(filters, item)

    return sum(get_production_cost(filters, item))

def get_cw_production_rate(_type=[], date=None):
    def get_cw_production_date(_type, filters):
        if frappe.get_all("CW Manufacturing", {
            "docstatus": ["!=", 2],
            "type": ["in", _type], 
            "molding_date": ["between", [filters.get('from_date'), filters.get('to_date')]]
            }):
            return filters
        
        date = frappe.get_all("Material Manufacturing",{
            "docstatus": ["!=", 2],
            "type": ["in", _type], 
            "molding_date": ["<=", filters.get('to_date'),]
            }, order_by="molding_date desc", pluck="molding_date", limit=1)

        if not date:
            date = frappe.get_all("Material Manufacturing",{
            "docstatus": ["!=", 2],
            "type": ["in", _type], 
            }, order_by="molding_date desc", pluck="molding_date", limit=1)
        
        if not date:
            return filters
    
        filters["from_date"] = get_first_day(date[0]).strftime(DATE_FORMAT)
        filters["last_date"] = get_last_day(date[0]).strftime(DATE_FORMAT)
        return filters
    

    if not date:
        date=nowdate()
    
    filters = {
        "from_date": get_first_day(date).strftime(DATE_FORMAT),
        "to_date": get_last_day(date).strftime(DATE_FORMAT),
    }
    filters = get_cw_production_date(_type, filters)

    cw_docs = frappe.get_all("CW Manufacturing", {
        "molding_date":["between", (filters.get("from_date"), filters.get("to_date"))],
        "type":["in",_type],
        "production_sqft":["!=",0],
        "docstatus":["!=",2]
        }, order_by = 'molding_date')
    
    cw_cost = get_cw_cost(doc_list=cw_docs)
    prod_cost = []
    for row in cw_cost:
        cost=(row.get("prod_cost", 0) or 0)+(row.get("labour_operator_cost", 0) or 0)+(row.get("strapping_cost", 0) or 0)+(row.get("additional_cost", 0) or 0)
        prod_cost.append(cost)

    return sum(prod_cost)/len(prod_cost) if prod_cost and len(prod_cost)>0 else 0
