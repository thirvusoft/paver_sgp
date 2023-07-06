# ganapathy_pavers.custom.py.site_transport_cost.update_transport_cost

import frappe
from frappe.utils import formatdate

class SiteTransportCost:
    def __init__(self, site: str) -> float:
        self.site = site
        
    def get_transport_cost(self):
        doc = frappe.get_doc('Project', self.site)
        self.vehicle_logs = self.get_vehicle_logs()
        self.driver_salary = self.get_vehicle_log_driver_cost()
        self.operator_salary = self.get_vehicle_log_operator_cost()
        self.get_fuel_maintenance_cost()
        self.fastag_charges = sum([(row.amount or 0) for row in doc.additional_cost if 'fastag' in (row.description or '').lower()])
        self.vehicle_daily_cost = self.get_yearly_maintenance_cost()


        return {
            "value": (sum(self.operator_salary.values()) or 0) + (sum(self.driver_salary.values()) or 0) + (self.maintenance_cost or 0) + (self.fastag_charges or 0) + (self.fuel_cost or 0) + (sum(self.vehicle_daily_cost.values()) or 0),
            "description": f"""<div>
                        <b>Driver Salary:</b> {", ".join([f"<b>{emp or '-'}</b>: {'%.2f'%(self.driver_salary.get(emp) or 0)}" for emp in self.driver_salary])} <br>
                        <b>Operator Salary:</b> {", ".join([f"<b>{opr or '-'}</b>: {'%.2f'%(self.operator_salary.get(opr) or 0)}" for opr in self.operator_salary])} <br>
                        <b>Maintenance Cost:</b> {'%.2f'%(self.maintenance_cost or 0)} <br>
                        <b>Fuel:</b> {'%.2f'%(self.fuel_cost or 0)} <br>
                        <b>Fastag: </b> {'%.2f'%(self.fastag_charges or 0)} <br>
                        <b>Vehicle Yearly:</b> {", ".join([f"<b>{formatdate(date)}</b>: {'%.2f'%(self.vehicle_daily_cost.get(date) or 0)}" for date in self.vehicle_daily_cost])}
                    </div>""",
            "splitup": [
                *[
                    {
                        'table_head': 'Driver Salary',
                        'row_head': emp,
                        'amount': self.driver_salary.get(emp),
                    }
                    for emp in self.driver_salary
                ],
                {
                    'table_head': 'Driver Salary',
                    'row_head': "Total",
                    'amount': sum(self.driver_salary.values()),
                    'is_total_row': 1
                },

                *[
                    {
                        'table_head': 'Operator Salary',
                        'row_head': opr,
                        'amount': self.operator_salary.get(opr),
                    }
                    for opr in self.operator_salary
                ],
                {
                    'table_head': 'Operator Salary',
                    'row_head': "Total",
                    'amount': sum(self.operator_salary.values()),
                    'is_total_row': 1
                },
                {'table_head': 'Maintenance', 'row_head': 'Maintenance Cost', 'amount': self.maintenance_cost or 0},
                {'table_head': 'Fuel', 'row_head': 'Fuel Cost', 'amount': self.fuel_cost or 0},
                {'table_head': 'Fastag', 'row_head': 'Fastag Charge', 'amount': self.fastag_charges or 0},
                *sorted([
                    {
                        'table_head': 'Vehicle Yearly',
                        'row_head': formatdate(date),
                        'data': date,
                        'amount': self.vehicle_daily_cost.get(date),
                    }
                    for date in self.vehicle_daily_cost
                ], key = lambda x: ((x.get('table_head') or ''), (x.get('data') or ''), (x.get('amount') or ''),)),
                {
                    'table_head': 'Vehicle Yearly',
                    'row_head': "Total",
                    'amount': sum(self.vehicle_daily_cost.values()),
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
            "odometer", 
            "mileage",
            "last_odometer", 
            "delivery_note", 
        ])
        return vehicle_logs

    def get_vehicle_log_driver_cost(self):
        driver_trips_on_date={}

        for vl in self.vehicle_logs:
            if vl.get("employee") not in driver_trips_on_date:
                driver_trips_on_date[vl.get("employee")] = {}

            if vl.get("date") not in driver_trips_on_date[vl.get("employee")]:
                driver_trips_on_date[vl.get("employee")][vl.get("date")] = []

            driver_trips_on_date[vl.get("employee")][vl.get("date")].append(vl)

        driver_salary = {}
        for employee in driver_trips_on_date:
            per_day_salary = frappe.db.get_value("Driver", {"employee": employee}, "salary_per_day") or 0
            for date in driver_trips_on_date.get(employee, {}) or {}:
                vls = (driver_trips_on_date.get(employee, {}) or {}).get(date, []) or []
                odometer = sum([(i.get("odometer") or 0) - (i.get("last_odometer") or 0) for i in vls])

                total_odometer = sum(frappe.get_all("Vehicle Log", {
                    "docstatus": 1,
                    "employee": employee,
                    "date": date,
                    "select_purpose": ["!=", "Fuel"],
                }, pluck="today_odometer_value")) or 1

                if employee not in driver_salary:
                    driver_salary[employee] = 0

                               
                salary = (per_day_salary or 0) * len((driver_trips_on_date.get(employee, {}) or {}).get(date, []) or []) * odometer / total_odometer
                driver_salary[employee] += (salary or 0)

        return driver_salary

    def get_vehicle_log_operator_cost(self):
        operator_trips_on_date={}

        for vl in self.vehicle_logs:
            operator = frappe.db.get_value("Vehicle", vl.get("license_plate"), "operator")
            if operator not in operator_trips_on_date:
                operator_trips_on_date[operator] = {}

            if vl.get("date") not in operator_trips_on_date[operator]:
                operator_trips_on_date[operator][vl.get("date")] = []

            operator_trips_on_date[operator][vl.get("date")].append(vl)

        operator_salary = {}

        for operator in operator_trips_on_date:
            per_day_salary = frappe.db.get_value("Driver", operator, "salary_per_day") or 0
            for date in operator_trips_on_date.get(operator, {}) or {}:
                vls = (operator_trips_on_date.get(operator, {}) or {}).get(date, []) or []
                odometer = sum([(i.get("odometer") or 0) - (i.get("last_odometer") or 0) for i in vls])

                op_vehicles = frappe.get_all("Vehicle", {"operator": operator}, pluck='name')
                total_odometer = sum(frappe.get_all("Vehicle Log", {
                    "docstatus": 1,
                    "license_plate": ['in', op_vehicles],
                    "date": date,
                    "select_purpose": ["!=", "Fuel"],
                }, pluck="today_odometer_value")) or 1

                if operator not in operator_salary:
                    operator_salary[operator] = 0

                               
                salary = (per_day_salary or 0) * len((operator_trips_on_date.get(operator, {}) or {}).get(date, []) or []) * odometer / total_odometer
                operator_salary[operator] += (salary or 0)

        return operator_salary

    def get_fuel_maintenance_cost(self):
        fuel_cost = 0
        maintenance_cost = 0
        for vl in self.vehicle_logs:
            rate = self.get_last_fuel_rate(vl.get("date"), vl.get("license_plate"))
            distance = (vl.get("odometer", 0) or 0) - (vl.get("last_odometer", 0) or 0)
            maint_rate = frappe.db.get_value("Vehicle", vl.get("license_plate"), "maintenance_per_km") or 0
            maintenance_cost += ((maint_rate or 0) * (distance or 0)) or 0
            mileage = vl.get("mileage")
            cost = ((distance*rate/(mileage or 1)) or 0)

            fuel_cost += cost or 0

        self.maintenance_cost = maintenance_cost
        self.fuel_cost = fuel_cost

    def get_yearly_maintenance_cost(self):
        yearl_maintenance = {}
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
                    total_odometer = sum(frappe.get_all("Vehicle Log", {
                        "license_plate": vehicle,
                        "date": date,
                        "select_purpose": ["!=", "Fuel"],
                        "docstatus": 1
                    }, pluck="today_odometer_value"))

                    if date not in yearl_maintenance:
                        yearl_maintenance[date] = 0

                    main_cost = frappe.db.get_all("Vehicle Yearly Maintenance", {
                        "parenttype": "Vehicle",
                        "parent": vehicle,
                        "from_date": ["<=", date],
                        "to_date": [">=", date]
                    }, ["amount", "no_of_days"])

                    if main_cost:
                        main_cost = (main_cost[0].amount or 0)/(main_cost[0].no_of_days or 1)
                    else:
                        main_cost = 0

                    cost = main_cost * len((date_vehicle_wise_logs.get(date, {}) or {}).get(vehicle, {}) or {}) * ((vl.get("odometer") or 0) - (vl.get("last_odometer") or 0)) / total_odometer
                    yearl_maintenance[date] += (cost or 0)

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
