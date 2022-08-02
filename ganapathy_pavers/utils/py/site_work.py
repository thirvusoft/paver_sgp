from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
def batch_customization():
    batch_custom_fields()
def batch_custom_fields():
    custom_fields = {
        "Project": [
            dict(
                fieldname="previous_state",
                fieldtype="Data",
                label="Previous State",
                hidden=1,
                insert_after="status",
                no_copy=1
            ),
            dict(
                fieldname="more_info",
                fieldtype="Section Break",
                label="More Info",
                insert_after="dust_sweeping",            ),
            dict(
                fieldname="total_rework",
                fieldtype="Int",
                label="Total Rework",
                read_only=1,
                insert_after="more_info",
                no_copy=1
            ),
            ]
    }
    create_custom_fields(custom_fields)
