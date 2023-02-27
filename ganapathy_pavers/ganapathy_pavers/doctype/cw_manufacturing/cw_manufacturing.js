// Copyright (c) 2022, Thirvusoft and contributors
// For license information, please see license.txt

function throw_error(doc, field) {
    frappe.throw({ message: "Please enter value for " + field + " in " + doc });
}

frappe.ui.form.on("CW Manufacturing", {
    refresh: async function (frm) {
        if (frm.is_new()) {
            default_value(frm, "labour_cost_per_hrs", "labour_salary_per_hrs");
            default_value_from_table(frm, "strapping_cost", frm.doc.type, "strapping_cost_per_sqft_unmold", 0);
            default_value(frm, "labour_cost_per_sqft", "labour_cost_per_sqft_curing");
            frm.trigger("get_bin_items");
        }

        frm.set_query("item", "item_details", function () {
            return {
                filters: {
                    item_group: "Compound Walls",
                },
            };
        });
        frm.set_query("bom", "item_details", function (frm, cdt, cdn) {
            let data = locals[cdt][cdn];
            return {
                filters: {
                    item: data.item,
                },
            };
        });
        frm.set_query("item", "item_details", function (frm1, cdt, cdn) {
            return {
                filters: {
                    compound_wall_type: frm.doc.type,
                    item_group: "Compound Walls",
                },
            };
        });
        frm.set_query("item_code", "bin_items", function () {
            return {
                "filters": {
                    item_group: "Raw Material"
                }
            }
        })
        set_css(frm);
    },
    get_bin_items: async function (frm) {
        frm.clear_table("bin_items");
        frm.fields_dict.bin_items?.refresh()
        await frappe.db.get_doc("CW Settings").then(bin_items_map => {
            (bin_items_map.bin_items || []).forEach(bin => {
                let row = frm.add_child("bin_items")
                row.item_code = bin.item_code
                row.bin = bin.bin
            });
            frm.fields_dict.bin_items?.refresh()
        })
    },
    onload: function (frm) { },
    type: function (frm) {
        default_value_from_table(frm, "strapping_cost", frm.doc.type, "strapping_cost_per_sqft_unmold", 0);
    },
    ts_before_save: function (frm) {
        let rm_consmp = frm.doc.raw_material_consumption ? frm.doc.raw_material_consumption : [],
            bin_items = frm.doc.bin_items ? frm.doc.bin_items : [],
            check_duplicate = [];

        bin_items.forEach(row => {
            if (check_duplicate.includes(row.item_code)) {
                frappe.throw(`Bin <b>${row.bin}</b> is repeating more than once in <b>Bin Item Mapping</b>`)
            } else {
                row.total_qty = 0
                check_duplicate.push(row.item_code)
            }
        });

        rm_consmp.forEach(row => {
            bin_items.forEach(bin => {
                bin.total_qty += (row[frappe.model.scrub(bin.bin || "")] || 0)
            });
        });
        frm.fields_dict.bin_items.refresh()

        item_details_total(frm);
        raw_material_cost(frm);
        total_expense_per_sqft(frm);
        total_expense_per_sqft_unmold(frm);
        labour_expense_curing(frm);
    },
    before_save: async function (frm) {
        await frm.trigger("ts_before_save").then(async (ret) => {
            no_of_batches_count(frm);
            // if (!frm.is_new()) {
            //     await frappe.call({
            //         method: "ganapathy_pavers.ganapathy_pavers.doctype.cw_manufacturing.cw_manufacturing.find_batch",
            //         args: {
            //             name: frm.doc.name,
            //         },
            //         callback: function (r) {
            //             frm.set_value("cw_manufacturing_batch_details", r.message[0]);
            //             frm.set_value("cw_unmolding_batch_details", r.message[1]);
            //             frm.set_value("cw_curing_batch_details", r.message[2]);
            //         },
            //     });
            // }
        });
    },
    labour_salary_per_hrs: function (frm) {
        frm.set_value("total_labour_wages", frm.doc.labour_salary_per_hrs * frm.doc.manually_total_working_hrs);
    },
    manually_total_working_hrs: function (frm) {
        frm.set_value("total_labour_wages", frm.doc.labour_salary_per_hrs * frm.doc.manually_total_working_hrs);
    },
    total_labour_wages: function (frm) {
        frm.set_value("total_expence", frm.doc.total_labour_wages + frm.doc.total_operator_wages + frm.doc.additional_cost_in_wages + frm.doc.raw_material_cost);
    },
    total_operator_wages: function (frm) {
        frm.set_value("total_expence", frm.doc.total_labour_wages + frm.doc.total_operator_wages + frm.doc.additional_cost_in_wages + frm.doc.raw_material_cost);
    },
    additional_cost_in_wages: function (frm) {
        frm.set_value("total_expence", frm.doc.total_labour_wages + frm.doc.total_operator_wages + frm.doc.additional_cost_in_wages + frm.doc.raw_material_cost);
    },
    total_expence: function (frm) {
        frm.set_value("total_expence_per_sqft", frm.doc.total_expence / frm.doc.ts_production_sqft);
    },
    molding_date: function (frm) {
        working_hrs(frm);
    },
    get_working_hrs_for_compound_wall: function (frm) {
        working_hrs(frm);
    },
    get_operators: function (frm) {
        frappe.call({
            method: "ganapathy_pavers.ganapathy_pavers.doctype.cw_manufacturing.cw_manufacturing.get_operators",
            args: {
                doc: frm.doc.item_details ? frm.doc.item_details : [],
                item_count: frm.doc.item_count ? frm.doc.item_count : 1,
            },
            callback: function (r) {
                frm.set_value("operator_details", r.message);
                frm.set_value("no_of_operators", r.message.length);
                var total_operator_wages = 0;
                for (let row = 0; row < r.message.length; row++) {
                    total_operator_wages += r.message[row].division_salary;
                }
                frm.set_value("total_operator_wages", total_operator_wages);
            },
        });
    },
    item_count: function (frm) {
        let operator_details = frm.doc.operator_details ? frm.doc.operator_details : [],
            total_operator_wages = 0;
        for (let row = 0; row < operator_details.length; row++) {
            let cdt = operator_details[row].doctype,
                cdn = operator_details[row].name;
            let data = locals[cdt][cdn];
            let wages = (data.salary ? data.salary : 0) / (frm.doc.item_count ? frm.doc.item_count : 1);
            frappe.model.set_value(cdt, cdn, "division_salary", wages);
            total_operator_wages += wages;
        }
        frm.set_value("total_operator_wages", total_operator_wages);
    },
    get_bom_items: async function (frm) {
        frm.clear_table("items");
        await std_item(frm).then((a) => item_adding(frm));

        raw_material_cost(frm);
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
    additional_cost_unmold: function (frm) {
        total_expense_per_sqft_unmold(frm);
    },
    production_sqft: function (frm) {
        total_expense_per_sqft(frm);
    },
    total_production_sqft: function (frm) {
        total_expense_per_sqft_unmold(frm);
    },
    raw_material_cost: function (frm) {
        total_expense_per_sqft(frm);
    },
    strapping_cost_per_sqft_unmold: function (frm) {
        total_expense_per_sqft_unmold(frm);
    },
    create_stock_entry_for_molding: async function (frm) {
        if (frm.is_dirty()) {
            frappe.show_alert({
                message: "Please save this form before doing this operation.",
                indicator: "red",
            });
        } else {
            frappe.call({
                method: "ganapathy_pavers.ganapathy_pavers.doctype.cw_manufacturing.cw_manufacturing.make_stock_entry_for_molding",
                args: {
                    doc: frm.doc,
                },
                callback: async function (r) {
                    if (r.message) {
                        await frm.reload_doc()
                        frm.save();
                    }
                },
            });
        }
    },
    create_stock_entry_for_bundling: function (frm) {
        if (frm.is_dirty()) {
            frappe.show_alert({
                message: "Please save this form before doing this operation.",
                indicator: "red",
            });
        } else {
            frappe.call({
                method: "ganapathy_pavers.ganapathy_pavers.doctype.cw_manufacturing.cw_manufacturing.make_stock_entry_for_bundling",
                args: {
                    doc: frm.doc,
                },
                callback: async function (r) {
                    if (r.message) {
                        await frm.reload_doc()
                        frm.save();
                    }
                },
            });
        }
    },
    create_stock_entry_for_curing: function (frm) {
        if (frm.is_dirty()) {
            frappe.show_alert({
                message: "Please save this form before doing this operation.",
                indicator: "red",
            });
        } else {
            frappe.call({
                method: "ganapathy_pavers.ganapathy_pavers.doctype.cw_manufacturing.cw_manufacturing.make_stock_entry_for_curing",
                args: {
                    doc: frm.doc,
                },
                callback: async function (r) {
                    if (r.message) {
                        await frm.reload_doc()
                        frm.save();
                    }
                },
            });
        }
    },
    labour_cost_per_sqft_curing: function (frm) {
        labour_expense_curing(frm);
    },
});

function labour_expense_curing(frm) {
    frm.set_value("labour_expense_for_curing", (frm.doc.bundled_sqft_curing ? frm.doc.bundled_sqft_curing : 0) * (frm.doc.labour_cost_per_sqft_curing ? frm.doc.labour_cost_per_sqft_curing : 0));
}

function working_hrs(frm) {
    if (frm.doc.molding_date) {
        frappe.db.get_single_value("CW Settings", "working_area").then((value) => {
            if (!value) {
                frappe.throw({ message: "Please choose Working Area for compound wall in CW Settings" });
            }
            if (!frm.doc.molding_date) {
                frappe.throw({ message: "Please enter Manufacturing Date" });
            }
            frm.set_value("work_area", value ? value : "");
            frappe.call({
                method: "ganapathy_pavers.ganapathy_pavers.doctype.cw_manufacturing.cw_manufacturing.get_working_hrs",
                args: {
                    attendance_date: frm.doc.molding_date,
                    machine: value,
                },
                callback: function (r) {
                    frm.set_value("total_working_hrs", r.message.hours ? r.message.hours : 0);
                    frm.set_value("no_of_labour", r.message.labours ? r.message.labours : 0);
                },
            });
        });
    }
}

function no_of_batches_count(frm) {
    let raw_material = frm.doc.items ? frm.doc.items : [];
    let usb_count = frm.doc.raw_material_consumption ? frm.doc.raw_material_consumption.length : 0;
    for (let row = 0; row < raw_material.length; row++) {
        let cdt = raw_material[row].doctype,
            cdn = raw_material[row].name;
        let data = locals[cdt][cdn];
        if (data.from_usb == 1) {
            frappe.model.set_value(cdt, cdn, "no_of_batches", usb_count);
        }
    }
}
function bom_fetch(frm, item, cdt = "", cdn = "", is_child = 0) {
    frappe.db
        .get_list("BOM", {
            filters: {
                item: item,
                is_default: 1,
                is_active: 1,
            },
        })
        .then((value) => {
            if (value.length > 0) {
                if (is_child == 1) {
                    frappe.model.set_value(cdt, cdn, "bom", value[0].name);
                } else {
                    frm.set_value("bom", value[0].name);
                }
            }
        });
}

function production_qty_calc(frm, cdt, cdn) {
    let data = locals[cdt][cdn];
    let produced_qty = (data.production_qty ? data.production_qty : 0) - (data.damaged_qty ? data.damaged_qty : 0);
    frappe.model.set_value(cdt, cdn, "produced_qty", produced_qty);
    if (data.item) {
        frappe.call({
            method: "ganapathy_pavers.ganapathy_pavers.doctype.cw_manufacturing.cw_manufacturing.uom_conversion",
            args: {
                item: data.item,
                from_uom: "Nos",
                from_qty: data.produced_qty ? data.produced_qty : 0,
                to_uom: "SQF",
            },
            callback: function (r) {
                frappe.model.set_value(cdt, cdn, "production_sqft", r.message || 0);
            },
        });
        frappe.call({
            method: "ganapathy_pavers.ganapathy_pavers.doctype.cw_manufacturing.cw_manufacturing.uom_conversion",
            args: {
                item: data.item,
                from_uom: "Nos",
                from_qty: data.production_qty ? data.production_qty : 0,
                to_uom: "SQF",
            },
            callback: function (r) {
                frappe.model.set_value(cdt, cdn, "ts_production_sqft", r.message || 0);
            },
        });
    }
}

function show_alert(doc, field) {
    frappe.show_alert({
        message: "Please enter value for " + field + " in " + doc,
    });
    return 0;
}

function item_details_total(frm) {
    let item_details = frm.doc.item_details ? frm.doc.item_details : [];
    let production_qty = 0,
        damage_qty = 0,
        produced_qty = 0,
        production_sqft = 0,
        ts_production_sqft = 0;
    for (let i = 0; i < item_details.length; i++) {
        production_qty += item_details[i].production_qty ? item_details[i].production_qty : 0;
        damage_qty += item_details[i].damaged_qty ? item_details[i].damaged_qty : 0;
        produced_qty += item_details[i].produced_qty ? item_details[i].produced_qty : 0;
        production_sqft += item_details[i].production_sqft ? item_details[i].production_sqft : 0;
        ts_production_sqft += item_details[i].ts_production_sqft ? item_details[i].ts_production_sqft : 0;
    }
    frm.set_value("production_qty", production_qty);
    frm.set_value("produced_qty", produced_qty);
    frm.set_value("damaged_qty", damage_qty);
    frm.set_value("production_sqft", production_sqft);
    frm.set_value("ts_production_sqft", ts_production_sqft);
}

function total_expense_per_sqft(frm) {
    let total_cost = frm.doc.total_operator_wages ? frm.doc.total_operator_wages : 0;
    total_cost += frm.doc.total_labour_wages ? frm.doc.total_labour_wages : 0;
    total_cost += frm.doc.additional_cost_in_wages ? frm.doc.additional_cost_in_wages : 0;
    total_cost += frm.doc.raw_material_cost ? frm.doc.raw_material_cost : 0;
    frm.set_value("total_expence", total_cost);
    frm.set_value("total_expence_per_sqft", frm.doc.ts_production_sqft ? (total_cost ? total_cost : 0) / frm.doc.ts_production_sqft : 0);
}

function raw_material_cost(frm) {
    let items = frm.doc.items ? frm.doc.items : [],
        total_raw_material_cost = 0;
    for (let i = 0; i < items.length; i++) {
        total_raw_material_cost += items[i].amount ? items[i].amount : 0;
    }
    frm.set_value("raw_material_cost", total_raw_material_cost);
}

async function std_item(frm) {
    if (frm.doc.item_details) {
        await frappe.call({
            method: "ganapathy_pavers.ganapathy_pavers.doctype.cw_manufacturing.cw_manufacturing.std_item",
            args: {
                doc: frm.doc,
            },
            callback(r) {
                var item1 = [];
                for (const d of r.message) {
                    item1.push(d.item_code ? d.item_code : "");
                }
                for (const d of r.message) {
                    for (const i of frm.doc.items ? frm.doc.items : []) {
                        if (i.item_code == d.item_code && i.from_usb == 1 && item1.includes(d.item_code ? d.item_code : "")) {
                            item1.splice(item1.indexOf(d.item_code ? d.item_code : ""), 1);
                        }
                    }
                }
                if (item1) {
                    for (const d of r.message) {
                        if (item1.includes(d.item_code ? d.item_code : "")) {
                            var row = frm.add_child("items");
                            row.item_code = d.item_code;
                            row.no_of_batches = frm.doc.raw_material_consumption ? frm.doc.raw_material_consumption.length : 0;
                            row.qty = d.qty;
                            row.bom_qty = d.ts_qty;
                            row.is_usb_item = 1;
                            row.from_usb = 1;
                            row.stock_uom = d.stock_uom;
                            row.source_warehouse = d.source_warehouse
                            row.uom = d.uom;
                            if (d.rate == 0) {
                                row.rate = d.validation_rate;
                            } else {
                                row.rate = d.rate;
                            }
                            row.amount = d.amount;
                        }
                    }
                }
                refresh_field("items");
                raw_material_cost(frm);
            },
        });
    }
}

async function item_adding(frm) {
    if (frm.doc.item_details) {
        await frappe.call({
            method: "ganapathy_pavers.ganapathy_pavers.doctype.cw_manufacturing.cw_manufacturing.add_item",
            args: {
                doc: frm.doc.item_details ? frm.doc.item_details : [],
                batches: frm.doc.total_no_of_batche ? frm.doc.total_no_of_batche : 0,
            },
            callback(r) {
                var item1 = [];
                for (const d of r.message) {
                    item1.push(d.item_code ? d.item_code : "");
                }
                for (const d of r.message) {
                    for (const i of frm.doc.items ? frm.doc.items : []) {
                        if (i.item_code == d.item_code && i.from_bom == 1 && item1.includes(d.item_code ? d.item_code : "")) {
                            item1.splice(item1.indexOf(d.item_code ? d.item_code : ""), 1);
                        }
                    }
                }
                if (item1) {
                    for (const d of r.message) {
                        if (item1.includes(d.item_code ? d.item_code : "")) {
                            var row = frm.add_child("items");
                            row.item_code = d.item_code;
                            row.qty = d.qty;
                            row.bom_qty = d.ts_qty;
                            row.stock_uom = d.stock_uom;
                            row.source_warehouse = d.source_warehouse
                            row.from_bom = 1;
                            row.uom = d.uom;
                            row.rate = d.rate;
                            row.amount = d.amount;
                            row.source_warehouse = d.source_warehouse;
                        }
                    }
                }
                refresh_field("items");
                raw_material_cost(frm);
            },
        });
    }
}

async function get_production_capacity(frm, cdt, cdn) {
    let data = locals[cdt][cdn],
        production_capacity = 0;
    if (data.workstation && data.item) {
        await frappe.db.get_doc("Workstation", data.workstation).then((doc) => {
            let item_details = doc.item_wise_production_capacity ? doc.item_wise_production_capacity : [];
            for (let row = 0; row < item_details.length; row++) {
                if (item_details[row].item_code == data.item) {
                    production_capacity += item_details[row].production_capacity;
                }
            }
        });
    }
    frappe.model.set_value(cdt, cdn, "production_qty", production_capacity);
}

frappe.ui.form.on("CW Items", {
    workstation: function (frm, cdt, cdn) {
        let data = locals[cdt][cdn];
        if (data.workstation) {
            production_qty_calc(frm, cdt, cdn);
            frappe.db.get_doc("Workstation", data.workstation).then((value) => {
                let operator_cost = value.ts_no_of_operator ? (value.ts_sum_of_operator_wages ? value.ts_sum_of_operator_wages : 0) / value.ts_no_of_operator : value.ts_sum_of_operator_wages ? value.ts_sum_of_operator_wages : 0;
                frappe.model.set_value(cdt, cdn, "operator_cost_per_day", operator_cost);
                frappe.model.set_value(cdt, cdn, "no_of_operators", value.ts_no_of_operator ? value.ts_no_of_operator : 0);
                get_production_capacity(frm, cdt, cdn);
            });
        } else {
            frappe.model.set_value(cdt, cdn, "operator_cost_per_day", 0);
        }
    },
    item: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (row.item) {
            var is_child = 1;
            bom_fetch(frm, row.item, cdt, cdn, is_child);
        } else {
            frappe.model.set_value(cdt, cdn, "bom", "");
        }
        production_qty_calc(frm, cdt, cdn);
        get_production_capacity(frm, cdt, cdn);
    },
    item_details_add: function (frm, cdt, cdn) {
        total_qty(frm, frm.doc.item_details);
    },
    item_details_remove: function (frm, cdt, cdn) {
        total_qty(frm, frm.doc.item_details);
    },
    production_qty: function (frm, cdt, cdn) {
        production_qty_calc(frm, cdt, cdn);
        total_qty(frm, frm.doc.item_details);
    },
    damaged_qty: function (frm, cdt, cdn) {
        production_qty_calc(frm, cdt, cdn);
        total_qty(frm, frm.doc.item_details);
    },
    produced_qty: function (frm, cdt, cdn) {
        total_qty(frm, frm.doc.item_details);
    },
    // no_of_batches: function (frm, cdt, cdn) {
    //     total_qty(frm, frm.doc.item_details);
    // },
    production_sqft: function (frm, cdt, cdn) {
        total_qty(frm, frm.doc.item_details);
    },
});
async function total_qty(frm, table_name) {
    var total_production_qty = 0;
    var total_dam_qty = 0;
    var total_produced_qty = 0;
    // var total_no_of_batche = 0;
    var total_production_sqft = 0;
    var ts_production_sqft = 0;
    for (var i = 0; i < table_name.length; i++) {
        total_production_qty += table_name[i].production_qty ? table_name[i].production_qty : 0;
        total_dam_qty += table_name[i].damaged_qty ? table_name[i].damaged_qty : 0;
        total_produced_qty += table_name[i].produced_qty ? table_name[i].produced_qty : 0;
        // table_name[i].item
        //     ? await frappe.db.get_value("Item", table_name[i].item, "compound_wall_type").then((value) => {
        //         if (value.message.compound_wall_type == "Post") {
        //             total_no_of_batche += table_name[i].no_of_batches ? table_name[i].no_of_batches : 0;
        //         }
        //     })
        //     : "";
        total_production_sqft += table_name[i].production_sqft ? table_name[i].production_sqft : 0;
        ts_production_sqft += table_name[i].ts_production_sqft ? table_name[i].ts_production_sqft : 0;
    }
    frm.set_value("production_qty", total_production_qty);
    frm.set_value("produced_qty", total_produced_qty);
    frm.set_value("damaged_qty", total_dam_qty);
    frm.set_value("production_sqft", total_production_sqft);
    frm.set_value("ts_production_sqft", ts_production_sqft);
    // if (total_no_of_batche) {
    //     frm.set_value("total_no_of_batche", total_no_of_batche);
    // }
}

function default_value(frm, usb_field, set_field) {
    frappe.db.get_single_value("CW Settings", usb_field).then((value) => {
        frm.set_value(set_field, value);
    });
    frm.refresh_field(set_field);
}

async function default_value_from_table(frm, usb_field, type, set_field, default_value_to_set = 0) {
    let table = (await frappe.db.get_doc("CW Settings"))[usb_field]
    frm.set_value(set_field, default_value_to_set);
    if (table) {
        (table || []).forEach(row => {
            if (row.type == type) {
                frm.set_value(set_field, row.cost)
            }
        });
    }
    frm.refresh_field(set_field);
}
function total_amount(frm, cdt, cdn) {
    var d = locals[cdt][cdn];
    frappe.model.set_value(cdt, cdn, "amount", d.qty * d.rate);
}

frappe.ui.form.on("BOM Item", {
    rate: function (frm, cdt, cdn) {
        total_amount(frm, cdt, cdn);
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

function total_expense_per_sqft_unmold(frm) {
    let total_cost = frm.doc.additional_cost_unmold ? frm.doc.additional_cost_unmold : 0;
    total_cost += (frm.doc.strapping_cost_per_sqft_unmold ? frm.doc.strapping_cost_per_sqft_unmold : 0) * (frm.doc.total_production_sqft ? frm.doc.total_production_sqft : 0);
    frm.set_value("total_expense_for_unmolding", total_cost);
    frm.set_value("total_expense_per_sqft_unmold", frm.doc.ts_production_sqft ? (total_cost ? total_cost : 0) / frm.doc.ts_production_sqft : 0);
}

function set_css(frm) {
    document.querySelectorAll("[data-fieldname='create_stock_entry_for_molding']")[1].style.color = "white";
    document.querySelectorAll("[data-fieldname='create_stock_entry_for_molding']")[1].style.fontWeight = "bold";
    document.querySelectorAll("[data-fieldname='create_stock_entry_for_molding']")[1].style.backgroundColor = "#3399ff";
    document.querySelectorAll("[data-fieldname='create_stock_entry_for_bundling']")[1].style.color = "white";
    document.querySelectorAll("[data-fieldname='create_stock_entry_for_bundling']")[1].style.fontWeight = "bold";
    document.querySelectorAll("[data-fieldname='create_stock_entry_for_bundling']")[1].style.backgroundColor = "#3399ff";
    document.querySelectorAll("[data-fieldname='create_stock_entry_for_curing']")[1].style.color = "white";
    document.querySelectorAll("[data-fieldname='create_stock_entry_for_curing']")[1].style.fontWeight = "bold";
    document.querySelectorAll("[data-fieldname='create_stock_entry_for_curing']")[1].style.backgroundColor = "#3399ff";
}
