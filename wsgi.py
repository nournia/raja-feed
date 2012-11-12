#!/usr/bin/env python
# coding=utf8

import sys, os, json, time

def mongodb_uri():
	local = os.environ.get("MONGODB", None)
	if local:
		return local
	services = json.loads(os.environ.get("VCAP_SERVICES", "{}"))
	if services:
		creds = services['mongodb-1.8'][0]['credentials']
		uri = "mongodb://%s:%s@%s:%d/%s" % (creds['username'], creds['password'], creds['hostname'], creds['port'], creds['db'])
		print >> sys.stderr, uri
		return uri
	else:
		raise Exception, "No services configured"

# my app
from flask import Flask, Request, Response
from werkzeug.contrib.atom import AtomFeed
import urllib2, datetime
from lxml import etree
from pymongo import Connection

application = app = Flask('wsgi')

def getRajaLastNews():
	domain = 'http://www.rajanews.com/'
	tree = etree.parse(domain, etree.HTMLParser())

	posts = []

	# featured post
	title = tree.xpath('//table[@id="ShowRotateNews"]//div[@class="Titr2"]/a')[0]
	desc = tree.xpath('//table[@id="ShowRotateNews"]//td')[0]
	img = tree.xpath('//table[@id="ShowRotateNews"]//img')[0]
	posts.append({'title': title.text, 'subtitle': '', 'description': desc.get('title').strip(), 'link': domain + title.get('href'), 'image': domain + img.get('src'), 'published': datetime.datetime.now()})

	# last posts
	for i in [1, 4, 7, 10]:
		title = tree.xpath('//table[@id="NewsWithImage1"]/tr['+ str(i) +']//div[@class="Titr2"]/a')[0]
		subtitle = tree.xpath('//table[@id="NewsWithImage1"]/tr['+ str(i) +']//div[@class="Titr1"]/a')[0]
		img = tree.xpath('//table[@id="NewsWithImage1"]/tr['+ str(i+1) +']//img')[0]
		desc = tree.xpath('//table[@id="NewsWithImage1"]/tr['+ str(i+1) +']//div[@class="Lead"]')[0]
		posts.append({'title': title.text, 'subtitle': subtitle.text, 'description': desc.text.strip(), 'link': domain + title.get('href'), 'image': domain + img.get('src'), 'published': datetime.datetime.now()})

	return posts

@app.route('/main.atom')
def main_feed():
	posts = Connection(mongodb_uri()).db.posts

	feed = AtomFeed(u'خبرخوان رجا نیوز', feed_url=Request.url, url=Request.url_root)

	for post in posts.find().limit(10):
		content = '<img style="float: right; margin-left: 15px; width: 80px" src="%s"><p style="color: #777">%s</p><p>%s</p>' % (post['image'], post['subtitle'] if post['subtitle'] else '', post['description'])
		feed.add(post['title'], unicode(content), content_type='html', url=post['link'], updated=post['published'], published=post['published'])

	return feed.get_response()

@app.route('/update')
def check_raja():
	posts = Connection(mongodb_uri()).db.posts

	inserted = False
	for post in getRajaLastNews():
		if len(list(posts.find({'link': post['link']}))) == 0:
			posts.insert(post, safe=True)
			inserted = True

	if inserted:
		return 'new post'
	return 'unchanged'

if __name__ == '__main__':
	 app.run()
