import copy
from ganapathy_pavers.ganapathy_pavers.report.itemwise_monthly_paver_production_report.itemwise_monthly_paver_production_report import get_production_cost
import frappe
from frappe.utils import nowdate, get_first_day, get_last_day
from ganapathy_pavers import uom_conversion
from erpnext.stock.get_item_details import get_item_price

DATE_FORMAT = "%Y-%m-%d"

def site_work(doc):
    doc=frappe.get_doc("Project",doc)
    items={}
    exp={}
    production_rate={}
    without_transport_cost=doc.total
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
        items[i.item]["nos"]+=round(uom_conversion(i.item,i.stock_uom,((i.delivered_stock_qty or 0) + (i.returned_stock_qty or 0)),'Nos'),2)
        nos+=uom_conversion(i.item,i.stock_uom,((i.delivered_stock_qty or 0) + (i.returned_stock_qty or 0)),"Nos")
        items[i.item]["sqf"]+=round(uom_conversion(i.item,i.stock_uom,((i.delivered_stock_qty or 0) + (i.returned_stock_qty or 0)),"SQF"),2)
        supply_sqf+=uom_conversion(i.item,i.stock_uom,((i.delivered_stock_qty or 0) + (i.returned_stock_qty or 0)),"SQF")
    
    _items = copy.deepcopy(items)
    for row in _items:
        if not _items[row].get('nos') and not _items[row].get('sqf'):
            del items[row]

    for row in doc.additional_cost:
        if row.description.lower().strip() not in exp:
            exp[row.description.lower().strip()]={"description": row.description, "nos": row.nos, "amount": row.amount, "sqft_amount": (row.amount or 0)/sqf if sqf else 0, "supply_sqft_amount": (row.amount or 0)/supply_sqf if supply_sqf else 0}
        else:
            exp[row.description.lower().strip()]["nos"]+=row.nos
            exp[row.description.lower().strip()]["amount"]+=row.amount
            exp[row.description.lower().strip()]["sqft_amount"]+=(row.amount or 0)/sqf if sqf else 0
            exp[row.description.lower().strip()]["supply_sqft_amount"]+=(row.amount or 0)/supply_sqf if supply_sqf else 0
    
    for i in list(exp.values()):
        if "transport" in i["description"].lower():
            without_transport_cost -= i["amount"]

    delivered_items=(items.keys())
    dn_items=frappe.get_all("Delivery Note Item", {"parenttype": "Delivery Note", "parent": ["in", dn], "item_code": ["in", delivered_items]}, ["creation", "item_code", "warehouse"])
    dn_items+=frappe.get_all("Sales Invoice Item", {"parenttype": "Sales Invoice", "parent": ["in", si], "item_code": ["in", delivered_items]}, ["creation", "item_code", "warehouse"])
    
    paver_prod_details = []
    # cw_types={}
    for item in dn_items:
        # if frappe.db.get_value("Item", item['item_code'], "item_group") == "Pavers":
            if item['item_code'] not in production_rate:
                production_rate[item['item_code']] = []
            
            if [item["item_code"], get_first_day(item["creation"])] not in paver_prod_details:
                prod_cost=get_item_price_list_rate(item["item_code"], item["creation"])
                # get_paver_production_rate(item["item_code"], item["creation"])
                paver_prod_details.append([item["item_code"], get_first_day(item["creation"])])
                if prod_cost:
                    production_rate[item['item_code']].append(prod_cost)
        
        # if frappe.db.get_value("Item", item['item_code'], "item_group") == "Compound Walls":
        #     _type = frappe.db.get_value("Item", item['item_code'], "compound_wall_type")
        #     if item['item_code'] not in production_rate:
        #         production_rate[item['item_code']] = 0
            
        #     month = get_first_day(item["creation"])

        #     if month not in cw_types:
        #         cw_types[month]=[]

        #     if _type not in cw_types[month]:
        #         cw_types[month].append(_type)
    
    # prod_cost = []
    # for i in cw_types:
    #     cost = get_cw_production_rate(_type=cw_types[i], date = i)
    #     if cost:
    #         prod_cost.append(cost)
    
    # prod_cost = (sum(prod_cost) / len(prod_cost)) if prod_cost else 0
    
    # for item in dn_items:
    #     if frappe.db.get_value("Item", item['item_code'], "item_group") == "Compound Walls":
    #         production_rate[item['item_code']] = prod_cost

    for item in production_rate:
        if isinstance(production_rate[item], list):
            if len(list(set(production_rate[item]))):
                production_rate[item]= sum(list(set(production_rate[item])))/len(list(set(production_rate[item])))

    total_job_worker_cost = sum([(i.amount or 0) for i in doc.job_worker if not i.other_work])
    total_other_worker_cost = sum([(i.amount or 0) for i in doc.job_worker if i.other_work])
    return {
            'items':items,
            'nos':round(nos,2),
            'sqf':round(sqf,2), 
            'expense': list(exp.values()), 
            'transporting_cost': (doc.transporting_cost + (doc.total - without_transport_cost)) / sqf if sqf else 0,
            'supply_transporting_cost': (doc.transporting_cost + (doc.total - without_transport_cost)) / supply_sqf if supply_sqf else 0,
            'total_job_worker_cost': total_job_worker_cost / sqf if sqf else 0,
            'total_other_worker_cost': total_other_worker_cost / sqf if sqf else 0,
            'supply_total_job_worker_cost': total_job_worker_cost / supply_sqf if supply_sqf else 0,
            'supply_total_other_worker_cost': total_other_worker_cost / supply_sqf if supply_sqf else 0,
            'total': without_transport_cost / sqf if sqf else 0, 
            'supply_total': without_transport_cost / supply_sqf if supply_sqf else 0,
            'supply_sqf': supply_sqf, 
            'production_rate': production_rate
        }
    

def site_completion_delivery_uom(site_work, item_group='Raw Material'):
    query=f"""
        SELECT 
            dni.item_code,
            SUM(dni.qty) as qty,
            dni.uom,
            AVG(rate) as rate,
            SUM(dni.amount) as amount,
            ROUND(
                ifnull((
                    SELECT sle.valuation_rate
                    FROM `tabStock Ledger Entry` sle
                    WHERE
                        sle.is_cancelled=0 and
                        sle.voucher_type = 'Purchase Invoice' and
                        sle.item_code = dni.item_code and
                        sle.posting_date  <= dn.posting_date and
                        sle.is_cancelled = 0
                    order by posting_date desc
                    limit 1
                ), 0) *
                ifnull((
                    SELECT
                        uom.conversion_factor
                    FROM `tabUOM Conversion Detail` uom
                    WHERE
                        uom.parenttype='Item' and
                        uom.parent=dni.item_code and
                        uom.uom=dni.uom
                    limit 1
                )    
                , 0)
            , 2) as valuation_rate
        FROM `tabDelivery Note Item` dni
        LEFT OUTER JOIN `tabDelivery Note` dn
        ON dn.name=dni.parent AND dni.parenttype="Delivery Note"
        WHERE
            dni.item_group='{item_group}'
            AND dn.site_work='{site_work}'
            AND dn.docstatus=1
        GROUP BY dni.item_code, dni.uom
    """
    res = frappe.db.sql(query, as_dict=True)
    f_res = {}

    for row in res:
        if row.item_code not in f_res:
            f_res[row.item_code] = []
        f_res[row.item_code].append(row)
    return f_res

def get_item_price_list_rate(item, date):
    price_list=frappe.db.get_value("Price List", {"site_work_print_format": 1, "selling": 1}, "name")
    if not price_list:
        return 0
    args = {
	'item_code': item, 
		'price_list': price_list, 
		'uom': frappe.db.get_value("Item", item, "stock_uom"), 
		'transaction_date': None, 
		'posting_date': date or nowdate(), 
		'batch_no': None,
	}
    item_price=get_item_price(args=args, item_code=item)
    return item_price[0][1] if len(item_price) and len(item_price[0])>1 else 0

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
        
        date = frappe.get_all("CW Manufacturing",{
            "docstatus": ["!=", 2],
            "type": ["in", _type], 
            "molding_date": ["<=", filters.get('to_date'),]
            }, order_by="molding_date desc", pluck="molding_date", limit=1)

        if not date:
            date = frappe.get_all("CW Manufacturing",{
            "docstatus": ["!=", 2],
            "type": ["in", _type], 
            }, order_by="molding_date desc", pluck="molding_date", limit=1)
        
        if not date:
            return filters
    
        filters["from_date"] = get_first_day(date[0]).strftime(DATE_FORMAT)
        filters["to_date"] = get_last_day(date[0]).strftime(DATE_FORMAT)
        return filters
    

    if not date:
        date=nowdate()
    
    filters = {
        "from_date": get_first_day(date).strftime(DATE_FORMAT),
        "to_date": get_last_day(date).strftime(DATE_FORMAT),
    }

    filters = get_cw_production_date(_type, filters)
    exp_group="cw_group"
    prod="cw"

    if _type == ["Lego Block"]:
        exp_group="lg_group"
        prod="lego"

    elif _type == ['Fencing Post']:
        exp_group="fp_group" 
        prod="fp"
    
    cw_cost = sum(get_cw_monthly_cost(filters=filters,
                                  _type=_type,
                                  exp_group=exp_group,
                                  prod=prod))

    return cw_cost

def get_cw_monthly_cost(filters=None, _type=["Post", "Slab"], exp_group="cw_group", prod="cw"):
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")

    cw_list = frappe.db.get_list("CW Manufacturing",filters={'molding_date':["between",[from_date,to_date]],'type':["in",_type]},pluck="name")
    total_cost_per_sqft = 0
    rm_cost = 0

    if cw_list:
        bom_item = frappe.db.sql(""" 
                                select item_code,sum(qty),uom,avg(rate),sum(amount) from `tabBOM Item` where parent {0} group by item_code """.format(f" in {tuple(cw_list)}" if len(cw_list)>1 else f" = '{cw_list[0]}'"),as_list=1)
        production_qty = frappe.db.sql(""" 
                                select sum(ts_production_sqft) as production_sqft,
                                avg(total_cost_per_sqft) as total_cost_per_sqft,
                                sum(total_expence) as total_expence,
                                sum(raw_material_cost) as raw_material_cost,
                                sum(total_expense_for_unmolding) as total_expense_for_unmolding,
                                sum(labour_expense_for_curing) as total_expense_for_curing,
                                AVG(total_labour_wages + labour_expense_for_curing)/AVG(ts_production_sqft) as labour_cost_per_sqft,
                                AVG(total_operator_wages)/AVG(ts_production_sqft) as operator_cost_per_sqft,
                                avg(strapping_cost_per_sqft) as strapping_cost_per_sqft,
                                avg(additional_cost_per_sqft) as additional_cost_per_sqft,
                                avg(raw_material_cost_per_sqft) as raw_material_cost_per_sqft from `tabCW Manufacturing` where name {0}""".format(f" in {tuple(cw_list)}" if len(cw_list)>1 else f" = '{cw_list[0]}'"),as_dict=1)
        
        for item in bom_item:
            rm_cost += item[4] / (production_qty[0]['production_sqft'] or 1)

        total_cost_per_sqft +=  ((production_qty[0]['strapping_cost_per_sqft'] or 0)
                                + (production_qty[0]['additional_cost_per_sqft']  or 0)
                                + (production_qty[0]["labour_cost_per_sqft"] or 0) 
                                + (production_qty[0]['operator_cost_per_sqft'] or 0))

    return rm_cost, total_cost_per_sqft