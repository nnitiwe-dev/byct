import sqlite3
import time
from bs4 import BeautifulSoup
import requests

# Initialize the database
db_conn = sqlite3.connect('recipes.db')
db_cursor = db_conn.cursor()
db_cursor.execute('''CREATE TABLE IF NOT EXISTS recipes (
                         title TEXT, 
                         ingredients TEXT, 
                         rating REAL
                     )''')

# Function to extract recipe details from a given URL
def fetch_recipe_details(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Retrieve the recipe title
    recipe_title = soup.find('h1', class_='headline heading-content').text.strip()

    # Retrieve the ingredients
    ingredient_tags = soup.find_all('span', class_='ingredients-item-name')
    ingredient_list = [tag.text.strip() for tag in ingredient_tags]
    ingredients_str = ', '.join(ingredient_list)

    # Retrieve the rating
    rating_tag = soup.find('span', class_='review-star-text')
    recipe_rating = None
    if rating_tag:
        rating_text = rating_tag.text.strip()
        recipe_rating = float(rating_text.split()[1])  # Assumes the format is "Rating: X.Y stars"

    return recipe_title, ingredients_str, recipe_rating

# Main function to gather recipe links and scrape their details
def scrape_main_page():
    main_page_url = 'https://www.allrecipes.com/recipes/'
    response = requests.get(main_page_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract all recipe links
    link_tags = soup.find_all('a', href=True)
    recipe_urls = [tag['href'] for tag in link_tags if '/recipe/' in tag['href']]

    # Scrape each recipe page
    for recipe_url in recipe_urls:
        try:
            title, ingredients, rating = fetch_recipe_details(recipe_url)
            print(f'Successfully scraped: {title}')

            # Store the scraped data in the database
            db_cursor.execute('INSERT INTO recipes (title, ingredients, rating) VALUES (?, ?, ?)',
                              (title, ingredients, rating))
            db_conn.commit()
        except Exception as error:
            print(f'Error scraping {recipe_url}: {error}')

# Function to repeatedly scrape the main page at specified intervals
def continuous_scraping(interval_minutes):
    while True:
        scrape_main_page()
        print(f"Waiting {interval_minutes} minutes before the next scrape...")
        time.sleep(interval_minutes * 60)

if __name__ == '__main__':
    try:
        continuous_scraping(10)
    except KeyboardInterrupt:
        print("Scraping process interrupted by the user.")
    finally:
        db_conn.close()
        print('Scraping process completed.')
