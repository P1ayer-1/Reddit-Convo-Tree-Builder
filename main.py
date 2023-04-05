from scrapyd_api import ScrapydAPI
import os


SUBREDDIT = "amitheasshole"


CSV_DIR = "csv_files"

csv_files = [CSV_DIR + "/" + f for f in os.listdir(CSV_DIR) if f.endswith(".csv")]



scrapyd = ScrapydAPI("http://localhost:6800/")
for csv_file in csv_files:

    # use csv name as output file name
    settings = {'FEED_URI': "scraped_data/{}_{}.jsonl".format(SUBREDDIT, csv_file.split("/")[-1].split(".")[0])}

    
    job_id = scrapyd.schedule("reddit_scraper_OA", "oldreddit", csv_file=csv_file, settings=settings)
