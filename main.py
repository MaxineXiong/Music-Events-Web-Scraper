from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import json
import psycopg2
import math



class MusicEventScraper:
    """Define a class that handles web scraping tasks, emailing tasks,
       and database operations
    """
    def __init__(self, country: str, city: str, max_events: int = 0):
        """Initialize a new instance of the MusicEventScraper class.
           Arguments:
           - country (str): The country where the music events are located.
                         This is used to build the URL for scraping.
           - city (str): The city within the specified country where the music
                         events occur. It is also used to build the URL for
                         scraping.
           - max_events (int, optional): The maximum number of events to scrape.
                         If set to 0, all available events will be scraped.
                         Default is 0.
        """
        # Initialize instance variables for scraper settings
        self.country = country
        self.city = city
        self.max_events = max_events
        # Initialize instance variables to store scraped data
        self.output_df = None
        self.event_count = 0
        self.scraping_finished = False
        self.event_names = []
        self.event_booking_statuses = []
        self.event_times = []
        self.event_durations = []
        self.event_venues = []
        self.event_addresses = []
        self.event_URLs = []
        self.event_low_prices = []
        self.event_high_prices = []


    def create_soup(self, url: str):
        """Method to fetch and parse the HTML content from a specified URL to create a
           BeautifulSoup object.
           Arguments:
           - url (str): The URL of the webpage from which to fetch the content.
        """
        # Set the user agent to mimic a browser request
        headers = {'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'}
        # Perform an HTTP GET request
        r = requests.get(url, headers=headers)
        # Extract content from the response
        c = r.content
        # Parse the content using BeautifulSoup and return the soup object
        soup = BeautifulSoup(c, 'html.parser')
        return soup


    def convert_to_datetime(self, dt_str: str):
        """Method to convert a date and time string into a datetime object.
           Arguments:
           - dt_str (str): The date and time string input.
        """
        # Check if the string contains '+'
        if '+' in dt_str:
            # Remove the string part that is behind ' + '
            dt_str = dt_str.split(' + ')[0]

        # Check if the string contains 'at' which is used to separate...
        # ...day of week and time
        if ' at ' in dt_str:
            # Split the string into day of week and time components
            day_of_week, event_time = dt_str.split(' at ')
            # Left pad the event time into 'hh:mm AM/PM' format
            event_time = event_time.rjust(8, '0')
            # Check if the string indicates the event is happening 'Tomorrow'
            if day_of_week == 'Tomorrow':
                # Compute tomorrow's date
                tomorrow_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
                # Construct the full datetime string for tomorrow's event in proper format
                revised_datetime = tomorrow_date + ', ' + event_time
            # Check if the string indicates the event is happening 'Today'
            elif day_of_week == 'Today':
                # Compute today's date
                today_date = datetime.now().strftime('%Y-%m-%d')
                # Construct the full datetime string for today's event in proper format
                revised_datetime = today_date + ', ' + event_time
            else:
                # Compute the weekday number for the event from the day of week name
                event_dow = time.strptime(day_of_week, '%A').tm_wday
                # Get today's weekday number
                today_dow = datetime.now().weekday()
                # Calculate the difference in days between today and the event day
                if event_dow > today_dow:
                    diff_days = event_dow - today_dow
                else:
                    diff_days = event_dow - today_dow + 7
                # Calculate the date of the event based on the difference
                event_date = (datetime.now() + timedelta(days=diff_days)).strftime('%Y-%m-%d')
                # Construct the full datetime string for the event in proper format
                revised_datetime = event_date + ', ' + event_time
        else:
            # Split the string into day of the week, event date, and event time
            day_of_week, event_date, event_time = dt_str.split(', ')
            # Split the event date string further into month and day
            event_month, event_day = event_date.split(' ')
            # Left pad the event day into 'dd' format
            event_day = event_day.rjust(2, '0')
            # Left pad the event time into 'hh:mm AM/PM' format
            event_time = event_time.rjust(8, '0')
            # Construct the full datetime string for the event in proper format
            revised_datetime = str(datetime.now().year) + '-' + event_month \
                               + '-' + event_day + ', ' + event_time
            # Return the datetime object for the parsed date and time
            return datetime.strptime(revised_datetime, '%Y-%b-%d, %I:%M %p')

        # Return the datetime object for the parsed date and time
        return datetime.strptime(revised_datetime, '%Y-%m-%d, %I:%M %p')


    def extract_event_name(self, soup):
        """Method to extract the event name from a BeautifulSoup object.
           Arguments:
           - soup: The BeautifulSoup object to extract the event name from.
        """
        try:
            # Attempt to find and return the text of the first <h2> tag
            event_name = soup.find('h2').text
        except:
            # Return None if no <h2> tag is found or another error occurs
            event_name = None
        return event_name


    def extract_event_url(self, soup):
        """Method to extract the event URL from a BeautifulSoup object.
           Arguments:
           - soup: The BeautifulSoup object to extract the event URL from.
        """
        try:
            # Attempt to find the first <a> tag with a href attribute
            a = soup.find('a', href=True)
            # Extract and return the href attribute value
            event_url = a['href']
        except:
            # Return None if no <a> tag with href is found or another error occurs
            event_url = None
        # Append the event URL to corresponding list
        self.event_URLs.append(event_url)
        # Return the extracted event URL
        return event_url


    def extract_listed_details(self, soup):
        """Method to extract additional event attributes such as booking
           status and time from a BeautifulSoup object.
           Arguments:
           - soup: The BeautifulSoup object to extract the additional attributes from.
        """
        # Assign None to the two variables as their initial values
        event_booking_status = None
        event_time = None
        # Find all <p> tags and iterate over them to extract relevant details
        event_details = soup.find_all('p')
        if event_details:
            for detail in event_details:
                # Remove the leading and trailing white spaces
                detail = detail.text.strip()
                # Check if the extracted detail matches the certain regex pattern
                if re.match('.*\s\d+\:\d{2}\s*[PpMmAa]{2}.*', detail):
                    # If the pattern matches, assign the extracted detail value...
                    # ...to the event_time variable
                    event_time = detail
                # Check if the extracted detail contains the status value
                if detail.lower() in ['almost full', 'sales end soon', 'going fast']:
                    # If it does, assign it to the event_booking_status variable
                    event_booking_status = detail
        # Convert extracted time into a datetime object
        if event_time:
            event_time = self.convert_to_datetime(event_time)
        # Append the two variables to the corresponding lists
        self.event_booking_statuses.append(event_booking_status)
        self.event_times.append(event_time)


    def extract_prices(self, soup):
        """Method to extract lowest price and highest price from a BeautifulSoup object.
           Arguments:
           - soup: The BeautifulSoup object to extract the prices from.
        """
        try:
            # Try find the <script> tag containing the data, and extract the JSON string
            json_str = soup.find('script', {'type': 'application/ld+json'}).text.strip()
            # Parse the JSON string into a Python dictionary
            json_data = json.loads(json_str)
            # Navigate the dictionary to find the lowest and highest price values
            lowest_price = json_data['offers'][0]['lowPrice']
            highest_price = json_data['offers'][0]['highPrice']
        except:
             # Set price values to None if any errors occur during extraction
            lowest_price = None
            highest_price = None

        # Append the extracted price values to corresponding lists
        self.event_low_prices.append(lowest_price)
        self.event_high_prices.append(highest_price)


    def extract_location(self, soup):
        """Method to extract location information such as venue and address
           from a BeautifulSoup object.
           Arguments:
           - soup: The BeautifulSoup object to extract location information from.
        """
        try:
            # Find a div with class 'location-info__address'
            location = soup.find('div', {'class': "location-info__address"})
            # Further extract the venue name from the extracted div part
            venue = location.find('p').text.strip()
            # Extract the event address from the remaining part
            address = location.text.replace('Show map', '').replace(venue, '').strip()
        except:
            # Set venue and address to None if any errors occur during extraction
            venue = None
            address = None
        # Append the extracted venue and address to corresponding lists
        self.event_venues.append(venue)
        self.event_addresses.append(address)


    def extract_duration(self, soup):
        """Method to extract event duration from a BeautifulSoup object.
           Arguments:
           - soup: The BeautifulSoup object to extract event duration from.
        """
        try:
            # Find an <ul> tag with a specific data-testid attribute...
            # ...and extract its plain text as duration value
            duration = soup.find('ul', {'data-testid': "highlights"}).text.strip()
            duration = duration.replace('Event lasts', '').strip()
        except:
            # Set duration to None if no matching <ul> is found or another error occurs
            duration = None

        if duration:
            # Initialize an empty dictionary to hold duration components
            duration_dict = {}
            # Split the duration string into values and keys
            duration_list = duration.split(' ')
            # Convert each value to numeric number
            duration_values = [int(x) for x in duration_list[::2]]
            # Transform the keys into a list of either 'hour' or 'minute'
            duration_keys = [x.replace('s', '') for x in duration_list[1::2]]
            # Populate the dictionary with the keys and values
            for key, value in zip(duration_keys, duration_values):
                duration_dict[key] = value
            # Calculate the duration in minutes
            duration_mins = sum([value * 60 if key == 'hour'
                                 else value if key == 'minute' else 0
                                 for key, value in duration_dict.items()])
        else:
            duration_mins = None

        # Append the calculated duration to the corresponding list
        self.event_durations.append(duration_mins)


    def scrap_event_page(self, event_url: str):
        """Method to handle web scraping of an individual event page.
           Arguments:
           - event_url (str): The URL of an event page to scrap data from.
        """
        if event_url:
            # Create a soup object for the event page
            event_page_soup = self.create_soup(event_url)
            # Extract the lowest price, highest price, venue, address,...
            # ...and duration information from the event page
            self.extract_prices(event_page_soup)
            self.extract_location(event_page_soup)
            self.extract_duration(event_page_soup)
        else:
            # Append None values to the corresponding instance lists...
            # ...if no URL was extracted
            self.event_low_prices.append(None)
            self.event_high_prices.append(None)
            self.event_venues.append(None)
            self.event_addresses.append(None)
            self.event_durations.append(None)


    def scrap_listing_page(self, soup):
        """Method to perform web scraping of an event listing page that displays
           multiple music events.
           Arguments:
           - soup: The BeautifulSoup object to extract information from.
        """
        # Find all sections with class 'event-card-details' and iterate over them
        listed_events = soup.find_all('section', {'class': 'event-card-details'})
        for event in listed_events:
            # Extract event name from the current event section
            event_name = self.extract_event_name(event)
            if event_name not in self.event_names:
                # If the extracted event name is not found in the event_names list,...
                # ...increment the event count and append the event name to the list
                self.event_count += 1
                self.event_names.append(event_name)
            else:
                # If the extracted event name is already included in the ...
                # ...event_names list, skip and move on to the next event section
                continue

            # Extract the event URL from the current event section
            event_url = self.extract_event_url(event)

            # Extract booking status and event time from the current event section
            self.extract_listed_details(event)

            # Further extract the lowest price, highest price, venue, address, ...
            # ...and duration information from the event page
            self.scrap_event_page(event_url)

            # Check if the maximum number of events has been reached
            if self.max_events > 0:
                if self.event_count >= self.max_events:
                    # If so, mark the scraping process as finished
                    self.scraping_finished = True
                    # And exit the loop
                    break


    def to_dataframe(self):
        """Method to convert all collected data into a Pandas DataFrame.
        """
        # Create a pandas DataFrame from the collected data
        self.output_df = pd.DataFrame({'Event': self.event_names,
                                       'Date and Time': self.event_times,
                                       'Duration (in minutes)': self.event_durations,
                                       'Venue': self.event_venues, 'Address': self.event_addresses,
                                       'Lowest Price': self.event_low_prices,
                                       'Highest Price': self.event_high_prices,
                                       'Booking Status': self.event_booking_statuses,
                                       'URL': self.event_URLs})
        # Drop the rows that have missing values for either 'Date and Time', ...
        # ... 'Venue', or 'URL' columns
        self.output_df.dropna(subset=['Date and Time', 'Venue', 'URL'], how='any')
        # Keep the events that will occur after right now
        self.output_df = self.output_df[self.output_df['Date and Time'] > datetime.now()]
        # Sort the DataFrame by 'Date and Time' and Event Name in ascending order
        self.output_df.sort_values(by=['Date and Time', 'Event'], ascending=[True, True], inplace=True)
        # Reset the index
        self.output_df.reset_index(drop=True, inplace=True)


    def scrap_data(self):
        """Method to scrap music events data from Eventbrite website.
        """
        # Construct the base URL for event listings
        url_key = 'https://www.eventbrite.com.au/d/{}--{}/music--events/' \
                     .format(self.country.lower(), self.city.lower())
        # Create a soup object for a random page
        random_page_soup = self.create_soup(url_key + '?page=2')
        # Extract the total number of pages from the random page
        total_page_number = int(random_page_soup.find('li', {'data-testid': 'pagination-parent'}) \
                                .text.split('of')[-1].strip())

        # Iterate through all listing pages and scrap data for each event
        for page_num in range(1, total_page_number + 1):
            # Construct the full URL for the current listing page
            listing_page_url = url_key + '?page=' + str(page_num)
            # Create a soup object for the current listing page
            listing_page_soup = self.create_soup(listing_page_url)
            # Scrap data from the current listing page
            self.scrap_listing_page(listing_page_soup)
            # Check if the scraping process has been marked as finished
            if self.scraping_finished:
                # If so, exit the loop
                break

        # Convert all collected data into a Pandas DataFrame
        self.to_dataframe()

        # Print a status message for successful data scraping
        print('Data successfully scraped!')


    def send_email(self):
        """Method to send an email with the scraped data as an attachment.
        """
        # Construct an unique CSV file name using city, country, and current datetime
        csv_file_name = 'music-events-{}-{}-{}.csv'.format(self.city.lower(), self.country.lower(),
                          datetime.now().strftime('%Y%m%d%H%M%S'))
        # Save the dataframe as a CSV file
        self.output_df.to_csv(csv_file_name)
        # Print a message indicating the file save location
        print(f'The extracted data has been saved as {csv_file_name}.')

        # Define the email subject line, incorporating city and country names
        subject = "🎶 Unmissable Music Events Coming Up in {}, {}! 🌟".format(self.city.title(), self.country.title())

        # Read the content from the email template file
        with open('email-html-body-template.txt', 'r') as file:
            body = file.read()
        # Format the email template string to construct the HTML body of the email
        body = body%(self.city.title(), self.city.title(), self.city.title())

        # Set up Email account credentials and SMTP server details
        sender_email = "[SENDER-EMAIL-ADDRESS]"
        recipient_email = "[RECIPIENT-EMAIL-ADDRESS]"
        # To generate an app password for this program, go to ...
        # ...https://myaccount.google.com/security, search "App Passwords", ...
        # ...and create one
        sender_password = "[YOUR-APP-PASSWORD]"
        smtp_server = 'smtp.gmail.com'
        smtp_port = 465    # Port number for SSL
        path_to_attachment = csv_file_name

        # Create a MIMEMultipart object to combine different parts of the email
        message = MIMEMultipart()
        message['Subject'] = subject
        message['From'] = sender_email
        message['To'] = recipient_email
        # Attach the HTML body part to the email
        body_part = MIMEText(body, 'html')
        message.attach(body_part)

        # Attach the CSV file to the email
        with open(path_to_attachment, 'rb') as file:
            message.attach(MIMEApplication(file.read(), Name=csv_file_name))

        # Login to the SMTP server and send the email
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
           server.login(sender_email, sender_password)
           server.sendmail(sender_email, recipient_email, message.as_string())

        # Print a confirmation message after sending the email
        print(f'An email with the CSV file has been sent to {recipient_email}.')


    def move_to_pgDB(self):
        """Method to transfer the scraped data to a local PostgreSQL database.
        """
        # Connect to a local PostgreSQL database with credentials and specifics
        conn = psycopg2.connect("dbname='[DATABASE-NAME]' user='[USERNAME]' password='[PASSWORD]' \
                                 port='5432' host='localhost'")
        # Enable autocommit to ensure that changes are immediately saved to the database
        conn.set_session(autocommit=True)
        # Create a cursor object to execute SQL commands
        cur = conn.cursor()

        # Create a table named MusicEvents in the database if it does not exist
        cur.execute("""
                     CREATE TABLE IF NOT EXISTS MusicEvents (
                                ID              SERIAL PRIMARY KEY,
                                Event           TEXT NOT NULL,
                                DateAndTime     TIMESTAMP NOT NULL,
                                Duration        DECIMAL,
                                Venue           TEXT NOT NULL,
                                Address         TEXT,
                                LowPrice        DECIMAL,
                                HighPrice       DECIMAL,
                                BookingStatus   TEXT,
                                URL             TEXT NOT NULL
                     )
                    """)

        # Truncate the table to remove all existing records
        cur.execute("""TRUNCATE MusicEvents""")

        # Iterate through each row in the DataFrame to insert data into the SQL table
        for row_id in range(len(self.output_df)):
            # Get the current row
            row = self.output_df.loc[row_id]
            # Extract data for each attribute from the current row
            event = row['Event']
            date_and_time = row['Date and Time']
            duration = row['Duration (in minutes)']
            venue = row['Venue']
            address = row['Address']
            low_price = row['Lowest Price']
            high_price = row['Highest Price']
            booking_status = row['Booking Status']
            url = row['URL']

            # Replace the NaN values for duration, low_price, and high_price...
            # ...with None
            if math.isnan(duration):
                duration = None
            if math.isnan(low_price):
                low_price = None
            if math.isnan(high_price):
                high_price = None

            # Insert current row of data into the SQL table
            cur.execute("""
                            INSERT INTO MusicEvents(Event, DateAndTime, Duration,
                                                    Venue, Address, LowPrice,
                                                    HighPrice,
                                                    BookingStatus, URL)
                            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,(event, date_and_time, duration, venue, address,
                             low_price, high_price, booking_status, url)
                        )

        # Execute a query to count the total number of records inserted into...
        # ...the SQL table
        cur.execute("""SELECT COUNT(*) FROM MusicEvents""")
        records_count = cur.fetchall()[0][0]

        # Provide feedback on the success of the data migration
        if records_count > 0:
            print('Data successfully migrated to your PostgreSQL database.')
            print('Records count: ' + str(records_count))
        else:
            print('No records added to your PostgreSQL database.')

        # Close the connection to the database
        conn.close()


    def run(self):
        """Method to orchestrate web scraping, emailing, and database operations
        """
        # Call method to scrap music event data from Eventbrite website
        self.scrap_data()
        # Call method to send email with the CSV file attachment
        self.send_email()
        # Call method to migrate data to a local PostgreSQL database
        self.move_to_pgDB()



# Check if this script is being run directly (and not imported as a module)
if __name__ == '__main__':
    # Create a MusicEventScraper object to scrap data for all available music events...
    # ...that will occur in Sydney, Australia
    scraper = MusicEventScraper(country='Australia', city='Sydney',
                                max_events=0)
    # Start the program
    scraper.run()
