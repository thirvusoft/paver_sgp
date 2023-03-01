var from_lp = 0;

frappe.ui.form.on("Vehicle Log", {
    onload: function (frm) {
        frm.set_query("workstations", function () {
            return {
                filters: {
                    used_in_expense_splitup: 1
                }
            }
        });
        if (cur_frm.is_new()) {
            frappe.call({
                method: "ganapathy_pavers.custom.py.vehicle_log.fuel_supplier",
                args: { name: frm.doc.name },
                callback(fuel) {
                    cur_frm.set_value("supplier", fuel.message)
                }
            })
        }
    },


    odometer: function (frm) {
        distance(frm)
        total_cost(frm)
    },
    last_odometer: function (frm) {
        distance(frm)
    },
    select_purpose: async function (frm) {
        distance(frm)
        if (frm.doc.select_purpose == "Service") {
            frm.set_value("odometer", frm.doc.last_odometer)
        }
        if (frm.doc.select_purpose == "Fuel") {
            await frappe.db.get_single_value("Vehicle Settings", "default_fuel_warehouse").then(res => {
                frm.set_value("fuel_warehouse", res || "");
            })
        } else {
            frm.set_value("fuel_warehouse", "");
        }
    },
    fuel_odometer_value: function (frm) {
        distance(frm)
    },
    license_plate: function (frm) {
        distance(frm)
        total_cost(frm)
        fetch_expense_details(frm)
    },
    driver_cost: function (frm) {
        if (from_lp) {
            total_cost(frm)
        }
        else {
            from_lp = 1
        }
    },
    ts_driver_cost: function (frm) {
        from_lp = 0
        frm.set_value("driver_cost", frm.doc.ts_driver_cost)
    },
    after_save: function (frm) {
        frappe.db.set_value("Vehicle", frm.doc.license_plate, "driver_cost", frm.doc.driver_cost)
        frappe.db.get_doc('Vehicle', frm.doc.license_plate).then(async (doc) => {
            if (doc.fuel_type == 'Petrol') {
                await frappe.db.set_value("Vehicle Settings", "vehicle_settings", "petrol_per_liter", frm.doc.price)
            }
            else if (doc.fuel_type == 'Diesel') {
                await frappe.db.set_value("Vehicle Settings", "vehicle_settings", "diesel_per_liter", frm.doc.price)

            }
        })
    }
});

async function fetch_expense_details(frm) {
    if (frm.doc.license_plate) {
        await frappe.model.with_doc("Vehicle", frm.doc.license_plate).then(async vehicle => {
            frm.set_value("expense_type", vehicle.expense_type)
            await frm.set_value("workstations", [])
            vehicle.workstations.forEach(async row => {
                let d = frm.add_child("workstations")
                d.workstation = row.workstation || ""
            })
            refresh_field("workstations")
            frm.set_value("paver", vehicle.paver)
            frm.set_value("compound_wall", vehicle.compound_wall)
            frm.set_value("fencing_post", vehicle.fencing_post)
            frm.set_value("lego_block", vehicle.lego_block)
        });
    }
}

function distance(frm) {
    frm.set_value('today_odometer_value', (frm.doc.odometer ? frm.doc.odometer : 0) - (["Fuel"].includes(frm.doc.select_purpose) ? (frm.doc.fuel_odometer_value || 0) : (frm.doc.last_odometer || 0)))
}
function total_cost(frm) {
    if (frm.doc.license_plate) {
        frappe.db.get_doc('Vehicle', frm.doc.license_plate).then(async (doc) => {
            let fuel_cost = 0
            if (doc.fuel_type == 'Petrol') {
                await frappe.db.get_single_value("Vehicle Settings", "petrol_per_liter").then((i) => { fuel_cost = i })
                if (fuel_cost == 0) {
                    zero_alert('Petrol Cost', 'vehicle-settings', 'Vehicle Settings')
                }
            }
            else if (doc.fuel_type == 'Diesel') {
                await frappe.db.get_single_value("Vehicle Settings", "diesel_per_liter").then((i) => { fuel_cost = i })
                if (fuel_cost == 0) {
                    zero_alert('Diesel Cost', 'vehicle-settings', 'Vehicle Settings')
                }
            }
            else {
                frappe.show_alert({ message: 'Please Choose Petrol or Diesel as Fuel Type for ' + frappe.utils.get_form_link('Vehicle', cur_frm.doc.license_plate, cur_frm.doc.license_plate) + '..!', indicator: 'red' })
            }

            let fuel_cost_per_km = (fuel_cost ? fuel_cost : 0) * (frm.doc.today_odometer_value ? frm.doc.today_odometer_value : 0) / (doc.mileage ? doc.mileage : zero_alert('Mileage'));
            let mc = (frm.doc.today_odometer_value ? frm.doc.today_odometer_value : 0) * (doc.maintenance_cost ? doc.maintenance_cost : zero_alert('Maintenance Cost'))
            let dc = (frm.doc.today_odometer_value ? frm.doc.today_odometer_value : 0) * (frm.doc.driver_cost ? frm.doc.driver_cost : 0)
            frm.set_value('ts_total_cost', (fuel_cost_per_km ? fuel_cost_per_km : 0) + (mc ? mc : 0) + (dc ? dc : 0))
            frm.refresh()
        })

    }
}

function zero_alert(field, vehicle = "Vehicle", lp = cur_frm.doc.license_plate, name = cur_frm.doc.license_plate) {
    frappe.show_alert({ message: field + ' is Empty in ' + frappe.utils.get_form_link(vehicle, lp, name) + '..!', indicator: 'red' })

    return 0
}

