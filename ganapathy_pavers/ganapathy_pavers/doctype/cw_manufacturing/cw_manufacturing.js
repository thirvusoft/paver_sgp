// Copyright (c) 2022, Thirvusoft and contributors
// For license information, please see license.txt

frappe.ui.form.on("CW Manufacturing", {
    refresh: function (frm) {
      if (frm.is_new()) {
        default_value(frm, "no_of_labours_for_molding", "no_of_labours");
        default_value(frm, "no_of_labours_for_unmolding", "no_of_labours_unmould");
        default_value(frm, "strapping_cost_per_sqft", "strapping_cost_per_sqft_unmold");
        default_value(frm, "labour_cost_per_sqft", "labour_cost_per_sqft_curing");
        default_value(frm, "chips_for_post", "post_chips");
        default_value(frm, "chips_for_slab", "slab_chips_item_name");
        default_value(frm, "m_sand", "m_sand_item_name");
        default_value(frm, "cement", "cement_item_name");
        default_value(frm, "ggbs", "ggbs_item_name");
      }
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
    item_to_manufacture: function (frm) {
      if (frm.doc.item_to_manufacture) {
        bom_fetch(frm);
      } else {
        frm.set_value("bom", "");
      }
    },
    ts_before_save: function (frm) {
      let post_chips = 0,
        slab_chips = 0,
        cement = 0,
        m_sand = 0,
        ggbs = 0;
      let rm_consmp = frm.doc.raw_material_consumption ? frm.doc.raw_material_consumption : [];
      for (let i = 0; i < rm_consmp.length; i++) {
        post_chips += rm_consmp[i].bin1 ? rm_consmp[i].bin1 : 0;
        slab_chips += rm_consmp[i].bin2 ? rm_consmp[i].bin2 : 0;
        cement += rm_consmp[i].bin3 ? rm_consmp[i].bin3 : 0;
        m_sand += rm_consmp[i].bin4 ? rm_consmp[i].bin4 : 0;
        ggbs += rm_consmp[i].bin5 ? rm_consmp[i].bin5 : 0;
      }
      frm.set_value("post_chips_qty", post_chips ? post_chips : 0);
      frm.set_value("slab_chips_qty", slab_chips ? slab_chips : 0);
      frm.set_value("cement_qty", cement ? cement : 0);
      frm.set_value("m_sand_qty", m_sand ? m_sand : 0);
      frm.set_value("ggbs_qty", ggbs ? ggbs : 0);
      std_item(frm);
      item_adding(frm);
      item_details_total(frm);
      item_details_total_unmold(frm);
      raw_material_cost(frm);
      total_expense_per_sqft(frm);
      total_expense_per_sqft_unmold(frm);
      labour_expense_curing(frm);
    },
    before_save: async function (frm) {
      await frm.trigger("ts_before_save").then( async (ret) => {
        abstract_calc(frm);
        if (!frm.is_new()) {
          await frappe.call({
            method: "ganapathy_pavers.ganapathy_pavers.doctype.cw_manufacturing.cw_manufacturing.find_batch",
            args: {
              name: frm.doc.name,
            },
            callback: function (r) {
              frm.set_value("molding_batch", r.message[0]);
              frm.set_value("unmolding_batch", r.message[1]);
              frm.set_value("curing_batch", r.message[2]);
            },
          });
        }
      });
    },
    avg_labour_wages: function (frm) {
      frm.set_value("labour_cost", (frm.doc.avg_labour_wages ? frm.doc.avg_labour_wages : 0) * (frm.doc.no_of_labours ? frm.doc.no_of_labours : 0) * (frm.doc.manufacturing_hrs ? frm.doc.manufacturing_hrs : 0));
    },
    avg_labour_wages_unmold: function (frm) {
      frm.set_value("labour_cost_unmold", (frm.doc.avg_labour_wages_unmold ? frm.doc.avg_labour_wages_unmold : 0) * (frm.doc.no_of_labours_unmould ? frm.doc.no_of_labours_unmould : 0) * (frm.doc.total_unmolding_hrs ? frm.doc.total_unmolding_hrs : 0));
    },
    no_of_labours: function (frm) {
      frm.trigger("avg_labour_wages");
    },
    manufacturing_hrs: function (frm) {
      frm.trigger("avg_labour_wages");
    },
    no_of_labours_unmould: function (frm) {
      frm.trigger("avg_labour_wages_unmold");
    },
    total_unmolding_hrs: function (frm) {
      frm.trigger("avg_labour_wages_unmold");
    },
    operator_cost: function (frm) {
      total_expense_per_sqft(frm);
    },
    operator_cost_unmold: function (frm) {
      total_expense_per_sqft_unmold(frm);
    },
    labour_cost: function (frm) {
      total_expense_per_sqft(frm);
    },
    labour_cost_unmold: function (frm) {
      total_expense_per_sqft_unmold(frm);
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
    production_sqft_unmold: function (frm) {
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
              frm.set_value("status1", r.message);
              frm.clear_table("unmolding_details");
              refresh_field("unmolding_details");
              let workstation = frm.doc.item_details ? frm.doc.item_details : [];
              for (let row = 0; row < workstation.length; row++) {
                let new_row = frm.add_child("unmolding_details");
                new_row.workstation = workstation[row].workstation;
                new_row.production_qty = workstation[row].production_qty;
                new_row.damaged_qty = workstation[row].damaged_qty;
                new_row.produced_qty = workstation[row].produced_qty;
                new_row.production_sqft = workstation[row].production_sqft;
                if (frm.doc.item_to_manufacture) {
                  await frappe.db.get_value("Item", frm.doc.item_to_manufacture, "bundle_per_sqr_ft", (doc) => {
                    new_row.no_of_bundles = doc.bundle_per_sqr_ft ? (workstation[row].production_sqft ? workstation[row].production_sqft : 0) / doc.bundle_per_sqr_ft : show_alert(frm.doc.item_to_manufacture, "Sqft Per Bundle");
                  });
                }
                if (workstation[row].workstation) {
                  await frappe.db.get_doc("Workstation", workstation[row].workstation).then((value) => {
                    let operator_cost = value.ts_no_of_operator ? (value.ts_sum_of_operator_wages ? value.ts_sum_of_operator_wages : 0) / value.ts_no_of_operator : value.ts_sum_of_operator_wages ? value.ts_sum_of_operator_wages : 0;
                    new_row.operator_cost_per_day = operator_cost;
                  });
                }
              }
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
              frm.set_value("status1", r.message);
              frm.set_value("bundled_sqft_curing", frm.doc.production_sqft_unmold ? frm.doc.production_sqft_unmold : 0);
              frm.set_value("no_of_bundle_curing", frm.doc.no_of_bundle_unmold ? frm.doc.no_of_bundle_unmold : 0);
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
              frm.set_value("status1", r.message);
              frm.save();
            }
          },
        });
      }
    },
    total_no_of_batches: function (frm) {
      for (let row = 0; row < (frm.doc.items ? frm.doc.items.length : 0); row++) {
        let cdt = frm.doc.items[row].doctype,
          cdn = frm.doc.items[row].name;
        let data = locals[cdt][cdn];
        if (data.from_bom == 1) {
          frappe.model.set_value(cdt, cdn, "qty", (data.ts_qty ? data.ts_qty : 0) * (frm.doc.total_no_of_batches ? frm.doc.total_no_of_batches : 0));
        }
      }
      refresh_field("items");
    },
    labour_cost_per_sqft_curing: function (frm) {
      labour_expense_curing(frm);
    },
  });
  
  function labour_expense_curing(frm) {
    frm.set_value("labour_expense_for_curing", (frm.doc.bundled_sqft_curing ? frm.doc.bundled_sqft_curing : 0) * (frm.doc.labour_cost_per_sqft_curing ? frm.doc.labour_cost_per_sqft_curing : 0));
  }
  
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
  
  function production_bundle(frm, cdt, cdn) {
    let data = locals[cdt][cdn];
    if (frm.doc.item_to_manufacture) {
      frappe.db.get_value("Item", frm.doc.item_to_manufacture, "bundle_per_sqr_ft", (doc) => {
        frappe.model.set_value(cdt, cdn, "no_of_bundles", doc.bundle_per_sqr_ft ? (data.production_sqft ? data.production_sqft : 0) / doc.bundle_per_sqr_ft : show_alert(frm.doc.item_to_manufacture, "Sqft Per Bundle"));
      });
    }
  }
  
  function show_alert(doc, field) {
    frappe.show_alert({
      message: "Please enter value for " + field + " in " + doc,
    });
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
    frm.set_value("production_qty", production_qty);
    frm.set_value("produced_qty", produced_qty);
    frm.set_value("damaged_qty", damage_qty);
    frm.set_value("production_sqft", production_sqft);
  }
  
  function total_expense_per_sqft(frm) {
    let total_cost = frm.doc.operator_cost ? frm.doc.operator_cost : 0;
    total_cost += frm.doc.labour_cost ? frm.doc.labour_cost : 0;
    total_cost += frm.doc.additional_cost ? frm.doc.additional_cost : 0;
    total_cost += frm.doc.raw_material_cost ? frm.doc.raw_material_cost : 0;
    frm.set_value("total_expense", total_cost);
    frm.set_value("total_expense_per_sqft", frm.doc.production_sqft ? (total_cost ? total_cost : 0) / frm.doc.production_sqft : 0);
  }
  
  function raw_material_cost(frm) {
    let items = frm.doc.items,
      total_raw_material_cost = 0;
    for (let i = 0; i < items.length; i++) {
      total_raw_material_cost += items[i].amount ? items[i].amount : 0;
    }
    frm.set_value("raw_material_cost", total_raw_material_cost);
  }
  
  function std_item(frm) {
    if (frm.doc.bom) {
      frappe.call({
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
                row.qty = d.qty;
                row.ts_qty = d.qty;
                row.from_usb = 1;
                row.stock_uom = d.stock_uom;
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
  
  function item_adding(frm) {
    if (frm.doc.bom) {
      frappe.call({
        method: "ganapathy_pavers.ganapathy_pavers.doctype.material_manufacturing.material_manufacturing.add_item",
        args: {
          bom_no: frm.doc.bom,
          doc: frm.doc,
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
                // row.layer_type = d.layer_type;
                row.qty = d.qty * (frm.doc.total_no_of_batches ? frm.doc.total_no_of_batches : 0);
                row.ts_qty = d.ts_qty;
                row.stock_uom = d.stock_uom;
                row.from_bom = 1;
                row.uom = d.uom;
                row.rate = d.rate;
                row.amount = d.amount * (frm.doc.total_no_of_batches ? frm.doc.total_no_of_batches : 0);
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
  
  function default_value(frm, usb_field, set_field) {
    frappe.db.get_single_value("CW Settings", usb_field).then((value) => {
      frm.set_value(set_field, value);
    });
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
  
  frappe.ui.form.on("CW Unmolding", {
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
    production_sqft: function (frm, cdt, cdn) {
      production_bundle(frm, cdt, cdn);
    },
  });
  
  async function item_details_total_unmold(frm) {
    let item_details = frm.doc.unmolding_details ? frm.doc.unmolding_details : [];
    let total_hrs = 0,
      total_operators = 0,
      total_opr_cost = 0,
      production_qty = 0,
      damage_qty = 0,
      produced_qty = 0,
      production_sqft = 0,
      total_labour_wages = 0,
      total_bundles = 0,
      remaining_qty_from_bundles = 0,
      table_length = 0;
    for (let i = 0; i < item_details.length; i++) {
      total_hrs += item_details[i].this_hrs ? item_details[i].this_hrs : 0;
      total_operators += item_details[i].no_of_operators ? item_details[i].no_of_operators : 0;
      total_opr_cost += item_details[i].operator_cost ? item_details[i].operator_cost : 0;
      production_qty += item_details[i].production_qty ? item_details[i].production_qty : 0;
      damage_qty += item_details[i].damaged_qty ? item_details[i].damaged_qty : 0;
      produced_qty += item_details[i].produced_qty ? item_details[i].produced_qty : 0;
      production_sqft += item_details[i].production_sqft ? item_details[i].production_sqft : 0;
      total_bundles += item_details[i].no_of_bundles ? item_details[i].no_of_bundles : 0;
      total_labour_wages += item_details[i].labour_cost_per_hour ? item_details[i].labour_cost_per_hour : 0;
      if (item_details[i].workstation) {
        table_length += 1;
      }
    }
    if (frm.doc.item_to_manufacture) {
      await frappe.db.get_doc("Item", frm.doc.item_to_manufacture).then((value) => {
        remaining_qty_from_bundles = (total_bundles - parseInt(total_bundles)) * (value.pavers_per_bundle ? value.pavers_per_bundle : 0);
        total_bundles = parseInt(total_bundles);
        production_sqft -= remaining_qty_from_bundles / (value.pavers_per_sqft ? value.pavers_per_sqft : 0);
      });
    }
    frm.set_value("total_unmolding_hrs", total_hrs);
    frm.set_value("total_no_of_operators_unmold", total_operators);
    frm.set_value("operator_cost_unmold", total_opr_cost);
    frm.set_value("avg_labour_wages_unmold", (total_labour_wages ? total_labour_wages : 0) / (table_length ? table_length : 0));
    frm.set_value("produced_qty_unmold", production_qty);
    frm.set_value("actual_bundle_qty", produced_qty);
    frm.set_value("damaged_qty_at_bundling", damage_qty);
    frm.set_value("production_sqft_unmold", production_sqft);
    frm.set_value("no_of_bundle_unmold", total_bundles);
    frm.set_value("remaining_qty_from_bundles", remaining_qty_from_bundles);
  }
  
  function total_expense_per_sqft_unmold(frm) {
    let total_cost = frm.doc.operator_cost_unmold ? frm.doc.operator_cost_unmold : 0;
    total_cost += frm.doc.labour_cost_unmold ? frm.doc.labour_cost_unmold : 0;
    total_cost += frm.doc.additional_cost_unmold ? frm.doc.additional_cost_unmold : 0;
    total_cost += (frm.doc.strapping_cost_per_sqft_unmold ? frm.doc.strapping_cost_per_sqft_unmold : 0) * (frm.doc.production_sqft_unmold ? frm.doc.production_sqft_unmold : 0);
    frm.set_value("total_expense_for_unmolding", total_cost);
    frm.set_value("total_expense_per_sqft_unmold", frm.doc.production_sqft_unmold ? (total_cost ? total_cost : 0) / frm.doc.production_sqft_unmold : 0);
  }
  
  function abstract_calc(frm) {
    let labour_cost = frm.doc.labour_cost_per_sqft_curing;
    labour_cost += frm.doc.production_sqft ? (frm.doc.labour_cost ? frm.doc.labour_cost : 0) / frm.doc.production_sqft : 0;
    labour_cost += frm.doc.production_sqft_unmold ? (frm.doc.labour_cost_unmold ? frm.doc.labour_cost_unmold : 0) / frm.doc.production_sqft_unmold : 0;
  
    let operator_cost = frm.doc.production_sqft ? (frm.doc.operator_cost ? frm.doc.operator_cost : 0) / frm.doc.production_sqft : 0;
    operator_cost += frm.doc.production_sqft_unmold ? (frm.doc.operator_cost_unmold ? frm.doc.operator_cost_unmold : 0) / frm.doc.production_sqft_unmold : 0;
  
    let additional_cost = frm.doc.production_sqft ? (frm.doc.additional_cost ? frm.doc.additional_cost : 0) / frm.doc.production_sqft : 0;
    additional_cost += frm.doc.production_sqft_unmold ? (frm.doc.additional_cost_unmold ? frm.doc.additional_cost_unmold : 0) / frm.doc.production_sqft_unmold : 0;
  
    let strapping_cost = frm.doc.strapping_cost_per_sqft_unmold ? frm.doc.strapping_cost_per_sqft_unmold : 0;
  
    let raw_material_cost = frm.doc.production_sqft ? (frm.doc.raw_material_cost ? frm.doc.raw_material_cost : 0) / frm.doc.production_sqft : 0;
  
    let total_cost = (labour_cost ? labour_cost : 0) + (operator_cost ? operator_cost : 0) + (additional_cost ? additional_cost : 0) + (strapping_cost ? strapping_cost : 0) + (raw_material_cost ? raw_material_cost : 0);
  
    frm.set_value("labour_cost_per_sqft", labour_cost);
    frm.set_value("operator_cost_per_sqft", operator_cost);
    frm.set_value("strapping_cost_per_sqft", strapping_cost);
    frm.set_value("additional_cost_per_sqft", additional_cost);
    frm.set_value("raw_material_cost_per_sqft", raw_material_cost);
    frm.set_value("total_cost_per_sqft", total_cost);
  }
  