import os
import json
import requests
from bs4 import BeautifulSoup

# Set up file and folder paths
folderPath = os.path.join(os.getenv('LOCALAPPDATA'), "AmazonPriceTracker")
filePath = os.path.join(folderPath, 'trackedlinks.json')

# Create the folder if it doesn't exist
os.makedirs(folderPath, exist_ok=True)

def loadData():
    if os.path.exists(filePath):
        with open(filePath, "r") as file:
            return json.load(file)
    return []

def saveData(data):
    with open(filePath, "w") as file:
        json.dump(data, file, indent=4)

def printMenu():
    print("What do you want to do?")
    print("1) Add new amazon link for tracking")
    print("2) Check the prices for existing items")

def fetchPrice(link):
    targetLink = link

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "en-US,en;q=0.9"
    }

    response = requests.get(targetLink, headers=headers)
    html = response.text

    soup = BeautifulSoup(html, "html.parser")

    priceSpan = soup.find("span", {"class": "aok-offscreen"})

    if priceSpan:
        rawText = priceSpan.text.strip()  # Example: "$25.98 with 7 percent savings"
        priceText = rawText.split(" ")[0]    # Extract "$25.98"
        price = priceText.replace("$", "")    # Extract "25.98" for float conversion

        try:
            price = float(price)

            return price
        except ValueError:
            print("❌ Couldn't convert extracted price to float.")
    else:
        print("❌ Price not found.")

def addProduct(data):
    targetLink = input("Please provide the product link: ")
    price = fetchPrice(targetLink)
    
    if price is None:
        print("❌ Failed to extract price. Cannot add product.")
        return
    
    print(f"✅ Extracted Price: ${price:.2f}")

    targetPrice = input("Please set your target price: ")

    try:
        targetPrice = float(targetPrice)
        if targetPrice > 0:
            trackedProductInfo = {
                "link": targetLink,
                "price": price,
                "target_price": targetPrice
            }

            data.append(trackedProductInfo)
            saveData(data)

            print("✅ Product information saved for tracking!")
        else:
            print("❌ The price cannot be negative or zero.")
    except ValueError:
        print("❌ Invalid price. Please enter a number.")

def checkPrices(data):

    for trackedProductInfo in data:
        print(f"\nChecking product: {trackedProductInfo['link']}")
        try:
            currentPrice = fetchPrice(trackedProductInfo['link'])

            print(f"Current price: ${currentPrice:.2f}")

            if currentPrice <= trackedProductInfo.get("target_price", float('inf')):
                print("🎉 Price is at or below your target! Time to buy!")
            else:
                print("❌ Price is still above your target.")

            trackedProductInfo["price"] = currentPrice
        except Exception as e:
            print(f"❌ Error checking price: {e}")
def main():
    data = loadData()

    while True:
        printMenu()
        choice = input("> ")

        if choice == "1":
            addProduct(data)
        elif choice == "2":
            checkPrices(data)
        else:
            print("❌ Invalid choice.")

if __name__ == "__main__":
    main()
