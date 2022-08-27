import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
def item_customization():
    custom_fields={
    "Asset": [
            dict(
            fieldname='tsasset_manufacture',
            label='Based on Manufacture',
            fieldtype='Check',
            insert_after='maintenance_required'
            ),
        dict(
            fieldname='tsasset_manufacture_value',
            label='Manufacture',
            fieldtype='Float',
            insert_after='tsasset_manufacture',
            depends_on="eval:doc.tsasset_manufacture==1"
            ), 
        dict(
            fieldname='tsasset_manufacture_total',
            label='Total Count',
            fieldtype='Float',
            insert_after='tsasset_manufacture_value',
            depends_on="eval:doc.tsasset_manufacture==1",
            read_only=1
            ),  
        dict(
             fieldname='column_break_asset',
             fieldtype='Column Break',
             insert_after='tsasset_manufacture_value',
        ),
        dict(
            fieldname='tsasset_timing',
            label='Based on Timing',
            fieldtype='Check',
            insert_after='column_break_asset'
            ),
        dict(
            fieldname='tsasset_timing_value',
            label='Timing',
            fieldtype='Float',
            insert_after='tsasset_timing',
            depends_on="eval:doc.tsasset_timing==1"
            ), 
        dict(
            fieldname='tsasset_timing_total',
            label='Total Time',
            fieldtype='Float',
            insert_after='tsasset_timing_value',    
            depends_on="eval:doc.tsasset_timing==1",
            read_only=1
            ),      
            
    ]
    }
    create_custom_fields(custom_fields)

