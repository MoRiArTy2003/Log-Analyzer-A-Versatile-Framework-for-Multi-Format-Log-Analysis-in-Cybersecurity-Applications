import streamlit as st
import firebase_admin

from firebase_admin import credentials
from firebase_admin import auth

if not firebase_admin._apps:
	# Linking of Database to The Application
	cred = credentials.Certificate(r'D:\Programming\streamlit\log-analyser-960ca-efb8cc98a12b.json')
	firebase_admin.initialize_app(cred)

def app():
	st.title("Welcome to Log Analyser")
    
	choice = st.selectbox('Login/Signup' , ['Login','Sign Up'])
 
	def f():
		try:
			user = auth.get_user_by_email(email)
			# print(user.uid)
			st.success('Login Successfull')

           
		except:
			st.warning('Login Failed')
 
	if choice == 'Login':
     
		email = st.text_input('Email Address')
		password = st.text_input('Password', type= 'password')
		st.button('Login', on_click=f)
  
	else:
	
		email = st.text_input('Email Address')
		password = st.text_input('Password', type='password')

		username = st.text_input('Enter the unique username')
  
		if st.button('Create my account'):
			try:
				user = auth.create_user(email = email, password = password, uid = username)

				st.success('Account created successfully')
				st.markdown('Please Login using your email and password')
				# st.balloons()
			except Exception as e:
				st.error(f"Error Creating Account: {e}")
  
if __name__ == '__main__':
	app()