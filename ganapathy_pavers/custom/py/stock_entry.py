import frappe

def update_asset(self, event):
    if(self.stock_entry_type=="Manufacture" and self.bom_no and self.fg_completed_qty):
        asset=frappe.get_value('BOM', self.bom_no, 'asset_name')
        if(asset):
            doc=frappe.get_doc('Asset', asset)
            if(event=='on_submit'):
                doc.update({
                    'current_number_of_strokes': float(self.fg_completed_qty)+float(float(doc.current_number_of_strokes) or 0)
                })  
            if(event=='on_cancel'):
                doc.update({
                    'current_number_of_strokes': -float(self.fg_completed_qty)+float(float(doc.current_number_of_strokes) or 0)
                })
            if((float(doc.notification_alert_at or 0)>float(doc.current_number_of_strokes or 0)) and doc.to_notify!=1):
                doc.update({
                    'to_notify': 1
                })
            elif((float(doc.notification_alert_at or 0)<float(doc.current_number_of_strokes or 0)) and doc.to_notify!=0):
                doc.update({
                    'to_notify': 0
                })
            doc.save('Update')
