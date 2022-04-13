function setquery(frm,cdt,cdn){
	frm.set_query("item", "item_details", function(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
	return {
		filters: {
			'item_group': cur_frm.doc.project_type,
			'has_variants': 0
		}
	}
});
	frm.set_query("item", "item_details_compound_wall", function(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
	return {
		filters: {
			'item_group': cur_frm.doc.project_type,
			'has_variants': 0
		}
	}
});
}





frappe.ui.form.on("Project",{
    project_type:function(frm,cdt,cdn){
        setquery(frm,cdt,cdn)
    },
    onload:function(frm,cdt,cdn){
        setquery(frm,cdt,cdn)
        frm.set_query('name1','job_worker',function(frm){
            return{
                filters:
					{
						'designation': 'Job Worker'
					}
			}
        })
        frm.set_query('supervisor', function(frm){
            return {
                filters:{
                    'designation': 'Supervisor'
                }
            }
        });
        
    }
})


frappe.ui.form.on("Item Detail Pavers", {
	item : function(frm,cdt,cdn) {
		let data = locals[cdt][cdn]
		let item_code = data.item
		if (item_code){
			frappe.call({
				method:"ganapathy_pavers.custom.py.site_work.item_details_fetching_pavers",
				args:{item_code},
				callback(r)
				{
					frappe.model.set_value(cdt,cdn,"area_per_bundle",r['message'][0]?parseFloat(r["message"][0]):0)
					frappe.model.set_value(cdt,cdn,"rate",r["message"][1]?parseFloat(r["message"][1]):0)
				}
			})
		}
	},
	required_area : function(frm,cdt,cdn) {
			let data = locals[cdt][cdn]
			let bundle = data.area_per_bundle?data.required_area / data.area_per_bundle :0
			let no_of_bundle = Math.ceil(bundle)
			frappe.model.set_value(cdt,cdn,"number_of_bundle",no_of_bundle?no_of_bundle:0)
			
			
	},
	number_of_bundle : function(frm,cdt,cdn) {
			let data = locals[cdt][cdn]
			let allocated_paver = data.number_of_bundle * data.area_per_bundle
			frappe.model.set_value(cdt,cdn,"allocated_paver_area",allocated_paver?allocated_paver:0)
	},
	allocated_paver_area :function(frm,cdt,cdn) {
			let data = locals[cdt][cdn]
			let allocated_paver = data.allocated_paver_area
			let tot_amount = data.rate * allocated_paver
			frappe.model.set_value(cdt,cdn,"amount",tot_amount?tot_amount:0)
	},
	rate : function(frm,cdt,cdn) {
			let data = locals[cdt][cdn]
			let rate = data.rate
			let tot_amount = rate * data.allocated_paver_area
			frappe.model.set_value(cdt,cdn,"amount",tot_amount?tot_amount:0)
	}  
})



frappe.ui.form.on('TS Job Worker Details',{
	rate: function(frm, cdt, cdn){
		amount(frm, cdt, cdn)
	},
	sqft_allocated: function(frm, cdt, cdn){
		amount(frm, cdt, cdn)
	},
	amount: function(frm, cdt, cdn){
		balance_amount(frm, cdt, cdn)
	},
	paid_amount: function(frm, cdt, cdn){
		balance_amount(frm, cdt, cdn)
	}
})


function amount(frm,cdt,cdn){
	let row=locals[cdt][cdn]
	if(row.rate && row.sqft_allocated){
		frappe.model.set_value(cdt, cdn, 'amount', row.rate*row.sqft_allocated)
	}
	else{
		frappe.model.set_value(cdt, cdn, 'amount', 0)
	}
}


function balance_amount(frm,cdt,cdn){
	let row=locals[cdt][cdn]
	if(row.amount){
		frappe.model.set_value(cdt, cdn, 'balance_amount', row.amount- (row.paid_amount?row.paid_amount:0))
	}
	else{
		frappe.model.set_value(cdt, cdn, 'balance_amount', 0)
	}
}


frappe.ui.form.on('TS Raw Materials',{
    item: function(frm,cdt,cdn){
        let row=locals[cdt][cdn]
        if(row.item){
            frappe.db.get_doc('Item',row.item).then((item)=>{
                frappe.model.set_value(cdt,cdn,'rate', item.standard_rate);
                frappe.model.set_value(cdt,cdn,'uom', item.stock_uom);
            })
        }
    },
    rate: function(frm,cdt,cdn){
        amount_rawmet(frm,cdt,cdn)
    },
    qty: function(frm,cdt,cdn){
        amount_rawmet(frm,cdt,cdn)
    }
})


function amount_rawmet(frm,cdt,cdn){
    let row=locals[cdt][cdn]
    frappe.model.set_value(cdt,cdn,'amount', (row.rate?row.rate:0)*(row.qty?row.qty:0))
}

//compound wall

// frappe.ui.form.on("Item Detail Compound Wall", {
// 	item : function(frm,cdt,cdn) {      
// 		let data = locals[cdt][cdn]
// 		let item_code = data.item
// 		if(item_code){
// 			frappe.call({
// 				method:"ganapathy_pavers.custom.py.site_work.item_details_fetching_compoundwall",
// 				args:{item_code},
// 				callback(r)
// 				{
// 					frappe.model.set_value(cdt,cdn,"area_per_bundle",r['message'][0]?parseFloat(r["message"][0]):0)
// 					frappe.model.set_value(cdt,cdn,"rate",r["message"][1]?parseFloat(r["message"][1]):0)
// 				}
// 			})
// 		}
// 	},
// 	running_sqft : function(frm,cdt,cdn) {
// 			let data = locals[cdt][cdn]
// 			let rft = data.running_sqft
// 			let bundle = rft / cw_area_bundle
// 			let no_of_bundle = Math.ceil(bundle)
// 			frappe.model.set_value(cdt, cdn, "allocated_ft",no_of_bundle)
		
// 	},
// 	allocated_ft : function(frm,cdt,cdn) {
// 			let data = locals[cdt][cdn]
// 			let aft = data.allocated_ft
// 			cwtot_amount = item_price * no_of_bundle
// 			frappe.model.set_value(cdt, cdn,"rate",item_price)
// 			frappe.model.set_value(cdt, cdn,"amount",cwtot_amount)
	
// 	},
// 	rate : function(frm,cdt,cdn) {
// 			let data = locals[cdt][cdn]
// 			let cwtot_amount = data.rate * data.number_of_bundle
// 			frappe.model.set_value(cdt, cdn,"amount",cwtot_amount)
// 	}
// })


// frappe.ui.form.on('Project',{
// 	validate: function(frm,cdt,cdn){
// 		let arg;
// 		if(cur_frm.doc.project_type == "Pavers"){
// 			arg = cur_frm.doc.item_details
// 		}
// 		if(cur_frm.doc.project_type == "Compound Walls"){
// 			arg = cur_frm.doc.item_details_compound_wall
// 		}
// 		if(arg){
// 			frappe.call({
// 				method:"ganapathy_pavers.custom.py.site_work.add_total_amount",
// 				args:{items: arg},
// 				callback: function(res){
// 					cur_frm.set_value('estimated_costing',res.message)
// 				}
// 			})
// 	}
// 	}
// })