# import frappe

def get_sbc_group_items(items):
    try:
        res = {}
        for row in items:
            row = vars(row)
            if row['item_name'] not in res:
                res[row['item_name']] = row
            else:
                for col in row:
                    if (isinstance(row.get(col), int) or isinstance(row.get(col), float)):
                            res[row['item_name']][col] = (res[row['item_name']].get(col) or 0) + row[col]
        return list(res.values())
    except:
         return items