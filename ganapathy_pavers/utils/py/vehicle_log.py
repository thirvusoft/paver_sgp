from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.custom.doctype.property_setter.property_setter import make_property_setter
def batch_customization():
    batch_custom_fields()
    batch_property_setter()
def batch_custom_fields():
    custom_fields = {
        "Vehicle Log": [
            dict(
                fieldname="select_purpose",
                fieldtype="Select",
                label="Purpose",
                insert_after="today_odometer_value",
                options="\nFuel\nRaw Material\nService\nGoods Supply"
            ),
            dict(
                fieldname="sales_invoice",
                fieldtype="Link",
                label="Sales Invoice",
                insert_after="odometer",
                options="Sales Invoice",
                depends_on="eval:doc.select_purpose == 'Goods Supply' "
            ),
            dict(
                fieldname="purchase_invoice",
                fieldtype="Link",
                label="Purchase Invoice",
                insert_after="odometer",
                options="Purchase Invoice",
                depends_on="eval:doc.select_purpose == 'Raw Material' "
            )
            ]
    }
    create_custom_fields(custom_fields)
def batch_property_setter():                
    make_property_setter("Vehicle Log", "add_on_service_details", "hidden", "1", "Section Break")
    make_property_setter("Vehicle Log", "purpose", "hidden", "1", "Data")
    