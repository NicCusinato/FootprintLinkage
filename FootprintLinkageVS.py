import streamlit as st
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time

# Install Chromium and ChromeDriver using sbase
@st.cache_resource
def install_chromium():
    """
    Install Chromium and ChromeDriver in Streamlit Cloud.
    """
    os.system("sbase install chromium")  # Install Chromium browser
    os.system("sbase install chromedriver")  # Install ChromeDriver for Selenium
    # Link ChromeDriver to the bin directory
    os.system("ln -s /home/appuser/venv/lib/python3.7/site-packages/seleniumbase/drivers/chromedriver /home/appuser/venv/bin/chromedriver")

_ = install_chromium()

# Function to set up Selenium WebDriver with Chrome
def setup_chrome_driver():
    """
    Set up Selenium WebDriver with Chromium for Streamlit Cloud.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.binary_location = "/usr/bin/chromium-browser"  # Path to Chromium
    driver = webdriver.Chrome(service=Service("/home/appuser/venv/bin/chromedriver"), options=chrome_options)
    return driver

# Function to perform the search automation
def search_footprint(driver, footprint_id):
    """
    Automate the search for a given FootprintId and return the resulting URL.
    """
    try:
        # Step 1: Open the website
        driver.get("https://search.miproducts.cimpress.io/home")
        time.sleep(1)

        # Step 2: Click on the tab to search by attributes
        nav_element = driver.find_element(By.XPATH, "//a[@id='ngb-nav-1']")
        nav_element.click()
        time.sleep(1)

        # Step 3: Click the input field
        input_field = driver.find_element(By.XPATH, "//div[10]/div[2]/input")
        input_field.click()

        # Step 4: Type the FootprintId
        input_field.clear()
        input_field.send_keys(str(footprint_id))
        input_field.send_keys(Keys.ENTER)

        # Wait for the results to load
        time.sleep(3)

        # Return the resulting URL
        return driver.current_url
    except Exception as e:
        st.error(f"Error processing FootprintId {footprint_id}: {e}")
        return None

# Main Streamlit app
def main():
    st.title("Footprint Search Automation with Chromium")
    st.write("Upload an Excel file with `FootprintId`s and automate the search process.")

    # File upload
    uploaded_file = st.file_uploader("Upload an Excel file with a column named 'FootprintId':", type=["xlsx"])

    if uploaded_file:
        # Read the uploaded Excel file
        df = pd.read_excel(uploaded_file)
        if "FootprintId" not in df.columns:
            st.error("The uploaded file must have a column named 'FootprintId'.")
            return
        
        footprint_ids = df["FootprintId"].dropna().unique()  # Get unique FootprintIds

        # Initialize Selenium WebDriver
        driver = setup_chrome_driver()

        # Process results
        results = []
        with st.spinner("Processing..."):
            for footprint_id in footprint_ids:
                st.write(f"Processing FootprintId: {footprint_id}")
                result_url = search_footprint(driver, footprint_id)
                results.append({"FootprintId": footprint_id, "ResultURL": result_url})

        # Close the browser
        driver.quit()

        # Convert results to DataFrame
        results_df = pd.DataFrame(results)

        # Display results in Streamlit
        st.write("Results:")
        st.dataframe(results_df)

        # Download results as Excel
        output_file = "footprint_results.xlsx"
        results_df.to_excel(output_file, index=False)
        with open(output_file, "rb") as f:
            st.download_button(
                label="Download Results as Excel",
                data=f,
                file_name="footprint_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

if __name__ == "__main__":
    main()
