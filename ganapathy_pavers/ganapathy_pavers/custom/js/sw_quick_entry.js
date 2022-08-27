frappe.ui.form.ProjectQuickEntryForm = frappe.ui.form.QuickEntryForm.extend({
    render_dialog: async function() {
        this._super();
        if(this.dialog.fields.map(item => { return item.fieldname }).includes('naming_series')){
            this.dialog.set_df_property('naming_series', 'hidden', 1)
        }
        this.doc.additional_cost=[{'description': 'Any Food Exp in Site'}, 
                                {'description': 'Other Labour Work'}, 
                                {'description': 'Site Advance'}]
    }
});