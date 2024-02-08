import frappe

def stock_entry_type_permission(user):
    if not user:
        user = frappe.session.user
    
    if user == "Administrator" or 'Stock Reconciliation' in frappe.get_roles():
        return ''

    return f"""(`tabStock Entry Type`.purpose != "Material Issue")"""

def has_stock_entry_type_permission(doc, user):
    if (user or frappe.session.user) == "Administrator" or 'Stock Reconciliation' in frappe.get_roles():
        return True
    
    if doc.purpose == "Material Issue":
        return False

    return True