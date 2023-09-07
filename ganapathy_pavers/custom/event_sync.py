import frappe

def a():
    frappe.call("from frappe.event_streaming.doctype.event_update_log.event_update_log.get_update_logs_for_consumer", 
        event_consumer="https://sgpprime.thirvusoft.co.in",
        doctypes=["Company", "Account", "Warehouse", "Item", "Item Group", "Item Tax Template", "Tax Category", "Tax Withholding Category", "Sales Taxes and Charges Template", "Purchase Taxes and Charges Template", "Employee", "Project", "Sales Invoice", "Sales Order", "Payment Entry", "Journal Entry", "Purchase Invoice", "Purchase Order", "Purchase Receipt", "Workstation", "Address", "Contact", "Branch", "Accounting Dimension", "UOM", "Warehouse Type", "Customer", "Supplier", "Bank Account"],
        last_update="2023-07-07 13:15:50"
    )
