import scrapy
import csv
from scrapy.loader import ItemLoader
from ..items import RedditScraperOaItem

class OldredditSpider(scrapy.Spider):
    name = "oldreddit"
    allowed_domains = ["old.reddit.com"]
    start_urls = ["https://old.reddit.com/over18?dest=https%3A%2F%2Fold.reddit.com%2F"]

    csv_file = None


    def start_requests(self):
        if self.csv_file is None:
            raise ValueError("The csv_file argument is required.")


        return [scrapy.Request(self.start_urls[0], callback=self.parse)]


    def parse(self, response):
        formdata = {
            'over18': 'yes',
        }
        yield scrapy.FormRequest.from_response(response, formdata=formdata, callback=self.after_age_check)

    def after_age_check(self, response):
        if response.url.startswith('https://old.reddit.com/'): # check if age check passed
            self.logger.info('Successfully passed the age check.')
            # Read the list of permalinks from a text file
            with open(self.csv_file, 'r') as file:
                reader = csv.DictReader(file)

                # Initialize a dictionary to store permalinks with corresponding post_id and title
                permalinks_dict = {}

                # Loop through each row in the CSV file
                for row in reader:
                    # Get the post ID and title from the row
                    post_id = row['post_id']
                    title = row['title']
                    subreddit = row['subreddit']
                    link_flair_text = row['link_flair_text']
                    self_text = row['self_text']



                    if title != "[deleted by user]":
                                # Create the permalink by concatenating 'old.reddit.com/' and the post ID
                                permalink = f'https://old.reddit.com/{post_id}'

                                # Add the permalink, title, and self_text to the dictionary
                                permalinks_dict[permalink] = {'title': title, 'self_text': self_text, 'post_id': post_id, 'link_flair_text': link_flair_text}

                                # Send a request for each permalink to the parse_post method
                                yield scrapy.Request(url=permalink.strip(), callback=self.parse_post, meta={'permalink_data': permalinks_dict[permalink], 'subreddit': subreddit})
        else:
            self.logger.error('Failed to pass the age check.')

            

    def parse_post(self, response):
        permalink_data = response.meta['permalink_data']
        subreddit = response.meta['subreddit']
        item_loader = ItemLoader(item=RedditScraperOaItem())
        comments = []
        top_comments = []

        # extract comment_count
        comment_count = response.css('div.content div.sitetable.linklisting div::attr(data-comments-count)').get()

        if comment_count is not None and int(comment_count) < 5:  # skip post if comment count is less than 5
            self.logger.info(f'Skipping post with {comment_count} comments.')
            return

        # extract over_18
        over_18 = response.css('div.content div.sitetable.linklisting div::attr(data-nsfw)').get()
        # convert to boolean
        if over_18 == 'true':
            over_18 = True
        else:
            over_18 = False
        item_loader.add_value("over_18", over_18)

        for comment in response.css("div.comment"):
            score = comment.css("span.score.unvoted::text").get()
            # use .usertext.warn-on-unload input::attr(value) to get the comment id
            comment_id = comment.css('div[class^=" thing id"]::attr(data-fullname)').get()
            author = comment.css('div[class^=" thing id"]::attr(data-author)').get() or 'deleted'


            if score is not None:
                score = score.replace(' points', '')
                if 'k' in score:
                    score = score.replace('k', '')
                    score = float(score) * 1000
                    score = int(score)
                else:
                    score = score.replace('point', '')
                    score = int(score)
                
                if author != 'AutoModerator':
                    comment_item = {"score": score, "comment_id": comment_id}
                    comments.append(comment_item)

        comments = sorted([c for c in comments if c['score'] is not None], key=lambda c: c['score'], reverse=True)[:5]

        for comment in comments:
            comment_id = comment['comment_id']
            comment_text = response.css(f'form[id^="form-{comment_id}"] p::text').getall()
            if comment_text:
                top_comments.append({'comment_id': comment_id, 'comment_text': comment_text})



        # check if atleast 5 comments before extracting top 5 comments
        if len(top_comments) >= 5:
            comment_texts = []
            for comment in top_comments:
                comment_texts.append(comment['comment_text'])
                if len(comment_texts) == 5:
                    break
            item_loader.add_value("C1", comment_texts[0])
            item_loader.add_value("C2", comment_texts[1])
            item_loader.add_value("C3", comment_texts[2])
            item_loader.add_value("C4", comment_texts[3])
            item_loader.add_value("C5", comment_texts[4])
        else:
            return

        # extract subreddit
        item_loader.add_value("subreddit", subreddit)

        # extract link_flair_text
        item_loader.add_value("link_flair_text", permalink_data['link_flair_text'])


        item_loader.add_value("is_self", True)


       # add post_id
        post_id = permalink_data['post_id']
        item_loader.add_value("post_id", post_id)



        
        
        # use subreddit variable from $subreddit
        title = response.css(f'div[data-subreddit="{subreddit}"] div.top-matter p.title > a.title.may-blank::text').extract_first().strip() # extract title



        post_content = response.css(f'div[data-subreddit="{subreddit}"] div.expando form.usertext.warn-on-unload div.usertext-body.may-blank-within.md-container div.md p::text').extract() # extract post content 


        if title == '[deleted by user]':
            title = permalink_data['title']  # if deleted by user, get title from the CSV

        if post_content == '[removed]' or post_content == '[deleted]':
            post_content = permalink_data['self_text']

        item_loader.add_value("title", title)
        item_loader.add_value("post_content", post_content)


        post_karma = response.xpath('/html/body/div[3]/div[2]/div/div[2]//text()').extract()
        post_score = int(post_karma[0])
        item_loader.add_value("score", post_score)

        upvote_percentage = post_karma[-1].strip().replace('%', '').replace('(', '').replace(')', '').replace('upvoted', '')
        upvote_percentage = float(upvote_percentage) / 100
        item_loader.add_value("upvote_ratio", upvote_percentage)



        yield item_loader.load_item()