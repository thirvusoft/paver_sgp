frappe.ui.form.on("Vehicle", {
    onload: function (frm) {
        frm.trigger("odometer_depends_on")
        frm.set_query("workstations", function () {
            return {
                filters: {
                    used_in_expense_splitup: 1
                }
            }
        });
        frm.set_query('operator', function (frm) {
            return {
                filters: {
                    'employee_categories': 'Operator'
                }
            }
        });
        // frm.set_query('employee', function (frm) {
        //     return {
        //         filters: {
        //             'employee_categories': 'Driver'
        //         }
        //     }
        // });
        frm.set_query("add_on", function (frm) {
            return {
                filters: {
                    'is_add_on': ['!=', 1]
                }
            };
        });
    },
    odometer_depends_on: function (frm) {
        if (frm.doc.odometer_depends_on == "Hours") {
            frm.fields_dict.last_odometer.set_label("Last Hours");
            frm.fields_dict.fuel_odometer.set_label("Last Hours  (Fuel or Service)");
        } else {
            frm.fields_dict.last_odometer.set_label("Odometer Value (Last)");
            frm.fields_dict.fuel_odometer.set_label("Odometer (Fuel or Service)");
        }
    },
});

frappe.ui.form.on('Vehicle', {
    refresh: async function (frm) {
        var acc_filters;
        await frappe.call({
            method: "ganapathy_pavers.ganapathy_pavers.doctype.expense_accounts.expense_accounts.get_child_under_vehicle_expense",
            callback(r) {
                acc_filters = r.message;
            }
        });
        frm.set_query("expense_account", "maintanence_details_", function () {
            return {
                filters: {
                    name: ['in', acc_filters],
                    is_group: 0
                }
            }
        });
        frm.set_query("fuel_account", function () {
            return {
                filters: {
                    name: ['in', acc_filters],
                    is_group: 0
                }
            }
        });
    },
});

frappe.ui.form.on("Vehicle Yearly Maintenance", {
    calculate_no_of_days: function (frm, cdt, cdn) {
        let data = locals[cdt][cdn];
        if (data.from_date && data.to_date) {
            let weekends = 0;
            let to_date = new Date(data.to_date);
            let from_date = new Date(data.from_date);

            while (from_date <= to_date) {
                if (from_date.getDay() === 0) {
                    weekends++;
                }
                from_date.setDate(from_date.getDate() + 1);
            }
            let no_of_days = 1 + frappe.datetime.get_day_diff(data.to_date, data.from_date) - weekends
            frappe.model.set_value(cdt, cdn, 'no_of_days', no_of_days)
        } else {
            frappe.model.set_value(cdt, cdn, 'no_of_days', 0)
        }
    }
});
