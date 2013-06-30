import requests 
import re
from bs4 import BeautifulSoup

HOST = 'http://www.urbanoutfitters.com/'
CATEGORY_URL = 'http://www.urbanoutfitters.com/urban/catalog/category.jsp?id='
IMG_URL = 'http://images.urbanoutfitters.com/is/image/UrbanOutfitters/%s_%s_' 
FORMS = ['?$detailThumb$', '?$detailMain$']

def make_soup(url):
    r = requests.get(url)
    s = BeautifulSoup(r.content, 'lxml')
    return s

def get_image_paths(category):
    s = make_soup(CATEGORY_URL + category)
    images = s.findAll('p', class_='category-product-image')
    path = [i.a['href'] for i in images]
    return path

def get_colors(path):
    s = make_soup(HOST + path)
    swatches = s.find(class_='swatches').findAll('a')
    return [s['href'][1:] for s in swatches]

def compose_img_link(img_id, color): 
    return [IMG_URL % (img_id, color) + char + form
            for char in 'bdef'
            for form in FORMS]

def letsparse(category):
    paths = get_image_paths(category) 
    return  [l for p in paths
               for color in get_colors(p)
               for l in compose_img_link(re.findall('\d+', p)[0], color)]           
