import json

# Read the original JSON data from the file
with open('amazon_reviews.json', 'r', encoding='utf-8') as f:
    original_data = json.load(f)

# Transform the data into the desired format
transformed_data = []
for link, reviews in original_data.items():
    try:
        # Ensure the link contains "/dp/"
        if "/dp/" in link:
            asin_part = link.split("/dp/")[1]
            # Extract ASIN before the next "/" or "?"
            asin = asin_part.split("/")[0].split("?")[0]
        else:
            raise ValueError(f"Invalid link format: {link}")

        # Append the transformed entry
        transformed_data.append({
            'product_link': link,
            'reviews': reviews,
            'asin': asin
        })
    except Exception as e:
        print(f"Error processing link {link}: {e}")

# Output the transformed data to the console
print(json.dumps(transformed_data, indent=2))

# Optionally, save the transformed data to a new file
with open('transformed_reviews.json', 'w', encoding='utf-8') as f:
    json.dump(transformed_data, f, indent=2)

print("Transformed data has been saved to transformed_reviews.json")
