from googleplaces import GooglePlaces, types, ranking
import datetime

API_KEY = 'AIzaSyCNlEds4VQwtuFbjw6LFN_CfvCawEsZOMI'
google_places = GooglePlaces(API_KEY)

class Place(object):
	name = ''
	phone_number = ''
	address = ''
	rating = ''
	website = ''
	id = ''
	price = ''
	store_hours = {}
	reviews = {}

def getQueryResults(location, query):
	query_result = google_places.nearby_search(
        location=location, keyword=query,
        radius=50000, types=[types.TYPE_FOOD], rankby=ranking.DISTANCE)
	places = []
	for result in query_result.places:
		result.get_details()
		place = Place()
		place.name = result.name
		place.phone_number = result.local_phone_number
		place.address = result.formatted_address[:-15]
		place.rating = result.rating
		place.id = result.place_id
		place.website = result.website
		place.price = getPrice(result.price_level)
		places.append(place)
	return {'column_one_title': 'RESTAURANT NAME', 
			'places': places, 
			'location': location, 
			'query': query}

def getPlaceDetails(place_id):
	result = google_places.get_place(place_id)
	result.get_details()
	place = Place()
	place.name = result.name
	place.phone_number = result.local_phone_number
	place.address = result.formatted_address[:-15]
	place.rating = result.rating
	place.id = result.place_id
	place.website = result.website
	place.price = getPrice(result.price_level)
	place.reviews = getReviews(result.reviews)
	place.store_hours = getStoreHours(result.opening_hours)
	photos = getPhotos(result.photos)
	return {'place': place, 'photos': photos}

def getReviews(reviews):
	if not reviews:
		return []
	myReviews = []
	for review in reviews:
		details = {}
		details['rating'] = review.get('rating')
		details['author'] = review.get('author_name')
		details['description'] = review.get('text')
		details['time'] = datetime.datetime.utcfromtimestamp(review.get('time')).strftime('%m/%d/%y %I:%M %p')
		myReviews.append(details)
	return myReviews

def getStoreHours(opening_hours):
	store_hours = {}
	if opening_hours:
		for period in opening_hours['periods']:
			open, close = convertMilitaryTimeToStandardTime(str(period.get('open').get('time')), str(period.get('close').get('time')))
			store_hours[str(period.get('open').get('day'))] = open + " - " + close
	else:
		for i in range(7):
			store_hours[str(i)] = 'N/A'
	return store_hours

def getPhotos(photos):
	if not photos:
		return []
	myPhotos = []
	for photo in reversed(photos):
		myPhotos.append(getPhotoLink(photo.photo_reference))
	return myPhotos

def getPhotoLink(photo_reference):
	return "https://maps.googleapis.com/maps/api/place/photo?maxheight=700&maxwidth=700&key=" + API_KEY + "&photoreference=" + photo_reference

def convertMilitaryTimeToStandardTime(start, end):
	start_t = datetime.time(hour=int(start[0:2]), minute=int(start[2:4]))
	end_t = datetime.time(hour=int(end[0:2]), minute=int(end[2:4]))
	# datetime format
	fmt = "%I:%M %p"
	return start_t.strftime(fmt), end_t.strftime(fmt)

def getPrice(price_level):
	if not price_level:
		return 'N/A'
	price = ''
	for _ in range(price_level):
		price += '$'
	if not price:
		price = 'Free'
	return price


