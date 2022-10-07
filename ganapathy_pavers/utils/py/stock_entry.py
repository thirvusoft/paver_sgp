from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def stock_entry_custom_field():
    custom_fields={
        "Stock Entry Detail":[
            dict(
                fieldname= "basic_rate_hidden",
                fieldtype= "Currency",
                insert_after= "basic_rate",
                label= "Basic Rate Hidden",
                
            ),
            
        ]
    }
    create_custom_fields(custom_fields)