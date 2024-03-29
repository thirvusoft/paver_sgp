# ganapathy_pavers.custom.py.site_transport_cost.update_transport_cost

import frappe
from frappe.utils import formatdate

class SiteTransportCost:
    def __init__(self, site: str):
        self.site = site
        
    def get_transport_cost(self):
        doc = frappe.get_doc('Project', self.site)
        self.vehicle_logs = self.get_vehicle_logs()
        self.driver_salary = self.get_vehicle_log_driver_cost()
        self.operator_salary = self.get_vehicle_log_operator_cost()
        self.get_fuel_maintenance_cost()
        self.fastag_charges = {
            'full_amount': sum(frappe.db.get_all('Vehicle Log', {'docstatus': 1, 'select_purpose': 'Goods Supply', 'site_work': self.site}, pluck='fastag_charge')),
            'customer_scope_amount': sum(frappe.db.get_all('Vehicle Log', {'docstatus': 1, 'select_purpose': 'Goods Supply', 'site_work': self.site, 'is_customer_scope_expense': 'Yes'}, pluck='fastag_charge'))
        }

        self.vehicle_daily_cost = self.get_yearly_maintenance_cost()

        return {
            "value": (sum(self.operator_salary['full_amount'].values()) or 0) + (sum(self.driver_salary['full_amount'].values()) or 0) + (self.maintenance_cost['full_amount'] or 0) + (self.fastag_charges['full_amount'] or 0) + (self.fuel_cost['full_amount'] or 0) + (sum(self.vehicle_daily_cost['full_amount'].values()) or 0),
            "customer_scope_value": (sum(self.operator_salary['customer_scope_amount'].values()) or 0) + (sum(self.driver_salary['customer_scope_amount'].values()) or 0) + (self.maintenance_cost['customer_scope_amount'] or 0) + (self.fastag_charges['customer_scope_amount'] or 0) + (self.fuel_cost['customer_scope_amount'] or 0) + (sum(self.vehicle_daily_cost['customer_scope_amount'].values()) or 0),
            "description": f"""<div>
                        <b>Driver Salary:</b> {", ".join([f"<b>{emp or '-'}</b>: {'%.2f'%(self.driver_salary['full_amount'].get(emp) or 0)}" for emp in self.driver_salary['full_amount']])} <br>
                        <b>Operator Salary:</b> {", ".join([f"<b>{opr or '-'}</b>: {'%.2f'%(self.operator_salary['full_amount'].get(opr) or 0)}" for opr in self.operator_salary['full_amount']])} <br>
                        <b>Maintenance Cost:</b> {'%.2f'%(self.maintenance_cost['full_amount'] or 0)} <br>
                        <b>Fuel:</b> {'%.2f'%(self.fuel_cost['full_amount'] or 0)} <br>
                        <b>Fastag: </b> {'%.2f'%(self.fastag_charges['full_amount'] or 0)} <br>
                        <b>Vehicle Yearly:</b> {", ".join([f"<b>{formatdate(date)}</b>: {'%.2f'%(self.vehicle_daily_cost['full_amount'].get(date) or 0)}" for date in self.vehicle_daily_cost['full_amount']])}
                    </div>""",
            "splitup": [
                *[
                    {
                        'table_head': 'Driver Salary',
                        'row_head': emp,
                        'amount': self.driver_salary['full_amount'].get(emp),
                        'customer_scope_amount': self.driver_salary['customer_scope_amount'].get(emp),
                    }
                    for emp in self.driver_salary['full_amount']
                ],
                {
                    'table_head': 'Driver Salary',
                    'row_head': "Total",
                    'amount': sum(self.driver_salary['full_amount'].values()),
                    'customer_scope_amount': sum(self.driver_salary['customer_scope_amount'].values()),
                    'is_total_row': 1
                },
                *[
                    {
                        'table_head': 'Operator Salary',
                        'row_head': opr,
                        'amount': self.operator_salary['full_amount'].get(opr),
                        'customer_scope_amount': self.operator_salary['customer_scope_amount'].get(opr),
                    }
                    for opr in self.operator_salary['full_amount']
                ],
                {
                    'table_head': 'Operator Salary',
                    'row_head': "Total",
                    'amount': sum(self.operator_salary['full_amount'].values()),
                    'customer_scope_amount': sum(self.operator_salary['customer_scope_amount'].values()),
                    'is_total_row': 1
                },
                {'table_head': 'Maintenance', 'row_head': 'Maintenance Cost', 'amount': self.maintenance_cost['full_amount'] or 0, 'customer_scope_amount': self.maintenance_cost['customer_scope_amount']},
                {'table_head': 'Fuel', 'row_head': 'Fuel Cost', 'amount': self.fuel_cost['full_amount'] or 0, 'customer_scope_amount': self.fuel_cost['customer_scope_amount']},
                {'table_head': 'Fastag', 'row_head': 'Fastag Charge', 'amount': self.fastag_charges['full_amount'] or 0, 'customer_scope_amount': self.fastag_charges['customer_scope_amount']},
                *sorted([
                    {
                        'table_head': 'Vehicle Yearly',
                        'row_head': formatdate(date),
                        'data': date,
                        'amount': self.vehicle_daily_cost['full_amount'].get(date),
                        'customer_scope_amount': self.vehicle_daily_cost['customer_scope_amount'].get(date),
                    }
                    for date in self.vehicle_daily_cost['full_amount']
                ], key = lambda x: ((x.get('table_head') or ''), (x.get('data') or ''), (x.get('amount') or ''),)),
                {
                    'table_head': 'Vehicle Yearly',
                    'row_head': "Total",
                    'amount': sum(self.vehicle_daily_cost['full_amount'].values()),
                    'customer_scope_amount': sum(self.vehicle_daily_cost['customer_scope_amount'].values()),
                    'is_total_row': 1
                },
            ]
        }

    def get_vehicle_logs(self):
        delivery_notes = frappe.get_all("Delivery Note", {"docstatus": 1, "site_work": self.site}, pluck="name")
        vehicle_logs = frappe.get_all("Vehicle Log", filters={
            "docstatus": 1,
            "delivery_note": ["in", delivery_notes],
            "select_purpose": "Goods Supply",
        }, fields=[
            "name", 
            "license_plate", 
            "date", 
            "employee",
            "operator",
            "odometer", 
            "mileage",
            "last_odometer", 
            "delivery_note", 
            "site_work",
            "is_customer_scope_expense"
        ]) if delivery_notes else []
        return vehicle_logs

    def get_vehicle_log_driver_cost(self):
        driver_trips_on_date={}

        for vl in self.vehicle_logs:
            if vl.get("employee") not in driver_trips_on_date:
                driver_trips_on_date[vl.get("employee")] = {}

            if vl.get("date") not in driver_trips_on_date[vl.get("employee")]:
                driver_trips_on_date[vl.get("employee")][vl.get("date")] = []

            driver_trips_on_date[vl.get("employee")][vl.get("date")].append(vl)

        driver_salary = {
            'full_amount': {},
            'customer_scope_amount': {}
        }
        for employee in driver_trips_on_date:
            per_day_salary = frappe.db.get_value("Driver", {"employee": employee}, "salary_per_day") or 0
            for date in driver_trips_on_date.get(employee, {}) or {}:
                vls = (driver_trips_on_date.get(employee, {}) or {}).get(date, []) or []
                odometer = sum([(i.get("odometer") or 0) - (i.get("last_odometer") or 0) for i in vls])
                customer_scope_odometer = sum([(i.get("odometer") or 0) - (i.get("last_odometer") or 0) for i in vls if i.get('is_customer_scope_expense') == 'Yes'])

                total_odometer = sum(frappe.get_all("Vehicle Log", {
                    "docstatus": 1,
                    "employee": employee,
                    "date": date,
                    "select_purpose": ["!=", "Fuel"],
                }, pluck="today_odometer_value"))

                if employee not in driver_salary['full_amount']:
                    driver_salary['full_amount'][employee] = 0
                
                if employee not in driver_salary['customer_scope_amount']:
                    driver_salary['customer_scope_amount'][employee] = 0

                vl_count = []
                for i in vls:
                    if i.get('site_work') not in vl_count:
                        vl_count.append(i.get('site_work'))
                
                salary = ((per_day_salary or 0) * len(vl_count) * odometer / total_odometer) if total_odometer else 0
                driver_salary['full_amount'][employee] += (salary or 0)

                salary = ((per_day_salary or 0) * len(vl_count) * customer_scope_odometer / total_odometer) if total_odometer else 0
                driver_salary['customer_scope_amount'][employee] += (salary or 0)

        return driver_salary

    def get_vehicle_log_operator_cost(self):
        operator_trips_on_date={}

        for vl in self.vehicle_logs:
            operator = vl.get("operator")
            if operator not in operator_trips_on_date:
                operator_trips_on_date[operator] = {}

            if vl.get("date") not in operator_trips_on_date[operator]:
                operator_trips_on_date[operator][vl.get("date")] = []

            operator_trips_on_date[operator][vl.get("date")].append(vl)

        operator_salary = {
            'full_amount': {},
            'customer_scope_amount': {}
        }

        for operator in operator_trips_on_date:
            per_day_salary = frappe.db.get_value("Driver", {'employee': operator}, "salary_per_day") or 0
            for date in operator_trips_on_date.get(operator, {}) or {}:
                vls = (operator_trips_on_date.get(operator, {}) or {}).get(date, []) or []
                odometer = sum([(i.get("odometer") or 0) - (i.get("last_odometer") or 0) for i in vls])
                customer_scope_odometer = sum([(i.get("odometer") or 0) - (i.get("last_odometer") or 0) for i in vls if i.get('is_customer_scope_expense') == 'Yes'])

                total_odometer = sum(frappe.get_all("Vehicle Log", {
                    "docstatus": 1,
                    "operator": operator,
                    "date": date,
                    "select_purpose": ["!=", "Fuel"],
                }, pluck="today_odometer_value"))

                if operator not in operator_salary['full_amount']:
                    operator_salary['full_amount'][operator] = 0
                if operator not in operator_salary['customer_scope_amount']:
                    operator_salary['customer_scope_amount'][operator] = 0

                vl_count = []
                for i in vls:
                    if i.get('site_work') not in vl_count:
                        vl_count.append(i.get('site_work'))

                salary = ((per_day_salary or 0) * len(vl_count) * odometer / total_odometer) if total_odometer else 0
                operator_salary['full_amount'][operator] += (salary or 0)

                salary = ((per_day_salary or 0) * len(vl_count) * customer_scope_odometer / total_odometer) if total_odometer else 0
                operator_salary['customer_scope_amount'][operator] += (salary or 0)

        return operator_salary

    def get_fuel_maintenance_cost(self):
        fuel_cost, customer_scope_fuel_cost = 0, 0
        maintenance_cost, customer_scope_maintenance_cost = 0, 0
        for vl in self.vehicle_logs:
            rate = self.get_last_fuel_rate(vl.get("date"), vl.get("license_plate"))
            distance = (vl.get("odometer", 0) or 0) - (vl.get("last_odometer", 0) or 0)
            maint_rate = frappe.db.get_value("Vehicle", vl.get("license_plate"), "maintenance_per_km") or 0

            maintenance_cost += ((maint_rate or 0) * (distance or 0)) or 0
            if vl.get("is_customer_scope_expense") == 'Yes':
                customer_scope_maintenance_cost += ((maint_rate or 0) * (distance or 0)) or 0

            mileage = vl.get("mileage")
            cost = ((distance*rate/(mileage or 1)) or 0) if mileage else 0

            fuel_cost += cost or 0
            if vl.get("is_customer_scope_expense") == 'Yes':
                customer_scope_fuel_cost += cost or 0

        self.maintenance_cost = {
            "full_amount": maintenance_cost,
            "customer_scope_amount": customer_scope_maintenance_cost
        }

        self.fuel_cost = {
            "full_amount": fuel_cost,
            "customer_scope_amount": customer_scope_fuel_cost
        }

    def get_yearly_maintenance_cost(self):
        yearl_maintenance = {
            'full_amount': {},
            'customer_scope_amount': {}
        }
        date_vehicle_wise_logs = {}

        for vl in self.vehicle_logs:
            if vl.get("date") not in date_vehicle_wise_logs:
                date_vehicle_wise_logs[vl.get("date")] = {}

            if vl.get("license_plate") not in date_vehicle_wise_logs[vl.get("date")]:
                date_vehicle_wise_logs[vl.get("date")][vl.get("license_plate")] = []

            date_vehicle_wise_logs[vl.get("date")][vl.get("license_plate")].append(vl)

        for date in date_vehicle_wise_logs:
            for vehicle in date_vehicle_wise_logs.get(date, {}) or {}:
                for vl in date_vehicle_wise_logs.get(date, {}).get(vehicle):
                    vls = (date_vehicle_wise_logs.get(date, {}) or {}).get(vehicle, []) or []
                    total_odometer = sum(frappe.get_all("Vehicle Log", {
                        "license_plate": vehicle,
                        "date": date,
                        "select_purpose": ["!=", "Fuel"],
                        "docstatus": 1
                    }, pluck="today_odometer_value"))

                    if date not in yearl_maintenance['full_amount']:
                        yearl_maintenance['full_amount'][date] = 0
                    if date not in yearl_maintenance['customer_scope_amount']:
                        yearl_maintenance['customer_scope_amount'][date] = 0

                    main_cost = frappe.db.get_all("Vehicle Yearly Maintenance", {
                        "parenttype": "Vehicle",
                        "parent": vehicle,
                        "from_date": ["<=", date],
                        "to_date": [">=", date]
                    }, ["amount", "no_of_days"])

                    if main_cost:
                        main_cost = ((main_cost[0].amount or 0)/(main_cost[0].no_of_days)) if main_cost[0].no_of_days else 0
                    else:
                        main_cost = 0

                    vl_count = []
                    for i in vls:
                        if i.get('site_work') not in vl_count:
                            vl_count.append(i.get('site_work'))

                    cost = (main_cost * len(vl_count) * ((vl.get("odometer") or 0) - (vl.get("last_odometer") or 0)) / (total_odometer or 1)) if total_odometer else 0
                    yearl_maintenance['full_amount'][date] += (cost or 0)

                    if vl.get('is_customer_scope_expense') == 'Yes':
                        cost = (main_cost * len(vl_count) * ((vl.get("odometer") or 0) - (vl.get("last_odometer") or 0)) / (total_odometer or 1)) if total_odometer else 0
                        yearl_maintenance['customer_scope_amount'][date] += (cost or 0)

        return yearl_maintenance
    
    def get_last_fuel_rate(self, date, vehicle):
        rate = frappe.db.get_all("Vehicle Log", filters = {
            "license_plate": vehicle,
            "date": ["<=", date],
            "select_purpose": "Fuel",
            "docstatus": 1
        }, pluck = "price", order_by="date desc", limit = 1)

        if not rate:
            rate = frappe.db.get_all("Vehicle Log", filters = {
            "license_plate": vehicle,
            "date": [">=", date],
            "select_purpose": "Fuel",
            "docstatus": 1
        }, pluck = "price", order_by="date asc", limit = 1)

        return (rate[0] if len(rate) else 0) or 0

@frappe.whitelist()
def update_transport_cost(sitename):
    cost = SiteTransportCost(sitename)
    trans_cost = cost.get_transport_cost()
    frappe.db.set_value("Project", sitename, "transporting_cost", trans_cost.get("value", 0) or 0, update_modified=False)
    frappe.db.set_value("Project", sitename, "customer_scope_transporting_cost", trans_cost.get("customer_scope_value", 0) or 0, update_modified=False)
    frappe.db.set_value("Project", sitename, "transport_cost_details", trans_cost.get("description", "") or "", update_modified=False)

    site = frappe.get_doc("Project", sitename)
    site.update({
        "transport_cost_splitup": trans_cost.get("splitup", "") or []
    })
    
    site.flags.ignore_validate = True
    site.save()

def update_transport_cost_of_all_sites(self, event = None):
    if self.delivery_note:
        sites = [frappe.get_value("Delivery Note", self.delivery_note, "site_work")]
        vls = frappe.get_all("Vehicle Log", filters={
                    "docstatus": 1,
                    "select_purpose": "Goods Supply",
                    "date": self.date,
                }, fields=["site_work", "delivery_note"])
        for vl in vls:
            if not vl.site_work and vl.delivery_note:
                vl.site_work = frappe.db.get_value("Delivery Note", vl.delivery_note, "site_work")
            
            if vl.site_work and vl.site_work not in sites:
                sites.append(vl.site_work)

        for site in sites:
            if site:
                update_transport_cost(site)
