var pavers_per_bundle
frappe.ui.form.on("Item", {
    pavers_per_layer : function(frm,cdt,cdn) {
        var data = locals[cdt][cdn]
        var pavers_per_layer = data.pavers_per_layer
        var no_of_layers_per_bundle= data.no_of_layers_per_bundle
        pavers_per_bundle = pavers_per_layer * no_of_layers_per_bundle
        frm.set_value("pavers_per_bundle",pavers_per_bundle)
    },
    weight_per_paver : function(frm,cdt,cdn) {
        var data = locals[cdt][cdn]
        var weight_per_paver = data.weight_per_paver
        var weight_per_bundle = pavers_per_bundle * weight_per_paver
        frm.set_value("weight_per_bundle",weight_per_bundle)
    }
})