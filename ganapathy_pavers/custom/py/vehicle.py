import frappe
from frappe.utils import add_months, add_days, nowdate,get_first_day,get_last_day

def notification(remainder_type, owner, license_plate, maintenance_item, doctype):
    emailid = frappe.get_single("Vehicle Settings").email_id_for_notification
    for email in emailid:
        doc=frappe.new_doc('Notification Log')
        doc.update({
        'subject': f'{license_plate} - Maintenance Alert for {maintenance_item}',
        'for_user': email.email_id,
        'send_email': 1,
        'type': 'Alert',
        'document_type': doctype,
        'document_name': license_plate,
        'from_user':owner,
        'email_content': f'A {remainder_type} Remainder for a Maintenance item: {maintenance_item} in Vehicle: {license_plate}'
        })
        doc.flags.ignore_permissions=True
        doc.save()


def vehicle_maintenance_notification():
    vehicle = frappe.get_all("Maintenance Details", {'parenttype': 'Vehicle'}, pluck='name')
    for doc in vehicle:
        doc=frappe.get_doc('Maintenance Details', doc)
        if (doc.to_date):
            if(doc.month_before and str(doc.to_date) == add_months(nowdate(), 1)):
                notification("Month Before", frappe.session.user, doc.parent, doc.maintenance,'Vehicle')
            if(doc.week_before and str(doc.to_date) == add_days(nowdate(), 7)):
                notification("Week Before", frappe.session.user, doc.parent, doc.maintenance,'Vehicle')
            if(doc.day_before and str(doc.to_date) == add_days(nowdate(), 1)):
                notification("Day Before", frappe.session.user, doc.parent, doc.maintenance,'Vehicle')


@frappe.whitelist()
def get_vehicle_expenses(date):
    month_start_date = get_first_day(date)
    month_end_date = get_last_day(date)
    fuel_query=f"""
        SELECT 
            IFNULL(veh.fuel_account, (SELECT value FROM `tabSingles` sin WHERE sin.doctype='Expense Accounts' and sin.field='default_fuel_account')) AS account,
            veh.name AS vehicle,
            (
                SELECT 
                    SUM(vl.total_fuel)
                FROM `tabVehicle Log` vl
                WHERE
                    vl.docstatus=1
                    AND vl.select_purpose="Fuel"
                    AND vl.license_plate=veh.name
                    AND vl.date between '{month_start_date}' and '{month_end_date}' 
            ) AS amount
        FROM `tabVehicle` veh
    """
    vehicle_expense_query=f"""
        SELECT 
            IFNULL(md.expense_account, md.default_expense_account) AS account,
            CASE 
                WHEN IFNULL(md.from_date, "")!="" AND IFNULL(md.to_date, "")!=""
                    THEN 
                        md.expense / (SELECT TIMESTAMPDIFF(MONTH, md.from_date, md.to_date))
                ELSE md.expense
            END
            *
            CASE
                WHEN md.expense_calculation_per_km=1
                    THEN (
                        SELECT 
                            SUM(vl.today_odometer_value)
                        FROM `tabVehicle Log` vl
                        WHERE
                            vl.docstatus=1
                            AND vl.select_purpose IN (
                                SELECT vlp.select_purpose
                                FROM `tabVehicle Log Purpose` vlp
                                WHERE vlp.parent=md.maintenance and vlp.parentfield="vehicle_log_purpose_per_km"
                            ) 
                            AND vl.license_plate=md.parent
                            AND vl.date between '{month_start_date}' and '{month_end_date}' 
                    )
                WHEN md.expense_calculation_per_vehicle_log=1
                    THEN (
                        SELECT 
                            COUNT(*)
                        FROM `tabVehicle Log` vl
                        WHERE
                            vl.docstatus=1
                            AND vl.select_purpose IN (
                                SELECT vlp.select_purpose
                                FROM `tabVehicle Log Purpose` vlp
                                WHERE vlp.parent=md.maintenance and vlp.parentfield="vehicle_log_purpose_per_log"
                            ) 
                            AND vl.license_plate=md.parent
                            AND vl.date between '{month_start_date}' and '{month_end_date}' 
                    )
                WHEN md.expense_calculation_per_day=1
                    THEN (
                        SELECT 
                            COUNT(DISTINCT(vl.date))
                        FROM `tabVehicle Log` vl
                        WHERE
                            vl.docstatus=1
                            AND vl.select_purpose IN (
                                SELECT vlp.select_purpose
                                FROM `tabVehicle Log Purpose` vlp
                                WHERE vlp.parent=md.maintenance and vlp.parentfield="vehicle_log_purpose_per_day"
                            ) 
                            AND vl.license_plate=md.parent
                            AND vl.date between '{month_start_date}' and '{month_end_date}'
                    )
                ELSE 1
            END
            AS amount,
            md.parent AS vehicle
        FROM `tabMaintenance Details` md
        WHERE
            md.parenttype="Vehicle"
            AND md.expense>0
            AND IFNULL(md.expense_account, IFNULL(md.default_expense_account, ''))!=''
            AND CASE
                    WHEN IFNULL(md.from_date, '')!=''
                        THEN md.from_date<='{month_start_date}'
                    ELSE 1
                    END
            AND CASE
                    WHEN IFNULL(md.to_date, '')!=''
                        THEN md.to_date>='{month_end_date}'
                    ELSE 1
                    END
    """
    fuel_expenses=frappe.db.sql(fuel_query, as_dict=True)
    vehicle_expenses=frappe.db.sql(vehicle_expense_query, as_dict=True)
    return sorted(fuel_expenses+vehicle_expenses, key=lambda x: x.get("vehicle", ""))
