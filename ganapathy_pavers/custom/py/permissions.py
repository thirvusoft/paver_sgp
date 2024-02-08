import frappe
from frappe.permissions import add_permission, update_permission_property

def create_permissions():
    for role in ['Fuel Entry', 'Site Status Update']:
        if(not frappe.db.exists('Role', role)):
            doc=frappe.get_doc({
                'doctype': 'Role',
                'role_name': role
            })
            doc.flags.ignore_mandatory=True
            doc.save()


    add_permission("Vehicle", "Fuel Entry", "1")
    update_permission_property("Vehicle", "Fuel Entry", "1", "read", "1")
    update_permission_property("Vehicle", "Fuel Entry", "1", "write", "1")

    add_permission("Project", "System Manager", "1")
    update_permission_property("Project", "System Manager", "1", "read", "1")

    add_permission("Project", "Site Status Update", "1")
    update_permission_property("Project", "Site Status Update", "1", "read", "1")
    update_permission_property("Project", "Site Status Update", "1", "write", "1")