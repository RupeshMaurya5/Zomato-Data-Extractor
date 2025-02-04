import streamlit as st
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time

st.title("🍽 Zomato Data Extractor")

# User input for Zomato URL
url = st.text_input("Enter Zomato URL:")

# Select fields to scrape
fields = st.multiselect("Select fields to extract:", ["Restaurant Name", "URL", "Location"])

if st.button("Scrape Data"):
    if url:
        s = webdriver.Chrome()
        s.get(url)
        time.sleep(6)

        html = s.page_source
        soup = BeautifulSoup(html, "html.parser")

        restaurants = soup.find_all("div", class_="jumbo-tracker")
        
        res_names, res_urls, res_locations = [], [], []

        base_url = "https://www.zomato.com"

        for res in restaurants:
            name = res.find("h4").text.strip() if "Restaurant Name" in fields else ""
            res_url = base_url + res.find("a")["href"] if "URL" in fields else ""
            location = res.find("div", class_="sc-clNaTc vNCcy").text.strip() if "Location" in fields else ""

            if name:
                res_names.append(name)
                res_urls.append(res_url)
                res_locations.append(location)

        df = pd.DataFrame({"Name": res_names, "URL": res_urls, "Location": res_locations})
        st.dataframe(df)

        # Download button
        st.download_button("Download Excel", df.to_csv(index=False), "zomato_data.csv", "text/csv")

        s.quit()
    else:
        st.warning("Please enter a valid Zomato URL.")
