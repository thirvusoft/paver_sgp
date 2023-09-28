
import frappe

def sales_invoice_print_format(doc, field_name="item_code"):
    data={}
    conv = 1
    if doc.get('running_meter'):
        conv = 19.679411764705883

    for row in doc.items:
        if row.get(field_name):
            _key=f"""{row.get(field_name)} {row.get("rate")}  {row.get("uom")}"""
            if _key not in data:
                row.update({
                "item_name": row.get("item_name"),
                field_name: row.get(field_name),
                "uom": row.get("uom"),
                "rate": row.get("rate") * conv,
                "hsn_code":row.get("gst_hsn_code"),
                "amount": row.get("amount"),
                "qty": row.get("qty") / conv
            })
                data[_key]=row
            else:
                data[_key].amount += row.get("amount")
                data[_key].qty += row.get("qty") / conv
        else:
            _key=f"""{row.get("item_name")} {row.get("rate")}  {row.get("uom")}"""
            if _key not in data:
                row.update({
                "item_name": row.get("item_name"),
                field_name: row.get(field_name),
                "uom": row.get("uom"),
                "rate": row.get("rate") * conv,
                "hsn_code":row.get("gst_hsn_code"),
                "amount": row.get("amount"),
                "qty": row.get("qty") / conv
            })
                data[_key]=row
            else:
                data[_key].amount += row.get("amount")
                data[_key].qty += row.get("qty") / conv

    data=list(data.values())
    return data
  


    