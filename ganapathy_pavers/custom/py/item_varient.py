import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.modules.utils import export_customizations

def colour_creation(self,event):
    attribute_table=[]
    color_table=[]
    color_table_sb=[]
    final_color_details=[]
    final_color_table_sb=[]
    # item attribute table
    for i in self.item_attribute_values:
        attribute_table.append((i.attribute_value))

    # Colour Details Child Table
    color_details=frappe.get_meta("Colour Details").fields
    for i in color_details:
        color_table.append(i.fieldname)

     # Colour Details of SB Child Table
    color_details_sb=frappe.get_meta("Colour Details of SB").fields
    for i in color_details_sb:
        color_table_sb.append(i.fieldname)
   
    for j in attribute_table:
        if frappe.scrub(j) not in color_table:
            final_color_details.append(j)
        if frappe.scrub(j) not in color_table_sb:
            final_color_table_sb.append(j)

    # create custom fields for colour details table
    if final_color_details:
        for k in final_color_details:
            color_details_fields(k)
        export_customizations("Ganapathy Pavers", "Colour Details", sync_on_migrate=1, with_permissions=1)
    
    # create custom fields for colour details sb table  
    if final_color_table_sb:
        for k in final_color_table_sb:
            color_details_sb_fields(k)
        export_customizations("Ganapathy Pavers", "Colour Details of SB", sync_on_migrate=1, with_permissions=1)




 # create custom fields for colour details table
def color_details_fields(j):
    custom_fields={
    "Colour Details": [
            dict(
                fieldname=frappe.scrub(j),
                label=f"{j}",
                fieldtype="Float",   
            ),]
    }
    create_custom_fields(custom_fields)
    
   
 # create custom fields for colour details sb table  
def color_details_sb_fields(j):
    custom_fields={
    "Colour Details of SB": [
   
            dict(
                fieldname=frappe.scrub(j),
                label=f"{j}",
                fieldtype="Float",
                
            ),]
    }
    create_custom_fields(custom_fields)