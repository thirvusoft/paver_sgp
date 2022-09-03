// Copyright (c) 2022, Thirvusoft and contributors
// For license information, please see license.txt

frappe.ui.form.on('Contractor Commission Rate', {
	onload: function(frm){
		frm.set_query('contractor', function(frm){
            return {
                filters:{
                    'designation': 'Operator'
                }
            }
        });   
    }
});
