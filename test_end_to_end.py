from datetime import date,timedelta
from copy import deepcopy
import pytest
from services.travel_service import generate_trip,optimize_trip,packing_list,DESTINATIONS
from services.features import (add_day,add_attraction,change_accommodation,route_optimizer,hotel_recommender,transport_planner,restaurant_recommender,attraction_recommender,destination_recommender,weather_advisor)
from agent.travel_agent import answer

def inputs(**kw):
 t=dict(origin='Nagpur',destination='Goa',start=date(2026,11,4),end=date(2026,11,6),travelers=2,budget=15000,style='Budget',interests=['Nature'],transport='Train',accommodation='Hostel');t.update(kw);return t

def test_all_destinations_generate():
 for dest in DESTINATIONS:
  p=generate_trip(inputs(destination=dest));assert len(p['itinerary'])==3 and p['total']==sum(p['costs'].values())
@pytest.mark.parametrize('field,value', [('destination','Mumbai'),('travelers',4),('end',date(2026,11,8)),('style','Luxury'),('transport','Flight'),('accommodation','Luxury hotel')])
def test_price_sensitive(field,value):
 assert generate_trip(inputs(**{field:value}))['total']!=generate_trip(inputs())['total']
@pytest.mark.parametrize('field,value', [('origin',''),('destination',''),('budget',0),('travelers',0),('end',date(2026,11,3))])
def test_validation(field,value):
 with pytest.raises(ValueError):generate_trip(inputs(**{field:value}))
def test_budget_optimize():
 p=generate_trip(inputs());n=optimize_trip(p);assert n['total']<p['total'] and n['optimization']['savings']==p['total']-n['total']
def test_add_day_preserves_custom_activity():
 p=add_attraction(generate_trip(inputs()),'Custom museum');n=add_day(p);assert n['days']==4 and n['itinerary'][0]['afternoon']=='Custom museum'
def test_change_hotel_preserves_activity():
 p=add_attraction(generate_trip(inputs()),'Custom museum');n=change_accommodation(p,'Luxury hotel');assert n['itinerary'][0]['afternoon']=='Custom museum' and n['total']>p['total']
def test_chat_plan_and_tools():
 response,p=answer('Plan a 3-day trip to Goa for 2 people under ₹15,000.',None);assert p and p['days']==3 and p['inputs']['budget']==15000
 for command in ['make my trip cheaper','add one more day','change hotel','add a beach','replace afternoon activity','vegetarian food','packing checklist','route','weather','day 2','change transport to flight']:
  response,p=answer(command,p);assert isinstance(response,str) and response.strip() and p
 assert p['inputs']['transport']=='Flight'
def test_all_feature_outputs():
 p=generate_trip(inputs())
 assert hotel_recommender(p) and transport_planner(p) and restaurant_recommender(p) and attraction_recommender(p)
 assert destination_recommender(15000,3,2) and weather_advisor(p)['tips'] and packing_list(p)
 assert route_optimizer(p)['points']
def test_no_mutation():
 p=generate_trip(inputs());old=deepcopy(p)
 optimize_trip(p);add_day(p);change_accommodation(p);add_attraction(p,'Custom')
 assert p==old
