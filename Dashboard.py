import streamlit as st
import requests

VACCINE_CHOICES = ["COVISHIELD","COVAXIN"]
AGE_CHOICES = [60,45,18]

Apis={
    "states":"https://cdn-api.co-vin.in/api/v2/admin/location/states",
    "dictricts":"https://cdn-api.co-vin.in/api/v2/admin/location/districts/{}",
    "bypincode":"https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByPin?pincode={0}&date={1}",
    "bydistrict":"https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByDistrict?district_id={0}&date={1}"
}
headers={
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
}

def about_dev():
    st.sidebar.title("About the developer")
    st.sidebar.markdown("""
    #### Hi there, I am Akshansh Kumar <img src="https://media.giphy.com/media/hvRJCLFzcasrR4ia7z/giphy.gif" width="25px">
    ###### Please visit my [github page](https://github.com/akshanshkmr) for more such utilities
    ###### If you liked my work and would like to support me, consider buying me a coffee 😄
    <br><a href="https://www.buymeacoffee.com/akshanshkmr" target="_blank">
    <img class="center" src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a> 
    """,unsafe_allow_html=True)

def get_states():
    res = requests.get(Apis['states'],headers=headers)
    return res.json()

def get_districts(state_id):
    res = requests.get(Apis['dictricts'].format(state_id),headers=headers)
    return res.json()

def get_vaccine_slots_by_pin(pincode, date):
    res = requests.get(Apis['bypincode'].format(pincode, date),headers=headers)
    return res.json()

def get_vaccine_slots_by_distirct(id, date):
    res = requests.get(Apis['bydistrict'].format(id, date),headers=headers)
    return res.json()

def format_session(session):
    centre_name = session['name']
    address = session['address']
    age_limit = session['min_age_limit']
    vaccine = session['vaccine']
    slots = session['slots']
    st.markdown("""
    ### {0}
    #### {1}
    ##### Age limit: `{2}`
    ##### Vaccine: `{3}`
    ##### Slots: `{4}`
    -----------------------
    """.format(centre_name,
    address,
    age_limit,
    vaccine,
    slots))

def show_slots(sessions):
    st.info(str(len(sessions)) + " centres found")
    for session in sessions:
        format_session(session)

def filter_by_vaccine(sessions, vaccine):
    filtred_sessions = [i for i in sessions if i['vaccine'] == vaccine]
    return filtred_sessions

def filter_by_age(sessions, age):
    filtred_sessions = [i for i in sessions if i['min_age_limit'] == age]
    return filtred_sessions

def find_by_pin(date):
    cols = st.beta_columns([.5, .5])
    pincode = cols[0].text_input("Enter pincode")
    vaccine = cols[1].selectbox("Vaccine", VACCINE_CHOICES)
    if pincode:
        with st.spinner("Fetching data ..."):
            sessions = [i for i in get_vaccine_slots_by_pin(pincode, date)['sessions']]
        if sessions:
            show_slots(filter_by_vaccine(sessions,vaccine))
        else:
            st.warning("No slots found!")

def find_by_district(date):
    cols = st.beta_columns([.33, .33, .33])
    vaccine = cols[2].selectbox("Vaccine", VACCINE_CHOICES)
    with st.spinner("Fetching data ..."):
        statename_to_id_map = {i['state_name']:i['state_id'] for i in get_states()['states']}
        st_id = statename_to_id_map[cols[0].selectbox("Select state", list(statename_to_id_map.keys()))]
    with st.spinner("Fetching data ..."):
        districtname_to_id_map = {i['district_name']:i['district_id'] for i in get_districts(st_id)['districts']}
        dst_id = districtname_to_id_map[cols[1].selectbox("Select District", list(districtname_to_id_map.keys()))]
    with st.spinner("Fetching data ..."):
        sessions = [i for i in get_vaccine_slots_by_distirct(dst_id, date)['sessions']]
    if sessions:   
        show_slots(filter_by_vaccine(sessions,vaccine))
    else:
        st.warning("No slots found!")

if __name__ == "__main__":
    st.set_page_config(page_title="Vaccination", layout='wide', initial_sidebar_state='collapsed')
    about_dev()
    st.title("Vaccination Slots")
    cols = st.beta_columns([.5, .5])
    choice = cols[0].radio("Find by",['Pincode','State/District'])
    date = cols[1].date_input("Select date").strftime("%d-%m-%Y")
    if choice == "Pincode":
        find_by_pin(date)
    elif choice == "State/District":
        find_by_district(date)
