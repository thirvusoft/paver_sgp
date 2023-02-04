frappe.ui.form.on("Vehicle", {
    onload: function (frm) {
        frm.set_query('operator', function (frm) {
            return {
                filters: {
                    'employee_categories': 'Operator'
                }
            }
        });
        frm.set_query('employee', function (frm) {
            return {
                filters: {
                    'employee_categories': 'Driver'
                }
            }
        });
        frm.set_query("add_on", function (frm) {
            return {
                filters: {
                    'is_add_on': ['!=', 1]
                }
            };
        });
    }
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
