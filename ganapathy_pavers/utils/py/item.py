from frappe.custom.doctype.property_setter.property_setter import make_property_setter
def batch_customization():
    batch_property_setter()
def batch_property_setter():                
    make_property_setter("Item", "serial_nos_and_batches", "depends_on", "eval:doc.item_group != 'Raw Material'", "Data")
    make_property_setter("Item", "reorder_section", "depends_on", "eval:doc.item_group != 'Pavers' && doc.item_group != 'Compound Walls'", "Data")
    make_property_setter("Item", "section_break_11", "depends_on", "eval:doc.item_group != 'Compound Walls'", "Data")
    make_property_setter("Item", "brand", "depends_on", "eval:doc.item_group != 'Compound Walls'", "Data")
    make_property_setter("Item", "opening_stock", "depends_on", "eval:doc.item_group != 'Compound Walls'", "Data")
    make_property_setter("Item", "valuation_rate", "depends_on", "eval:doc.item_group != 'Compound Walls'", "Data")
    make_property_setter("Item", "standard_rate", "depends_on", "eval:doc.item_group != 'Compound Walls'", "Data")
    make_property_setter("Item", "is_fixed_asset", "depends_on", "eval:doc.item_group != 'Compound Walls'", "Data")
    make_property_setter("Item", "per_rack", "depends_on", "eval:doc.item_group != 'Compound Walls'", "Data")
    make_property_setter("Item", "per_plate", "depends_on", "eval:doc.item_group != 'Compound Walls'", "Data")
    make_property_setter("Item", "pavers_per_layer", "depends_on", "eval:doc.item_group != 'Compound Walls'", "Data")
    make_property_setter("Item", "no_of_layers_per_bundle", "depends_on", "eval:doc.item_group != 'Compound Walls'", "Data")
    make_property_setter("Item", "stock_uom", "default", "Nos", "Data")