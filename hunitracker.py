import smtplib
import pandas as pd
import requests
from bs4 import BeautifulSoup
from price_parser import Price
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import configparser

PRODUCT_URL_CSV = "huni.csv"
SAVE_TO_CSV = True
PRICES_CSV = "hunihistory.csv"
SEND_MAIL = True

config = configparser.ConfigParser()
config.read('secrets.txt')
email = config['credentials']['email']
password = config['credentials']['password']


def get_urls(csv_file):
    df = pd.read_csv("C:/Users/PyryAamu/Documents/price tracker/huni.csv")
    return df


def get_response(url):
    response = requests.get(url)
    return response.text

def get_availability(html):
    soup = BeautifulSoup(html, "lxml")
    
    # Check for availability (if sold out text is present)
    availability_element = soup.select_one(".add-to-cart-text")
    availability = availability_element and 'sold out' in availability_element.text.lower()
    
    return availability

def process_products(df):
    updated_products = []
    for product in df.to_dict("records"):
        html = get_response(product["url"])
        
        # Check availability and store whether the product is not sold out
        product["availability"] = get_availability(html)  # True if not sold out
        
        updated_products.append(product)
    
    return pd.DataFrame(updated_products)

#From here we get the mail sent

def get_mail(df):
    subject = "Restock alert"
    body = df[df["availability"]].to_string()
    subject_and_message = f"Subject:{subject}\n\n{body}"
    return subject_and_message

#def send_mail(df):
    #message_text = get_mail(df)
    #with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        #smtp.starttls()
        #smtp.login(mail_user, mail_pass)
        #smtp.sendmail(mail_user, mail_to, message_text)

def send_mail(df):
    message_text = get_mail(df)
    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = email
    msg['Subject'] = 'Price Drop Alert'
    
    # Encode the message body as UTF-8 to support non-ASCII characters
    body = MIMEText(message_text, 'plain', 'utf-8')
    msg.attach(body)

    try:
        # Connect to the SMTP server
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(email, password)
            smtp.sendmail(email, email, msg.as_string())
            print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")



def main():
    df = get_urls(PRODUCT_URL_CSV)
    df_updated = process_products(df)
    if SAVE_TO_CSV:
        df_updated.to_csv(PRICES_CSV, index=False, mode="a")
    if SEND_MAIL:
        send_mail(df_updated)

if __name__ == "__main__":
    main()