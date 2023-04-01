from scrapyd_api import ScrapydAPI


SUBREDDIT = "amitheasshole"

csv_files = [
    "csv_files/split_csv_0.csv",
    "csv_files/split_csv_1.csv",
    "csv_files/split_csv_2.csv",
    "csv_files/split_csv_3.csv",
    "csv_files/split_csv_4.csv",
    "csv_files/split_csv_5.csv",
    "csv_files/split_csv_6.csv",
    "csv_files/split_csv_7.csv",
]



scrapyd = ScrapydAPI("http://localhost:6800/")
for csv_file in csv_files:

    # use csv name as output file name
    settings = {'FEED_URI': "scraped_data/{}_{}.jsonl".format(SUBREDDIT, csv_file.split("/")[-1].split(".")[0])}

    
    job_id = scrapyd.schedule("reddit", "oldreddit", csv_file=csv_file, settings=settings)
