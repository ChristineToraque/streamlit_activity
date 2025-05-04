import streamlit as st
import sqlalchemy as db
from sqlalchemy import text # Import text for literal SQL execution or parameterized queries
import pandas as pd
import hashlib # For password hashing
import os      # For generating a salt

# --- Database Connection using Streamlit Secrets ---
try:
    # Uses connection details from .streamlit/secrets.toml section [connections.mydb]
    conn = st.connection("mydb", type="sql")
    st.sidebar.success("Connected to Database!") # Optional: Confirmation message
except Exception as e:
    st.error(f"Failed to connect to the database using secrets.toml. Error: {e}")
    st.stop() # Stop execution if connection fails

# --- Define Table Structure (still useful for ORM-like operations) ---
metadata = db.MetaData()
users_table = db.Table('users', metadata,
                       db.Column('id', db.Integer, primary_key=True, autoincrement=True),
                       db.Column('name', db.String(50), nullable=False), # Added nullable=False for demonstration
                       db.Column('email', db.String(100), unique=True, nullable=False, index=True),
                       db.Column('password_hash', db.String(64), nullable=False), # SHA256 hex is 64 chars
                       db.Column('salt', db.String(32), nullable=False) # 16 bytes salt -> 32 hex chars
                       )
products_table = db.Table('products', metadata,
    db.Column('id', db.Integer, primary_key=True, autoincrement=True),
    db.Column('name', db.String(100), nullable=False),
    db.Column('category', db.String(50)),
    db.Column('price', db.Numeric(10, 2), nullable=False), # e.g., 12345678.90
    db.Column('added_by_email', db.String(100)) # Optional: track who added the product
)

# --- Create Table if it doesn't exist (run once) ---
# Use the engine provided by st.connection
try:
    with conn.session as s: # Get underlying SQLAlchemy session
        metadata.create_all(s.get_bind()) # Creates users and app_settings tables
except Exception as e:
    st.warning(f"Could not check/create tables. They might already exist. Error: {e}")

# --- User Password Hashing Utilities ---
def hash_user_password(password):
    """Hashes a password and returns salt (hex) and hash (hex)."""
    salt_bytes = os.urandom(16)  # Generate a new 16-byte salt
    salted_password = salt_bytes + password.encode('utf-8')
    hashed_password_hex = hashlib.sha256(salted_password).hexdigest()
    return salt_bytes.hex(), hashed_password_hex

def verify_user_password(provided_password, stored_salt_hex, stored_password_hash):
    """Checks a provided password against a stored salt and hash."""
    salt_bytes = bytes.fromhex(stored_salt_hex)
    salted_provided_password = salt_bytes + provided_password.encode('utf-8')
    hashed_provided_password_hex = hashlib.sha256(salted_provided_password).hexdigest()
    return hashed_provided_password_hex == stored_password_hash

# --- Initialize session state for authentication ---
if "authentication_status" not in st.session_state:
    st.session_state["authentication_status"] = False
    st.session_state["logged_in_user_email"] = None

# --- Login Functionality ---
def attempt_login():
    """Handles the login form and logic. Returns True if login is successful this interaction."""
    st.sidebar.title("Login")
    email = st.sidebar.text_input("Email", key="login_email")
    password = st.sidebar.text_input("Password", type="password", key="login_password")

    if st.sidebar.button("Login", key="login_button"):
        if not email or not password:
            st.sidebar.warning("Please enter both email and password.")
            return False

        try:
            user_data = conn.query(
                f"SELECT password_hash, salt FROM {users_table.name} WHERE email = :email",
                params={"email": email},
                ttl=0  # No cache for login attempts
            )
            if not user_data.empty:
                stored_hash = user_data['password_hash'].iloc[0]
                stored_salt = user_data['salt'].iloc[0]
                if verify_user_password(password, stored_salt, stored_hash):
                    st.session_state["authentication_status"] = True
                    st.session_state["logged_in_user_email"] = email
                    # st.sidebar.success("Login successful!") # Message shown on rerun
                    st.rerun()  # Important to update the app state immediately
                else:
                    st.sidebar.error("Invalid email or password.")
            else:
                st.sidebar.error("Invalid email or password.")
        except Exception as e:
            st.sidebar.error(f"Login error: {e}")
            return False
    return False

# --- Registration Functionality ---
def registration_section():
    st.subheader("Don't have an account? Register below.")
    with st.form("registration_form", clear_on_submit=True):
        reg_name = st.text_input("Full Name", key="reg_name")
        reg_email = st.text_input("Email Address", key="reg_email")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        reg_confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm_password")
        reg_submitted = st.form_submit_button("Register")

        if reg_submitted:
            if not all([reg_name, reg_email, reg_password, reg_confirm_password]):
                st.warning("Please fill all registration fields.")
            elif reg_password != reg_confirm_password:
                st.error("Passwords do not match.")
            elif len(reg_password) < 6: # Basic password length check
                st.error("Password must be at least 6 characters long.")
            else:
                # Check for email uniqueness
                try:
                    existing_user = conn.query(
                        f"SELECT id FROM {users_table.name} WHERE email = :email",
                        params={"email": reg_email},
                        ttl=0 # No cache for this check
                    )
                    if not existing_user.empty:
                        st.error("This email is already registered. Please use a different email or login.")
                    else:
                        # Hash password and insert user
                        salt_hex, hashed_pwd_hex = hash_user_password(reg_password)
                        with conn.session as s:
                            insert_stmt = users_table.insert().values(
                                name=reg_name,
                                email=reg_email,
                                password_hash=hashed_pwd_hex,
                                salt=salt_hex
                            )
                            s.execute(insert_stmt)
                            s.commit()
                        st.success(f"User '{reg_name}' registered successfully! Please log in using the sidebar.")
                except Exception as e:
                    st.error(f"Registration error: {e}")

# --- Main App Flow ---
if not st.session_state["authentication_status"]:
    st.title("Welcome to the Database App")
    attempt_login()  # Displays login form in sidebar and handles login attempts
    registration_section() # Displays registration form in the main area

    # Additional guidance if not yet logged in after forms are shown
    if not st.session_state["authentication_status"]:
        st.info("Please log in using the sidebar, or register a new account above to access application features.")
        st.stop() # Stop further execution until logged in

# --- Authenticated App Content (if login was successful) ---
if st.session_state["authentication_status"]:
    st.sidebar.success(f"Logged in as: {st.session_state['logged_in_user_email']}")
    if st.sidebar.button("Logout", key="logout_button"):
        st.session_state["authentication_status"] = False
        st.session_state["logged_in_user_email"] = None
        st.rerun()

    st.title("Database Interaction with Streamlit")

    st.header("Current Registered Users")

    # Display data from the database
    try:
        # Use conn.query for SELECT statements, returns a DataFrame directly
        # Select only non-sensitive columns
        df_users = conn.query(f"SELECT id, name, email FROM {users_table.name}", ttl=60) # Cache for 60 seconds
        st.dataframe(df_users, use_container_width=True)
    except Exception as e:
        st.error(f"Error reading data: {e}")
        st.info("The database might be empty.")

    # --- Add New Product Form (for logged-in users) ---
    st.header("Add New Product")
    with st.form("product_form", clear_on_submit=True):
        product_name = st.text_input("Product Name")
        product_category = st.text_input("Product Category (e.g., Electronics, Books)")
        product_price = st.number_input("Price", min_value=0.0, format="%.2f")
        product_submitted = st.form_submit_button("Add Product")

        if product_submitted:
            if product_name and product_price > 0: # Basic validation
                try:
                    with conn.session as s:
                        insert_stmt = products_table.insert().values(
                            name=product_name,
                            category=product_category,
                            price=product_price,
                            added_by_email=st.session_state.get("logged_in_user_email") # Store who added it
                        )
                        s.execute(insert_stmt)
                        s.commit()
                    st.success(f"Product '{product_name}' added successfully!")
                except Exception as e:
                    st.error(f"Error adding product: {e}")
            else:
                st.warning("Please fill in at least Product Name and a valid Price.")

    st.header("Current Products in Database")
    try:
        df_products = conn.query(f"SELECT id, name, category, price, added_by_email FROM {products_table.name}", ttl=60)
        st.dataframe(df_products, use_container_width=True)
    except Exception as e:
        st.error(f"Error reading products: {e}")