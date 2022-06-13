var pavers_per_bundle
frappe.ui.form.on("Item", {
    pavers_per_layer : function(frm,cdt,cdn) {
        var data = locals[cdt][cdn]
        pavers_per_bundle = data.pavers_per_layer *data.no_of_layers_per_bundle
        frm.set_value("pavers_per_bundle",pavers_per_bundle)
    },
    pavers_per_bundle : function(frm,cdt,cdn) {
        bundle(frm,cdt,cdn)
    },
    weight_per_paver:function(frm,cdt,cdn){
        bundle(frm,cdt,cdn)
    },
    no_of_layers_per_bundle:function(frm,cdt,cdn){
        var data = locals[cdt][cdn]
        pavers_per_bundle = data.pavers_per_layer *data.no_of_layers_per_bundle
        frm.set_value("pavers_per_bundle",pavers_per_bundle)
        bundle(frm,cdt,cdn)
    },
    pavers_per_sqft:function(frm,cdt,cdn){
        bundle(frm,cdt,cdn)
    }
})


function bundle(frm,cdt,cdn) {
    var data = locals[cdt][cdn]
    var weight_per_paver = data.weight_per_paver
    var weight_per_bundle = data.pavers_per_bundle * weight_per_paver
    frm.set_value("weight_per_bundle",weight_per_bundle.toFixed(2))
    var bundle_per_sqr_ft = data.pavers_per_bundle/data.pavers_per_sqft
    frm.set_value("bundle_per_sqr_ft" , bundle_per_sqr_ft.toFixed(2))
}