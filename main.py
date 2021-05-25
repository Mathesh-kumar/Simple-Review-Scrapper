# Flipcart product review scrapping - python code file

# Import needed libraries
from flask import Flask, request, render_template  # Light weight WSGI web application framework
from urllib.request import urlopen  # Extensible library for opening URL's
from bs4 import BeautifulSoup  # Makes easy to scrap contents from web page
import requests  # Simple, elegant HTTP library

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
        productURL = "https://www.flipkart.com/search?q=" + productName  # URL to search on flipcart

        openedProductURL = urlopen(productURL)  # Request webpage from internet
        productPage = openedProductURL.read()  # Read content from the page (HTML code)
        openedProductURL.close()  # Cancel the connection with the web server
        beautyProductPage = BeautifulSoup(productPage, "html.parser")  # Parse web page as html

        allProducts = beautyProductPage.findAll("div", {"class": "_1AtVbE col-12-12"})  # Select all products
        del allProducts[0:3]  # Delete unwanted contents
        firstProduct = allProducts[0]  # Select first item only
        firstProductLink = "https://www.flipkart.com" + firstProduct.div.div.div.a['href']  # Select first item link

        #  openFirstProduct = urlopen(firstProductLink)  # Request webpage from internet
        #  firstProductPage = openFirstProduct.read()  # Read content from the page (HTML code)
        #  openFirstProduct.close()  # Cancel the connection with the web server
        #  beautyFirstProductPage = BeautifulSoup(firstProductPage, "html.parser")  # Parse web page as html

        # Instead of these upcoming two lines we can also use the above four lines
        firstProductPage = requests.get(firstProductLink)  # Request webpage from internet
        beautyFirstProductPage = BeautifulSoup(firstProductPage.text, "html.parser")  # Parse web page as html

        commentBoxes = beautyFirstProductPage.findAll("div", {"class": "_16PBlm"})  # Select all comments
        reviews = []  # List to store the comments

        # This for loop will iterate through each comments and retrieve all the information from it.
        # Information line Comment name, rating, heading, review
        for cBox in commentBoxes:
            try:
                name = cBox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text
            except:
                name = 'No Name'
            try:
                rating = cBox.div.div.div.div.text
            except:
                rating = 'No Rating'
            try:
                commentHead = cBox.div.div.div.p.text
            except:
                commentHead = 'No Comment Heading'
            try:
                commentTag = cBox.div.div.find_all('div', {'class': ''})
                customerComment = commentTag[0].div.text
            except:
                customerComment = 'No Customer Comment'
            reviewDictionary = dict(Product=productName, Name=name, Rating=rating, CommentHead=commentHead,
                                    Comment=customerComment)  # Store retrieved information as a dictionary
            reviews.append(reviewDictionary)  # Append each comment dictionary into reviews list
        return render_template('results.html', reviews=reviews)  # Show product reviews to the user
    else:  # If method==GET, show the index page to type product name
        return render_template('index.html')  # Show search bar page to the user


if __name__ == '__main__':  # Starting point of program - main function
    app.run(debug=True)  # Run app on local host
