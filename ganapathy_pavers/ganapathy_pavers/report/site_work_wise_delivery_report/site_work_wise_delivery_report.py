# Copyright (c) 2022, Thirvusoft and contributors
# For license information, please see license.txt
 
import frappe
from frappe import _
 
def execute(filters=None):
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")
    customer = filters.get("customer")
    site_name = filters.get("site_name")
    sales_type = filters.get("sales_type")
    group_by = filters.get("group_by")
    conditions = ""
    if from_date or to_date or customer or site_name or sales_type or group_by:
        conditions = " where 1 = 1"
        if from_date and to_date:
            conditions += "  and doc.posting_date between '{0}' and '{1}' ".format(from_date, to_date)
        if customer:
            conditions += " and doc.customer ='{0}' ".format(customer)
        if site_name:
            conditions += " and doc.site_work = '{0}' ".format(site_name)
        if sales_type:
            conditions += " and doc.type = '{0}' ".format(sales_type)
        if group_by == "Date":
            order_by = "doc.posting_date,doc.name"
        else:
            order_by = "child.item_code"
            
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
                                order by {1}
                                """.format(conditions,order_by))
 
    data = [list(i) for i in report_data]
    #    order by doc.posting_date,doc.name
    matched_item=""
    for i in range (0,len(data)-1,1):
        if data[i][1] == data[i+1][1]:
            matched_item = data[i][1]
            data[i+1][0]=""
            data[i+1][1]=""
            data[i+1][2]=""
            data[i+1][3]=""
            data[i+1][4]=""
            data[i+1][12]=""
    
        elif matched_item == data[i+1][1]:
            data[i+1][0]=""
            data[i+1][1]=""
            data[i+1][2]=""
            data[i+1][3]=""
            data[i+1][4]=""
            data[i+1][12]=""
        else:
            matched_item=""
    
    columns = get_columns()
    return columns, data
 
def get_columns():
    columns = [
        _("Date") + ":Date:100",
        _("Document Name") + ":Link/Delivery Note:100",
        _("Customer Name") + ":Link/Customer:200",
        _("Sales Type") + ":Data:100",
        _("Site Name") + ":Link/Project:150",
        _("Item Name") + ":Link/Item:150",
        _("Qty") + ":Int:80",
        _("UOM") + ":Link/UOM:100",
        _("Bundle") + ":Int:80",
        _("Pieces") + ":Int:80",
        _("Rate") + ":Currency:100",
        _("Amount") + ":Currency:150",
        _("Grand Total") + ":Currency:150"
        ]
    
    return columns
