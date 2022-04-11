var pavers_per_bundle
frappe.ui.form.on("Item", {
    pavers_per_layer : function(frm,cdt,cdn) {
        var data = locals[cdt][cdn]
        pavers_per_bundle = data.pavers_per_layer *data.no_of_layers_per_bundle
        frm.set_value("pavers_per_bundle",pavers_per_bundle)
    },
    pavers_per_bundle : function(frm,cdt,cdn) {
        var data = locals[cdt][cdn]
        var weight_per_paver = data.weight_per_paver
        var weight_per_bundle = pavers_per_bundle * weight_per_paver
        frm.set_value("weight_per_bundle",weight_per_bundle)
        var bundle_per_sqr_ft = data.pavers_per_sqft* data.pavers_per_bundle
        frm.set_value("bundle_per_sqr_ft" , bundle_per_sqr_ft)
    }
})
