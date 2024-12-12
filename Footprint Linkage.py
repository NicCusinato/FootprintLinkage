import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

def setup_driver():
    """
    Set up Selenium WebDriver with headless Chrome for Streamlit Cloud.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--start-maximized")

    # Path to ChromeDriver (Streamlit Cloud automatically uses the correct PATH)
    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def search_footprint(driver, footprint_id):
    """
    Automate the search for a given footprintId and return the resulting URL.
    """
    try:
        # Open the website
        driver.get("https://search.miproducts.cimpress.io/home")

        # Click on the tab to search for footprints
        driver.find_element(By.ID, "ngb-nav-1").click()
        time.sleep(1)  # Adjust delay if necessary

        # Click the input field
        driver.find_element(By.CSS_SELECTOR, ".row:nth-child(10) .form-control").click()

        # Type the footprintId
        search_field = driver.find_element(By.XPATH, "//div[10]/div[2]/input")
        search_field.clear()
        search_field.send_keys(str(footprint_id))

        # Press Enter
        search_field.send_keys(Keys.ENTER)

        # Wait for the results to load (adjust timing as needed)
        time.sleep(3)

        # Get and return the current URL
        return driver.current_url
    except Exception as e:
        st.error(f"Error processing FootprintId {footprint_id}: {e}")
        return None

def main():
    st.title("Footprint Search Automation Tool")
    st.write("Upload an Excel file with `FootprintId`s and fetch search results.")

    # File upload
    uploaded_file = st.file_uploader("Upload an Excel file with FootprintId column:", type=["xlsx"])

    if uploaded_file:
        # Read the uploaded Excel file
        df = pd.read_excel(uploaded_file)
        if "FootprintId" not in df.columns:
            st.error("The uploaded file must have a column named 'FootprintId'.")
            return
        
        footprint_ids = df["FootprintId"].dropna().unique()  # Get unique FootprintIds

        # Display the input IDs
        st.write(f"Found {len(footprint_ids)} FootprintId(s):")
        st.write(footprint_ids)

        # Initialize Selenium WebDriver
        driver = setup_driver()

        # Process results
        results = []
        with st.spinner("Fetching results..."):
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
