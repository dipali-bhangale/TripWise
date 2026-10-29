import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date,timedelta
from services.travel_service import DESTINATIONS,generate_trip,optimize_trip,packing_list
from database.db import save_trip,list_trips,load_trip,delete_trip
from agent.travel_agent import answer
from config import GEMINI_API_KEY
from services.features import destination_recommender,hotel_recommender,transport_planner,attraction_recommender,restaurant_recommender,weather_advisor,route_optimizer,add_attraction,add_day
st.set_page_config(page_title='TripWise | AI Travel Companion',page_icon='🌍',layout='wide')
st.markdown("""<style>
/* Consistent light dashboard and readable text */
.stApp {background:#f5f9fc; color:#17324d;}
.block-container {padding-top:1.5rem; padding-bottom:3rem;}
h1,h2,h3,h4 {color:#123b5a !important;}
p, label, .stMarkdown, [data-testid="stMetricLabel"], [data-testid="stMetricValue"] {color:#17324d;}
[data-testid="stMetric"] {background:#fff; border:1px solid #e2eaf1; border-radius:16px; padding:18px; box-shadow:0 3px 14px rgba(20,58,90,.07);}
[data-testid="stMetricLabel"] *, [data-testid="stMetricValue"] * {color:#17324d !important; opacity:1 !important;}
/* Inputs always use light backgrounds with dark legible text */
[data-testid="stTextInput"] input, [data-testid="stNumberInput"] input,
[data-testid="stDateInput"] input, [data-baseweb="select"] > div,
[data-baseweb="input"] {background:#fff !important; color:#17324d !important; border-color:#cbd9e5 !important;}
[data-testid="stTextInput"] input, [data-testid="stNumberInput"] input,
[data-testid="stDateInput"] input, [data-baseweb="select"] * {color:#17324d !important;}
[data-baseweb="tag"] {background:#d9f2f1 !important;}
[data-baseweb="tag"] * {color:#075a63 !important;}
/* High-contrast primary buttons */
.stButton > button[kind="primary"], [data-testid="stFormSubmitButton"] button {background:#087f8c !important; color:#fff !important; border:1px solid #087f8c !important; font-weight:650;}
.stButton > button[kind="primary"] *, [data-testid="stFormSubmitButton"] button * {color:#fff !important;}
.stButton > button:not([kind="primary"]) {background:#fff; color:#075a63; border:1px solid #a9cbd0; font-weight:600;}
.stButton > button:not([kind="primary"]) * {color:#075a63 !important;}
.stButton > button:hover {border-color:#087f8c !important; box-shadow:0 2px 8px rgba(8,127,140,.12);}
/* Sidebar remains dark, with readable labels */
[data-testid="stSidebar"] {background:#172a3c;}
[data-testid="stSidebar"] *, [data-testid="stSidebar"] label, [data-testid="stSidebar"] p {color:#eef7fc !important;}
[data-testid="stSidebar"] [data-testid="stAlert"] {background:#214b60;}
/* Tabs and expanders */
[data-testid="stExpander"], [data-testid="stVerticalBlockBorderWrapper"] {border-color:#dce7ef;}
button[role="tab"] {color:#244a65 !important;}
[data-testid="stChatMessage"] {border:1px solid #e0e9f1; border-radius:14px; padding:14px 18px; background:#fff !important;}
[data-testid="stChatMessage"] p, [data-testid="stChatMessage"] span {color:#17324d !important;}
[data-testid="stChatInput"] {background:#fff !important; border:1px solid #c6d8e4 !important;}
[data-testid="stChatInput"] textarea {color:#17324d !important; background:#fff !important;}
[data-testid="stChatInput"] button {color:#087f8c !important;}
[data-testid="stForm"] {background:#fff; padding:20px; border-radius:16px; border:1px solid #e0e9f1;}
</style>""",unsafe_allow_html=True)
st.sidebar.title('🌍 TripWise')
st.sidebar.caption('Your Smart AI Travel Companion')
page=st.sidebar.radio('Navigate',['Dashboard','Plan a Trip','Explore Destinations','My Trips','AI Travel Assistant','Trip Details','Settings'])
st.sidebar.info("🟡 Demo Mode – Some information is simulated.")
if 'trip' not in st.session_state:st.session_state.trip=None
if 'messages' not in st.session_state:st.session_state.messages=[]

def show_trip(p):
 st.title(f"✈️ {p['destination']} · {p['days']} days")
 st.caption(p['notes'])
 a,b,c,d=st.columns(4)
 budget=p['inputs']['budget'];a.metric('Estimated cost',f"₹{p['total']:,}");b.metric('Per traveler',f"₹{p['total']/p['inputs']['travelers']:,.0f}");c.metric('Remaining budget',f"₹{budget-p['total']:,}");d.metric('Budget used',f"{100*p['total']/budget:.1f}%")
 tabs=st.tabs(['Itinerary','Budget','Hotels & Transport','Attractions & Food','Weather & Route','Packing'])
 with tabs[0]:
  for day in p['itinerary']:
   with st.expander(f"Day {day['day']} · {day['date']}",expanded=day['day']==1):
    st.write('🌅 Morning:',day['morning']);st.write('☀️ Afternoon:',day['afternoon']);st.write('🌙 Evening:',day['evening']);st.write('🍲 Food:',day['food']);st.caption(f"Illustrative activity cost ₹{day['estimated_activity_cost']:,}; travel time not verified")
 with tabs[1]:
  st.plotly_chart(px.pie(names=list(p['costs']),values=list(p['costs'].values()),title='Estimated cost distribution'),use_container_width=True)
  st.dataframe(pd.DataFrame([{'Category':k,'Estimated INR':v} for k,v in p['costs'].items()]),hide_index=True)
  st.caption('All figures are illustrative. Re-generate the plan after changing inputs to recalculate.')
  if p.get('optimization'):
   st.success(f"Optimization saved approximately ₹{p['optimization']['savings']:,}. Changes: "+', '.join(p['optimization']['changes']))
  if st.button('Optimize budget'):
   n=optimize_trip(p);st.session_state.trip=n;st.success(f"Estimated savings: ₹{p['total']-n['total']:,}");st.rerun()
 with tabs[2]:
  st.subheader('Accommodation options — illustrative categories, not bookable listings')
  st.dataframe(pd.DataFrame(hotel_recommender(p)),hide_index=True,use_container_width=True)
  st.subheader('Transportation comparison — illustrative round-trip estimates')
  st.dataframe(pd.DataFrame(transport_planner(p)),hide_index=True,use_container_width=True)
 with tabs[3]:
  st.subheader('Attractions')
  attractions=attraction_recommender(p)
  st.dataframe(pd.DataFrame(attractions),hide_index=True,use_container_width=True)
  chosen=st.selectbox('Add an attraction to day 1 afternoon',[x['name'] for x in attractions],key='attraction_pick')
  if st.button('Add attraction to itinerary'):
   st.session_state.trip=add_attraction(p,chosen);st.rerun()
  st.subheader('Regional food suggestions')
  diet=st.selectbox('Diet preference',['Any','Vegetarian'],key='diet')
  st.dataframe(pd.DataFrame(restaurant_recommender(p,diet)),hide_index=True,use_container_width=True)
 with tabs[4]:
  st.warning(weather_advisor(p)['status'])
  for tip in weather_advisor(p)['tips']:st.write('• '+tip)
  mode=st.selectbox('Preferred travel mode',['Walking','Driving','Public transportation'],key='route_mode')
  route=route_optimizer(p,mode)
  st.caption(route['status'])
  if route['points']:
   st.write(' → '.join(x['name'] for x in route['points']))
   points=pd.DataFrame(route['points'])
   st.map(points[['lat','lon']])
   st.caption(f"Straight-line sum: {route['straight_line_km']} km. NOT a road-route distance or ETA. The map displays attraction markers, not a navigable route.")
  elif p['lat'] is not None:st.map(pd.DataFrame([{'lat':p['lat'],'lon':p['lon']}]))
 with tabs[5]:
  items=packing_list(p);all_items=[(k,v) for k,vals in items.items() for v in vals]
  checked=0
  for k,v in all_items:
   if st.checkbox(v,key=f"pack_{p['destination']}_{k}_{v}"):checked+=1
  st.progress(checked/len(all_items));st.caption(f'{checked}/{len(all_items)} items packed')
 if st.button('➕ Extend trip by one day'):
  st.session_state.trip=add_day(p);st.rerun()
 if st.button('💾 Save this trip'):st.success(f"Trip saved (ID {save_trip(p)})")
 st.download_button('⬇️ Export itinerary JSON',data=__import__('json').dumps(p,indent=2,default=str),file_name='tripwise_'+p['destination'].lower().replace(' ','_')+'.json',mime='application/json')

if page=='Dashboard':
 st.title('🌍 Welcome to TripWise');st.write('Plan personalized trips with an AI-assisted itinerary, budget and packing dashboard.')
 a,b=st.columns(2);a.metric('Popular destinations',len(DESTINATIONS));b.metric('Saved trips',len(list_trips()))
 st.subheader('Explore popular destinations');st.write(' · '.join(DESTINATIONS))
 st.subheader('Recently saved trips')
 for tid,dest,created in list_trips()[:5]:st.write(f'• {dest} — {created}')
 st.info('Select **Plan a Trip** in the sidebar to create your itinerary.')
 if st.session_state.trip:st.subheader('Current trip');st.write(st.session_state.trip['destination'])
elif page=='Plan a Trip':
 st.title('🧳 Plan a Trip')
 with st.form('planner'):
  a,b=st.columns(2)
  with a:
   origin=st.text_input('Starting city','Nagpur');destination=st.text_input('Destination','Goa');start=st.date_input('Departure date',date.today()+timedelta(days=7));travelers=st.number_input('Travelers',1,30,2);style=st.selectbox('Travel style',['Budget','Moderate','Luxury','Adventure','Family','Romantic','Relaxation','Cultural'])
  with b:
   end=st.date_input('Return date',date.today()+timedelta(days=9));budget=st.number_input('Total budget (₹)',min_value=1,value=15000,step=1000);interests=st.multiselect('Interests',['Beaches','Nature','History','Food','Adventure','Shopping','Culture'],default=['Nature','Food']);transport=st.selectbox('Transport',['Train','Bus','Car','Flight']);accommodation=st.selectbox('Accommodation',['Hostel','Budget hotel','Mid-range hotel','Luxury hotel','Homestay'])
  submitted=st.form_submit_button('✨ Generate my itinerary',use_container_width=True)
 if submitted:
  try:st.session_state.trip=generate_trip({'origin':origin,'destination':destination,'start':start,'end':end,'travelers':travelers,'budget':budget,'style':style,'interests':interests,'transport':transport,'accommodation':accommodation});st.success('Trip generated!')
  except ValueError as e:st.error(str(e))
 if st.session_state.trip:show_trip(st.session_state.trip)
elif page=='Explore Destinations':
 st.title('🧭 Explore Destinations')
 origin=st.text_input('Starting location','Nagpur',key='explore_origin')
 budget=st.number_input('Total travel budget (₹)',min_value=1000,value=15000,step=1000)
 days=st.slider('Days',1,14,3)
 people=st.number_input('Travelers',1,20,2,key='explore_people')
 interests=st.multiselect('Interests',['Beach','Nature','History','Culture','Adventure','Food'],default=['Nature'],key='explore_interests')
 weather=st.selectbox('Preferred weather',['Any','Warm','Cool','Mild'])
 st.caption('Recommendations and prices are illustrative; weather preference is not a verified forecast filter.')
 for suggestion in destination_recommender(budget,days,people,interests,weather):
  name=suggestion['destination']
  with st.expander(f'{name} · estimated ₹{suggestion["estimated_total"]:,} total'):
   st.write('Attractions:',', '.join(suggestion['attractions']))
   st.write('Why:',suggestion['reason'])
   if st.button(f'Plan {name}',key='recommend_'+name):
    start=date.today()+timedelta(days=7)
    st.session_state.trip=generate_trip({'origin':origin,'destination':name,'start':start,'end':start+timedelta(days=days-1),'travelers':people,'budget':budget,'style':'Budget','interests':interests,'transport':'Train','accommodation':'Budget hotel'})
    st.success('Trip generated. Open Trip Details in the sidebar.')
elif page=='My Trips':
 st.title('💾 My Trips')
 for i,d,created in list_trips():
  a,b,c=st.columns([4,1,1]);a.write(f'**{d}** · {created}')
  if b.button('Load',key=f'load{i}'):st.session_state.trip=load_trip(i);st.success('Trip loaded. Open Trip Details.')
  if c.button('Delete',key=f'del{i}'):delete_trip(i);st.rerun()
elif page=='Trip Details':
 if st.session_state.trip:show_trip(st.session_state.trip)
 else:st.info('Create or load a trip first.')
elif page=='AI Travel Assistant':
 st.title('🤖 AI Travel Assistant');st.caption('Trip-editing commands run locally; Gemini is optional for open-ended questions. Prices and suggestions are illustrative. Try: Plan a 3-day trip to Goa for 2 people under ₹15,000.')
 for m in st.session_state.messages:
  with st.chat_message(m['role']):st.write(m['content'])
 q=st.chat_input('Ask: Make my trip cheaper, what to visit on day 2, packing checklist...')
 if q:
  st.session_state.messages.append({'role':'user','content':q});response,trip=answer(q,st.session_state.trip);st.session_state.trip=trip;st.session_state.messages.append({'role':'assistant','content':response});st.rerun()
elif page=='Settings':
 st.title('⚙️ Settings');st.write('AI mode:', 'Gemini key configured + local tools' if GEMINI_API_KEY else 'Rule-based demo');st.write('Set GEMINI_API_KEY in .env to enable Gemini for general questions.')
 st.write('The deterministic assistant can modify budget, duration, accommodation preference and itinerary activities without Gemini.');st.warning('Prices, accommodations, restaurant data, route pins and weather suggestions are illustrative unless explicitly verified.')
