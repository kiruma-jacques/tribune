from django.test import TestCase
from .models import Article, tags
import datetime as dt
from django.contrib.auth.models import User
# Create your tests here.
class tagsTestClass(TestCase):

    def setUp(self):
        self.tuff = tags (name ="Gengetone")

    def test_tags_instance(self):
        self.assertTrue(isinstance(self.tuff, tags))

    def test_tags_save(self):
        self.tuff.save_tag()
        tageth = tags.objects.all()
        self.assertTrue(len(tageth)>0)

class ArticleTestClass(TestCase):
    def setUp(self):
        self.james = User (first_name = 'James', last_name='Muriuki', email='james@moringaschool.com')
        self.james.save()
        self.new_tag = tags(name='testing')
        self.new_tag.save()
        self.new_article = Article (title='Test Article', post = 'This is a random test post', editor = self.james)
        self.new_article.save()
        self.new_article.tags.add(self.new_tag)

    def tearDown(self):
        User.objects.all().delete()
        tags.objects.all().delete()
        Article.objects.all().delete()

    def test_get_news_today(self):
        today_news = Article.todays_news()
        self.assertTrue(len(today_news)>0)

    def test_get_news_by_date(self):
        test_date = '2019-12-14'
        date = dt.datetime.strptime(test_date, '%Y-%m-%d').date()
        news_by_date = Article.days_news(date)
        self.assertTrue(len(news_by_date) == 0 )
