# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt

import frappe 
from frappe import _


def execute(filters=None):
    columns, data = [], [{}]
    columns = get_columns(filters)
    data = get_purchase_fuel_data(filters)
    data += get_data(filters)
    return columns, data

def get_purchase_fuel_data(filters):
    conditions = ""
    if filters.get("unit"):
        warehouse_name=frappe.get_value("Location",filters.get("unit"),"warehouse")
        all_warehouse = get_warehouse_with_children(warehouse_name)
        conditions += f'''
            and ifnull(poi.warehouse, '') in ({', '.join([f"'{i}'" for i in all_warehouse or ['']])})
        '''
         
    query = f"""
    select
        fip.item_code,
        fip.fuel_type as license_plate,
        sum(poi.stock_qty) as fuel_qty,
        sum(poi.amount) as total_fuel,
        poi.warehouse as warehouse
    from `tabPurchase Invoice Item` poi
    inner join `tabPurchase Invoice` po on po.name=poi.parent and poi.parenttype="Purchase Invoice"
    inner join `tabFuel Item Map` fip on fip.item_code=poi.item_code and fip.parenttype="Vehicle Settings"
    where
        case 
            when IFNULL('{filters.get("fuel_type") or ""}', "")!="" 
                then fip.fuel_type='{filters.get("fuel_type")}' 
            else 1=1 
        end and
        po.docstatus=1 and
        po.update_stock=1 and
        po.posting_date between '{filters.get("from_date")}' and '{filters.get("to_date")}'
        {conditions}
       
    group by poi.item_code, poi.warehouse
    """
    
    data = frappe.db.sql(query, as_dict=True)
    for row in data:
        row["vehicle_unit"]=" "
        row_warehouse=frappe.get_value("Warehouse",row.get("warehouse"),"parent_warehouse")
        if row_warehouse:
            location=frappe.get_doc("Location",{"warehouse":row_warehouse})
            if location:
                row["vehicle_unit"]=location.name or " "

    return ([{'license_plate': "FUEL PURCHASED", "bold": 1,"vehicle_unit":" "}] + data) if data else []

def get_columns(filters):
    columns = [
        {
            "label": _("Vehicle"),
            "fieldtype": "Link",
            "fieldname": "license_plate",
            "options":"Vehicle",
            "width": 150
        },
        {
            "label": _("Qty"),
            "fieldtype": "Float",
            "fieldname": "fuel_qty",
            "width": 100
        },
        {
            "label": _("Amount"),
            "fieldtype": "Float",
            "fieldname": "total_fuel",
            "width": 100
        },
        {
            "label": _("Unit"),
            "fieldtype": "Link",
            "fieldname": "vehicle_unit",
            "options":"Location",
            "default":" ",
            "width": 100
        },
        {
            "fieldname": 'bold',
            "fieldtype": "Check",
            "hidden": 1
        },
        {
            "fieldname": 'only_bold',
            "fieldtype": "Check",
            "hidden": 1
        }
        ]
    return columns

def get_data(filters, add_total = True):
    vehicle_log = (get_stock_entry_data(filters) or [])
    filters_2={}
    fuel=filters.get('fuel_type')

    filters_1={
        'select_purpose': 'Fuel',
        'docstatus':1, 
        'fuel_qty':['>',0],
        'from_barrel': filters.get("from_barrel", 0) or 0
        }
    
    if filters.get('from_date'):
        filters_1['date'] = [">=", filters.get('from_date')]
    if filters.get('to_date'):
        filters_1['date'] = ["<=", filters.get('to_date')]
    if filters.get('to_date') and filters.get('from_date'):
        filters_1['date'] = ['between',[filters.get('from_date'),filters.get('to_date')]]
    
    if filters.get('fuel_type'):
        filters_2={'fuel_type':fuel}

    if filters.get("unit"):
        filters_2['unit']= ['in',filters.get("unit")]
        
    if fuel or filters.get("unit"):
        vehicle=frappe.get_all("Vehicle", filters=filters_2, pluck='name')
        filters_1['license_plate']= ['in', vehicle]
    vehicle_log+=frappe.db.get_all("Vehicle Log", filters=filters_1, fields=['license_plate','sum(fuel_qty) as fuel_qty','sum(total_fuel) as total_fuel'], group_by='license_plate')
    for row in vehicle_log:
        row["vehicle_unit"]=frappe.get_value("Vehicle",row.get("license_plate"),"unit") or " "
       
    if add_total:
        total = {"license_plate": "Total", "fuel_qty": 0, "total_fuel": 0, "only_bold": 1}
        for row in vehicle_log:
            total["fuel_qty"] += (row.get("fuel_qty") or 0)
            total["total_fuel"] += (row.get("total_fuel") or 0)
            
        vehicle_log.append(total)

    return ([{'license_plate': "FUEL USED", "bold": 1,"vehicle_unit":" "}] + vehicle_log) if vehicle_log else []

def get_stock_entry_data(filters):
    if not filters.get("from_barrel", 0):
        return []
    conditions = ""
    if (filters.get("fuel_type")):
        conditions += f'''and
        sed.item_code IN (
        SELECT
            f.item_code
        FROM `tabFuel Item Map` f
        WHERE f.fuel_type='{filters.get("fuel_type")}'
        )'''
    if filters.get('from_date') and filters.get("to_date"):
        conditions += f'''
            and se.posting_date between '{filters.get("from_date")}' and '{filters.get("to_date")}'
        '''
   
    res=[]
    query=f"""
    SELECT 
        sed.item_code,
        SUM(sed.qty) as fuel_qty,
        SUM(sed.basic_amount) as total_fuel,
        se.internal_fuel_consumption as license_plate
    FROM `tabStock Entry Detail` sed
    LEFT OUTER JOIN `tabStock Entry` se
    ON se.name = sed.parent
    WHERE
        se.docstatus = 1 and
        IFNULL(se.internal_fuel_consumption, "")!="" and
        se.stock_entry_type = "Material Issue" 
        {conditions}
    GROUP BY se.internal_fuel_consumption, sed.item_code
        """

    res = frappe.db.sql(query, as_dict=True)
    return res


def get_warehouse_with_children(warehouse):
	if not isinstance(warehouse, list):
		warehouse = [d.strip() for d in warehouse.strip().split(",") if d]

	all_warehouse = []
	for d in warehouse:
		if frappe.db.exists("Warehouse", d):
			lft, rgt = frappe.db.get_value("Warehouse", d, ["lft", "rgt"])
			children = frappe.get_all("Warehouse", filters={"lft": [">=", lft], "rgt": ["<=", rgt]})
			all_warehouse += [c.name for c in children]
		else:
			frappe.throw(_("Warehouse: {0} does not exist").format(d))

	return list(set(all_warehouse))