frappe.ui.form.ProjectQuickEntryForm = frappe.ui.form.QuickEntryForm.extend({
    render_dialog: async function() {
        this._super();
        this.doc.additional_cost=[{'description': 'Any Food Exp in Site'}, 
                                {'description': 'Other Labour Work'}, 
                                {'description': 'Site Advance'}]
    }
});