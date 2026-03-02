import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import os

def get_product_id(url):
    # Extract product ID from URL using regex
    match = re.search(r"/([A-Z0-9]{10})(?:[/?]|$)", url)
    return match.group(1) if match else "Unknown"

def scrape_amazon_reviews(url, max_reviews=80):
    # Set up the Selenium driver (e.g., Chrome)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode (no UI)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(2)  # Give the page time to load

    reviews = []
    page = 1

    while len(reviews) < max_reviews:
        print(f"Scraping page {page}...")

        # Parse the current page content
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Select the review elements
        review_elements = soup.select(".review-text-content span")
        if not review_elements:
            print("No more reviews found or unable to locate reviews.")
            break

        for review in review_elements:
            reviews.append(review.get_text(strip=True))
            # Stop if we have reached the maximum number of reviews
            if len(reviews) >= max_reviews:
                break

        # Try to go to the next page if we need more reviews
        if len(reviews) < max_reviews:
            try:
                next_page = driver.find_element(By.CSS_SELECTOR, "li.a-last a")
                next_page.click()
                page += 1
                time.sleep(2)  # Wait for the new page to load
            except Exception as e:
                print("No more pages or unable to navigate to the next page.")
                break

    driver.quit()
    return reviews

def check_product_id_in_file(product_id, filename):
    # Check if the product ID is in the file
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            if product_id in f.read():
                return True
    return False

# Function to save reviews to a text file, appending only if product ID is new
def save_reviews_to_file(reviews, product_id, filename="amazon_review.txt"):
    # Check if product ID already exists in file
    if check_product_id_in_file(product_id, filename):
        print(f"Product ID {product_id} already exists in {filename}. Skipping append.")
        return

    with open(filename, "a", encoding="utf-8") as f:  # Open in append mode
        # Write product ID and reviews in the file
        f.write(f"\nProduct ID: {product_id}\n")
        f.write("=" * 50 + "\n\n")

        for index, review in enumerate(reviews, start=1):
            f.write(f"Review {index}:\n")
            f.write(review + "\n")
            f.write("-" * 50 + "\n")  # Separator line for uniform format
    print(f"Reviews for Product ID {product_id} appended to {filename}")

# Example usage:
url = "https://www.amazon.in/Logitech-G435-Lightspeed-Bluetooth-Wireless/dp/B09GFYV9YJ/ref=pd_ci_mcx_mh_mcx_views_0_title?pd_rd_w=rwcuN&content-id=amzn1.sym.fa0aca50-60f7-47ca-a90e-c40e2f4b46a9%253Aamzn1.symc.ca948091-a64d-450e-86d7-c161ca33337b&pf_rd_p=fa0aca50-60f7-47ca-a90e-c40e2f4b46a9&pf_rd_r=M1GFMMBENV39A7F0ABB3&pd_rd_wg=nEBXo&pd_rd_r=bed8ac38-bd70-4a50-a61d-99a06b84f975&pd_rd_i=B09GFYV9YJ"  # replace with your product review page URL
product_id = get_product_id(url)
reviews = scrape_amazon_reviews(url, max_reviews=80)
save_reviews_to_file(reviews, product_id)
