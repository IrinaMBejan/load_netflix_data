import os
import time
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from syftbox.lib import Client, SyftPermission
from pathlib import Path

NETFLIX_FILE = "NetflixViewingActivity.csv"

class NetflixFetcher:
    def __init__(self, output_dir:str=None):
        """Initialize the downloader with environment variables."""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Create handler and formatter
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        
        # Add the handler to the logger
        self.logger.addHandler(console_handler)

        self.logger.info("Initializing Netflix Fetcher")

        self.email = os.getenv("NETFLIX_EMAIL")
        self.password = os.getenv("NETFLIX_PASSWORD")
        self.profile = os.getenv("NETFLIX_PROFILE")
        self.output_dir = output_dir
        self.driver_path = os.getenv("CHROMEDRIVER_PATH")
        self.csv_name = NETFLIX_FILE
        self.driver = None

    def setup_driver(self):
        """Set up the Chrome WebDriver."""
        chrome_options = Options()

        if isinstance(self.output_dir, Path):
            self.output_dir = str(self.output_dir)
        if not os.path.isdir(self.output_dir):
            raise ValueError(f"Invalid output directory: {self.output_dir}")

        if isinstance(self.driver_path, Path):
            self.driver_path = str(self.driver_path)
        # if not os.path.isfile(self.driver_path):
        #     raise FileNotFoundError(f"ChromeDriver not found at: {self.driver_path}")

        prefs = {
            "download.default_directory": self.output_dir,
            "download.prompt_for_download": False,
        }

        self.logger.info("Downloading Netflix Viewing Activity to %s", self.output_dir)

        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_service = Service(self.driver_path)
        self.driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

    def login(self):
        """Log in to Netflix."""
        if self.email == "<your-netflix-email@provider.com>" or self.profile == "<profile-name>" or self.password == "<your-password>":
            raise Exception("[!] Error: Need to setup Netflix Credential! Edit .env file.")

        print(f"🍿 Downloading Netflix Activity for: {self.email}, Profile {self.profile}")
        self.driver.get("https://www.netflix.com/login")
        email_input = self.driver.find_element(By.NAME, "userLoginId")
        password_input = self.driver.find_element(By.NAME, "password")
        email_input.send_keys(self.email)
        password_input.send_keys(self.password)
        print(">> Logging In")
        password_input.send_keys(Keys.ENTER)
        time.sleep(3)

    def switch_profile(self):
        """Switch to the specified Netflix profile."""
        print(">> Switching Profiles")
        self.driver.get(f"https://www.netflix.com/SwitchProfile?tkn={self.profile}")
        time.sleep(3)

    def download_viewing_activity(self):
        """Download the viewing activity for the current profile."""
        print(">> Getting Viewing Activity")
        self.driver.get("https://www.netflix.com/viewingactivity")
        time.sleep(3)
        self.driver.find_element(By.LINK_TEXT, "Download all").click()
        time.sleep(10)
        self.rename_downloaded_file()

    def rename_downloaded_file(self):
        """Rename the downloaded file into a subfolder with the date and include datetime in the name."""
        print(">> Renaming downloaded file")
        downloaded_file = None

        # Wait until the file appears in the output directory
        for _ in range(20):  # Poll for 20 seconds
            files = os.listdir(self.output_dir)
            for file in files:
                if os.path.basename(file) == self.csv_name:  # Assuming Netflix downloads a CSV file
                    downloaded_file = file
                    break
            if downloaded_file:
                break

        if not downloaded_file:
            self.logger.info("Download file not found. Please check the download directory.")


    def close(self):
        """Close the WebDriver."""
        if self.driver:
            self.driver.quit()

    def run(self):
        """Execute the full routine."""
        try:
            self.setup_driver()
            self.login()
            self.switch_profile()
            self.download_viewing_activity()
        finally:
            self.close()

# Create a folder called "datasets/netflix" to store the downloaded file
client = Client.load()

client_path = client.my_datasite
output_folder = "datasets/netflix"
output_path = client_path / output_folder
output_path.mkdir(parents=True, exist_ok=True)

downloader = NetflixFetcher(output_path)
downloader.run()

# Validate the file exists after download
file_path = os.path.join(output_path, NETFLIX_FILE)
if not os.path.exists(file_path):
    raise FileNotFoundError(f"Netflix viewing history file was not created: {file_path}")
