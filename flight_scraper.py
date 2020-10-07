# The usual webdriver imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Import my email and pass from secrets
from secrets import gmail_username, gmail_password, outlook_username


# For structuring captured data
import pandas as pd

# For time/date-time (setting delays & returning current time)
import time
import datetime
from time import sleep

# And to connect email
import smtplib
from email.mime.multipart import MIMEMultipart

# Disable this out of habit
opts = Options()
opts.add_argument("--no-sandbox")

# Init a variable to hold the chrome driver methods
browser = webdriver.Chrome(ChromeDriverManager().install())


# Function to choose departing airport


def dep_airport_chooser(dep_airport):
    fly_from = browser.find_element_by_class_name("airport-code.d-block")
    sleep(1.5)
    fly_from.click()
    sleep(1.5)
    # Hit the 'X' button
    clear_out = browser.find_element_by_xpath(
        "//*[@id='airport-serach-panel']/div/div[1]/span/button")
    clear_out.click()
    sleep(1.5)
    # Type my chosen port
    clear_out = browser.find_element_by_xpath("//*[@id='search_input']")
    clear_out.send_keys(dep_airport)
    sleep(1.5)
    # And select the auto complete result below
    first_item = browser.find_element_by_xpath(
        "//*[@id='airport-serach-panel']/div/div[2]/div/ul/li/a/span[1]")
    sleep(1.5)
    first_item.click()

    # Function for fly-to


def dest_airport_chooser(dest_airport):
    fly_to = browser.find_element_by_id(
        "toAirportName")
    sleep(1.5)
    fly_to.click()
    sleep(1.5)
    # Type my chosen port
    clear_out = browser.find_element_by_xpath("//*[@id='search_input']")
    clear_out.send_keys(dest_airport)
    sleep(1.5)
    # And select the auto complete result below
    first_item = browser.find_element_by_xpath(
        "//*[@id='airport-serach-panel']/div/div[2]/div/ul/li/a/span[1]")
    sleep(1.5)
    first_item.click()


# Setting ticket type paths
return_ticket = "//*[@id='selectTripType-val']"
first_option = "//*[@id ='ui-list-selectTripType0']"
# Todo
#one_way_ticket = ""
#multi_ticket = ""


# Def a function to choose ticket type


def ticket_chooser(ticket, options):

    try:
        ticket_type = browser.find_element_by_xpath(ticket)
        ticket_type.click()
        drop_options = browser.find_element_by_xpath(options)
        drop_options.click()
    except Exception as e:
        pass


# Set date paths - Update as needed for running script with different dates

dep_date = "//tr[4]/td[3]/a"

return_date = "//tr[5]/td[3]/a"

# Function for date selection


def date_chooser(departure, returning):
    dates_button = browser.find_element_by_xpath(
        "//*[@id='calDepartLabelCont']/span[2]").click()
    sleep(1.5)
    fly_out = browser.find_element_by_xpath(departure).click()
    sleep(1.5)
    fly_home = browser.find_element_by_xpath(returning).click()
    sleep(1.5)
    done_button = browser.find_element_by_xpath("//button[2]").click()

# And finally, click continue


def search():
    proceed_button = browser.find_element_by_xpath(
        "//*[@id='btn-book-submit']").click()
    sleep(10)
    print("Results ready!")


# Creating a table with Pandas - will export to Excel
df = pd.DataFrame()


def compile_data():
    global df

    global price_list

    # prices

    prices = browser.find_elements_by_xpath("//div[2]/a")
    price_list = [value.text for value in prices]

    now = datetime.datetime.now()
    current_date = (str(now.year) + '-' + str(now.month) + '-' + str(now.day))
    current_time = (str(now.hour) + ':' + str(now.minute))
    current_price = 'price' + '(' + current_date + '---' + current_time + ')'
    for i in range(len(price_list)):
        try:
            df.loc[i, str(current_price)] = price_list[i]
        except Exception as e:
            pass

    print("Excel sheet created!")

# Create msg template for email


def create_msg():
    global msg
    msg = '\nCurrent Cheapest flight:\nPrice: {}'.format(cheapest_price)


# Connect to email
def connect_mail(username, password):
    try:
        global server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_username, gmail_password)
    except:
        print("Something's not right..")


# Send the email


def send_email(msg):
    global message
    message = MIMEMultipart()
    message['Subject'] = 'Current Best flight'
    message['From'] = gmail_username
    message['to'] = outlook_username

    server.sendmail(gmail_username,
                    outlook_username, msg)


for i in range(3):
    link = "https://www.delta.com/"
    browser.get(link)
    sleep(5)
    dep_airport_chooser("MSP")
    dest_airport_chooser("LAX")
    ticket_chooser(return_ticket, first_option)
    date_chooser(dep_date, return_date)
    search()
    compile_data()

    # save vals for email

    current_values = df.iloc[0]

    cheapest_price = current_values[0]

    print('run {} completed!'.format(i))

    create_msg()
    connect_mail(gmail_username, gmail_password)
    send_email(msg)
    print("Email sent!")

    df.to_excel('flights.xlsx')

    sleep(3600)
