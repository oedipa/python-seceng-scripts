import smtplib
from email.mime.text import MIMEText

def send_email_alert(domain, expiry_date):
    msg = MIMEText(f'The SSL certificate for {domain} is expiring on {expiry_date}')
    msg['Subject'] = f'SSL Certificate Expiry Alert for {domain}'
    msg['From'] = 'youremail@example.com'
    msg['To'] = 'recipient@example.com'

    with smtplib.SMTP('smtp.example.com') as server:
        server.login('youremail@example.com', 'yourpassword')
        server.send_message(msg)

# Update the generate_ssl_inventory function to include alerting
def generate_ssl_inventory(domains):
    data = []
    for domain in domains:
        try:
            expiry_date = get_ssl_expiry_date(domain)
            data.append({'Domain': domain, 'Expiry Date': expiry_date})
            if (expiry_date - datetime.now()).days < 30:  # Alert if less than 30 days to expiry
                send_email_alert(domain, expiry_date)
        except Exception as e:
            data.append({'Domain': domain, 'Expiry Date': 'Error: ' + str(e)})
    return pd.DataFrame(data)
