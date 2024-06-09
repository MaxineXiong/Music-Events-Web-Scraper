# Music Events Web Scraper

[![GitHub](https://badgen.net/badge/icon/GitHub?icon=github&color=black&label)](https://github.com/MaxineXiong)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Made with Python](https://img.shields.io/badge/Python->=3.6-blue?logo=python&logoColor=white)](https://www.python.org)

<br>

## Project Description

The **Music Events Web Scraper** is a web scraping program engineered to extract detailed information about music events from the [**Eventbrite**](http://eventbrite.com.au), a popular event management and ticketing platform. Users can specify a country and a city to gather attribute data on upcoming music events, including event names, venues, addresses, dates and times, durations, prices, booking statuses, and web URLs. The collected data is subsequently saved in a CSV file, which is then attached to a marketing email sent to designated recipients. Additionally, the data is transferred to a local PostgreSQL database for efficient storage and management.

<br>

## Features

- **Web Scraping**: Efficiently extracts detailed attributes of music events such as names, venues, addresses, dates and times, durations, prices, booking statuses, and URLs.
- **CSV Export**: Saves the scraped data into a CSV file for easy access and analysis.
- **Email Notification**: Sends a marketing email with the attached CSV file to specified recipient(s).
- **Database Storage**: Transfers the collected data to a local PostgreSQL database for structured storage and retrieval.

<br>

## Repository Structure

```
MusicEventsWebScraper/
├── main.py
├── "sample outputs"/
│   ├── 🎶 Unmissable Music Events Coming Up in Sydney, Australia! 🌟.eml
│   └── music-events-sydney-australia-20240609220753.csv
├── requirements.txt
├── .gitignore
├── README.md                 
└── LICENSE 
```

- **main.py**: This file is the core script containing the Python code responsible for scraping music events data, emailing the CSV output, and handling database operations.
- **sample outputs/**: This directory houses example outputs from the scraper, including an output CSV file and a marketing email, showcasing the functionality of the program.
- **requirements.txt**: This file lists all the required Python modules and packages necessary to run the desktop app. You can install these dependencies on your local computer by running the command `pip install -r requirements.txt`.
- **.gitignore**: Prevents specific files and directories from being tracked by Git, maintaining the cleanliness of the repository by excluding temporary files and sensitive information.
- **README.md**: Provides a detailed overview of the repository, including descriptions of its functionality, usage instructions, and information on how to contribute.
- **LICENSE**: The license file for the project.

<br>

## Usage

To run the web scraping program on your local computer, please follow these steps:

1. **Clone the repository:**
    ```
    git clone https://github.com/yourusername/MusicEventsWebScraper.git
    cd MusicEventsWebScraper
    ```
    
2. **Install the required packages:**
    ```
    pip install -r requirements.txt
    ```
    
3. **Configure email settings:**
   
   Open `main.py` and update the `sender_email`, `recipient_email`, and `sender_password` variables with your own email credentials and app password.
     
4. **Configure database settings:**
   
   Update the `[DATABASE-NAME]`, `[USERNAME]`, and `[PASSWORD]` values in the `move_to_pgDB` method with your PostgreSQL database credentials.
     
5. **Run the web scraping program:**
    ```
    python main.py
    ```

<br>

## Contribution

Contributions are welcome! Please fork the repository and create a pull request with your changes. Ensure that your code adheres to the project’s coding standards and includes appropriate tests.

<br>

## License

This project is licensed under the MIT License. See the [LICENSE](https://choosealicense.com/licenses/mit/) file for more details.

<br>

## Acknowledgements

I would like to acknowledge the following organizations and technologies for their contributions to this project:

- [**BeautifulSoup**](https://beautiful-soup-4.readthedocs.io/en/latest/): For providing powerful tools for web scraping and HTML parsing, enabling the extraction of detailed event data.
- [**Requests**](https://requests.readthedocs.io/en/latest/): For its robust HTTP capabilities, facilitating seamless interactions with web services.
- [**Pandas**](https://pandas.pydata.org/): For its extensive data manipulation and analysis features, which significantly streamline the handling of structured data.
- [**SMTP and Email Libraries**](https://docs.python.org/3/library/smtplib.html): For their comprehensive support in email handling, allowing the scraper to dispatch notifications and attachments effectively.
- [**Psycopg2**](https://www.psycopg.org/docs/): For enabling efficient interaction with PostgreSQL databases, ensuring secure and reliable data storage and retrieval.

Each of these tools has contributed to the functionality and efficiency of this project, and their ongoing development support is greatly appreciated.

<br>

### Disclaimer
The data extracted by the Music Events Web Scraper is solely for project showcasing purposes. It will not be sold to any third party, nor will it be used for any commercial activities beyond the scope of project demonstration and academic presentation. All data handling will adhere to ethical guidelines and respect privacy considerations.
