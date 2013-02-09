#!/usr/bin/env python

from bs4 import BeautifulSoup
import sys
import os.path

base_url = 'http://guij.emont.org/blog'

comment_file = sys.argv[1]
comment_dir = sys.argv[2]

def sanitize_field(data):
    return data.replace("'", "").replace('\n', '\n  ')

def get_comments(file_name):
    f = open(file_name)
    soup = BeautifulSoup(f, 'html.parser')
    for item in soup.find_all('item'):
        url = item.link.next.strip()
        post_id = url.replace(base_url, '')
        post_id = post_id.rstrip('/')
        for comment_xml in item.find_all('wp:comment'):
            comment = {}
            approved = False
            comment['post_id'] = post_id
            for field in ('author', 'author_email', 'author_url', 'author_ip', 'date', 'date_gmt', 'content', 'approved'):
                data = comment_xml.find('wp:comment_'+field).get_text().strip()
                if data:
                    if field == 'approved':
                        approved = bool(int(data))
                    else:
                        comment[field] = sanitize_field(data)
            if approved:
                yield comment

def comment_file_name(comment):
    path = comment['post_id'].strip('/').replace('/', '_').replace(' ', '_')
    file_name = comment['date_gmt'].replace(' ', '_') + '.yaml'
    return os.path.join(path, file_name)

def comment_string(comment):
    s = ""
    for item in comment.iteritems():
        s += u"%s: '%s'\n" % item
    return s

def make_files(comment_strings, path):
    for filepath, comment in comment_strings:
        full_file_name = os.path.join(path, filepath)
        full_path, _ = os.path.split(full_file_name)
        if not os.path.exists(full_path):
            os.mkdir(full_path)
        f = open(full_file_name, "w")
        f.write(comment.encode("UTF-8"))
        f.close()

def comment_strings(comments):
    for comment in comments:
        yield comment_file_name(comment), comment_string(comment)

comments = get_comments(comment_file)
make_files(comment_strings(comments), comment_dir)
