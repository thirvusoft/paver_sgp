// Copyright (c) 2022, Thirvusoft and contributors
// For license information, please see license.txt

frappe.ui.form.on("CW Manufacturing", {
    refresh: function (frm) {
        frm.set_query("item_to_manufacture", function () {
            return {
                filters: {
                    item_group: "Compound Walls",
                },
            };
        });
        frm.set_query("bom", function () {
            return {
                filters: {
                    item: frm.doc.item_to_manufacture,
                },
            };
        });
    },
    setup: function (frm) {},
    item_to_manufacture: function (frm) {
        if (frm.doc.item_to_manufacture) {
            bom_fetch(frm);
        } else {
            frm.set_value("bom", "");
        }
    },
    before_save: function (frm) {
        item_details_total(frm);
    },
    avg_labour_wages: function (frm) {
        frm.set_value("labour_cost", (frm.doc.avg_labour_wages ? frm.doc.avg_labour_wages : 0) * (frm.doc.no_of_labours ? frm.doc.no_of_labours : 0));
    },
    no_of_labours: function (frm) {
        frm.trigger("avg_labour_wages");
    },
    operator_cost: function (frm) {
        total_expense_per_sqft(frm);
    },
    labour_cost: function (frm) {
        total_expense_per_sqft(frm);
    },
    additional_cost: function (frm) {
        total_expense_per_sqft(frm);
    },
    production_sqft: function (frm) {
        total_expense_per_sqft(frm);
    },
    raw_material_cost: function (frm) {
        total_expense_per_sqft(frm);
    },
});

function bom_fetch(frm) {
    frappe.db
        .get_list("BOM", {
            filters: {
                item: frm.doc.item_to_manufacture,
                is_default: 1,
                is_active: 1,
            },
        })
        .then((value) => {
            if (value.length > 0) {
                frm.set_value("bom", value[0].name);
            }
        });
}

function production_qty_calc(frm, cdt, cdn) {
    let data = locals[cdt][cdn];
    let produced_qty = (data.production_qty ? data.production_qty : 0) - (data.damaged_qty ? data.damaged_qty : 0);
    frappe.model.set_value(cdt, cdn, "produced_qty", produced_qty);
    if (frm.doc.item_to_manufacture) {
        frappe.db.get_value("Item", frm.doc.item_to_manufacture, "pavers_per_sqft", (doc) => {
            frappe.model.set_value(cdt, cdn, "production_sqft", doc.pavers_per_sqft ? (data.produced_qty ? data.produced_qty : 0) / doc.pavers_per_sqft : show_alert(frm.doc.item_to_manufacture, "Pieces Per Sqft"));
        });
    }
}

function show_alert(doc, field) {
    frappe.show_alert({ message: "Please enter value for " + field + " in " + doc });
    return 0;
}

function cost_and_expense(frm, cdt, cdn) {
    let data = locals[cdt][cdn];
    let opr_per_hour_cost = data.operator_cost_per_day ? data.operator_cost_per_day : 0;
    opr_per_hour_cost = opr_per_hour_cost / (data.division > 1 ? (data.total_hrs ? data.total_hrs : 0) : data.this_hrs ? data.this_hrs : 0);
    let opr_cost = (opr_per_hour_cost ? opr_per_hour_cost : 0) * (data.this_hrs ? data.this_hrs : 0) * (data.no_of_operators ? data.no_of_operators : 0);
    frappe.model.set_value(cdt, cdn, "operator_cost", opr_cost);
}

function item_details_total(frm) {
    let item_details = frm.doc.item_details ? frm.doc.item_details : [];
    let total_hrs = 0,
        total_operators = 0,
        total_opr_cost = 0,
        production_qty = 0,
        damage_qty = 0,
        produced_qty = 0,
        production_sqft = 0,
        total_labour_wages = 0,
        table_length = 0;
    for (let i = 0; i < item_details.length; i++) {
        total_hrs += item_details[i].this_hrs ? item_details[i].this_hrs : 0;
        total_operators += item_details[i].no_of_operators ? item_details[i].no_of_operators : 0;
        total_opr_cost += item_details[i].operator_cost ? item_details[i].operator_cost : 0;
        production_qty += item_details[i].production_qty ? item_details[i].production_qty : 0;
        damage_qty += item_details[i].damaged_qty ? item_details[i].damaged_qty : 0;
        produced_qty += item_details[i].produced_qty ? item_details[i].produced_qty : 0;
        production_sqft += item_details[i].production_sqft ? item_details[i].production_sqft : 0;
        total_labour_wages += item_details[i].labour_cost_per_hour ? item_details[i].labour_cost_per_hour : 0;
        if (item_details[i].workstation) {
            table_length += 1;
        }
    }
    frm.set_value("manufacturing_hrs", total_hrs);
    frm.set_value("total_no_of_operators", total_operators);
    frm.set_value("operator_cost", total_opr_cost);
    frm.set_value("avg_labour_wages", (total_labour_wages ? total_labour_wages : 0) / (table_length ? table_length : 0));
    frm.set_value("production_qty", produced_qty);
    frm.set_value("produced_qty", produced_qty);
    frm.set_value("damaged_qty", damage_qty);
    frm.set_value("production_sqft", production_sqft);
}

function total_expense_per_sqft(frm) {
    let total_cost = frm.doc.operator_cost ? frm.doc.operator_cost : 0;
    total_cost += frm.doc.labour_cost ? frm.doc.labour_cost : 0;
    total_cost += frm.doc.additional_cost ? frm.doc.additional_cost : 0;
    total_cost += frm.doc.raw_material_cost ? frm.doc.raw_material_cost : 0;
    frm.set_value("total_expense_per_sqft", frm.doc.production_sqft ? (total_cost ? total_cost : 0) / frm.doc.production_sqft : 0);
}

function raw_material_cost(frm) {
    let items = frm.doc.items,
        total_raw_material_cost = 0;
    for (let i = 0; i < frm.doc.items; i++) {
        total_raw_material_cost += items[i].amount ? items[i].amount : 0;
    }
    frm.set_value("raw_material_cost", total_raw_material_cost);
}

frappe.ui.form.on("CW Items", {
    workstation: function (frm, cdt, cdn) {
        let data = locals[cdt][cdn];
        cost_and_expense(frm, cdt, cdn);
        if (data.workstation) {
            production_qty_calc(frm, cdt, cdn);
            frappe.db.get_doc("Workstation", data.workstation).then((value) => {
                let operator_cost = value.ts_no_of_operator ? (value.ts_sum_of_operator_wages ? value.ts_sum_of_operator_wages : 0) / value.ts_no_of_operator : value.ts_sum_of_operator_wages ? value.ts_sum_of_operator_wages : 0;
                frappe.model.set_value(cdt, cdn, "operator_cost_per_day", operator_cost);
                frappe.model.set_value(cdt, cdn, "no_of_operators", value.ts_no_of_operator ? value.ts_no_of_operator : 0);
                frappe.model.set_value(cdt, cdn, "production_qty", value.production_capacity ? value.production_capacity : 0);
            });
        } else {
            frappe.model.set_value(cdt, cdn, "operator_cost_per_day", 0);
        }
    },
    production_qty: function (frm, cdt, cdn) {
        production_qty_calc(frm, cdt, cdn);
    },
    damaged_qty: function (frm, cdt, cdn) {
        production_qty_calc(frm, cdt, cdn);
    },
    division: function (frm, cdt, cdn) {
        cost_and_expense(frm, cdt, cdn);
    },
    this_hrs: function (frm, cdt, cdn) {
        cost_and_expense(frm, cdt, cdn);
    },
    no_of_operators: function (frm, cdt, cdn) {
        cost_and_expense(frm, cdt, cdn);
    },
    total_hrs: function (frm, cdt, cdn) {
        cost_and_expense(frm, cdt, cdn);
    },
    operator_cost_per_day: function (frm, cdt, cdn) {
        cost_and_expense(frm, cdt, cdn);
    },
});

frappe.ui.form.on("BOM Item", {
    rate: function (frm, cdt, cdn) {
        total_amount(frm, cdt, cdn);
        // frappe.model.set_value(cdt,cdn,"item_tax_template",r.message)
    },
    qty: function (frm, cdt, cdn) {
        total_amount(frm, cdt, cdn);
    },
    item_code: function (frm, cdt, cdn) {
        var d = locals[cdt][cdn];
        if (d.item_code) {
            frappe.call({
                method: "ganapathy_pavers.ganapathy_pavers.doctype.material_manufacturing.material_manufacturing.item_data",
                args: {
                    item_code: d.item_code,
                },
                callback(r) {
                    frappe.model.set_value(cdt, cdn, "rate", r.message[2]);
                    frappe.model.set_value(cdt, cdn, "uom", r.message[1]);
                    frappe.model.set_value(cdt, cdn, "stock_uom", r.message[1]);
                },
            });
        }
        total_amount(frm, cdt, cdn);
    },
});
function total_amount(frm, cdt, cdn) {
    var d = locals[cdt][cdn];
    frappe.model.set_value(cdt, cdn, "amount", d.qty * d.rate);
}
