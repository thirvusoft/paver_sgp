import frappe

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

def group_dn_items(name):
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
                    GROUP BY dni.item_code
                """, as_dict=True)
    return items
