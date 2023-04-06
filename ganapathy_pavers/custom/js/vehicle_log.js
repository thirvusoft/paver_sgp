var from_lp = 0;

frappe.ui.form.on("Vehicle Log", {
    onload: function (frm) {
        frm.trigger("set_odometer_field_labels");
        frm.set_query("workstations", function () {
            return {
                filters: {
                    used_in_expense_splitup: 1
                }
            }
        });
        if (cur_frm.is_new()) {
            frm.set_value("time", frappe.datetime.now_time())
            frappe.call({
                method: "ganapathy_pavers.custom.py.vehicle_log.fuel_supplier",
                args: { name: frm.doc.name },
                callback(fuel) {
                    cur_frm.set_value("supplier", fuel.message)
                }
            })
        }
    },
    set_odometer_field_labels: async function (frm) {
        if (frm.doc.license_plate) {
            await frappe.db.get_value("Vehicle", frm.doc.license_plate, "odometer_depends_on").then(res => {
                if (res?.message?.odometer_depends_on == "Hours") {
                    frm.fields_dict.today_odometer_value.set_label("Hours Travelled");
                    frm.fields_dict.odometer.set_label("Current Hour");
                    frm.fields_dict.last_odometer.set_label("Last Hours");
                    frm.fields_dict.fuel_odometer_value.set_label("Last Hours (Fuel or Service)");
                } else {
                    frm.fields_dict.today_odometer_value.set_label("Distance Travelled");
                    frm.fields_dict.odometer.set_label("Current Odometer value");
                    frm.fields_dict.last_odometer.set_label("Last Odometer Value");
                    frm.fields_dict.fuel_odometer_value.set_label("Last Odometer Value(Fuel or Service)");
                }
            });
        }
    },
    site_work: async function (frm) {
        if (frm.doc.site_work) {
            await frappe.db.get_doc("Project", frm.doc.site_work).then(site_work => {
                if (site_work.fastag_applicable) {
                    frm.set_value("fastag_charge", site_work.fastag_charge)
                } else {
                    frm.set_value("fastag_charge", 0)
                }
            })
        }
    },
    get_fastag_details: async function (frm) {
        if (frm.doc.select_purpose == "Goods Supply") { 
            await frappe.db.get_doc("Vehicle Settings").then(vs => {
                frm.set_value("payment_to_supplier", vs.payment_to_supplier);
                frm.set_value("fastag_supplier", vs.fastag_supplier);
                frm.set_value("fastag_exp_account", vs.fastag_exp_account);
            });
        } else {
            frm.set_value("payment_to_supplier", "");
            frm.set_value("fastag_supplier", "");
            frm.set_value("credit_account", "");
            frm.set_value("fastag_exp_account", "");
        }
    },
    odometer: function (frm) {
        distance(frm)
    },
    last_odometer: function (frm) {
        distance(frm)
    },
    select_purpose: async function (frm) {
        frm.trigger("get_fastag_details");
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

        if (frm.doc.select_purpose == "Adblue") {
            await frappe.db.get_single_value("Vehicle Settings", "adblue_item_code").then(res => {
                frm.set_value("adblue_item", res || "");
            });
            await frappe.db.get_single_value("Vehicle Settings", "adblue_warehouse").then(res => {
                frm.set_value("adblue_warehouse", res || "");
            });
        } else {
            frm.set_value("fuel_warehouse", "");
        }
    },
    fuel_odometer_value: function (frm) {
        distance(frm)
    },
    license_plate: function (frm) {
        frm.trigger("set_odometer_field_labels");
        distance(frm)
        fetch_expense_details(frm)
    },
    after_save: function (frm) {
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
            frm.set_value("is_shot_blast", vehicle.is_shot_blast)
            frm.set_value("compound_wall", vehicle.compound_wall)
            frm.set_value("fencing_post", vehicle.fencing_post)
            frm.set_value("lego_block", vehicle.lego_block)
        });
    }
}

function distance(frm) {
    frm.set_value('today_odometer_value', (frm.doc.odometer ? frm.doc.odometer : 0) - (["Fuel"].includes(frm.doc.select_purpose) ? (frm.doc.fuel_odometer_value || 0) : (frm.doc.last_odometer || 0)))
}

function zero_alert(field, vehicle = "Vehicle", lp = cur_frm.doc.license_plate, name = cur_frm.doc.license_plate) {
    frappe.show_alert({ message: field + ' is Empty in ' + frappe.utils.get_form_link(vehicle, lp, name) + '..!', indicator: 'red' })

    return 0
}

