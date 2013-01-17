#!/usr/bin/env python
# coding=utf8

import datetime
from flask import Flask, Request
from werkzeug.contrib.atom import AtomFeed
from lxml import etree

application = app = Flask('wsgi')


def getRajaLastNews(n=10):
	domain = 'http://www.rajanews.com/'
	tree = etree.parse(domain, etree.HTMLParser())

	posts = []

	# featured post
	title = tree.xpath('//table[@id="ShowRotateNews"]//div[@class="Titr2"]/a')[0]
	desc = tree.xpath('//table[@id="ShowRotateNews"]//td')[0]
	img = tree.xpath('//table[@id="ShowRotateNews"]//img')[0]
	posts.append({'title': title.text, 'subtitle': '', 'description': desc.get('title').strip(), 'link': domain + title.get('href'), 'image': domain + img.get('src'), 'published': datetime.datetime.now()})

	# last n posts
	for i in range(1, 3*n, 3):
		title = tree.xpath('//table[@id="NewsWithImage1"]/tr['+ str(i) +']//div[@class="Titr2"]/a')[0]
		subtitle = tree.xpath('//table[@id="NewsWithImage1"]/tr['+ str(i) +']//div[@class="Titr1"]/a')[0]
		img = tree.xpath('//table[@id="NewsWithImage1"]/tr['+ str(i+1) +']//img')[0]
		desc = tree.xpath('//table[@id="NewsWithImage1"]/tr['+ str(i+1) +']//div[@class="Lead"]')[0]
		posts.append({'title': title.text, 'subtitle': subtitle.text, 'description': desc.text.strip(), 'link': domain + title.get('href'), 'image': domain + img.get('src'), 'published': datetime.datetime.now()})

	return posts


def getFeed(posts):
	feed = AtomFeed(u'خبرخوان رجا نیوز', feed_url=Request.url, url=Request.url_root)

	for post in posts:
		content = '<img style="float: right; margin-left: 15px; width: 80px" src="%s"><p style="color: #777">%s</p><p>%s</p>' % (post['image'], post['subtitle'] if post['subtitle'] else '', post['description'])
		feed.add(post['title'], unicode(content), content_type='html', url=post['link'], updated=post['published'], published=post['published'])

	return feed.get_response()


@app.route('/')
def main_feed():
	return getFeed(getRajaLastNews())


if __name__ == '__main__':
	app.run()
