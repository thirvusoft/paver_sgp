import frappe

def get_sbc_group_items(items, average_fields = []):
    try:
        res = {}
        for row in items:
            row = vars(row)
            if row['item_name'] not in res:
                res[row['item_name']] = row
            else:
                for col in row:
                    if (isinstance(row.get(col), int) or isinstance(row.get(col), float)):
                            if row[col]:
                                if not res[row['item_name']].get("item_count"):
                                    res[row['item_name']]["item_count"] = {}
                                res[row['item_name']]["item_count"][col] = (res[row['item_name']]["item_count"].get(col) or 0) + 1  
                            res[row['item_name']][col] = (res[row['item_name']].get(col) or 0) + row[col]
        
        res = list(res.values())
        for row in res:
            for field in average_fields:
                if row.get(field):
                    row[field] = row[field] / (((row.get('item_count') or {}).get(field) or 0) + 1)
        
        return res
    except:
        frappe.log_error("SBC PRINT", frappe.get_traceback())
        return items
