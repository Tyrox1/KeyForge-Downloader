import os, sys, requests, json, time

SAVE_DIRECTORY = "images"  # The folder where the images get saved

# All expansions with their ID
# If you don't want to download a specific expansion, reduce the count to 0, don't comment the whole line, it will crash otherwise
EXPANSIONS = {
    "341": {"name": "Call of the Archons", "count": 370},
    "435": {"name": "Age of Ascension", "count": 370},
    "452": {"name": "Worlds Collide", "count": 415},
    "479": {"name": "Mass Mutation", "count": 431},  # 421 "normal" cards, 7 versions of Dark Æmber Vault + 3 gigantic cards
    "496": {"name": "Dark Tidings", "count": 429}
    }

# (Out-)Comment any languages you (don't) want to download
LANGUAGES = [
    {"code": "en-us", "folder": "english"},
    {"code": "de-de", "folder": "german"},
    #{"code": "es-es", "folder": "spanish"},
    #{"code": "fr-fr", "folder": "french"},
    #{"code": "it-it", "folder": "italian"},
    #{"code": "pl-pl", "folder": "polish"},
    #{"code": "pt-pt", "folder": "potuguese"},
    #{"code": "th-th", "folder": "thai"},
    #{"code": "zh-hans", "folder": "chinese-simplified"},
    #{"code": "zh-hant", "folder": "chinese-traditional"},
    #{"code": "ko-ko", "folder": "korean"}
    ]

# Create folders for all selected languages and expansions
for lang in LANGUAGES:
    if not os.path.exists(f"{SAVE_DIRECTORY}/{lang['folder']}"):  # if the folder doesn't exist, create it
        os.makedirs(f"{SAVE_DIRECTORY}/{lang['folder']}")
    for exp_id in EXPANSIONS:
        expansion = EXPANSIONS[exp_id]
        if not os.path.exists(f"{SAVE_DIRECTORY}/{lang['folder']}/{expansion['name']}"):
            os.makedirs(f"{SAVE_DIRECTORY}/{lang['folder']}/{expansion['name']}")

session = requests.Session()
session.get("https://www.keyforgegame.com/")    # to get all the cookies
session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64;)"})

# Iterate over all languages. Sadly there is no other way to get the card names in another language.
for lang in LANGUAGES:
    session.headers.update({"Accept-Language": lang["code"]})  # set the language to get translated card names

    # Iterate over all expansion to search for specific decks only
    for exp_id in EXPANSIONS:
        expansion = EXPANSIONS[exp_id]
        save_dir = f"{SAVE_DIRECTORY}/{lang['folder']}/{expansion['name']}"

        # Quick check to see if the cards have already been downloaded
        card_count = len(os.listdir(save_dir))
        if card_count < expansion["count"]:
            cards_missing = True
        else:
            cards_missing = False
            print(f"==== Download of expansion {expansion['name']} in {lang['folder']} already completed ====")

        # Go over new pages as long as cards are missing
        page_counter = 1
        while cards_missing:
            # load a list of decks including links to all the cards
            r = session.get(f"https://www.keyforgegame.com/api/decks/?page={page_counter}&expansion={exp_id}&links=cards&page_size=50&ordering=-date")

            if r.status_code == 429:  # Overloaded the API
                print("[!] Too many requests, waiting 15 seconds.")
                time.sleep(15)
                continue  # try again

            decks_raw = r.text

            decks = json.loads(decks_raw)

            for card in decks["_linked"]["cards"]:  # Get the info for every card
                card_number = str(card["card_number"])
                card_title = card["card_title"].replace(" ", "_").replace('"', "'").replace("?", "")
                card_image = card["front_image"]
                card_expansion = str(card["expansion"])
                card_type = card["card_type"]
                card_house = card["house"].replace(" ", "_")

                # Checking for certain unusual card patterns

                if card_expansion != exp_id:  # Possible legacy/anomaly card
                    if card_expansion in EXPANSIONS:  # Legacy, skip card
                        print("  Legacy card, skipping")
                        continue
                    elif card["is_anomaly"]:  # Anomaly, continue processing
                        pass
                    else:
                        print("[!] An unknown error occured, please report an issue on Github with the following information:")
                        print("==== Begin Bugreport ====")
                        print(card)
                        print("==== End Bugreport ====")
                        sys.exit(1)

                if card_type == "Creature2":  # Gigantic card second half
                    card_title += "_gigantic"

                if expansion["name"] == "Mass Mutation" and card_number == "001":  # Dark Æmber Vault
                    card_title = f"{card_title}_{card_house}"

                if card["rarity"] == "Evil Twin":
                    card_title += "_EvilTwin"

                filename = f"{save_dir}/{card_number}_{card_title}.png"  # local filename to save the image

                if not os.path.exists(filename):  # Download file if not already existing
                    print(f"  Downloading {filename}")
                    ri = session.get(card_image)
                    with open(filename, 'wb') as f:
                        f.write(ri.content)
                else:
                    print(f"  Already existing image, skipping {filename}")

            # Check if all cards have been downloaded
            cards_missing = False
            expansion = EXPANSIONS[exp_id]
            card_count = len(os.listdir(save_dir))
            print(f"==== Downloaded {card_count} out of {expansion['count']} images for expansion {expansion['name']} ====")
            if card_count < expansion["count"]:
                cards_missing = True

            page_counter += 1
