frappe.provide("ganapathy_pavers")


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
        frappe.model.set_value(cdt, cdn, 'qty', row.ts_qty * conv1 + row.pieces * conv2)
    } else {
        frappe.model.set_value(cdt, cdn, 'qty', row.ts_qty * conv1 + row.pieces * conv2)
    }
    let rate = row.rate
    frappe.model.set_value(cdt, cdn, 'rate', 0)
    frappe.model.set_value(cdt, cdn, 'rate', rate)

}



frappe.ui.form.on('Delivery Note', {
    onload: async function (frm) {
        frm.set_query('site_work', function (frm) {
            return {
                filters: {
                    'customer': cur_frm.doc.customer,
                    'status': ["not in", ['Completed', 'Billed', 'Cancelled']],
                }
            }
        })
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
            } else if (frm.doc.transporter == "Own Transporter" && frm.doc.own_vehicle_no && frm.doc.docstatus == 1) {
                cur_frm.add_custom_button("Create Vehicle Log", async function () {
                    date = cur_frm.doc.posting_date
                    distance = cur_frm.doc.distance
                    await frappe.run_serially([
                        async () => {
                            await frappe.new_doc("Vehicle Log", {
                                license_plate: frm.doc.own_vehicle_no,
                                employee: frm.doc.employee,
                                operator: frm.doc.operator_employee,
                                date: date,
                                select_purpose: "Goods Supply",
                                delivery_note: frm.doc.name,
                            })
                        },
                        () => {
                            cur_frm.set_value("employee", frm.doc.employee)
                            cur_frm.set_value("operator", frm.doc.operator_employee)
                            cur_frm.set_value("date", date)
                            if (distance) {
                                cur_frm.set_value("odometer", cur_frm.doc.last_odometer + distance)
                            }
                            cur_frm.refresh_fields()
                        }
                    ])

                }).removeClass("elipsis").addClass("btn-primary");
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
    },
    taxes_and_charges: function (frm) {
        if (frm.doc.branch) {
            frappe.db.get_value("Branch", frm.doc.branch, "is_accounting").then(value => {
                if (!value.message.is_accounting) {
                    if (frm.doc.taxes_and_charges)
                        frm.set_value("taxes_and_charges", "");
                    if (frm.doc.tax_category)
                        frm.set_value("tax_category", "");
                    if (frm.doc.taxes)
                        frm.clear_table("taxes");
                    refresh_field("taxes");
                    (cur_frm.doc.items || []).forEach(row => {
                        frappe.model.set_value(row.doctype, row.name, 'unacc', 1);
                        frappe.model.set_value(row.doctype, row.name, 'item_tax_template', '');
                    })
                    refresh_field("items");
                } else {
                    (cur_frm.doc.items || []).forEach(row => {
                        frappe.model.set_value(row.doctype, row.name, 'unacc', 0);
                    })
                }
            })
        }
    },
    tax_category: function (frm) {
        frm.trigger("taxes_and_charges")
    },
    branch: function (frm) {
        frm.trigger("taxes_and_charges")
    },
    validate: function (frm) {
        frm.trigger("taxes_and_charges")
    },
});

frappe.ui.form.on('Delivery Note', "refresh", function (frm) {
    frm.set_query("driver_name_2", function() {
        return {
            filters: {
                employee_categories: "Driver"
            }
        }
    });

    frm.set_query("operator_", function() {
        return {
            filters: {
                employee_categories: "Operator"
            }
        }
    });

    if (!ganapathy_pavers.delivery_note_save_fn) {
        ganapathy_pavers.delivery_note_save_fn = frm.save
        cur_frm.save = function (...args) {
            if (frm.doc.transporter == "Own Transporter" && args[0] == "Submit") {
                if (!cur_dialog) {
                    frappe.confirm(`
                        <div>
                            <div>
                                Is the provided Vehicle, Driver and Operator details are Correct?
                            <div>
                            <div>
                                Vehicle: ${frm.doc.own_vehicle_no || ""}<br> 
                                Driver: ${frm.doc.driver_name_2 || ""}<br>
                                Operator: ${frm.doc.operator_ || ""}<br>
                            <div>
                        <div>`,
                        () => ganapathy_pavers.delivery_note_save_fn.call(frm, ...args),
                        () => $(args[2]).prop('disabled', false)
                    )
                }
            } else {
                ganapathy_pavers.delivery_note_save_fn.call(frm, ...args)
            }
        }
    }
});
