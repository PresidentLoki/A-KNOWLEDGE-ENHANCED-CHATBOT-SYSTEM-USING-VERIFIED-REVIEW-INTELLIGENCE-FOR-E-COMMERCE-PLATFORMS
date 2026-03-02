import requests
from bs4 import BeautifulSoup
import time

def scrape_amazon_reviews(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US, en;q=0.5"
    }

    reviews = []
    page = 1

    for i in range(10):
        print(f"Scraping page {page}...")
        
        # Add parameters for pagination
        paginated_url = f"{url}&pageNumber={page}"
        response = requests.get(paginated_url, headers=headers)

        if response.status_code != 200:
            print("Failed to retrieve data.")
            break

        soup = BeautifulSoup(response.content, "html.parser")

        # Find review elements
        review_elements = soup.select(".review-text-content span")
        if not review_elements:
            print("No more reviews found.")
            break

        for review in review_elements:
            reviews.append(review.get_text(strip=True))

        page += 1
        time.sleep(2)  # Avoid sending too many requests quickly

    return reviews

# Function to save reviews to a text file with numbering and uniform format
def save_reviews_to_file(reviews, filename="amazon_reviewsss.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        for index, review in enumerate(reviews, start=1):
            f.write(f"Review {index}:\n")
            f.write(review + "\n")
            f.write("-" * 50 + "\n")  # Separator line for uniform format
    print(f"Reviews saved to {filename}")

# Example usage:
url = "https://www.amazon.in/Pigeon-Toaster-Without-Rotisserie-Grilling/dp/B01NCPFE7R/ref=pd_ci_mcx_mh_mcx_views_1_image?pd_rd_w=naAz1&content-id=amzn1.sym.529d03fa-575b-4f2b-a4d6-0c02eabf0a7e%3Aamzn1.symc.45dc5f4c-d617-4dba-aa26-2cadef3da899&pf_rd_p=529d03fa-575b-4f2b-a4d6-0c02eabf0a7e&pf_rd_r=EESP455F30J15ESS4EPW&pd_rd_wg=q8WtA&pd_rd_r=9228eddc-758d-4d11-9507-b8549aba556f&pd_rd_i=B01NCPFE7R"  # replace with your product review page URL
reviews = scrape_amazon_reviews(url)
save_reviews_to_file(reviews)
