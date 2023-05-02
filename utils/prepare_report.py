import pandas as pd
import numpy as np
import re
import calendar 
import string
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords as sw
from num2words import num2words
from nltk.stem import WordNetLemmatizer
from bs4 import BeautifulSoup as BS


def remove_a_tags(soup):
    for elem in soup.find_all('p'):
        if elem.a:
            elem.replace_with('')

def remove_images(soup):
    for elem in soup.find_all('img'):
        elem.extract()

def remove_names(soup):
    initials = soup.select('p:nth-of-type(2)')
    initials[0].replaceWith('')

def remove_newlines_and_url_numbers(text):
    text = re.sub('\n|\xa0|\[\d+\]', '', text)
    return text
    
def remove_dates(text):
    months = []
    for i in range(1, 13):
        months.append(calendar.month_name[i])
        
    pattern = "(" + "|".join(months) + ")" + r" \d+( and \d*)?"
    text = re.sub(pattern, '', text)
    return text

def remove_1_letter_words(text):
    words = word_tokenize(text, language="english")
    new_text = []
    
    for w in words:
        new_text.append(w if len(w) > 1 else '')
            
    return ' '.join(new_text) 

def remove_stopwords(text):
    stopwords = set(sw.words('english'))
    exclude = {'no','not'}
    stopwords -= exclude
    
    words = word_tokenize(text, language="english")
    new_text = []
    
    for w in words:
        new_text.append(w if w not in stopwords else '')
        
    return ' '.join(new_text)
    
def num_to_word(text):
    words = word_tokenize(text, language="english")
    pattern = '^-?\d+(?:\.\d+)?$'

    new_text = []
    for w in words: 
        new_text.append(num2words(w) if re.fullmatch(pattern, w) else w)
    
    return ' '.join(new_text)

def remove_punctuation(text):
    symbols = string.punctuation
    
    for symbol in symbols:
        text = text.replace(symbol, ' ')
        
    text = text.replace('  ', ' ')
    return text

def lemmatize(text):
    lemmatizer = WordNetLemmatizer()
    
    words = word_tokenize(text, language="english")
    new_text = []
    
    for w in words:
        new_text.append(lemmatizer.lemmatize(w))
    
    return ' '.join(new_text)

def transform(soup):
    soup = soup.body.find("div", attrs={'class':'field field-name-body field-type-text-with-summary field-label-hidden'})
    remove_a_tags(soup)
    remove_images(soup)
    remove_names(soup)
    
    text = soup.text
    text = remove_newlines_and_url_numbers(text)
    text = remove_dates(text)
    text = remove_1_letter_words(text)
    text = text.lower()
    text = remove_stopwords(text)
    text = num_to_word(text)
    text = remove_punctuation(text)
    text = lemmatize(text)
    
    return text
