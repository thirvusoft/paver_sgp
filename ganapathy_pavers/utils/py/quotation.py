from frappe.custom.doctype.property_setter.property_setter import make_property_setter
def batch_property_setter():
    make_property_setter("Quotation", "order_type", "default", "", "Small Text")               
    make_property_setter("Quotation", "order_type", "options", "\nPavers\nCompound Wall", "Small Text")