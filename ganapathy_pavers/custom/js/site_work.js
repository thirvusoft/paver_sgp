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
    
    refresh:function(frm,cdt,cdn){
        //percent_complete(frm,cdt,cdn)
		cur_frm.remove_custom_button('Duplicate Project with Tasks')
		cur_frm.remove_custom_button('Kanban Board')
		cur_frm.remove_custom_button('Gantt Chart')
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
        if(!cur_frm.is_new()){
            cur_frm.set_df_property('project_name','read_only',1)
            cur_frm.set_df_property('customer','read_only',1)
            cur_frm.set_df_property('customer_name','read_only',1)
            cur_frm.set_df_property('is_multi_customer','read_only',1)
        }
        if(cur_frm.doc.is_multi_customer){
            cur_frm.set_df_property('customer','reqd',0)
            cur_frm.set_df_property('customer_name','reqd',1)
            cur_frm.set_df_property('customer','hidden',1)
            cur_frm.set_df_property('customer_name','hidden',0)
        }
        else{
            cur_frm.set_df_property('customer','reqd',1)
            cur_frm.set_df_property('customer_name','reqd',0)
            cur_frm.set_df_property('customer','hidden',0)
            cur_frm.set_df_property('customer_name','hidden',1)
        }	
    },
    is_multi_customer:function(frm){
        if(cur_frm.doc.is_multi_customer){
            cur_frm.set_df_property('customer','reqd',0)
            cur_frm.set_df_property('customer_name','reqd',1)
            cur_frm.set_df_property('customer','hidden',1)
            cur_frm.set_df_property('customer_name','hidden',0)
        }
        else{
            cur_frm.set_df_property('customer','reqd',1)
            cur_frm.set_df_property('customer_name','reqd',0)
            cur_frm.set_df_property('customer','hidden',0)
            cur_frm.set_df_property('customer_name','hidden',1)
        }	
    }
})

function percent_complete(frm,cdt,cdn){ 
	let total_area=0;
	let total_bundle = 0;
	let paver= cur_frm.doc.item_details?cur_frm.doc.item_details:[]
	for(let row=0;row<paver.length;row++){
		total_area+= cur_frm.doc.item_details[row].required_area
		total_bundle += cur_frm.doc.item_details[row].number_of_bundle
	        }
	let completed_area=0;
	let total_comp_bundle = 0;
	let work= cur_frm.doc.job_worker?cur_frm.doc.job_worker:[]
	for(let row=0;row<work.length;row++){
		completed_area+= cur_frm.doc.job_worker[row].sqft_allocated
		total_comp_bundle += cur_frm.doc.job_worker[row].completed_bundle
	}
	let percent=(completed_area/total_area)*100
	frm.set_value('total_required_area',total_area)
	frm.set_value('total_completed_area',completed_area)
	frm.set_value('total_required_bundle',total_bundle)
	frm.set_value('total_completed_bundle',total_comp_bundle)
	frm.set_value('completed',percent)
}


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
			if(cur_frm.doc.type=="Project"){
			percent_complete(frm, cdt, cdn)
			}
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




frappe.ui.form.on("Pavers", {
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
	completed_bundle: function(frm,cdt,cdn){
		let data = locals[cdt][cdn]
		let bundle = data.completed_bundle
		var item_bundle_per_sqft
		let allocated_sqft
		frappe.db.get_doc('Item',data.item).then(value => {
			item_bundle_per_sqft = value.bundle_per_sqr_ft
			allocated_sqft = bundle * item_bundle_per_sqft
			frappe.model.set_value(cdt,cdn,"sqft_allocated",allocated_sqft?allocated_sqft:0)
		})
	},
	sqft_allocated: function(frm, cdt, cdn){
		percent_complete(frm, cdt, cdn)
		amount(frm, cdt, cdn)
		
	},
	job_worker_add: function(frm, cdt, cdn){
		let work= cur_frm.doc.job_worker?cur_frm.doc.job_worker:[]
		var name
		var start_date
		let rate
		var date
		for(let row=0;row<work.length;row++){
			if(row){
				name = cur_frm.doc.job_worker[row-1].name1
				start_date = cur_frm.doc.job_worker[row-1].start_date
				rate = cur_frm.doc.job_worker[row-1].rate
				date = frappe.datetime.add_days(start_date,1)
			}
			else{
				date = start_date
			}
		}
		frappe.model.set_value(cdt,cdn,"name1",name)
		frappe.model.set_value(cdt,cdn,"start_date",date)
		frappe.model.set_value(cdt,cdn,"end_date",date)
		frappe.model.set_value(cdt,cdn,"rate",rate)
	},
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



frappe.ui.form.on('Raw Materials',{
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