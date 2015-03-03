# coding=utf8

import datetime
from flask import Flask, request
from werkzeug.contrib.atom import AtomFeed
from pyquery import PyQuery as pq

app = Flask(__name__)


def getRajaLastNews():
	domain = 'http://www.rajanews.com/'
	raja = pq(domain)

	item = raja('.slider1 .item')
	yield {
		'title': item.find('.title').text(),
		'subtitle': item.find('.top-title').text(),
		'description': item.find('.lead').text(),
		'link': domain + item.find('a').attr('href'),
		'image': item.find('img').attr('src'),
		'published': datetime.datetime.now()
	}

	for item in raja('.homepage .item').items():
		yield {
			'title': item.find('.title').text(),
			'subtitle': item.find('.top-title').text(),
			'description': item.find('.lead').text(),
			'link': domain + item.find('a').attr('href'),
			'image': item.find('img').attr('src'),
			'published': datetime.datetime.now()
		}


def getFeed(posts):
	feed = AtomFeed(u'خبرخوان رجا نیوز', feed_url=request.url, url=request.url_root, icon='http://www.rajanews.com/favicon.ico', author={'name': u'رجا نیوز', 'uri': 'www.rajanews.com'})

	for post in posts:
		content = '<img style="float: right; margin-left: 15px; width: 80px" src="%s"><p style="color: #777">%s</p><p>%s</p>' % (post['image'], post['subtitle'] if post['subtitle'] else '', post['description'])
		feed.add(post['title'], unicode(content), content_type='html', url=post['link'], updated=post['published'], published=post['published'])

	return feed.get_response()


@app.route('/')
def main_feed():
	return getFeed(getRajaLastNews())


if __name__ == '__main__':
	app.run()
