import os
import http.cookiejar
import urllib.request
import json

SAVE_DIRECTORY = "images/" #The folder where the images get saved
#All expansions with their ID
EXPANSIONS = {
    "341": {"name": "Call of the Archons", "count": 370},
    "435": {"name": "Age of Ascension", "count": 370},
    "452": {"name": "Worlds Collide", "count": 415},
    "479": {"name": "Mass Mutation", "count": 422}
    }
#(Out-)Comment any languages you (don't) want to download
LANGUAGES = [
    {"code": "en-us", "folder": "english/"},
    {"code": "de-de", "folder": "german/"},
#    {"code": "es-es", "folder": "spanish/"},
#    {"code": "fr-fr", "folder": "french/"},
#    {"code": "it-it", "folder": "italian/"},
#    {"code": "pl-pl", "folder": "polish/"},
#    {"code": "pt-pt", "folder": "potuguese/"},
#    {"code": "th-th", "folder": "thai/"},
#    {"code": "zh-hans", "folder": "chinese-simplified/"},
#    {"code": "zh-hant", "folder": "chinese-traditional/"}
    ]

#Create folders for all selected languages and expansions
for lang in LANGUAGES:
    if not os.path.exists(SAVE_DIRECTORY + lang["folder"]): #if the folder doesn't exist, create it
        os.makedirs(SAVE_DIRECTORY + lang["folder"])
    for exp_id in EXPANSIONS:
        expansion = EXPANSIONS[exp_id]
        if not os.path.exists(SAVE_DIRECTORY + lang["folder"] + expansion["name"]):
            os.makedirs(SAVE_DIRECTORY + lang["folder"] + expansion["name"])

#Initialize URL opener
cj = http.cookiejar.CookieJar() #for handling all the cookies
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
opener.addheaders = [("User-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64;)")]

r = opener.open("https://www.keyforgegame.com/") # to get all the cookies

#Iterate over all languages. Sadly there is no other way to get the card names in another language.
for lang in LANGUAGES:
    opener.addheaders = [("Accept-Language", lang["code"])] #set the language to get translated card names

    #Iterate over all expansion to search for specific decks only
    for exp_id in EXPANSIONS:
        expansion = EXPANSIONS[exp_id]
        save_dir = SAVE_DIRECTORY + lang["folder"] + expansion["name"]

        #Quick check to see if the cards have already been downloaded
        card_count = len(os.listdir(save_dir))
        if card_count < expansion["count"]:
            cards_missing = True
        else:
            cards_missing = False
            print("==== Download of expansion {} in {} already completed ====".format(expansion["name"], lang["folder"]))

        #Go over new pages as long as cards are missing
        page_counter = 1
        while cards_missing:
                r = opener.open("https://www.keyforgegame.com/api/decks/?page={}&expansion={}&links=cards&page_size=50&ordering=-date".format(page_counter, exp_id)) #load a list of decks including links to all the cards
                decks_raw = r.read()

                decks = json.loads(decks_raw)

                for card in decks["_linked"]["cards"]:  #Get the info for every card
                        card_number = str(card["card_number"])
                        card_title = card["card_title"].replace(" ", "_").replace('"', "'").replace("?", "")
                        card_image = card["front_image"]
                        card_expansion = str(card["expansion"])
                        if(card_expansion != exp_id):   #Possible legacy card
                            if(card_expansion in EXPANSIONS):   #Only skip if we know that exp_id, otherwise it's an Anomaly
                                continue

                        filename = save_dir + "/" + card_number + "_" + card_title + ".png"    #local filename to save the image

                        if not os.path.exists(filename):    #Download file if not already exisiting
                                print("Downloading " + filename)
                                r = opener.open(card_image)
                                with open(filename, "wb") as f:
                                        f.write(r.read())
                        else:
                                print("Already exisiting image, skipping " + filename)

                #Check if all cards have been downloaded
                cards_missing = False
                expansion = EXPANSIONS[exp_id]
                card_count = len(os.listdir(save_dir))
                print("==== Downloaded {} out of {} images for expansion {} ====".format(card_count, expansion["count"], expansion["name"]))
                if card_count < expansion["count"]:
                        cards_missing = True

                page_counter += 1
