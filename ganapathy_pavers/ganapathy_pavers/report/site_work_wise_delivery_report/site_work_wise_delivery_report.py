# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt
 
from operator import add
from unittest.result import failfast
import frappe
from frappe import _
 
def execute(filters=None):
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")
    customer = filters.get("customer")
    site_name = filters.get("site_name")
    sales_type = filters.get("sales_type")
    group_by = filters.get("group_by")
    item_code = filters.get("item_code")
    conditions = ""
    if from_date or to_date or customer or site_name or sales_type or group_by or item_code:
        conditions = " where 1 = 1"
        if from_date and to_date:
            conditions += "  and doc.posting_date between '{0}' and '{1}' ".format(from_date, to_date)
        if customer:
            conditions += " and doc.customer ='{0}' ".format(customer)
        if site_name:
            conditions += " and doc.site_work = '{0}' ".format(site_name)
        if sales_type:
            conditions += " and doc.type = '{0}' ".format(sales_type)
        if item_code:
            conditions += " and child.item_code ='{0}' ".format(item_code)
        
    report_data = frappe.db.sql(""" select
                                doc.posting_date,
                                doc.name,
                                doc.customer,
                                doc.type,
                                doc.site_work,
                                child.item_code,
                                child.qty,
                                child.uom,
                                child.ts_qty,
                                child.pieces,
                                child.rate,
                                child.amount,
                                doc.grand_total
                                from `tabDelivery Note` as doc
                                left outer join `tabDelivery Note Item` as child
                                    on doc.name = child.parent
                                {0}
                                """.format(conditions))
    
    data = [list(i) for i in report_data]
    #    order by doc.posting_date,doc.name
    matched_item=""
    for i in range (0,len(data)-1,1):
        if data[i][1] == data[i+1][1]:
            matched_item = data[i][1]
            data[i+1][12]=None
        elif matched_item == data[i+1][1]:
            data[i+1][12]=None
        else:
            matched_item=""

    
    columns = get_columns()
    data.sort(key = lambda x: (x[1] if(group_by == "Date") else (x[5]), x[0]))
    matched_item=""
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
 
def get_columns():
    columns = [
        _("Date") + ":Date:100",
        _("Document Name") + ":Link/Delivery Note:100",
        _("Customer Name") + ":Link/Customer:200",
        _("Sales Type") + ":Data:100",
        _("Site Name") + ":Link/Project:150",
        _("Item Name") + ":Link/Item:350",
        _("Qty") + ":Data:80",
        _("UOM") + ":Link/UOM:100",
        _("Bundle") + ":Data:80",
        _("Pieces") + ":Data:80",
        _("Rate") + ":Data:100",
        _("Amount") + ":Data:150",
        _("Grand Total") + ":Data:150"
        ]
    
    return columns



def group_total(filters = {}, data = []):
    if(not filters.get("group_total")):
        return data
    else:
        if(filters.get("group_by") == "Date"):
            ret_list = []
            total = [0] * 13
            data.append([None]*13)
            for row in range(len(data)):
                if(data[row][0] and row!=0 or row == len(data)-1):
                    total[3] = "Group Total"
                    ret_list.append([frappe.bold(str(i)) if(i!=None) else '' for i in total])
                    ret_list.append([None] * 13)
                    ret_list.append(data[row])
                    total = [0] * 13
                    total = add_list(total, data[row])
                else:
                    ret_list.append(data[row])
                    total = add_list(total, data[row])
            return ret_list
        
        else:
            ret_list = []
            total = [0] * 13
            data.append([None]*13)
            for row in range(len(data)):
                if( row!=0 and data[row][5]!=data[row-1][5]):
                    total[3] = "Group Total"
                    ret_list.append([frappe.bold(str(i)) if(i!=None) else '' for i in total])
                    ret_list.append([None] * 13)
                    ret_list.append(data[row])
                    total = [0] * 13
                    total = add_list(total, data[row])
                else:
                    ret_list.append(data[row])
                    total = add_list(total, data[row])
            return ret_list
    
def add_list(a, b):
    ret_list1 = []
    for i in range(len(a)):
        if((isinstance(a[i], int) or isinstance(a[i], float)) and (isinstance(b[i], int) or isinstance(b[i], float))):
            ret_list1.append(a[i] + b[i])
        else:
            ret_list1.append(None)
    return ret_list1