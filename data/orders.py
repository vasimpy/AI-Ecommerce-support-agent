ORDERS = {
    "100234": {
        "id": "100234",
        "customer_id": "CUST-9021",
        "status": "in_transit",
        "items": ["Nike Air Max 270"],
        "total": 12499,
        "currency": "INR",
        "payment_status": "captured",
        "shipment": {
            "carrier": "BlueDart",
            "tracking_number": "BDX-998812",
            "status": "in_transit",
            "expected_delivery": "2026-10-10",
        },
    },
    "100345": {
        "id": "100345",
        "customer_id": "CUST-9021",
        "status": "pending",
        "items": ["Acer Predator Laptop"],
        "total": 196999,
        "currency": "INR",
        "payment_status": "authorized",
        "shipment": {
            "carrier": "FedEx",
            "tracking_number": "FX-112300",
            "status": "processing",
            "expected_delivery": "2026-10-15",
        },
    },
}

PAYMENTS = {
    "100234": {"amount": 12499, "currency": "INR", "status": "captured", "method": "Visa ending 4242"},
    "100345": {"amount": 196999, "currency": "INR", "status": "authorized", "method": "Mastercard ending 1123"},
}
