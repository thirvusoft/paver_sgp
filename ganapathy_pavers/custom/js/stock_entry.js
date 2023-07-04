var date, distance;
var conversion = true;
frappe.ui.form.on("Stock Entry", {
    refresh: async function (frm) {
        conversion = true;
        await frappe.db.get_list("Vehicle Log", {
            filters: {
                docstatus: ["!=", 2],
                stock_entry: cur_frm.doc.name
            }
        }).then(async res => {
            if (res && res[0]) {
                await cur_frm.add_custom_button("Open Vehicle Log", function () {
                    window.open(`/app/vehicle-log/${res[0].name}`)
                }).removeClass("elipsis").addClass("btn-primary")
            } else if (frm.doc.stock_entry_type == "Material Transfer" && frm.doc.vehicle && frm.doc.docstatus == 1) {
                cur_frm.add_custom_button("Create Vehicle Log", async function () {
                    date = cur_frm.doc.posting_date
                    distance = cur_frm.doc.distance
                    await frappe.run_serially([
                        async () => {
                            await frappe.new_doc("Vehicle Log", {
                                license_plate: frm.doc.vehicle,
                                employee: frm.doc.driver_employee,
                                operator: frm.doc.operator_employee,
                                date: date,
                                select_purpose: "Internal Material Transfer",
                                stock_entry: frm.doc.name,
                            })
                        },
                        () => {
                            cur_frm.set_value("employee", frm.doc.driver_employee)
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
    },
    before_save: function(frm) {
        conversion = false;
        frm.doc.items.forEach(async row => {
            let bdl = await ganapathy_pavers.uom_conversion(row.item_code, row.uom, row.qty, 'Bdl', 0);
            let pieces = await ganapathy_pavers.uom_conversion(row.item_code, 'Bdl', (bdl || 0)%1, 'Nos', 0);
            frappe.model.set_value(row.doctype, row.name, 'ts_qty', parseInt(bdl) || 0);
            frappe.model.set_value(row.doctype, row.name, 'pieces', pieces || 0);

        })
    }
})

frappe.ui.form.on("Stock Entry Detail", {
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
    if (!conversion) {
        return;
    }
    let data = locals[cdt][cdn];

    let pieces_qty = await ganapathy_pavers.uom_conversion(data.item_code, "Nos", data.pieces || 0, data.uom);
    let bdl_qty = await ganapathy_pavers.uom_conversion(data.item_code, "Bdl", data.ts_qty || 0, data.uom);

    frappe.model.set_value(cdt, cdn, "qty", (pieces_qty || 0) + (bdl_qty || 0));
}