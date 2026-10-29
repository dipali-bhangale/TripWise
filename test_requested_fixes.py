from datetime import date,timedelta
from services.features import destination_recommender
from services.travel_service import generate_trip
from agent.travel_agent import answer

def trip():
 d=date(2026,11,4)
 return generate_trip(dict(origin='Nagpur',destination='Goa',start=d,end=d+timedelta(days=4),travelers=2,budget=25000,style='Budget',interests=['Nature'],transport='Train',accommodation='Budget hotel'))

def test_destinations_have_different_estimates():
 estimates=[r['estimated_total'] for r in destination_recommender(30000,3,2,['Nature'])]
 assert len(set(estimates))>=4

def test_evenings_vary_by_day():
 evenings=[x['evening'] for x in trip()['itinerary']]
 assert len(set(evenings))>=4

def test_rain_question_has_real_advice():
 response,_=answer('Suggest indoor activities if it rains.',trip())
 assert 'indoor' in response.lower() and 'Try:' not in response

def test_transport_comparison_has_options():
 response,_=answer('Compare flight, train, bus and car for my trip.',trip())
 assert all(x in response for x in ['Flight','Train','Bus','Car'])
