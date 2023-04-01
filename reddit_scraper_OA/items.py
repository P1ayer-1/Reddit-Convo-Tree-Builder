

from itemloaders.processors import Compose, Join, MapCompose
from scrapy import Item, Field



def clean_post_content(value):
    return value.strip().replace('\n', ' ')


class RedditScraperOaItem(Item):
    title = Field()
    subreddit = Field()
    post_id = Field()
    score = Field()
    link_flair_text = Field()
    is_self = Field()
    over_18 = Field()

    upvote_ratio  = Field()
    post_content = Field(
        input_processor=MapCompose(str.strip),
        output_processor=Compose(Join(), clean_post_content)
    )
    C1 = Field()
    C2 = Field()
    C3 = Field()
    C4 = Field()
    C5 = Field()