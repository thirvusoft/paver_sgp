def set_qty(self, event):
    for row in self.items:
        row.stock_qty=row.ts_qty