import frappe


def colour_details(colour_stock=[]):
    color_table_label=[]

    # Colour Details Child Table
    color_details=frappe.get_meta("Colour Details").fields

    for i in color_details:
        if i.fieldtype == "Float":
            color_table_label.append(i.label)
    color_table_label=get_labels_with_value(color_table_label, colour_stock)
    color_table_label.sort()
    
    return color_table_label



def colour_details_sb(colour_stock=[]):
    color_table_sb=[]

     # Colour Details of SB Child Table
    color_details_sb=frappe.get_meta("Colour Details of SB").fields

    for i in color_details_sb:
        if i.fieldtype == "Float":
            color_table_sb.append(i.label)
    color_table_sb=get_labels_with_value(color_table_sb, colour_stock)
    color_table_sb.sort()
    return color_table_sb
    
   
def get_labels_with_value(label, table):
    label=[i for i in label if(sum([row.get(frappe.scrub(i), 0) or 0 for row in table])>0)]
    return label
   
   