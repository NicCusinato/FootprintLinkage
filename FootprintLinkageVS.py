import streamlit as st

"""
## Automate Footprint Searches with Selenium on Streamlit Cloud

Upload a list of FootprintIds to automate searches and collect results.
"""

with st.echo():
    import pandas as pd
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.core.os_manager import ChromeType

    @st.cache_resource
    def get_driver():
        """
        Set up Selenium WebDriver with Chromium.
        """
        options = Options()
        options.add_argument("--disable-gpu")
        options.add_argument("--headless")  # Run in headless mode
        return webdriver.Chrome(
            service=Service(
                ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
            ),
            options=options,
        )

    def search_footprint(driver, footprint_id):
        """
        Perform the search for a given FootprintId and return the resulting URL.
        """
        try:
            # Open the target website
            driver.get("https://search.miproducts.cimpress.io/home")

            # Click on "Search by Attributes" tab
            driver.find_element(By.XPATH, "//a[@id='ngb-nav-1']").click()

            # Find the input field and enter the FootprintId
            input_field = driver.find_element(By.XPATH, "//div[10]/div[2]/input")
            input_field.send_keys(str(footprint_id))
            input_field.send_keys(Keys.ENTER)

            # Wait for the results to load
            st.time.sleep(3)

            # Return the current URL
            return driver.current_url
        except Exception as e:
            st.error(f"Error processing FootprintId {footprint_id}: {e}")
            return None

    # Streamlit UI
    st.title("Footprint Search Automation")
    st.write("Upload an Excel file with FootprintIds to automate searches.")

    # File uploader
    uploaded_file = st.file_uploader("Upload an Excel file with a column named 'FootprintId':", type=["xlsx"])

    if uploaded_file:
        # Load the Excel file
        df = pd.read_excel(uploaded_file)
        if "FootprintId" not in df.columns:
            st.error("The uploaded file must have a column named 'FootprintId'.")
        else:
            # Initialize WebDriver
            driver = get_driver()

            # Perform searches
            results = []
            for footprint_id in df["FootprintId"].dropna().unique():
                st.write(f"Processing FootprintId: {footprint_id}")
                url = search_footprint(driver, footprint_id)
                results.append({"FootprintId": footprint_id, "ResultURL": url})

            # Close the browser
            driver.quit()

            # Display results
            results_df = pd.DataFrame(results)
            st.write(results_df)

            # Allow downloading results as Excel
            output_file = "footprint_results.xlsx"
            results_df.to_excel(output_file, index=False)
            with open(output_file, "rb") as f:
                st.download_button(
                    label="Download Results as Excel",
                    data=f,
                    file_name="footprint_results.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
