# KeyForge-Downloader

### Project Summary
Tool to download PNG image files of cards from all printed sets.

It currently supports Call of the Archons, Age of Ascension, Worlds Collide, Mass Mutation and Dark Tidings.

### Instructions
1. Make sure, python package `requests` is installed. If not install via `pip install requests` or `pip install -r requirements.txt`.
2. In a code editor of your choice, open the file **downloader.py**.  DO NOT double-click on the file or it will run the script.
3. On rows 7+ you can find all expansions that will be downloaded. If you don't want the images from a specific expansion, set the count to 0. Don't comment the line, otherwise the script will crash when it encounters a Legacy card.
4. On rows 16+ select the languages of cards that you would like to download.  To do so, comment out the languages you don't want. 
5. Double click to run the file **downloader.py**.
6. Once the script has run, you will have a new folder *images* that will hold the image files for all cards.
