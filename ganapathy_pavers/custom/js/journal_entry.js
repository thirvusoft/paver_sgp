var delivery_note = []
async function get_delivery_notes(name) {
    delivery_note = await frappe.db.get_list('Journal Entry', { filters: { 'name': ['!=', name], 'docstatus': 1, 'delivery_note': ['is', 'set'] }, fields: ['delivery_note'], pluck: 'delivery_note', limit: 0 })
    console.log(delivery_note)
}

frappe.ui.form.on("Journal Entry", {
    refresh: function (frm, cdt, cdn) {
        if (!cur_frm.fields_dict.delivery_note.$input) {
            cur_frm.fields_dict.delivery_note.make_input()
        }
        frm.fields_dict.delivery_note.$input.on("click", async function () {
            await get_delivery_notes(frm.doc.name);
        })

        frm.set_query("delivery_note", function () {
            return {
                filters: {
                    name: ['not in', delivery_note]
                }
            }
        });
    }
});
