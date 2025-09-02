import frappe
from frappe import _

def get_stone_receipt_dashboard(data):
    # Current document name get करें
    stone_receipt_name = frappe.form_dict.get('name') or data.get('name')
    
    # Existing transactions को extend करें
    if 'transactions' not in data:
        data['transactions'] = []
    
    # Stone Confirmation count get करें
    stone_confirmation_count = 0
    if stone_receipt_name:
        stone_confirmation_count = frappe.db.count('Stone Confirmation', {'stone_receipt_id': stone_receipt_name})
    
    # Stone Confirmation section add करें
    data['transactions'].append({
        'label': _('Stone Confirmation'),
        'items': ['Stone Confirmation']
    })
    
    # Field mapping add करें
    if 'non_standard_fieldnames' not in data:
        data['non_standard_fieldnames'] = {}
    
    # stone_receipt_id field mapping
    data['non_standard_fieldnames']['Stone Confirmation'] = 'stone_receipt_id'
    
    return data