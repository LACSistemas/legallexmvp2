import streamlit as st
import hashlib

class AuthSystem:
    USERS = {
        "Caper": {
            "password": "Caper",
            "role": "client"
        },
        "lucasaurich": {
            "password": "caneta123", 
            "role": "admin"
        }
    }
    
    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def authenticate(username: str, password: str) -> dict:
        if username in AuthSystem.USERS:
            user_data = AuthSystem.USERS[username]
            if user_data["password"] == password:
                return {
                    "username": username,
                    "role": user_data["role"],
                    "authenticated": True
                }
        return {"authenticated": False}
    
    @staticmethod
    def check_authentication():
        if "authenticated" not in st.session_state:
            st.session_state.authenticated = False
        
        if not st.session_state.authenticated:
            return AuthSystem.show_login_page()
        
        return True
    
    @staticmethod
    def show_login_page():
        st.set_page_config(
            page_title="LegalLex - Login",
            page_icon="⚖️",
            layout="centered"
        )
        
        # Display logo (centered)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            try:
                st.image("legallexmvplogo.png", width=200)
            except:
                st.title("⚖️ LegalLex")
        
        st.markdown("---")
        st.subheader("🔐 Login")
        
        with st.form("login_form"):
            username = st.text_input("Usuário")
            password = st.text_input("Senha", type="password")
            submitted = st.form_submit_button("Entrar")
            
            if submitted:
                auth_result = AuthSystem.authenticate(username, password)
                if auth_result["authenticated"]:
                    st.session_state.authenticated = True
                    st.session_state.username = auth_result["username"]
                    st.session_state.user_role = auth_result["role"]
                    st.success("Login realizado com sucesso!")
                    st.rerun()
                else:
                    st.error("Usuário ou senha inválidos!")
        
        return False
    
    @staticmethod
    def logout():
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.user_role = None
        st.rerun()
    
    @staticmethod
    def get_current_user():
        if st.session_state.get("authenticated", False):
            return {
                "username": st.session_state.get("username"),
                "role": st.session_state.get("user_role")
            }
        return None