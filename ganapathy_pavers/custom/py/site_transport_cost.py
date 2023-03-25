# ganapathy_pavers.custom.py.site_transport_cost.update_transport_cost

import frappe

class SiteTransportCost:
    def __init__(self, site: str) -> float:
        self.site = site
        
    def get_transport_cost(self):
        self.vehicle_logs = self.get_vehicle_logs()
        self.driver_salary = self.get_vehicle_log_driver_cost()
        self.get_fuel_maintenance_cost()

        return (sum(self.driver_salary.values()) or 0) + (self.maintenance_cost or 0) + (self.fuel_cost or 0)


    def get_vehicle_logs(self):
        delivery_notes = frappe.get_all("Delivery Note", {"docstatus": 1, "site_work": self.site}, pluck="name")
        vehicle_logs = frappe.get_all("Vehicle Log", filters={
            "docstatus": 1,
            "delivery_note": ["in", delivery_notes],
            "select_purpose": "Goods Supply",
        }, fields=["name", "license_plate", "date", "employee", "odometer", "last_odometer", "mileage", "delivery_note"])
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
            for date in driver_trips_on_date.get(employee, {}) or {}:
                count = len(frappe.get_all("Vehicle Log", {
                    "docstatus": 1,
                    "employee": employee,
                    "date": date,
                }))
                if employee not in driver_salary:
                    driver_salary[employee] = 0

                per_day_salary = frappe.db.get_value("Driver", {"employee": employee}, "salary_per_day") or 0
                               
                salary = (per_day_salary or 0) * len((driver_trips_on_date.get(employee, {}) or {}).get(date, {}) or {}) / count
                driver_salary[employee] += (salary or 0)

        return driver_salary

    def get_fuel_maintenance_cost(self):
        fuel_cost = 0
        maintenance_cost = 0
        for vl in self.vehicle_logs:
            rate = self.get_last_fuel_rate(vl.get("date"), vl.get("license_plate"))
            distance = (vl.get("odometer", 0) or 0) - (vl.get("last_odometer", 0) or 0)
            maint_rate = frappe.db.get_value("Vehicle", vl.get("license_plate"), "maintenance_per_km") or 0
            maintenance_cost += ((maint_rate or 0) * (distance or 0)) or 0
            mileage = frappe.db.get_value("Vehicle", vl.get("license_plate"), "mileage") or 0
            cost = ((distance*rate/(mileage or 1)) or 0)

            fuel_cost += cost or 0

        self.maintenance_cost = maintenance_cost
        self.fuel_cost = fuel_cost

    
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
    frappe.db.set_value("Project", sitename, "transporting_cost", cost.get_transport_cost(), update_modified=False)

def update_transport_cost_of_all_sites(self, event = None):
    if self.delivery_note:
        site = frappe.get_value("Delivery Note", self.delivery_note, "site_work")
        if site:
            update_transport_cost(site)
