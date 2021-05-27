# Flipcart product review scrapping - python code file

# Import needed libraries
from flask import Flask, request, render_template  # Light weight WSGI web application framework
from urllib.request import urlopen  # Extensible library for opening URL's
from bs4 import BeautifulSoup  # Makes easy to scrap contents from web page
# import requests  # Simple, elegant HTTP library
import pymongo  # Contains tools for interacting with MongoDB database from Python

app = Flask(__name__)  # Flask app initialization

"""
review_scrapping
----------------
Function to scrap reviews of a specified product from the flipcart page
"""
@app.route('/', methods=['POST', 'GET'])  # Route with POST & GET methods
def review_scrapping():  # Function to scrap contents
    if request.method == 'POST':  # If method==POST, scrap contents from flipcart page & display
        productName = request.form['content'].replace(" ", "")  # Product name to search

        try:
            (USER_NAME, PASSWORD, DB_NAME) = ("root", "root", "flipcart")  # Credentials for mongodb atlas connection with database name
            CONNECTION_URL = f"mongodb+srv://{USER_NAME}:{PASSWORD}@flipcartreview.t8qf3.mongodb.net/{DB_NAME}?ssl=true&ssl_cert_reqs=CERT_NONE"
            client = pymongo.MongoClient(CONNECTION_URL)  # Establish connection with mongodb server
            dataBase = client[DB_NAME]  # Create DB / Use existing database
            flipcartReviews = dataBase[productName].find({}, {'_id': 0})  # Search whether product reviews already present in the database

            reviews = []  # List to store the comments
            for review in enumerate(flipcartReviews):  # Iterate through each review. Since flipcartReviews is an mongodb cursor object
                reviews.append(review[1])  # Append each review to the reviews list

            if len(reviews) > 0:  # If the review count >0 show output to thee user
                return render_template('results.html', reviews=reviews)  # Show product reviews to the user
            else:  # else search in flipcart site
                productURL = "https://www.flipkart.com/search?q=" + productName  # URL to search on flipcart

                openedProductURL = urlopen(productURL)  # Request webpage from internet
                productPage = openedProductURL.read()  # Read content from the page (HTML code)
                openedProductURL.close()  # Cancel the connection with the web server
                beautyProductPage = BeautifulSoup(productPage, "html.parser")  # Parse web page as html

                allProducts = beautyProductPage.findAll("div", {"class": "_13oc-S"})  # Select all products
                firstProduct = allProducts[0]  # Select first product from the list of products
                firstProductLink = "https://www.flipkart.com" + firstProduct.div.div.a['href']  # Select first product link

                openFirstProduct = urlopen(firstProductLink)  # Request first product webpage from internet
                firstProductPage = openFirstProduct.read()  # Read content from the page (HTML code)
                openFirstProduct.close()  # Cancel the connection with the web server
                beautyFirstProductPage = BeautifulSoup(firstProductPage, "html.parser")  # Parse web page as html

                # Instead of above four lines we can also use these upcoming two lines
                # firstProductPage = requests.get(firstProductLink)  # Request webpage from internet
                # beautyFirstProductPage = BeautifulSoup(firstProductPage.text, "html.parser")  # Parse web page as html

                commentBoxes = beautyFirstProductPage.findAll("div", {"class": "col _2wzgFH"})  # Select all comments

                # This for loop will iterate through each comments and retrieve all the information from it.
                # Information line Comment name, rating, heading, review
                for cBox in commentBoxes:
                    try:
                        name = cBox.find_all("p", {"class": "_2sc7ZR _2V5EHH"})[0].text  # Name of the customer
                    except:
                        name = 'No Name'
                    try:
                        rating = cBox.find_all("div", {"class": "_3LWZlK _1BLPMq"})[0].text  # Rating given by the customer
                    except:
                        rating = 'No Rating'
                    try:
                        commentHead = cBox.find_all("p", {"class": "_2-N8zT"})[0].text  # Review heading given by the customer
                    except:
                        commentHead = 'No Comment Heading'
                    try:
                        customerComment = cBox.find_all("div", {"class": "t-ZTKy"})[0].div.text  # Review by customer
                        customerComment = customerComment.replace("READ MORE", "")
                    except:
                        customerComment = 'No Customer Comment'

                    reviewDictionary = dict(Product=productName, Name=name, Rating=rating, CommentHead=commentHead,
                                            Comment=customerComment)  # Store retrieved information as a dictionary
                    reviews.append(reviewDictionary)  # Append each review as dictionary into reviews list

                collection = dataBase[productName]  # Create a collection
                collection.insert_many(reviews)  # Insert all the reviews into the collection
                return render_template('results.html', reviews=reviews)  # Show product reviews to the user
        except:
            return "Something went wrong"
    else:  # If method==GET, show the index page to type product name
        return render_template('index.html')  # Show search bar page to the user


if __name__ == '__main__':  # Starting point of program - main function
    app.run(debug=True)  # Run app on local host
