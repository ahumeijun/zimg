# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import os
import requests
from pyquery import PyQuery as pq
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

baseUrl = 'https://www.aitaotu.com'
headers = {
    "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36"
}

def downloadimage(src, path):
    if os.path.exists(path):
        print('image %s is exists.'%src)
        return
    print('downloading image %s'%src)
    ir = requests.get(src, headers = headers, verify = False)
    if ir.status_code == 200:
        open(path.encode('utf-8'), 'wb+').write(ir.content)
    else:
        print('!!!download image %s failed'%src)

def downloadimages(pageurl):
    print('starting download images from page %s'%pageurl)
    resp = requests.get(baseUrl + pageurl, headers = headers, verify = False)
    doc = pq(resp.text)
    #creat dir
    title = doc('.imgtitle').find('h2').text()
    titles = title.split(' ')
    if len(titles) < 2:
        print('parse titles error!')
        print(doc('.imgtitle').html())
        return
    dir1 = titles[0][1:-1]
    dir2 = '_'.join(titles[1:])
    fulldir = '%s/%s'%(dir1, dir2)
    if not os.path.exists(fulldir.encode('utf-8')):
        os.makedirs(fulldir.encode('utf-8'))
    #download
    exist = False
    for img in doc('.big-pic').find('img').items():
        exist = True
        src = img.attr('src')
        name = src.split('/')[-1]
        path = '%s/%s'%(fulldir, name)
        downloadimage(src, path)
    if not exist:
        print('parse image url failed!')
    #next page
    nextUrl = None
    for a in doc('.pages').find('a').items():
        text = a.text()
        if text == '下一页':
            nextUrl = a.attr('href')
            break
    if nextUrl:
        downloadimages(nextUrl)

def isthumbdone(name):
    dirname = 'thumbs'
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    path = '%s/%s.jpg'%(dirname, name.replace(' ', ''))
    return os.path.exists(path)

def setthumbdone(name, thumbsrc):
    if not isthumbdone(name):
        resp = requests.get(thumbsrc, headers = headers, verify = False)
        img = resp.content
        path = 'thumbs/%s.jpg'%name.replace(' ', '')
        open(path, 'wb+').write(img) 


def downloadlist(listurl):
    print('starting process page list %s'%listurl)
    resp = requests.get(baseUrl + listurl, headers = headers, verify = False)
    doc = pq(resp.text)
    for a in doc('div.item_t').find('div.img').find('a').items():
        img = a.find('img')
        if not img:
            continue
        print('thumb item: %s'%a.html())
        href = a.attr('href')
        title = img.attr('title')
        if not title:
            title = img.attr('alt')
        thumbsrc = img.attr('data-original')
        if isthumbdone(title):
            print('%s did downloaded!'%href)
        else:
            downloadimages(href)
            setthumbdone(title, thumbsrc)

def processinglist(listurl):
    downloadlist(listurl)
    #next
    nextUrl = None
    resp = requests.get(baseUrl + listurl, headers = headers, verify = False)
    doc = pq(resp.text)
    for a in doc('#pageNum').find('a').items():
        text = a.text()
        if text == '下一页':
            nextUrl = a.attr('href')
            break
    if nextUrl:
        processinglist(nextUrl)
    else:
        print('DOWNLOAD END')

def main():
    try:
        print('main start')
        processinglist('/guonei')
    except Exception as e:
        print(e)
        main()
    finally:
        print('main end')

if __name__ == '__main__':
    main()
