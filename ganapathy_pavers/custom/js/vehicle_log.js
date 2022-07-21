frappe.ui.form.on("Vehicle Log" ,{
    onload:function(frm){
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
        total_cost(frm)
    },
    ts_driver_cost:function(frm){
        frm.set_value("driver_cost",frm.doc.ts_driver_cost)
    },
    after_save:function(frm){
        frappe.db.set_value("Vehicle",frm.doc.license_plate,"driver_cost",frm.doc.driver_cost)
    }
});


function distance(frm){
    frm.set_value('today_odometer_value', (frm.doc.odometer?frm.doc.odometer:0) - (frm.doc.last_odometer?frm.doc.last_odometer:0))
}

function total_cost(frm){
    if(frm.doc.license_plate){
        frappe.db.get_doc('Vehicle', frm.doc.license_plate).then( async(doc) => {
            let fuel_cost_per_km=(doc.fuel_cost_per_km?doc.fuel_cost_per_km:zero_alert('Fuel Cost'))*(frm.doc.today_odometer_value?frm.doc.today_odometer_value:0)/(doc.mileage?doc.mileage:zero_alert('Mileage'));
            let mc=(frm.doc.today_odometer_value?frm.doc.today_odometer_value:0)*(doc.maintenance_cost?doc.maintenance_cost:zero_alert('Maintenance Cost'))
            let dc=(frm.doc.today_odometer_value?frm.doc.today_odometer_value:0)*(frm.doc.driver_cost?frm.doc.driver_cost:0)
            frm.set_value('ts_total_cost', (fuel_cost_per_km?fuel_cost_per_km:0)+(mc?mc:0)+(dc?dc:0))
            frm.refresh()
        })
    }
}
function zero_alert(field){
    frappe.show_alert({message: field+' is Empty in Vehicle..!', indicator: 'red'})
    return 0
}    
