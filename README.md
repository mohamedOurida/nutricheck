# Nutricheck - take a photo of food and learn about it

**Note:** Nutricheck is a work in progress. Expect plenty of errors and bugs.




**End goal:** take a photo of food an learn about it (nutrition information, where it's from, recipes, etc).

**Status:** making a small application to collect large amounts of food images.

## What's in this repo?
TODO: document this better (will likely do a big refactor once the data engine for classification is fleshed out)

* `images/` - folder with misc images for the project
* `data_exploration/` - notebooks & data exploring the USDA FoodData Central data (this has info about the nutrition content of foods)
* `food_image_collector.py` - Streamlit-powered app that collects photos and uploads them to a Google Storage bucket and stores metadata in Google Sheets (these are private), see the workflow below.
* `save_to_gsheets.py` - Small utility script that saves a bunch of metadata about an uploaded image to a Google Sheet (this will likely move into a dedicated `utils/` folder later on.
* `utils.py` - Series of helper functions used in `food_image_collector.py`, for example, `upload_blod()`, a function that uploads a photo to Google Storage.
* `requirements.txt` - A text file with the dependency requirements for this project.



### Stage 1 (done)

Build food image collection app, need a way to store images at large scale, images: object storage (Google Storage), info about images: relational database (PostgreSQL).

### Stage 2 (done)

Build small prototype computer vision app to take a photo of ~100 different types of foods and return back their nutrition information (this'll be done via a public nutrition API, if you know of one, please let me know).

### Stage 3 (up to here)

Merge inputs to stage 1 and stage 2 into a database (start linking together the data flywheel, more images get taken, models get improved, more images, better models, more images, better models, etc).

### Stage 4

Upgrade stage 1, 2, 3 to work with world's 100 most commonly eaten foods (start with top of the Pareto curve and then start working backwards towards the tail).

### Stage 5

Repeat the above until almost every food you can eat is covered.
