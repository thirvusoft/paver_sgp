var pavers_per_bundle
frappe.ui.form.on("Item", {
    refresh: function (frm) {
        frm.set_query("compound_wall_sub_type", function() {
            return {
                filters: {
                    compound_wall_type: frm.doc.compound_wall_type
                }
            }
        });
    },
    pavers_per_layer: function (frm, cdt, cdn) {
        var data = locals[cdt][cdn]
        pavers_per_bundle = data.pavers_per_layer * data.no_of_layers_per_bundle
        frm.set_value("pavers_per_bundle", pavers_per_bundle)
    },
    pavers_per_bundle: function (frm, cdt, cdn) {
        Bdl(frm, cdt, cdn)
    },
    weight_per_paver: function (frm, cdt, cdn) {
        Bdl(frm, cdt, cdn)
    },
    weight_per_piece: function (frm, cdt, cdn) {
        Bdl(frm, cdt, cdn)
    },
    pieces_per_bundle: function (frm, cdt, cdn) {
        Bdl(frm, cdt, cdn)
    },
    no_of_layers_per_bundle: function (frm, cdt, cdn) {
        var data = locals[cdt][cdn]
        pavers_per_bundle = data.pavers_per_layer * data.no_of_layers_per_bundle
        frm.set_value("pavers_per_bundle", pavers_per_bundle)
        Bdl(frm, cdt, cdn)
    },
    pavers_per_sqft: function (frm, cdt, cdn) {
        Bdl(frm, cdt, cdn)
    },
    item_group: function (frm, cdt, cdn) {
        if (cur_frm.doc.item_group == "Pavers" || cur_frm.doc.item_group == "Compound Wall")
            frm.set_value("has_batch_no", 1)
        else
            frm.set_value("has_batch_no", 0)

    },

})


function Bdl(frm, cdt, cdn) {
    var data = locals[cdt][cdn]
    var weight_per_paver = data.weight_per_paver
    var weight_per_bundle = data.pavers_per_bundle * weight_per_paver
    if (data.weight_per_piece > 0 && data.pieces_per_bundle > 0) {
        weight_per_bundle = data.pieces_per_bundle * data.weight_per_piece
    }
    frm.set_value("weight_per_bundle", weight_per_bundle.toFixed(2))
    var bundle_per_sqr_ft = data.pavers_per_bundle / data.pavers_per_sqft
    frm.set_value("bundle_per_sqr_ft", bundle_per_sqr_ft.toFixed(2))
}


frappe.ui.form.on("Item", {
    item_group: function (frm) {
        uom(frm);
    },
    pavers_per_sqft: function (frm) {
        uom(frm);
    },
    pavers_per_bundle: function (frm) {
        uom(frm);
    },
    stock_uom: function (frm) {
        uom(frm);
    }
});

function uom(frm) {
    let dict = [];
    if (cur_frm.doc.item_group == "Compound Walls" || cur_frm.doc.item_group == "Pavers") {
        if (cur_frm.doc.stock_uom == "Nos") {
            dict.push({
                "uom": "Nos",
                "conversion_factor": "1"
            })

            if (cur_frm.doc.pavers_per_sqft) {
                dict.push({
                    "uom": "SQF",
                    "conversion_factor": cur_frm.doc.pavers_per_sqft
                })


            }

            if (cur_frm.doc.pavers_per_bundle) {
                dict.push({
                    "uom": "Bdl",
                    "conversion_factor": cur_frm.doc.pavers_per_bundle
                })


            }
            cur_frm.set_value("uoms", dict)
            refresh_field('uoms')
        }
    }
}