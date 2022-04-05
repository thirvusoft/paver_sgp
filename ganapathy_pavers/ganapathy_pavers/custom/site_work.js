var main_data
frappe.ui.form.on("Project",{
    onload:function(frm,cdt,cdn){
        frm.set_query("item", "item_details", function(doc, cdt, cdn) {
            const row = locals[cdt][cdn];
        return {
            filters: {
                'type': frm.doc.project_type
            }
        }
    });
        frm.set_query("item", "item_details_compound_wall", function(doc, cdt, cdn) {
            const row = locals[cdt][cdn];
        return {
            filters: {
                'type': frm.doc.project_type
            }
        }
    });
    },
	project_type : function(frm,cdt,cdn) {
		main_data = locals[cdt][cdn]
	}
})

//
var item_price
var area_bundle
var data
var no_of_bundle
var allocated_paver
var ttt
var tot_amount
frappe.ui.form.on("Item Details Pavers", {

	item : function(frm,cdt,cdn) {
		data = locals[cdt][cdn]
		var item_code = data.item
		frappe.call({
			method:"ganapathy_pavers.ganapathy_pavers.custom.py.site_work.item_details_fetching_pavers",
			args:{item_code},
			callback(r)
			{
				area_bundle = r["message"][0]
				item_price = r["message"][1]
				for(var i=0;i<main_data.item_details.length;i++){
					if(item_code==main_data.item_details[i].item){
						frappe.model.set_value(main_data.item_details[i].doctype,main_data.item_details[i].name,"area_per_bundle",parseFloat(r["message"]))
					}
			}	
		}
		})
	},
	required_area : function(frm,cdt,cdn) {
		for(var i=0;i<main_data.item_details.length;i++){
			var req_area = data.required_area
			var bundle = req_area / area_bundle
			no_of_bundle = Math.round((bundle+0.5))
			if(req_area==main_data.item_details[i].required_area){
				frappe.model.set_value(main_data.item_details[i].doctype,main_data.item_details[i].name,"number_of_bundle",no_of_bundle)
			}
		}
	},
	number_of_bundle : function(frm,cdt,cdn) {
		for(var i=0;i<main_data.item_details.length;i++){
			allocated_paver = no_of_bundle * area_bundle
			if(no_of_bundle==main_data.item_details[i].number_of_bundle){
				frappe.model.set_value(main_data.item_details[i].doctype,main_data.item_details[i].name,"allocated_paver_area",allocated_paver)
			}
		}
	},
	allocated_paver_area :function(frm,cdt,cdn) {
		for(var i=0;i<main_data.item_details.length;i++){
			var allocated_paver_area = data.allocated_paver_area
			var tot_amount = item_price * allocated_paver
			if(allocated_paver_area==main_data.item_details[i].allocated_paver_area){
				frappe.model.set_value(main_data.item_details[i].doctype,main_data.item_details[i].name,"rate",item_price)
				frappe.model.set_value(main_data.item_details[i].doctype,main_data.item_details[i].name,"amount",tot_amount)
			}
		}	
	},
	rate : function(frm,cdt,cdn) {
		for(var i=0;i<main_data.item_details.length;i++){
			var rate = data.rate
			tot_amount = rate * allocated_paver
			if(rate==main_data.item_details[i].rate){
				frappe.model.set_value(main_data.item_details[i].doctype,main_data.item_details[i].name,"amount",tot_amount)
			}
		}
	},
    amount : function(frm,cdt,cdn) {
            for(var i=0;i<main_data.item_details.length;i++){
				
			}
    }
})




//compound wall
var cw_area_bundle
var cwtot_amount;
frappe.ui.form.on("Item Details Compound Wall", {
	item : function(frm,cdt,cdn) {

        
		data = locals[cdt][cdn]
		var item_code = data.item
		frappe.call({
			method:"ganapathy_pavers.ganapathy_pavers.custom.py.site_work.item_details_fetching_compoundwall",
			args:{item_code},
			callback(r)
			{
				for(var i=0;i<main_data.item_details_compound_wall.length;i++){
					if(item_code==main_data.item_details_compound_wall[i].item){
						cw_area_bundle = r["message"][0]
						item_price = r["message"][1]
					}
			}	
		}
		})
	},
	running_sqft : function(frm,cdt,cdn) {
		for(var i=0;i<main_data.item_details_compound_wall.length;i++){
			var rft = data.running_sqft
			var bundle = rft / cw_area_bundle
			no_of_bundle = Math.round((bundle+0.5))
			if(rft==main_data.item_details_compound_wall[i].running_sqft){
				frappe.model.set_value(main_data.item_details_compound_wall[i].doctype,main_data.item_details_compound_wall[i].name,"allocated_ft",no_of_bundle)
			}
		}
	},
	allocated_ft : function(frm,cdt,cdn) {
		for(var i=0;i<main_data.item_details_compound_wall.length;i++){
			var aft = data.allocated_ft
			cwtot_amount = item_price * no_of_bundle
			if(aft==main_data.item_details_compound_wall[i].allocated_ft){
				frappe.model.set_value(main_data.item_details_compound_wall[i].doctype,main_data.item_details_compound_wall[i].name,"rate",item_price)
				frappe.model.set_value(main_data.item_details_compound_wall[i].doctype,main_data.item_details_compound_wall[i].name,"amount",cwtot_amount)
			}
		}
	},
	rate : function(frm,cdt,cdn) {
		for(var i=0;i<main_data.item_details_compound_wall.length;i++){
			var rate = data.rate
			cwtot_amount = rate * no_of_bundle
			if(rate==main_data.item_details_compound_wall[i].rate){
				frappe.model.set_value(main_data.item_details_compound_wall[i].doctype,main_data.item_details_compound_wall[i].name,"amount",cwtot_amount)
			}
		}
	}
})


frappe.ui.form.on('Project',{
	validate: function(frm,cdt,cdn){
		let p = locals[cdt][cdn]
		let arg;
		if(p.project_type == "Pavers"){
			arg = p.item_details
		}
		if(p.project_type == "Compound Walls"){
			arg = p.item_details_compound_wall
		}
		frappe.call({
			method:"ganapathy_pavers.ganapathy_pavers.custom.py.site_work.add_total_amount",
			args:{items: arg},
			callback: function(res){
				console.log("Total", res.message)
				frappe.model.set_value(cdt,cdn,'total_amount',res.message)
				frm.refresh_fields();
			}
		})
	}
})