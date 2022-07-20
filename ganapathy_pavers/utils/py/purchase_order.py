from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
def batch_customization():
    batch_custom_fields()
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