import requests 
import re
import time
from bs4 import BeautifulSoup

HOST = 'http://www.urbanoutfitters.com/'
CATEGORY_URL = 'http://www.urbanoutfitters.com/urban/catalog/category.jsp?id='
IMG_URL = 'http://images.urbanoutfitters.com/is/image/UrbanOutfitters/%s_%s_' 
FORMS = ['?$detailThumb$', '?$detailMain$']    
D = {}  #cache for categories

#-------------------  let's parse---------------------------------------------
def make_soup(url):
    r = requests.get(url)
    s = BeautifulSoup(r.content, 'lxml')
    return s    

def get_products(category):
    s = make_soup(CATEGORY_URL + category)
    cats = s.find(id='category-products')
    products = [p for p in cats.findAll('div', 'category-product')]
    return products

def compose_img_link(img_id, color): 
    return [IMG_URL % (img_id, color) + char + form
            for char in 'bdef'
            for form in FORMS] 

def check_colors(p):
    swatches = p.find('ul', 'category-product-swatches')
    return ([l.a['href'][-3:] for l in swatches.findAll('li')] if swatches 
            else [])
    
def find_id_and_colors(p):
    img_link = p.find('p', 'category-product-image').img['src']
    img_id, color, _ = img_link.split('/')[-1].split('_')
    swatches = check_colors(p) 
    return img_id, (swatches if swatches else [color])

def letsparse(category):
    links = D.get(category) or []
    if links:
        return links
    else: 
        for p in get_products(category):
            img_id, colors = find_id_and_colors(p)
            for c in colors:
                [links.append(l) for l in compose_img_link(img_id, c)]
        D[category] = links
    return links

#-------------------  let's parse end ---------------------------------------------

#other helper functions,
#it's faster.

def timedcalls(n, fn, *args):
    times =[]
    total = 0.
    while total < n:
        t = timedcall(fn,*args)[0]
        total += t
        times.append(t)
    return min(times), average(times), max(times)

def timedcall(fn, *args):
    t0 = time.clock()
    result = fn(*args)
    t1 = time.clock()
    return t1-t0, result

def average(n):
    return sum(n)/ len(n)+ 0.

categories = """W_APP_DRESSES WOMENS_SHOES W_NEWARRIVALS W_CAMP M_TOPS MENS_SHOES M_NEWARRIVALS M_PATTERN A_DEC_BEDDING A_MEDIA_GADGETS A_NEWARRIVALS W_WORKAHOLIC SALE_W SALE_M SALE_APT""".split(' ') 


if __name__ == '__main__':
    print 'categories to consider, '
    for c in categories:
        print c
    print timedcall(letsparse, raw_input('enter a category, lets parse \n').upper()) 

