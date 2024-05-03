# Importing necessary library
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
import pickle


pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

books = pd.read_csv('data/BX-Books.csv', sep=";", on_bad_lines="skip", encoding="latin-1", low_memory=False)
books.drop(["Image-URL-S", "Image-URL-M"], axis=1, inplace=True)
books.rename(columns={"Book-Title": 'title',
                      "Book-Author": "author",
                      "Year-Of-Publication": "year",
                      "Publisher": "publisher",
                      "Image-URL-L": "image_url"}, inplace=True)

users = pd.read_csv('data/BX-Users.csv', sep=";", on_bad_lines="skip", encoding='latin-1')
users.rename(columns={"User-ID": "user_id",
                      "Location": "location",
                      "Age": "age"}, inplace=True)

ratings = pd.read_csv('data/BX-Book-Ratings.csv', sep=";", on_bad_lines="skip", encoding='latin-1')
ratings.rename(columns={'User-ID': 'user_id',
                        'Book-Rating': 'rating'}, inplace=True)

print(books.shape, users.shape, ratings.shape, sep='\n')
ratings['user_id'].value_counts()

# Let's store users who had at least rated more than 200 books
x = ratings['user_id'].value_counts() > 200
y = x[x].index

ratings = ratings[ratings['user_id'].isin(y)]

# Now join ratings with books
ratings_with_books = ratings.merge(books, on='ISBN')
ratings_with_books.head()

number_rating = ratings_with_books.groupby('title')['rating'].count().reset_index()
number_rating.rename(columns={'rating': 'num_of_rating'}, inplace=True)
final_rating = ratings_with_books.merge(number_rating, on='title')

final_rating.head()
final_rating.sort_values("num_of_rating", ascending=False)

# Let's take those books which got at least 50 rating of user
final_rating = final_rating[final_rating['num_of_rating'] >= 50]

# let's drop the duplicates
final_rating.drop_duplicates(['user_id', 'title'], inplace=True)

book_pivot = final_rating.pivot_table(columns='user_id', index='title', values='rating')
book_pivot.fillna(0, inplace=True)

# Creating the model
book_sparse = csr_matrix(book_pivot)
model = NearestNeighbors(algorithm='brute')
model.fit(book_sparse)
distance, suggestion = model.kneighbors(book_pivot.iloc[237, :].values.reshape(1, -1), n_neighbors=6)


for i in range(len(suggestion)):
    print(book_pivot.index[suggestion[i]])


book_names = book_pivot.index

# Find URL
ids = np.where(final_rating['title'] == "Harry Potter and the Chamber of Secrets (Book 2)")[0][0]

book_name = []
for book_id in suggestion:
    book_name.append(book_pivot.index[book_id])


ids_index = []
for name in book_name[0]:
    ids = np.where(final_rating['title'] == name)[0][0]
    ids_index.append(ids)


for idx in ids_index:
    url = final_rating.iloc[idx]['image_url']
    print(url)


pickle.dump(model, open('models/model.pkl', 'wb'))
pickle.dump(book_names, open('models/book_names.pkl', 'wb'))
pickle.dump(final_rating, open('models/final_rating.pkl', 'wb'))
pickle.dump(book_pivot, open('models/book_pivot.pkl', 'wb'))


def recommend_book(book_name):
    books_list = []
    book_id = np.where(book_pivot.index == book_name)[0][0]
    distance, suggestion = model.kneighbors(book_pivot.iloc[book_id, :].values.reshape(1, -1), n_neighbors=6)

    poster_url = fetch_poster(suggestion)
    
    for i in range(len(suggestion)):
        books = book_pivot.index[suggestion[i]]
        for j in books:
            books_list.append(j)
    return books_list, poster_url


def fetch_poster(suggestion):
    book_name = []
    ids_index = []
    poster_url = []

    for book_id in suggestion:
        book_name.append(book_pivot.index[book_id])

    for name in book_name[0]: 
        ids = np.where(final_rating['title'] == name)[0][0]
        ids_index.append(ids)

    for idx in ids_index:
        url = final_rating.iloc[idx]['image_url']
        poster_url.append(url)

    return poster_url


recommend_book("Harry Potter and the Chamber of Secrets (Book 2)")
