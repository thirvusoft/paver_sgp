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