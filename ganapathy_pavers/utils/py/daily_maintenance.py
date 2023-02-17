import frappe


def colour_details():
   
    color_table_label=[]
    color_table_fieldname=[]
    finaldict={}

    # Colour Details Child Table
    color_details=frappe.get_meta("Colour Details").fields

    for i in color_details:
        if i.fieldtype == "Float":
            color_table_label.append(i.label)
            color_table_fieldname.append(i.label)
    color_table_label.sort()
    
    return color_table_label



def colour_details_sb():
    color_table_sb=[]
     # Colour Details of SB Child Table
    color_details_sb=frappe.get_meta("Colour Details of SB").fields
    for i in color_details_sb:
        if i.fieldtype == "Float":
            color_table_sb.append(i.label)
            
    color_table_sb.sort()
    return color_table_sb
    
   
    
   
   