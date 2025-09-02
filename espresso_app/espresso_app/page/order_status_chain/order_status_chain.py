import frappe
from frappe.utils import nowdate, getdate, now_datetime, get_datetime
from datetime import datetime, timedelta

def get_time_ago(creation_datetime):
    """Calculate time ago from creation datetime"""
    if not creation_datetime:
        return "Unknown"
    
    try:
        # Convert to datetime if it's a string
        if isinstance(creation_datetime, str):
            created_dt = get_datetime(creation_datetime)
        else:
            created_dt = creation_datetime
        
        current_dt = now_datetime()
        time_diff = current_dt - created_dt
        
        # Calculate different time units
        total_seconds = int(time_diff.total_seconds())
        
        if total_seconds < 60:
            return f"{total_seconds}s"
        
        minutes = total_seconds // 60
        if minutes < 60:
            return f"{minutes}m"
        
        hours = minutes // 60
        if hours < 24:
            return f"{hours} h"
        
        days = hours // 24
        if days < 7:
            return f"{days} d"
        
        weeks = days // 7
        if weeks < 4:
            return f"{weeks}w"
        
        months = days // 30
        if months < 12:
            return f"{months} M"
        
        years = days // 365
        return f"{years} y"
        
    except Exception as e:
        frappe.log_error(f"Error calculating time ago: {str(e)}")
        return "Unknown"

@frappe.whitelist()
def get_sales_order_status_counts():
    # CHANGED: Remove Stone type filter - include all SOs
    base_filters = {}  # No filter, include all types
    
    total = frappe.db.count('Sales Order', base_filters)

    in_progress_filters = base_filters.copy()
    in_progress_filters['status'] = ['in', ['To Deliver', 'To Deliver and Bill', 'To Bill']]
    in_progress = frappe.db.count('Sales Order', in_progress_filters)

    completed_filters = base_filters.copy()
    completed_filters['status'] = 'Completed'
    completed = frappe.db.count('Sales Order', completed_filters)

    overdue_filters = base_filters.copy()
    overdue_filters['delivery_date'] = ['<', nowdate()]
    overdue_filters['status'] = ['not in', ['Completed', 'Cancelled']]
    overdue = frappe.db.count('Sales Order', overdue_filters)

    return {
        'total': total,
        'in_progress': in_progress,
        'completed': completed,
        'overdue': overdue
    }

@frappe.whitelist()
def get_filtered_sales_orders(filters):
    """
    Fetch sales orders based on applied filters - UPDATED TO INCLUDE STONE TYPE AND TIME AGO
    """
    try:
        # Build filter conditions - CHANGED: No default Stone exclusion
        conditions = {}  # Start with empty conditions
        
        # Parse filters if it's a JSON string
        if isinstance(filters, str):
            import json
            try:
                filters = json.loads(filters)
            except:
                pass
        
        # Only add filters if they have values
        if filters.get('company') and str(filters.get('company')).strip() != '':
            conditions['company'] = filters['company']
        
        if filters.get('custom_sales_order_type') and str(filters.get('custom_sales_order_type')).strip() != '':
            conditions['custom_sales_order_type'] = filters['custom_sales_order_type']
        
        if filters.get('customer') and str(filters.get('customer')).strip() != '':
            conditions['customer'] = filters['customer']
        
        if filters.get('custom_department') and str(filters.get('custom_department')).strip() != '':
            conditions['custom_department'] = filters['custom_department']
        
        if filters.get('status') and str(filters.get('status')).strip() != '':
            conditions['status'] = filters['status']
        
        # Handle date filtering
        if filters.get('transaction_date'):
            date_filter = filters['transaction_date']
            
            # Handle different date formats
            if isinstance(date_filter, list) and len(date_filter) >= 1:
                # Remove empty strings from the list
                date_filter = [d for d in date_filter if d and str(d).strip() != '']
                
                if len(date_filter) == 2:
                    # Date range
                    conditions['transaction_date'] = ['between', date_filter]
                elif len(date_filter) == 1:
                    # Single date
                    conditions['transaction_date'] = date_filter[0]
            elif isinstance(date_filter, str) and date_filter.strip() != '':
                # Single date as string
                conditions['transaction_date'] = date_filter.strip()
        
        # Get filtered sales orders - CHANGED: Include all types AND creation datetime
        sales_orders = frappe.get_all("Sales Order", 
            filters=conditions,
            fields=[
                "name", 
                "customer", 
                "status", 
                "transaction_date", 
                "delivery_date",
                "custom_department",
                "custom_main_stone",
                "custom_sales_order_type",
                "company",
                "creation"  # Added creation field for time calculation
            ],
            order_by="creation desc",
            limit=20000
        )
        
        # For each sales order, get the attached image and calculate time ago
        for so in sales_orders:
            # Calculate time ago
            so.time_ago = get_time_ago(so.creation)
            
            # Get attached image
            product_image = None
            try:
                attachments = frappe.get_all("File", 
                    filters={
                        "attached_to_doctype": "Sales Order",
                        "attached_to_name": so.name,
                        "is_folder": 0
                    },
                    fields=["file_url", "file_name"]
                )
                
                # Get the first image attachment
                for attachment in attachments:
                    if attachment.file_name and attachment.file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
                        product_image = attachment.file_url
                        break
            except Exception as img_error:
                frappe.log_error(f"Image error for {so.name}", "Sales Order Image Error")
                product_image = None
            
            so.custom_product_image = product_image
        
        return sales_orders
        
    except Exception as e:
        error_msg = str(e)[:100] + "..." if len(str(e)) > 100 else str(e)
        frappe.log_error(f"Filter error: {error_msg}", "Sales Order Filter Error")
        return []

@frappe.whitelist()
def get_filtered_sales_order_counts(filters):
    """
    Get counts for filtered sales orders - UPDATED TO INCLUDE STONE TYPE
    """
    try:
        # Parse filters if it's a JSON string
        if isinstance(filters, str):
            import json
            try:
                filters = json.loads(filters)
            except:
                pass
        
        # Build filter conditions - CHANGED: No default Stone exclusion
        conditions = {}  # Start with empty conditions
        
        if filters.get('company') and str(filters.get('company')).strip() != '':
            conditions['company'] = filters['company']
        
        if filters.get('custom_sales_order_type') and str(filters.get('custom_sales_order_type')).strip() != '':
            conditions['custom_sales_order_type'] = filters['custom_sales_order_type']
        
        if filters.get('customer') and str(filters.get('customer')).strip() != '':
            conditions['customer'] = filters['customer']
        
        if filters.get('custom_department') and str(filters.get('custom_department')).strip() != '':
            conditions['custom_department'] = filters['custom_department']
        
        if filters.get('status') and str(filters.get('status')).strip() != '':
            conditions['status'] = filters['status']
        
        # Handle date filtering
        if filters.get('transaction_date'):
            date_filter = filters['transaction_date']
            
            if isinstance(date_filter, list) and len(date_filter) >= 1:
                # Remove empty strings from the list
                date_filter = [d for d in date_filter if d and str(d).strip() != '']
                
                if len(date_filter) == 2:
                    conditions['transaction_date'] = ['between', date_filter]
                elif len(date_filter) == 1:
                    conditions['transaction_date'] = date_filter[0]
            elif isinstance(date_filter, str) and date_filter.strip() != '':
                conditions['transaction_date'] = date_filter.strip()
        
        # Get total count
        total = frappe.db.count('Sales Order', conditions)
        
        # In Progress count
        in_progress_conditions = conditions.copy()
        in_progress_conditions['status'] = ['in', ['To Deliver', 'To Deliver and Bill', 'To Bill']]
        in_progress = frappe.db.count('Sales Order', in_progress_conditions)
        
        # Completed count
        completed_conditions = conditions.copy()
        completed_conditions['status'] = 'Completed'
        completed = frappe.db.count('Sales Order', completed_conditions)
        
        # Overdue count
        overdue_conditions = conditions.copy()
        overdue_conditions['delivery_date'] = ['<', nowdate()]
        overdue_conditions['status'] = ['not in', ['Completed', 'Cancelled']]
        overdue = frappe.db.count('Sales Order', overdue_conditions)
        
        return {
            'total': total,
            'in_progress': in_progress,
            'completed': completed,
            'overdue': overdue
        }
        
    except Exception as e:
        error_msg = str(e)[:100] + "..." if len(str(e)) > 100 else str(e)
        frappe.log_error(f"Count error: {error_msg}", "Sales Order Count Error")
        return {
            'total': 0,
            'in_progress': 0,
            'completed': 0,
            'overdue': 0
        }

@frappe.whitelist()
def get_all_sales_orders_summary():
    """
    Fetch all sales orders with basic information for summary view - UPDATED TO INCLUDE STONE TYPE AND TIME AGO
    """
    try:
        # CHANGED: Remove Stone type filter - include all types, ADD creation field
        sales_orders = frappe.get_all("Sales Order", 
            filters={},  # No filter - include all types
            fields=[
                "name", 
                "customer", 
                "status", 
                "transaction_date", 
                "delivery_date",
                "custom_department",
                "custom_main_stone",
                "custom_sales_order_type",
                "company",
                "creation"  # Added creation field for time calculation
            ],
            order_by="creation desc",
            limit=100000  # Limit to prevent performance issues
        )
        
        # For each sales order, get the attached image and calculate time ago
        for so in sales_orders:
            # Calculate time ago
            so.time_ago = get_time_ago(so.creation)
            
            # Get attached image
            product_image = None
            try:
                attachments = frappe.get_all("File", 
                    filters={
                        "attached_to_doctype": "Sales Order",
                        "attached_to_name": so.name,
                        "is_folder": 0
                    },
                    fields=["file_url", "file_name"]
                )
                
                # Get the first image attachment
                for attachment in attachments:
                    if attachment.file_name and attachment.file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
                        product_image = attachment.file_url
                        break
            except Exception as img_error:
                frappe.log_error(f"Error getting image for {so.name}: {str(img_error)}")
                product_image = None
            
            so.custom_product_image = product_image
        
        return sales_orders
        
    except Exception as e:
        frappe.log_error(f"Error in get_all_sales_orders_summary: {str(e)}")
        return []



# Rest of the functions remain the same...
@frappe.whitelist()
def get_sales_order_status_tree(sales_order_id):
    if not sales_order_id:
        return {}

    def get_doc_status(docname, doctype):
        if not docname:
            return "Pending"
        try:
            status = frappe.db.get_value(doctype, docname, "status")
            return status or "Pending"
        except:
            return "Pending"

    def get_doc_image(docname, doctype):
        """Get attached image for any document"""
        if not docname:
            return None
        try:
            attachments = frappe.get_all("File", 
                filters={
                    "attached_to_doctype": doctype,
                    "attached_to_name": docname,
                    "is_folder": 0
                },
                fields=["file_url", "file_name"]
            )
            
            # Get the first image attachment
            for attachment in attachments:
                if attachment.file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
                    return attachment.file_url
            return None
        except:
            return None

    def get_doc_details(docname, doctype):
        """Get detailed information for any document type"""
        if not docname:
            return None
        
        try:
            doc = frappe.get_doc(doctype, docname)
            image = get_doc_image(docname, doctype)
            
            if doctype == "Sales Order":
                return {
                    "id": doc.name,
                    "custom_product_image": image,
                    "customer": getattr(doc, 'customer', None),
                    "contact_person": getattr(doc, 'contact_person', None),
                    "custom_department": getattr(doc, 'custom_department', None),
                    "transaction_date": str(doc.transaction_date) if getattr(doc, 'transaction_date', None) else "Not Set",
                    "delivery_date": str(doc.delivery_date) if getattr(doc, 'delivery_date', None) else "Not Set",
                    "custom_main_stone": getattr(doc, 'custom_main_stone', None),
                    "custom_sales_order_type": getattr(doc, 'custom_sales_order_type', None),
                    "company": getattr(doc, 'company', None),
                    "time_ago": get_time_ago(getattr(doc, 'creation', None))  # Added time ago
                }
            
            elif doctype == "Purchase Order":
                return {
                    "id": doc.name,
                    "custom_product_image": image,
                    "supplier": getattr(doc, 'supplier', None),
                    "transaction_date": str(doc.transaction_date) if getattr(doc, 'transaction_date', None) else "Not Set",
                    "schedule_date": str(getattr(doc, 'schedule_date', None)) if getattr(doc, 'schedule_date', None) else "Not Set",
                    "order_confirmation_no": getattr(doc, 'order_confirmation_no', None),
                    "order_confirmation_date": str(getattr(doc, 'order_confirmation_date', None)) if getattr(doc, 'order_confirmation_date', None) else "Not Set",
                    "time_ago": get_time_ago(getattr(doc, 'creation', None))  # Added time ago
                }
            
            elif doctype == "Stone Request":
                return {
                    "id": doc.name,
                    "custom_product_image": image,
                    "requested_by": getattr(doc, 'requested_by', None),
                    "arranging_company": getattr(doc, 'arranging_company', None),
                    "request_date": str(getattr(doc, 'request_date', None)) if getattr(doc, 'request_date', None) else "Not Set",
                    "required_date": str(getattr(doc, 'required_date', None)) if getattr(doc, 'required_date', None) else "Not Set",
                    "time_ago": get_time_ago(getattr(doc, 'creation', None))  # Added time ago
                }
            
            elif doctype == "Stone Receipt":
                return {
                    "id": doc.name,
                    "custom_product_image": image,
                    "supplier": getattr(doc, 'supplier', None),
                    "receipt_date": str(getattr(doc, 'receipt_date', None)) if getattr(doc, 'receipt_date', None) else "Not Set",
                    "posting_date": str(getattr(doc, 'posting_date', None)) if getattr(doc, 'posting_date', None) else "Not Set",
                    "time_ago": get_time_ago(getattr(doc, 'creation', None))  # Added time ago
                }
            
            elif doctype == "Sales Invoice":
                return {
                    "id": doc.name,
                    "custom_product_image": image,
                    "customer": getattr(doc, 'customer', None),
                    "posting_date": str(getattr(doc, 'posting_date', None)) if getattr(doc, 'posting_date', None) else "Not Set",
                    "due_date": str(getattr(doc, 'due_date', None)) if getattr(doc, 'due_date', None) else "Not Set",
                    "total": getattr(doc, 'total', 0),
                    "time_ago": get_time_ago(getattr(doc, 'creation', None))  # Added time ago
                }
            
            elif doctype == "Purchase Invoice":
                return {
                    "id": doc.name,
                    "custom_product_image": image,
                    "supplier": getattr(doc, 'supplier', None),
                    "posting_date": str(getattr(doc, 'posting_date', None)) if getattr(doc, 'posting_date', None) else "Not Set",
                    "bill_date": str(getattr(doc, 'bill_date', None)) if getattr(doc, 'bill_date', None) else "Not Set",
                    "total": getattr(doc, 'total', 0),
                    "time_ago": get_time_ago(getattr(doc, 'creation', None))  # Added time ago
                }
            
            return None
            
        except Exception as e:
            frappe.log_error(f"Error getting details for {doctype} {docname}: {str(e)}")
            return None

    def build_tree(sales_order_id):
        sales_order = frappe.get_doc("Sales Order", sales_order_id)

        # Get Sales Order details
        sales_order_details = get_doc_details(sales_order_id, "Sales Order")

        # Rest of the function remains the same...
        # (keeping the existing tree building logic unchanged)
        
        # 1. Purchase Order (from items.custom_purchase_order_no)
        po_names = list(set(
            [row.custom_purchase_order_no for row in sales_order.items if row.custom_purchase_order_no]
        ))

        # 2. Sales Order (Stone) from custom_bom_items.custom_sales_order_id
        bom_links = []
        if hasattr(sales_order, 'custom_bom_items') and sales_order.custom_bom_items:
            bom_links = [
                row for row in sales_order.custom_bom_items
                if hasattr(row, 'custom_sales_order_id') and row.custom_sales_order_id
            ]

        stone_sales_orders = []
        added_stone_sales_orders = set()
        added_stone_requests = set()

        for bom_row in bom_links:
            stone_so = getattr(bom_row, 'custom_sales_order_id', None)
            stone_request = getattr(bom_row, 'custom_stone_request_id', None)

            if not stone_so or stone_so in added_stone_sales_orders:
                continue

            # Check if this Sales Order has custom_sales_order_type == "Stone"
            try:
                stone_so_type = frappe.db.get_value("Sales Order", stone_so, "custom_sales_order_type")
                if stone_so_type != "Stone":
                    continue  # Skip if not Stone type
            except:
                continue  # Skip if error fetching type

            so_status = get_doc_status(stone_so, "Sales Order")
            stone_so_details = get_doc_details(stone_so, "Sales Order")

            # Stone Request handling
            request_nodes = []
            if stone_request and stone_request not in added_stone_requests:
                sr_status = get_doc_status(stone_request, "Stone Request")
                stone_request_details = get_doc_details(stone_request, "Stone Request")

                # Stone Receipt from Stone Request's child table
                stone_receipt_nodes = []
                try:
                    stone_request_doc = frappe.get_doc("Stone Request", stone_request)
                    if hasattr(stone_request_doc, 'stone_request_items') and stone_request_doc.stone_request_items:
                        for item in stone_request_doc.stone_request_items:
                            stone_receipt_id = getattr(item, 'stone_receipt_id', None)
                            if stone_receipt_id:
                                receipt_status = get_doc_status(stone_receipt_id, "Stone Receipt")
                                receipt_details = get_doc_details(stone_receipt_id, "Stone Receipt")
                                stone_receipt_nodes.append({
                                    "title": "Stone Receipt",
                                    "name": stone_receipt_id,
                                    "status": receipt_status,
                                    "details": receipt_details
                                })
                except:
                    pass

                request_nodes.append({
                    "title": "Stone Request to Arranging Company by Requested Company",
                    "name": stone_request,
                    "status": sr_status,
                    "details": stone_request_details,
                    "children": stone_receipt_nodes
                })
                added_stone_requests.add(stone_request)

            stone_sales_orders.append({
                "title": "Sales Order (Stone) for Factory",
                "name": stone_so,
                "status": so_status,
                "details": stone_so_details,
                "children": request_nodes
            })
            added_stone_sales_orders.add(stone_so)

        # 3. Purchase Orders with details
        purchase_orders = []
        for po in po_names:
            po_status = get_doc_status(po, "Purchase Order")
            po_details = get_doc_details(po, "Purchase Order")
            
            purchase_orders.append({
                "title": "Purchase Order (SKU) to Factory",
                "name": po,
                "status": po_status,
                "details": po_details,
                "children": stone_sales_orders
            })

        # 4. Sales Invoice
        sales_invoice = frappe.db.get_value("Sales Invoice Item", {"sales_order": sales_order_id}, "parent")
        si_status = get_doc_status(sales_invoice, "Sales Invoice")
        si_details = get_doc_details(sales_invoice, "Sales Invoice") if sales_invoice else None

        # 5. Purchase Invoice
        purchase_order = frappe.db.get_value("Purchase Order Item", {"sales_order": sales_order_id}, "parent")
        purchase_invoice = frappe.db.get_value("Purchase Invoice Item", {"purchase_order": purchase_order}, "parent")
        pi_status = get_doc_status(purchase_invoice, "Purchase Invoice")
        pi_details = get_doc_details(purchase_invoice, "Purchase Invoice") if purchase_invoice else None

        return {
            "title": "Sales Order",
            "name": sales_order_id,
            "status": sales_order.status,
            "details": sales_order_details,
            "children": purchase_orders + [
                {
                    "title": "Sales Invoice",
                    "name": sales_invoice or "Not Created",
                    "status": si_status,
                    "details": si_details
                },
                {
                    "title": "Purchase Invoice",
                    "name": purchase_invoice or "Not Created",
                    "status": pi_status,
                    "details": pi_details
                }
            ]
        }

    return build_tree(sales_order_id)
