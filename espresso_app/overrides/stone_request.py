import frappe
from frappe import _

def get_stone_request_dashboard(data):
    """
    Dashboard configuration for Stone Request doctype
    Shows connected Stone Receipts in the dashboard
    """

    # Add Stone Receipt to transactions
    data.setdefault('transactions', []).append({
        'label': _('Stone Processing'),
        'items': ['Stone Receipt']
    })

    # Field mapping
    data.setdefault('non_standard_fieldnames', {})['Stone Receipt'] = 'sr_id'

    # Show in separate Connections tab
    data['show_connections_in_sidebar'] = 0

    return data
