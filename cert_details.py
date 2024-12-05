import ssl
import socket
from datetime import datetime
import pandas as pd

def get_ssl_expiry_date(hostname):
    context = ssl.create_default_context()
    with context.wrap_socket(socket.socket(), server_hostname=hostname) as conn:
        conn.settimeout(3.0)
        conn.connect((hostname, 443))
        ssl_info = conn.getpeercert()
        expiry_date = datetime.strptime(ssl_info['notAfter'], '%b %d %H:%M:%S %Y %Z')
        return expiry_date

def generate_ssl_inventory(domains):
    data = []
    for domain in domains:
        try:
            expiry_date = get_ssl_expiry_date(domain)
            data.append({'Domain': domain, 'Expiry Date': expiry_date})
        except Exception as e:
            data.append({'Domain': domain, 'Expiry Date': 'Error: ' + str(e)})
    return pd.DataFrame(data)

# Example list of domains
domains = ['example.com', 'sub.example.com']

# Generate the inventory
ssl_inventory = generate_ssl_inventory(domains)

# Display the inventory
ssl_inventory.to_csv('ssl_inventory.csv', index=False)
