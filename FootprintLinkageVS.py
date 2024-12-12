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
    Set up Selenium WebDriver without headless mode.
    """
    chrome_options = Options()
    # Remove the headless option to allow the browser to be visible
    chrome_options.add_argument("--start-maximized")  # Start browser maximized

    # Path to ChromeDriver
    service = Service("/path/to/chromedriver")  # Replace with your ChromeDriver path
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def search_footprint(driver, footprint_id):
    """
    Automate the search for a given footprintId and return the resulting URL.
    """
    try:
        # Step 1: Open the website
        driver.get("https://search.miproducts.cimpress.io/home")
        time.sleep(1)

        # Step 2: Click on the tab to search for footprints
        nav_element = driver.find_element(By.XPATH, "//a[@id='ngb-nav-1']")
        nav_element.click()

        # Step 3: Click the input field
        input_field = driver.find_element(By.XPATH, "//div[10]/div[2]/input")
        input_field.click()

        # Step 4: Type the footprintId
        input_field.clear()
        input_field.send_keys(str(footprint_id))

        # Step 5: Press Enter
        input_field.send_keys(Keys.ENTER)

        # Wait for the results to load
        time.sleep(3)

        # Return the resulting URL
        return driver.current_url
    except Exception as e:
        st.error(f"Error processing FootprintId {footprint_id}: {e}")
        return None

def main():
    st.title("Footprint Search Automation")
    st.write("Upload an Excel file with `FootprintId`s to automate the search process.")

    # File upload
    uploaded_file = st.file_uploader("Upload an Excel file with FootprintId column:", type=["xlsx"])

    if uploaded_file:
        # Read the uploaded Excel file
        df = pd.read_excel(uploaded_file)
        if "FootprintId" not in df.columns:
            st.error("The uploaded file must have a column named 'FootprintId'.")
            return
        
        footprint_ids = df["FootprintId"].dropna().unique()  # Get unique FootprintIds

        # Initialize Selenium WebDriver
        driver = setup_driver()

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
