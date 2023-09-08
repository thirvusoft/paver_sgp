import frappe

def a():
        try:
            res = frappe.call("frappe.event_streaming.doctype.event_update_log.event_update_log.get_update_logs_for_consumer", 
                event_consumer="https://sgpprime.thirvusoft.co.in",
                doctypes=["Company", "Account", "Warehouse", "Item", "Item Group", "Item Tax Template", "Tax Category", "Tax Withholding Category", "Sales Taxes and Charges Template", "Purchase Taxes and Charges Template", "Employee", "Project", "Sales Invoice", "Sales Order", "Payment Entry", "Journal Entry", "Purchase Invoice", "Purchase Order", "Purchase Receipt", "Workstation", "Address", "Contact", "Branch", "Accounting Dimension", "UOM", "Warehouse Type", "Customer", "Supplier", "Bank Account"],
                last_update="2023-07-07 13:15:50"
            )
            f= open("/home/frappe/frappe-bench/apps/ganapathy_pavers/ganapathy_pavers/custom/event_sync_result.txt","w+")
            f.write(res)
            f.close()
            frappe.log_error(title="EVENT SYNC RES", message=frappe.utils.now())
        except:
            frappe.log_error()

def event_sync():   
    frappe.enqueue(method=a, queue='long')

# from ganapathy_pavers.custom.event_sync import event_sync