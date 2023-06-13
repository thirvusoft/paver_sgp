import re

def si_validate(self, event=None):
    """
        Remove references
    """
    data = self.data
    data = re.sub(r'"set_posting_time": 0,', '"set_posting_time": 1,', data)

    data = re.sub(r'"so_detail": "[^"]+",', '', data)
    data = re.sub(r'"sales_order": "[^"]+",', '', data)
    
    data = re.sub(r'"delivery_note": "[^"]+",', '', data)
    data = re.sub(r'"dn_detail": "[^"]+",', '', data)

    data = re.sub(r'"batch_no": "[^"]+",', '', data)

    data = re.sub(r'"update_stock": 1,', '"update_stock": 0,', data)

    self.data = data
    