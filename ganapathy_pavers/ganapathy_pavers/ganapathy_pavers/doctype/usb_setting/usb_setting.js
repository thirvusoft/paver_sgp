// Copyright (c) 2022, Thirvusoft and contributors
// For license information, please see license.txt

frappe.ui.form.on('USB Setting', {
	refresh: function(frm) {
		frm.set_query("default_manufacture_source_warehouse",function(){
			return {
				filters: [
					["Warehouse", "company", "in", ["", cstr(frm.doc.company)]],
					["Warehouse","is_group","=","0"]
				]
			}
		})
		frm.set_query("scrap_warehouse",function(){
			return {
				filters: [
					["Warehouse", "company", "in", ["", cstr(frm.doc.company)]],
					["Warehouse","is_group","=","0"]
				]
			}
		})
		frm.set_query("default_manufacture_target_warehouse",function(){
			return {
				filters: [
					["Warehouse", "company", "in", ["", cstr(frm.doc.company)]],
					["Warehouse","is_group","=","0"]
				]
			}
		})
		frm.set_query("default_rack_shift_source_warehouse",function(){
			return {
				filters: [
					["Warehouse", "company", "in", ["", cstr(frm.doc.company)]],
					["Warehouse","is_group","=","0"]
				]
			}
		})
		frm.set_query("default_rack_shift_target_warehouse",function(){
			return {
				filters: [
					["Warehouse", "company", "in", ["", cstr(frm.doc.company)]],
					["Warehouse","is_group","=","0"]
				]
			}
		})
		frm.set_query("default_curing_source_warehouse",function(){
			return {
				filters: [
					["Warehouse", "company", "in", ["", cstr(frm.doc.company)]],
					["Warehouse","is_group","=","0"]
				]
			}
		})
		frm.set_query("default_curing_target_warehouse",function(){
			return {
				filters: [
					["Warehouse", "company", "in", ["", cstr(frm.doc.company)]],
					["Warehouse","is_group","=","0"]
				]
			}
		})
		frm.set_query("cement",function(){
			return {
				"filters": {
					item_group:"Raw Material"
				}
			}
		})
		frm.set_query("chips",function(){
			return {
				"filters": {
					item_group:"Raw Material"
				}
			}
		})
		frm.set_query("dust",function(){
			return {
				"filters": {
					item_group:"Raw Material"
				}
			}
		})
		frm.set_query("ggbs",function(){
			return {
				"filters": {
					item_group:"Raw Material"
				}
			}
		})
	}
});
