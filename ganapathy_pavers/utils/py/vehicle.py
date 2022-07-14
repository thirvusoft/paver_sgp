from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.custom.doctype.property_setter.property_setter import make_property_setter
def batch_customization():
    batch_custom_fields()
    batch_property_setter()
def batch_custom_fields():
    custom_fields = {
        "Vehicle": [
            dict(
                fieldname="is_add_on",
                fieldtype="Check",
                label="Is Add-on",
                insert_after="model"
            ),
            dict(
                fieldname="add_on",
                fieldtype="Link",
                label="Add-On",
                insert_after="make",
                options="Vehicle",
				depends_on="eval:doc.is_add_on == 1 "
            )
            ]
    }
    create_custom_fields(custom_fields)
def batch_property_setter():                
    make_property_setter("Vehicle", "add_on_details", "hidden", "1", "Check")