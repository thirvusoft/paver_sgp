
import frappe
import ganapathy_pavers

def sales_invoice_print_format(doc, field_name="item_code"):
    data={}

    for row in doc.items:
        conv = 1
        uom = row.get('uom')
        if doc.get('running_meter') and doc.get('running_meter_uom') and (item_meter_conv:=ganapathy_pavers.uom_conversion(item=row.get('item_code'), from_uom=row.get('uom'), from_qty=1, to_uom=doc.get('running_meter_uom'), throw_err=False)):
            conv = 1/item_meter_conv
            uom = doc.get('running_meter_uom')

        if row.get(field_name):
            _key=f"""{row.get(field_name)} {row.get("rate")}  {uom}"""
            if _key not in data:
                row.update({
                "item_name": row.get("item_name"),
                field_name: row.get(field_name),
                "uom": uom,
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
            _key=f"""{row.get("item_name")} {row.get("rate")}  {uom}"""
            if _key not in data:
                row.update({
                "item_name": row.get("item_name"),
                field_name: row.get(field_name),
                "uom": uom,
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
  


    