frappe.ui.form.on("Journal Entry", {
    onload_post_render: function (frm) {
        if (frm.is_new()) {
            frm.set_value("branch", "");
        }
    }
});