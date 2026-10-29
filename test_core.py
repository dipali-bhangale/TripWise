from datetime import date,timedelta
from services.travel_service import generate_trip,optimize_trip,packing_list
from agent.travel_agent import answer
from database.db import save_trip,load_trip,delete_trip
import pytest
@pytest.fixture
def trip():
 d=date.today();return generate_trip({'origin':'Nagpur','destination':'Goa','start':d,'end':d+timedelta(days=2),'travelers':2,'budget':15000,'style':'Budget','interests':['Beach'],'transport':'Train','accommodation':'Hostel'})
def test_itinerary(trip):assert len(trip['itinerary'])==3 and trip['days']==3
def test_budget(trip):assert sum(trip['costs'].values())==trip['total']
def test_optimization(trip):assert optimize_trip(trip)['total']<trip['total']
def test_packing(trip):assert len(packing_list(trip))>=5
def test_chat(trip):assert 'Day 2' in answer('what should I visit on the second day?',trip)[0]
def test_database(trip):
 i=save_trip(trip);assert load_trip(i)['destination']=='Goa';delete_trip(i);assert load_trip(i) is None
def test_invalid_dates(trip):
 from services.travel_service import validate_trip
 d=date.today();p={'destination':'Goa','start':d,'end':d-timedelta(days=1),'budget':10,'travelers':1}
 with pytest.raises(ValueError):validate_trip(p)
