import frappe

def delivery_slip_print_format(docname, print_as_bundle, doctype='Delivery Note Item'):
    posting_date, posting_time = frappe.db.get_value('Delivery Note', docname, ['posting_date', 'posting_time'])
    items =  frappe.db.sql(f"""
                            select 
                                dn_item.item_code,
                                dn_item.against_sales_order,
                                sum(dn_item.ts_qty) as Bdl, 
                                sum(dn_item.pieces) as pieces, 
                                count(dn_item.item_code) as count,
                                case
                                    when ifnull(dn_item.against_sales_order, '') != ''
                                        then (
                                            select
                                                sum(soi.qty)
                                            from `tabSales Order Item` soi
                                            where 
                                                soi.docstatus = 1 and
                                                soi.parent = dn_item.against_sales_order and
                                                soi.item_code = dn_item.item_code
                                        )
                                    else 0
                                end as order_qty,
                                case
                                    when ifnull(dn_item.against_sales_order, '') != ''
                                        then (
                                            select
                                                sum(dni.qty)
                                            from `tabDelivery Note Item` dni
                                            inner join `tabDelivery Note` dn on dn.name = dni.parent
                                            where 
                                                dn.docstatus = 1 and 
                                                dni.docstatus = 1 and
                                                dn.posting_date <= '{posting_date}' and
                                                dn.posting_time <= '{posting_time}' and
                                                dni.against_sales_order = dn_item.against_sales_order and
                                                dni.item_code = dn_item.item_code
                                        )
                                    else 0
                                end as delivered_qty
                            from `tab{doctype}` as dn_item 
                            where 
                                parent='{docname}' 
                            group by 
                                dn_item.item_code,
                                dn_item.against_sales_order
                        """,as_dict=1)
    
    res = {}

    for item in items:
        if item.item_code not in res:
            res[item.item_code] = {
                    'item_name': item.item_code,
                    'order_qty': {},
                    'delivered_qty': {},
                }
            
            order_qty = frappe.db.sql(f"""
                        select
                            sum(soi.qty) as qty,
                            soi.uom
                        from `tabSales Order Item` soi
                        where 
                            soi.docstatus = 1 and
                            soi.parent = "{item.against_sales_order}" and
                            soi.item_code = "{item.item_code}"
                        group by
                            soi.uom
                        """, as_dict=True)
            for r in order_qty:
                res[item.item_code]['order_qty'][r.uom] = r.qty + (res[item.item_code]['order_qty'].get(r.uom) or 0)

            delivered_qty = frappe.db.sql(f"""
                            select
                                sum(dni.qty) as qty,
                                dni.uom
                            from `tabDelivery Note Item` dni
                            inner join `tabDelivery Note` dn on dn.name = dni.parent
                            where 
                                dn.docstatus = 1 and 
                                dni.docstatus = 1 and
                                dn.posting_date <= '{posting_date}' and
                                dn.posting_time <= '{posting_time}' and
                                dni.against_sales_order = "{item.against_sales_order}" and
                                dni.item_code = "{item.item_code}"
                            group by
                                dni.uom
                            """, as_dict=True)
            for r in delivered_qty:
                res[item.item_code]['delivered_qty'][r.uom] = r.qty + (res[item.item_code]['delivered_qty'].get(r.uom) or 0)

    return list(res.values())


def print_format(docname, doctype='Delivery Note Item'):
    same_item=  frappe.db.sql(f"""
                            select 
                                dn_item.item_name, 
                                sum(dn_item.ts_qty) as Bdl, 
                                sum(dn_item.pieces) as pieces, 
                                count(dn_item.item_code) as count 
                            from `tab{doctype}` as dn_item 
                            where 
                                parent='{docname}' 
                            group by 
                                dn_item.item_code 
                            having count(dn_item.item_code)>1 
                        """,as_dict=1)
    return same_item

def check_only_rm(docname):
    doc=frappe.get_doc("Delivery Note", docname)
    return not bool([row for row in doc.items if(row.item_group in ["Pavers", "Compound Walls"])])

def group_dn_items(name, print_as_bundle):
    sum_fields = [
        'qty', 
        'pieces', 
        'ts_qty', 
        'ts_required_area_qty', 
        'pending_qty', 
        'delivery_qty_till_date', 
        'actual_qty'
        ]
    avg_fields = [
        'rate'
        ]
    items = frappe.db.sql(f"""
                    SELECT
                        *
                        {(',' + ",".join([f' sum(dni.{f}) as {f} ' for f in sum_fields])) if sum_fields else ''}
                        {(',' + ",".join([f' avg(dni.{f}) as {f} ' for f in avg_fields])) if avg_fields else ''},
                        GROUP_CONCAT(
                            IF(
                                IFNULL(dni.batch_no, '') != ''
                                , dni.batch_no
                                , NULL
                            ) 
                            SEPARATOR ', '
                        ) as batch_no
                    FROM `tabDelivery Note Item` dni
                    WHERE
                        dni.parenttype = 'Delivery Note' and
                        dni.parent = '{name}'
                    GROUP BY 
                        dni.item_code,
                        dni.rate
                """, as_dict=True)
    return items
