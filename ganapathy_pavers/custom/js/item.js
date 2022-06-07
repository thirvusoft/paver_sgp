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
    weight_per_piece : function(frm,cdt,cdn) {
        bundle(frm,cdt,cdn)
    },
    pieces_per_bundle : function(frm,cdt,cdn) {
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
    },
    item_group:function(frm,cdt,cdn){
            if(cur_frm.doc.item_group=="Pavers"||cur_frm.doc.item_group=="Compound Wall")
                frm.set_value("has_batch_no",1)
            else
                frm.set_value("has_batch_no",0)
    
     }
})


function bundle(frm,cdt,cdn) {
    var data = locals[cdt][cdn]
    var weight_per_paver = data.weight_per_paver
    var weight_per_bundle = data.pavers_per_bundle * weight_per_paver
    if(data.weight_per_piece > 0 && data.pieces_per_bundle > 0){
        weight_per_bundle = data.pieces_per_bundle * data.weight_per_piece
    }
    frm.set_value("weight_per_bundle",weight_per_bundle.toFixed(2))
    var bundle_per_sqr_ft = data.pavers_per_bundle/data.pavers_per_sqft
    frm.set_value("bundle_per_sqr_ft" , bundle_per_sqr_ft.toFixed(2))
}