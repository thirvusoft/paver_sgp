var date, distance;
frappe.ui.form.on('Delivery Note Item', {
    ts_qty: function (frm, cdt, cdn) {
        bundle_calc(frm, cdt, cdn)
    },
    conversion_factor: function (frm, cdt, cdn) {
        bundle_calc(frm, cdt, cdn)
    },
    pieces: function (frm, cdt, cdn) {
        bundle_calc(frm, cdt, cdn)
    }

})


async function bundle_calc(frm, cdt, cdn) {
    let row = locals[cdt][cdn]
    let uom = row.uom
    let conv1
    let conv2
    await frappe.db.get_doc('Item', row.item_code).then((doc) => {
        let bundle_conv = 1
        let other_conv = 1;
        let nos_conv = 1
        for (let doc_row = 0; doc_row < doc.uoms.length; doc_row++) {
            if (doc.uoms[doc_row].uom == uom) {
                other_conv = doc.uoms[doc_row].conversion_factor
            }
            if (doc.uoms[doc_row].uom == 'Bdl') {
                bundle_conv = doc.uoms[doc_row].conversion_factor
            }
            if (doc.uoms[doc_row].uom == 'Nos') {
                nos_conv = doc.uoms[doc_row].conversion_factor
            }
        }
        conv1 = bundle_conv / other_conv
        conv2 = nos_conv / other_conv
    })
    if (row.uom == "SQF") {
        frappe.model.set_value(cdt, cdn, 'qty', roundNumber(row.ts_qty * conv1 + row.pieces * conv2))
    } else {
        frappe.model.set_value(cdt, cdn, 'qty', row.ts_qty * conv1 + row.pieces * conv2)
    }
    let rate = row.rate
    frappe.model.set_value(cdt, cdn, 'rate', 0)
    frappe.model.set_value(cdt, cdn, 'rate', rate)

}



frappe.ui.form.on('Delivery Note', {
    onload: async function (frm) {
        if (cur_frm.is_new()) {
            for (let ind = 0; ind < cur_frm.doc.items.length; ind++) {
                let cdt = cur_frm.doc.items[ind].doctype
                let cdn = cur_frm.doc.items[ind].name
                let row = locals[cdt][cdn]
                let uom = row.uom
                let conv1
                let conv2
                if (row.item_code) {
                    await frappe.db.get_doc('Item', row.item_code).then((doc) => {
                        let bundle_conv = 1
                        let other_conv = 1;
                        let nos_conv = 1
                        for (let doc_row = 0; doc_row < doc.uoms.length; doc_row++) {
                            if (doc.uoms[doc_row].uom == uom) {
                                other_conv = doc.uoms[doc_row].conversion_factor
                            }
                            if (doc.uoms[doc_row].uom == 'Bdl') {
                                bundle_conv = doc.uoms[doc_row].conversion_factor
                            }
                            if (doc.uoms[doc_row].uom == 'Nos') {
                                nos_conv = doc.uoms[doc_row].conversion_factor
                            }
                        }
                        conv1 = bundle_conv / other_conv
                        conv2 = nos_conv / other_conv
                    })

                    let total_qty = row.qty
                    await frappe.model.set_value(cdt, cdn, 'ts_qty', parseInt(row.qty / conv1))
                    await frappe.model.set_value(cdt, cdn, 'pieces', 0)
                    let bundle_qty = row.qty
                    let pieces_qty = total_qty - bundle_qty
                    await frappe.model.set_value(cdt, cdn, 'pieces', pieces_qty / conv2)
                    let rate = row.rate
                    frappe.model.set_value(cdt, cdn, 'rate', 0)
                    frappe.model.set_value(cdt, cdn, 'rate', rate)
                }
            }
            let items = cur_frm.doc.items || [];
            let len = items.length;
            while (len--) {
                if (items[len].qty == 0) {
                    await cur_frm.get_field("items").grid.grid_rows[len].remove();
                }
            }
            cur_frm.refresh();


        }
        frm.set_query("own_vehicle_no", function (frm) {
            return {
                filters: {
                    'is_add_on': ['!=', 1]
                }
            };
        });

    },
    on_submit: function (frm) {
        // if (frm.doc.docstatus === 1) {
        //     frm.add_custom_button(__('Notify Supervisor'), function () {

        //     }).addClass("btn btn-primary btn-sm primary-action").css({ ' background-color': '#2490ef', });
        // }

    },
    current_odometer_value: function (frm) {
        cur_frm.set_value("return_odometer_value", (frm.doc.current_odometer_value || 0) + (frm.doc.distance || 0))
    },
    return_odometer_value: function (frm) {
        var total_distance = (cur_frm.doc.return_odometer_value - cur_frm.doc.current_odometer_value)
        cur_frm.set_value("total_distance", total_distance)
    },
    site_work: function (frm, cdt, cdn) {
        cur_frm.set_value('project', cur_frm.doc.site_work)
    },
    refresh: async function (frm) {
        await frappe.db.get_list("Vehicle Log", {
            filters: {
                docstatus: ["!=", 2],
                delivery_note: cur_frm.doc.name
            }
        }).then(async res => {
            if (res && res[0]) {
                await cur_frm.add_custom_button("Open Vehicle Log", function () {
                    window.open(`/app/vehicle-log/${res[0].name}`)
                }).removeClass("elipsis").addClass("btn-primary")
            } else if (frm.doc.transporter=="Own Transporter" && frm.doc.own_vehicle_no && frm.doc.docstatus == 1) {
                cur_frm.add_custom_button("Create Vehicle Log", async function () {
                    date = cur_frm.doc.posting_date
                    distance = cur_frm.doc.distance
                    await frappe.run_serially([
                        async () => {
                            await frappe.new_doc("Vehicle Log", {
                                license_plate: frm.doc.own_vehicle_no,
                                employee: frm.doc.employee,
                                date: date,
                                select_purpose: "Goods Supply",
                                delivery_note: frm.doc.name,
                            })
                        },
                        () => {
                            cur_frm.set_value("date", date)
                            if (distance) {
                                cur_frm.set_value("odometer", cur_frm.doc.last_odometer + distance)
                            }
                        }
                    ])

                }).removeClass("elipsis").addClass("btn-primary")
            }
        })
    }
})

frappe.ui.form.on("Delivery Note Item", {
    item_code: function (frm, cdt, cdn) {
        (cur_frm.doc.items || []).forEach(row => {
            if (row.unacc) {
                frappe.model.set_value(row.doctype, row.name, 'item_tax_template', null);
            }
        })
        refresh_field("items");
    },
    qty: function (frm, cdt, cdn) {
        (cur_frm.doc.items || []).forEach(row => {
            if (row.unacc) {
                frappe.model.set_value(row.doctype, row.name, 'item_tax_template', null);
            }
        })
        refresh_field("items");
    }
});

frappe.ui.form.on("Delivery Note", {
    validate: function (frm) {
        (cur_frm.doc.items || []).forEach(row => {
            if (row.unacc) {
                frappe.model.set_value(row.doctype, row.name, 'item_tax_template', null);
            }
        })
        refresh_field("items");
    }
});
