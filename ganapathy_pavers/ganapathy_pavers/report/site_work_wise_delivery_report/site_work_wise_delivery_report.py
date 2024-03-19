# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt
 
import frappe
from frappe import _
from frappe.utils import flt
 
def execute(filters=None):
    from_date = filters.get("from_date")
    to_date = filters.get("to_date") or frappe.utils.nowdate()
    customer = filters.get("customer")
    site_name = filters.get("site_name")
    sales_type = filters.get("sales_type")
    group_by = filters.get("group_by")
    item_code = filters.get("item_code")
    item_group = filters.get("item_group")
    vehicle = filters.get("vehicle_no")
    conditions = " where doc.docstatus = 1"
    if from_date or to_date or customer or site_name or sales_type or group_by or item_code:
        if from_date and to_date:
            conditions += "  and doc.posting_date between '{0}' and '{1}' ".format(from_date, to_date)
        if customer:
            conditions += " and doc.customer ='{0}' ".format(customer)
        if site_name:
            conditions += " and doc.site_work = '{0}' ".format(site_name)
        if sales_type:
            conditions += " and (item.paver_type = '{0}' or item.compound_wall_type = '{0}')".format(sales_type)
        if item_code:
            conditions += " and child.item_code ='{0}' ".format(item_code)
        if item_group:
            conditions += f" and child.item_group in {tuple(item_group)}" if len(item_group)>1 else f" and child.item_group = '{item_group[0]}'"
        if vehicle:
            conditions += f""" and (doc.own_vehicle_no {f"= '{vehicle[0]}'" if len(vehicle)==1 else f"in {tuple(vehicle)}"} or doc.vehicle_no {f"= '{vehicle[0]}'" if len(vehicle)==1 else f"in {tuple(vehicle)}"} )"""
        
    report_data = frappe.db.sql(""" select
                                doc.posting_date,
                                doc.name,
                                doc.customer,
                                doc.type,
                                doc.site_work,
                                child.item_code,
                                child.warehouse,
                                case 
                                    when ifnull(doc.own_vehicle_no, '')!='' 
                                        then doc.own_vehicle_no
                                    else
                                        doc.vehicle_no
                                end as own_vehicle_no,
                                child.ts_qty,
                                child.qty,
                                (child.qty*ifnull((
                                                SELECT
                                                    uom.conversion_factor
                                                FROM `tabUOM Conversion Detail` uom
                                                WHERE
                                                    uom.parenttype='Item' and
                                                    uom.parent=child.item_code and
                                                    uom.uom=child.uom
                                            )
                                            , 0)/
                                            ifnull((
                                                SELECT
                                                    uom.conversion_factor
                                                FROM `tabUOM Conversion Detail` uom
                                                WHERE
                                                    uom.parenttype='Item' and
                                                    uom.parent=child.item_code and
                                                    uom.uom='SQF'
                                            )    
                                            , 0)
                                ) as sqf,
                                child.uom,
                                child.pieces,
                                child.rate,
                                child.amount,
                                doc.grand_total
                                from `tabDelivery Note` as doc
                                left outer join `tabDelivery Note Item` as child
                                    on doc.name = child.parent
                                INNER JOIN `tabItem` as item
                                    on item.name = child.item_code
                                {0}
                                """.format(conditions))
    
    data = [list(i) for i in report_data]
    #    order by doc.posting_date,doc.name
    matched_item=""
    for i in range (0,len(data)-1,1):
        if data[i][1] == data[i+1][1]:
            matched_item = data[i][1]
            data[i+1][-1]=None
        elif matched_item == data[i+1][1]:
            data[i+1][-1]=None
        else:
            matched_item=""

    
    columns = get_columns(filters)
    data.sort(key = lambda x: ((x[0], x[1]) if(group_by == "Date") else ((x[5], x[0]) if(group_by == 'Item Wise') else (x[2], x[0]))))
    matched_item=""
    if group_by!="Customer Wise":
        for i in range (0,len(data)-1,1):
            
            if data[i][1] == data[i+1][1]:
                matched_item = data[i][1]
                data[i+1][0]=None
                data[i+1][1]=None
                data[i+1][2]=None
                data[i+1][3]=None
                data[i+1][4]=None
                    
        
            elif matched_item == data[i+1][1]:
                data[i+1][0]=None
                data[i+1][1]=None
                data[i+1][2]=None
                data[i+1][3]=None
                data[i+1][4]=None
            else:
                matched_item=""
    final_data = (group_total(filters, data) or []) if(data) else []
    return columns, final_data
 
def get_columns(filters={}):
    columns = [
        {
			"label": ("Date"),
			"fieldtype": "Date",
			"fieldname": "date",
			"width": 100,
            "hidden": (filters.get("summary") == 1 and filters.get("group_by") == "Item Wise") or (filters.get("summary") == 1 and filters.get("group_by") == "Customer Wise"),
		},
        {
			"label": ("Document Name"),
			"fieldtype": "Link",
			"fieldname": "document_name",
            "options":"Delivery Note",
			"width": 100,
            "hidden":(filters.get("summary") == 1 and filters.get("group_by") == "Item Wise") or (filters.get("summary") == 1 and filters.get("group_by") == "Customer Wise")
		},
        {
			"label": ("Customer Name"),
			"fieldtype": "Link",
			"fieldname": "customer_name",
            "options":"Customer",
			"width": 200,
            "hidden":(filters.get("summary") == 1 and filters.get("group_by") == "Date") or (filters.get("summary") == 1 and filters.get("group_by") == "Item Wise")
		},
        {
			"label": ("Sales Type"),
			"fieldtype": "Data",
			"fieldname": "sales_type",
			"width": 100,
            "hidden":(filters.get("summary") == 1 and filters.get("group_by") == "Date") or (filters.get("summary") == 1 and filters.get("group_by") == "Item Wise") or (filters.get("summary") == 1 and filters.get("group_by") == "Customer Wise")
		},
        {
			"label": ("Site Name"),
			"fieldtype": "Link",
			"fieldname": "site_name",
            "options":"Project",
			"width": 160,
            "hidden":(filters.get("summary") == 1 and filters.get("group_by") == "Date") or (filters.get("summary") == 1 and filters.get("group_by") == "Item Wise") or (filters.get("summary") == 1 and filters.get("group_by") == "Customer Wise")
		},
        {
			"label": ("Item Name"),
			"fieldtype": "Link",
			"fieldname": "item_name",
            "options":"Item",
			"width": 350,
            "hidden":(filters.get("summary") == 1 and filters.get("group_by") == "Date") or (filters.get("summary") == 1 and filters.get("group_by") == "Customer Wise")
		},
        {
			"label": ("Warehouse"),
			"fieldtype": "Link",
			"fieldname": "warehouse",
            "options":"Warehouse",
			"width": 160,
            "hidden":(filters.get("summary") == 1 and filters.get("group_by") == "Date") or (filters.get("summary") == 1 and filters.get("group_by") == "Item Wise") or (filters.get("summary") == 1 and filters.get("group_by") == "Customer Wise")
		},
        {
			"label": ("Vehicle"),
			"fieldtype": "Link",
			"fieldname": "vehicle",
            "options":"Vehicle",
			"width": 160,
            "hidden":(filters.get("summary") == 1 and filters.get("group_by") == "Date") or (filters.get("summary") == 1 and filters.get("group_by") == "Item Wise") or (filters.get("summary") == 1 and filters.get("group_by") == "Customer Wise")
		},
        {
			"label": ("Bundle"),
			"fieldtype": "Data",
			"fieldname": "bundle",
			"width": 80
		},
        {
			"label": ("Qty"),
			"fieldtype": "Data",
			"fieldname": "qty",
			"width": 80
		},
        {
			"label": ("SQF"),
			"fieldtype": "Data",
			"fieldname": "sqf",
			"width": 80
		},
        {
			"label": ("UOM"),
			"fieldtype": "Link",
            "options": "UOM",
			"fieldname": "uom",
			"width": 100,
            "hidden":(filters.get("summary") == 1 and filters.get("group_by") == "Date") or (filters.get("summary") == 1 and filters.get("group_by") == "Item Wise") or (filters.get("summary") == 1 and filters.get("group_by") == "Customer Wise")
		},
        {
			"label": ("Pieces"),
			"fieldtype": "Data",
			"fieldname": "pieces",
			"width": 80
		},
        {
			"label": ("Rate"),
			"fieldtype": "Data",
			"fieldname": "rate",
			"width": 100
		},
        {
			"label": ("Amount"),
			"fieldtype": "Data",
			"fieldname": "amount",
			"width": 160
		},
       {
			"label": ("Grand Total"),
			"fieldtype": "Data",
			"fieldname": "grand_total",
			"width": 160
		},
        ]
    
    return columns



def group_total(filters = {}, data = []):
    
    if(not filters.get("group_total") and (not filters.get("summary"))  ):
        return data
    else:
        if(filters.get("group_by") == "Date" and filters.get("group_total") ==1):
            ret_list = []
            total = [0] * 16
            data.append([None]*16)
            for row in range(len(data)):
                if(data[row][0] and row!=0 or row == len(data)-1):
                    total[3] = "Group Total"
                    ret_list.append([frappe.bold(("%.2f"%i if (isinstance(i, int) or isinstance(i, float)) else str(i))) if(i!=None) else '' for i in total])
                    ret_list.append([None] * 16)
                    ret_list.append(data[row])
                    total = [0] * 16
                    total = add_list(total, data[row])
                else:
                    ret_list.append(data[row])
                    total = add_list(total, data[row])
            return ret_list
        elif(filters.get("group_by") == "Date" and filters.get("summary") ==1):
            ret_list = []
            total = [0] * 16
            data.append([None]*16)
            count = 0
            for row in range(len(data)):
                if(data[row][0] and row!=0 or row == len(data)-1):
                    total[1] = (data[row][1])

                    if isinstance(total[13], (int, float)):
                        total[13] = flt(total[13], 2) / count

                    ret_list.append([(flt(i,2) if (isinstance(i, int) or isinstance(i, float)) else str(i)) if(i!=None) else '' for i in total])
                    count = 0
                    total = [0] * 16
                    total = add_list(total, data[row])
                    
                else:
                    total = add_list(total, data[row])
                
                count+=1
                
            return ret_list
        
        elif(filters.get("group_by") == "Customer Wise" and filters.get("group_total") ==1):
            ret_list = []
            total = [0] * 16
            data.append([None]*16)
            for row in range(len(data)):
                if(row!=0  and data[row][2]!=data[row-1][2]):
                    total[3] = "Group Total"
                    ret_list.append([frappe.bold(("%.2f"%i if (isinstance(i, int) or isinstance(i, float)) else str(i))) if(i!=None) else '' for i in total])
                    ret_list.append([None] * 16)
                    ret_list.append(data[row])
                    total = [0] * 16
                    total = add_list(total, data[row])
                    
                else:
                    ret_list.append(data[row])
                    total = add_list(total, data[row])
            return ret_list
        elif(filters.get("group_by") == "Customer Wise" and filters.get("summary") ==1):
            ret_list = []
            total = [0] * 16
            data.append([None]*16)
            count = 0
            for row in range(len(data)):
                if(row!=0  and data[row][2]!=data[row-1][2]):
                    total[2] = data[row-1][2]

                    if isinstance(total[13], (int, float)):
                        total[13] = flt(total[13], 2) / count

                    ret_list.append([(flt(i,2) if (isinstance(i, int) or isinstance(i, float)) else str(i)) if(i!=None) else '' for i in total])
                    count = 0
                    total = [0] * 16
                    total = add_list(total, data[row])
                else:
                    total = add_list(total, data[row])
                
                count+=1
            
            return ret_list
        elif(filters.get("group_by") == "Item Wise" and filters.get("summary") ==1):
            ret_list = []
            total = [0] * 16
            data.append([None]*16)
            count = 0
            for row in range(len(data)):
                if(row!=0  and data[row][5]!=data[row-1][5]):
                    total[5] = data[row-1][5]
                    
                    if isinstance(total[13], (int, float)):
                        total[13] = flt(total[13], 2) / count

                    ret_list.append([(flt(i,2) if (isinstance(i, int) or isinstance(i, float)) else str(i)) if(i!=None) else '' for i in total])
                    count = 0
                    total = [0] * 16
                    total = add_list(total, data[row])
                    
                else:
                
                    total = add_list(total, data[row])

                count+=1
            
            return ret_list
        else:
            ret_list = []
            total = [0] * 16
            data.append([None]*16)
            for row in range(len(data)):
                if( row!=0 and data[row][5]!=data[row-1][5]):
                    total[3] = "Group Total"
                    ret_list.append([frappe.bold(("%.2f"%i if (isinstance(i, int) or isinstance(i, float)) else str(i))) if(i!=None) else '' for i in total])
                    ret_list.append([None] * 16)
                    ret_list.append(data[row])
                    total = [0] * 16
                    total = add_list(total, data[row])
                else:
                    ret_list.append(data[row])
                    total = add_list(total, data[row])
            
            return ret_list
    
                
def add_list(a, b):
    ret_list1 = []
    for i in range(len(a)):
        if(isinstance(a[i], (int, float)) or isinstance(b[i], (int, float))):
            ret_list1.append(
                (a[i] if isinstance(a[i], (int, float)) else 0) + 
                (b[i] if isinstance(b[i], (int, float)) else 0)
            )
    
        else:
            ret_list1.append(None)
    return ret_list1
