import json

# Load the transformed data from the file
with open('transformed_reviews.json', 'r', encoding='utf-8') as f:
    transformed_data = json.load(f)

# Sort the products by the length of their reviews in descending order
sorted_data = sorted(transformed_data, key=lambda x: len(x['reviews']), reverse=True)

# Get the links of the top 10 products with the most reviews
top_10_links = [product['product_link'] for product in sorted_data[:10]]

# Write the links to a text file
with open('top_10_product_links.txt', 'w', encoding='utf-8') as file:
    file.write("Top 10 product links with the most reviews:\n")
    for link in top_10_links:
        file.write(f"{link}\n")

print("Top 10 product links have been written to 'top_10_product_links.txt'.")
