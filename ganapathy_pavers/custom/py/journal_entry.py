import frappe
def journal_entry(self, event):
    for i in self.accounts:
        if i.party and i.party_type :
            if i.party_type:
                address=frappe.get_value(i.party_type, i.party,"primary_address")
                self.party_address=address
            self.party_name=i.party
            break
