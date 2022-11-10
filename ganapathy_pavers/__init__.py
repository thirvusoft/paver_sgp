
__version__ = '0.0.1'

from ganapathy_pavers.ganapathy_pavers.doctype.cw_manufacturing.cw_manufacturing import throw_error
import frappe

def uom_conversion(item, from_uom='', from_qty=0, to_uom=''):
    if(not from_uom):
        from_uom = frappe.get_value('Item', item, 'stock_uom')
    item_doc = frappe.get_doc('Item', item)
    from_conv = 0
    to_conv = 0
    for row in item_doc.uoms:
        if(row.uom == from_uom):
            from_conv = row.conversion_factor
        if(row.uom == to_uom):
            to_conv = row.conversion_factor
    if(not from_conv):
        throw_error(from_uom + " Bundle Conversion", item)
    if(not to_conv):
        throw_error(to_uom + " Bundle Conversion", item)
    
    return (float(from_qty) * from_conv) / to_conv