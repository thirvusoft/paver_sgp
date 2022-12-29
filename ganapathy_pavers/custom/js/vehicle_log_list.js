frappe.listview_settings['Vehicle Log'] = {
    onload: function (list_view) {
        list_view.page.add_inner_button(__("Make Journal Entry for Fuel entries"), 
            function () { 
                frappe.call({
                    method: "ganapathy_pavers.custom.py.vehicle_log.supplier_fuel_entry_patch",
                    freeze: true,
                    freeze_message: "Creating Journal Entries",
                })
            });
    }
}