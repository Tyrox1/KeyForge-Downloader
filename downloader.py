import os
import http.cookiejar
import urllib.request
import json

SAVE_DIRECTORY = "images/" #The folder where the images get saved
LANGUAGES = [{"code": "en-us", "folder": "en/"}, {"code": "de-de", "folder": "de/"}] #Languages you want to download, choose from the following list:
#[{"code": "en-us", "folder": "en/"}, {"code": "de-de", "folder": "de/"}, {"code": "es-es", "folder": "es/"}, {"code": "fr-fr", "folder": "fr/"}, {"code": "it-it", "folder": "it/"}, {"code": "pl-pl", "folder": "pl/"}, {"code": "zh-hans", "folder": "chi-sim/"}, {"code": "zh-hant", "folder": "chi-trad/"}]

for lang in LANGUAGES:
    if not os.path.exists(SAVE_DIRECTORY + lang["folder"]): #if the folder doesn't exist, create it
        os.makedirs(SAVE_DIRECTORY + lang["folder"])

cj = http.cookiejar.CookieJar() #for handling all the cookies
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
opener.addheaders = [("User-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64;)")]

r = opener.open("https://www.keyforgegame.com/") # to get all the cookies


for lang in LANGUAGES:
    opener.addheaders = [("Accept-Language", lang["code"])] #set the language to get translated card names

    page_counter = 1
    while len(os.listdir(SAVE_DIRECTORY + lang["folder"])) < 370: #currently there are 370 released cards
        r = opener.open("https://www.keyforgegame.com/api/decks/?page=" + str(page_counter) + "&links=cards") #load a list of decks including links to all the cards
        decks_raw = r.read()

        decks = json.loads(decks_raw)

        for card in decks["_linked"]["cards"]:  #get the info for every card
            card_number = str(card["card_number"])
            card_title = card["card_title"].replace(" ", "_")
            card_image = card["front_image"]

            filename = SAVE_DIRECTORY + lang["folder"] + card_number + "_" + card_title + ".png"    #local filename to save the image

            if not os.path.exists(filename):    #download file if not already exisiting
                print("Downloading " + filename)
                r = opener.open(card_image)
                with open(filename, "wb") as f:
                    f.write(r.read())
            else:
                print("Already exisiting image, skipping " + filename)

        print("==== Downloaded " + str(len(os.listdir(SAVE_DIRECTORY + lang["folder"]))) + " images already ====")
        page_counter += 1
            
