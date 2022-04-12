frappe.ui.form.on('Timesheet', {
    on_submit: function(frm) {
            frappe.db.get_value('Workstation', {'name':cur_frm.doc.workstation}, '_assign', function(r) {
                cur_frm.assign_to.add();
                cur_frm.assign_to.assign_to.dialog.set_values({assign_to:r._assign});
                setTimeout(() => {
                    frm.assign_to.assign_to.dialog.primary_action();
                }, 100);
			});
        },
});
