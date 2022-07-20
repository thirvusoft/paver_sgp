from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.custom.doctype.property_setter.property_setter import make_property_setter
def batch_customization():
    batch_custom_fields()
    batch_property_setter()
def batch_custom_fields():
    custom_fields = {
        "Purchase Order": [
            dict(
                fieldname="required_by_date",
                fieldtype="Date",
                label="Required by date",
                insert_after="apply_tds",
                fetch_from="doc.shedule_date",
                allow_on_submit=1
            )
        ]
    }
    create_custom_fields(custom_fields)

def batch_property_setter():                
    make_property_setter("Purchase Order", "schedule_date", "allow_on_submit", "0", "Check")