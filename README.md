# Reddit-Convo-Tree-Builder


## Run


### Get csv

Use BigQuery to get a csv file

```
SELECT *
FROM reddit-safety-oa.reddit_submissions_oa.submission
WHERE subreddit = 'math';
```

A demo csv can be found here: https://www.kaggle.com/datasets/noahpersaud/176-million-ramitheasshole-submissions

Split the csv file using split_csv.py. The performance of your system should dictate how many splits you should make.

### Get proxies

I use 1 per concurrent request. The current configuration requires at least 4k proxies (500x8)


- https://github.com/jetkai/proxy-list/tree/main/online-proxies/txt 
- https://github.com/Zaeem20/FREE_PROXIES_LIST/blob/master/https.txt 
- https://github.com/officialputuid/KangProxy/tree/KangProxy/https 
- https://github.com/mmpx12/proxy-list/blob/master/https.txt 
- https://github.com/constverum/ProxyBroker

### Update settings.py with the path to your proxy list

### Upload spider to scrapyd 
```scrapy```

```scrapyd-deploy --build-egg=/dev/null```

```scrapyd-deploy -p reddit_scraper_OA```

Run main.py and update SUBREDDIT with the name of the subreddit you want to scrape
