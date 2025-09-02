import frappe
from frappe import _

def get_sales_order_dashboard(data):
    # Existing transactions को extend करें
    if 'transactions' not in data:
        data['transactions'] = []
    
    # Stone Management section add करें
    data['transactions'].append({
        'label': _('Stone Management'),
        'items': ['Stone Request']
    })
    
    # Field mapping add करें
    if 'non_standard_fieldnames' not in data:
        data['non_standard_fieldnames'] = {}
    
    data['non_standard_fieldnames']['Stone Request'] = 'sku_sales_order'
    
    return data