var from_lp=0;

frappe.ui.form.on("Vehicle Log" ,{
    onload:function(frm){
        frappe.call({
            method:"ganapathy_pavers.custom.py.vehicle_log.fuel_supplier",
            args:{name:frm.doc.name},
            callback(fuel){
                cur_frm.set_value("supplier",fuel.message)
            }
        })
            frm.set_query('employee', function(frm){
                        return {
                            filters:{
                                'designation': 'Driver'
                            }
                        }
                    });                
    },

    
    odometer: function(frm){
        distance(frm)
        total_cost(frm)
    },
    last_odometer: function(frm){
        distance(frm)
    },
    license_plate: function(frm){
        distance(frm)
        total_cost(frm)
    },
    driver_cost: function(frm){
        if(from_lp){
            total_cost(frm)
        }
        else{
            from_lp=1
        }
    },
    ts_driver_cost:function(frm){
        from_lp=0
        frm.set_value("driver_cost",frm.doc.ts_driver_cost)
    },
    after_save:function(frm){
        frappe.db.set_value("Vehicle",frm.doc.license_plate,"driver_cost",frm.doc.driver_cost)
        frappe.db.get_doc('Vehicle', frm.doc.license_plate).then( async(doc) => {
            if(doc.fuel_type=='Petrol'){
                await frappe.db.set_value("Vehicle Settings","vehicle_settings","petrol_per_liter",frm.doc.price)
            }
            else if(doc.fuel_type=='Diesel'){
                await frappe.db.set_value("Vehicle Settings","vehicle_settings","diesel_per_liter",frm.doc.price)

            }
        })
    }
});


function distance(frm){
    frm.set_value('today_odometer_value', (frm.doc.odometer?frm.doc.odometer:0) - (frm.doc.last_odometer?frm.doc.last_odometer:0))
}
function total_cost(frm){
    if(frm.doc.license_plate){
        frappe.db.get_doc('Vehicle', frm.doc.license_plate).then( async(doc) => {
            let fuel_cost=0
            if(doc.fuel_type=='Petrol'){
                await frappe.db.get_single_value("Vehicle Settings","petrol_per_liter").then((i)=> {fuel_cost=i})
                if(fuel_cost==0){
                    zero_alert('Petrol Cost', 'vehicle-settings', 'Vehicle Settings')
                }
            }
            else if(doc.fuel_type=='Diesel'){
                await frappe.db.get_single_value("Vehicle Settings","diesel_per_liter").then((i)=> {fuel_cost=i})
                if(fuel_cost==0){
                    zero_alert('Diesel Cost', 'vehicle-settings', 'Vehicle Settings')
                }
            }
            else{
                frappe.show_alert({message: 'Please Choose Petrol or Diesel as Fuel Type for '+frappe.utils.get_form_link('Vehicle', cur_frm.doc.license_plate, cur_frm.doc.license_plate)+'..!', indicator: 'red'})
            }
            
            let fuel_cost_per_km=(fuel_cost?fuel_cost:0)*(frm.doc.today_odometer_value?frm.doc.today_odometer_value:0)/(doc.mileage?doc.mileage:zero_alert('Mileage'));
            let mc=(frm.doc.today_odometer_value?frm.doc.today_odometer_value:0)*(doc.maintenance_cost?doc.maintenance_cost:zero_alert('Maintenance Cost'))
            let dc=(frm.doc.today_odometer_value?frm.doc.today_odometer_value:0)*(frm.doc.driver_cost?frm.doc.driver_cost:0)
            frm.set_value('ts_total_cost', (fuel_cost_per_km?fuel_cost_per_km:0)+(mc?mc:0)+(dc?dc:0))
            frm.refresh()
        })

    }
}

function zero_alert(field,vehicle="Vehicle", lp=cur_frm.doc.license_plate, name=cur_frm.doc.license_plate){
    frappe.show_alert({message: field+' is Empty in '+frappe.utils.get_form_link(vehicle, lp, name)+'..!', indicator: 'red'})

    return 0
}

