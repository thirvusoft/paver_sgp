
import frappe

def sales_invoice_print_format(docname):
    data={}
    sales_doc=frappe.db.get_all('Sales Invoice Item', filters={'parent':docname}, fields=['print_item_name','item_name',"gst_hsn_code","qty","uom","rate","amount"])
       
    for row in sales_doc:
        if row.print_item_name:
            _key=f"""{row.get("print_item_name")} {row.get("rate")}  {row.get("uom")}"""
            if _key not in data:
                data[_key]={
                "item_name": row.get("print_item_name"),
                "uom": row.get("uom"),
                "rate": row.get("rate"),
                "hsn_code":row.get("gst_hsn_code"),
                "amount": row.get("amount"),
                "qty": row.get("qty")
            }
            else:
                data[_key]["amount"] += row.get("amount")
                data[_key]["qty"] += row.get("qty")
        else:
            _key=f"""{row.get("item_name")} {row.get("rate")}  {row.get("uom")}"""
            if _key not in data:
                data[_key]={
                "item_name": row.get("item_name"),
                "uom": row.get("uom"),
                "rate": row.get("rate"),
                "hsn_code":row.get("gst_hsn_code"),
                "amount": row.get("amount"),
                "qty": row.get("qty")
            }
            else:
                data[_key]["amount"] += row.get("amount")
                data[_key]["qty"] += row.get("qty")

    data=list(data.values())
    return data
  


    