import requests
from newsapi import NewsApiClient
import smtplib
from twilio.rest import Client

# Mail and SMS activate/deactivate
SEND_MAIL: bool = True
SEND_SMS: bool = False

# Stock setup
STOCK_NAME: str = "TSLA"
COMPANY_NAME: str = "Tesla Inc"
PRICE_PERCENTAGE_LIMIT: int = 5  # Input the daily percentage change for the alert

# Email setup
MY_MAIL: str = ""  # example@email.com
MAIL_PASSWORD: str = ""  # Mail account password
SMTP: str = ""  # SMTP server address
PORT: int = 587  # Server port
SMTP_SERVER: tuple = (SMTP, PORT)  # Leave as is

# Sms setup
VIRTUAL_TWILIO_NUMBER: str = "your virtual twilio number"
VERIFIED_NUMBER: str = "your own phone number verified with Twilio"
TWILIO_SID: str = "YOUR TWILIO ACCOUNT SID"
TWILIO_AUTH_TOKEN: str = "YOUR TWILIO AUTH TOKEN"

# News setup
STOCK_API_KEY: str = "YOUR OWN API KEY FROM ALPHAVANTAGE"
NEWS_API_KEY: str = "YOUR OWN API KEY FROM NEWSAPI"

STOCK_ENDPOINT: str = "https://www.alphavantage.co/query"
NEWS_ENDPOINT: str = "https://newsapi.org/v2/everything"

# Get stock prices
stock_parameters = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK_NAME,
    "apikey": STOCK_API_KEY
}

response = requests.get(STOCK_ENDPOINT, params=stock_parameters)
response.raise_for_status()
data = response.json()["Time Series (Daily)"]
data_list = [value for (key, value) in data.items()]
yesterdays_data = data_list[0]
yesterdays_closing_price = yesterdays_data["4. close"]
day_before = data_list[1]
day_before_closing_price = day_before["4. close"]

difference = float(yesterdays_closing_price) - float(day_before_closing_price)
if difference > 0:
    up_down = "🔺"
else:
    up_down = "🔻"

pos_diff = abs(difference)

percentage_diff = round(pos_diff / float(yesterdays_closing_price) * 100)

# Alert if stock price change is above set percentage
if percentage_diff > PRICE_PERCENTAGE_LIMIT:
    news_api = NewsApiClient(api_key=NEWS_API_KEY)
    headlines = news_api.get_everything(q='Tesla',
                                        language='en',
                                        )
    first_three_headlines = headlines['articles'][:3]

    # Create a new list of the first 3 article's headline and description
    formatted_articles = [
        f"{STOCK_NAME}: {up_down}{percentage_diff}%\nHeadline: {article['title']}. \nBrief: {article['description']}"
        for
        article in first_three_headlines]
    print(formatted_articles)

    if SEND_MAIL:
        # Send each article as a separate mail
        for article in formatted_articles:
            with smtplib.SMTP(SMTP_SERVER) as connection:
                connection.starttls()
                connection.login(user=MY_MAIL, password=MAIL_PASSWORD)
                connection.sendmail(
                    from_addr=MY_MAIL,
                    to_addrs=MY_MAIL,
                    msg=f"Subject:{COMPANY_NAME} Price Alert News\n\n{article}."
                )

    if SEND_SMS:
        # Send each article as a separate message via Twilio.
        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

        for article in formatted_articles:
            message = client.messages.create(
                body=article,
                from_=VIRTUAL_TWILIO_NUMBER,
                to=VERIFIED_NUMBER
            )
