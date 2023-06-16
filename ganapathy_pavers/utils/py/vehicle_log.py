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
                options="\nAdblue\nFuel\nGoods Supply\nMaterial Shifting\nOther Work\nRaw Material\nService\nSite Visit"
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
            ),
            dict(
                fieldname="purchase_receipt",
                fieldtype="Link",
                label="Purchase Receipt",
                insert_after="select_purpose",
                options="Purchase Receipt",
                depends_on="eval:doc.select_purpose == 'Raw Material' "
            ),
            dict(
                fieldname="service_item_table",
                fieldtype="Table",
                label="Service Item",
                insert_after="service_detail",
                options="Vehicle Log Service"
            )
            ]
    }
    create_custom_fields(custom_fields)
def batch_property_setter():                
    make_property_setter("Vehicle Log", "add_on_service_details", "hidden", "1", "Check")
    make_property_setter("Vehicle Log", "purpose", "hidden", "1", "Check")
    make_property_setter("Vehicle Service", "frequency", "reqd", "0", "Check")
    make_property_setter("Vehicle Service", "frequency", "hidden", "1", "Check")
    make_property_setter("Vehicle Log", "service_detail", "hidden", "1", "Check")
    make_property_setter("Vehicle Log", "today_odometer_value", "label", "Distance Travelled", "Data")
    make_property_setter("Vehicle Log", "today_odometer_value", "read_only", "1", "Check")
    make_property_setter("Vehicle Log", "select_purpose", "reqd", "1", "Check")