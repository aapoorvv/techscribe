import streamlit as st
import sqlite3

st.set_page_config(
    page_title="TechScribe",  # Set the title
    page_icon="📘",                     # Optional: Set a favicon (emoji or image link)
    layout="wide",                      # Optional: Choose layout ('centered' or 'wide')
)

# Function to create a new SQLite3 database and table for blog posts
def create_database():
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS posts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 title TEXT NOT NULL,
                 content TEXT NOT NULL,
                 author TEXT NOT NULL)''')
    conn.commit()
    conn.close()


# Function to create a new SQLite3 database and table for user accounts
def create_user_database():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT UNIQUE NOT NULL,
                 password TEXT NOT NULL)''')
    conn.commit()
    conn.close()

# Function to register a new user
def register_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

# Function to authenticate a user
def authenticate_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()
    return user

# Function to add a new post to the database
def add_post(title, content,author):
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()
    c.execute("INSERT INTO posts (title, content, author) VALUES (?, ?, ?)", (title, content, author))
    conn.commit()
    conn.close()

# Function to edit an existing post in the database
def edit_post(post_id, title, content):
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()
    c.execute("UPDATE posts SET title=?, content=? WHERE id=?", (title, content, post_id))
    conn.commit()
    conn.close()

# Function to delete a post from the database
def delete_post(post_id):
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()
    c.execute("DELETE FROM posts WHERE id=?", (post_id,))
    conn.commit()
    conn.close()

# Function to retrieve all posts from the database
def get_all_posts():
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()
    c.execute("SELECT * FROM posts")  # Ensure this fetches all columns
    posts = c.fetchall()
    conn.close()
    return posts


# Function to retrieve a single post by its ID from the database
def get_post_by_id(post_id):
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()
    c.execute("SELECT * FROM posts WHERE id=?", (post_id,))
    post = c.fetchone()
    conn.close()
    return post

# Streamlit interface for user registration
def registration():
    st.title("User Registration")
    username = st.text_input("Enter username:")
    password = st.text_input("Enter password:", type="password")
    if st.button("Register"):
        if username and password:
            create_user_database()
            register_user(username, password)
            st.success("Registration successful! Please login.")
        else:
            st.warning("Please enter both username and password.")

# Streamlit interface for user login
def login():
    st.title("User Login")
    username = st.text_input("Enter username:")
    password = st.text_input("Enter password:", type="password")
    if st.button("Login"):
        if username and password:
            user = authenticate_user(username, password)
            if user:
                st.success(f"Welcome, {username}!")
                st.session_state.logged_in = True
                st.session_state.username = username  # Save the username
            else:
                st.error("Invalid username or password.")
        else:
            st.warning("Please enter both username and password.")

# Function to retrieve posts by a specific author
def get_posts_by_author(author):
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()
    c.execute("SELECT * FROM posts WHERE author=? ORDER BY id DESC", (author,))
    posts = c.fetchall()
    conn.close()
    return posts


# Streamlit interface for user logout
def logout():
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.success("You have been logged out.")

# Streamlit interface
def main():
    st.title("Techscribe")

    # Create database if not exists
    create_database()

    # Sidebar
    st.sidebar.header("Menu")
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        menu_choice = st.sidebar.selectbox("Select operation", ("Feed", "Add Post", "Edit Post", "Delete Post", "View Posts", "Logout"))
    else:
        menu_choice = st.sidebar.selectbox("Select operation", ("Feed", "Login", "Register"))
        
    if menu_choice == "Register":
        registration()
    elif menu_choice == "Login":
        login()
    elif menu_choice == "Logout":
        logout()
    elif menu_choice == "Feed":
        st.header("Latest Posts")

        # Check if an author is selected in session state
        if 'selected_author' in st.session_state and st.session_state.selected_author:
            author = st.session_state.selected_author
            st.subheader(f"Posts by {author}")
            posts = get_posts_by_author(author)
            if posts:
                for post in posts:
                    st.write(f"**Post ID:** {post[0]}")
                    st.write(f"**Title:** {post[1]}")
                    st.write(f"**Author:** {post[3]}")
                    st.write(f"**Content:** {post[2]}")
                    st.write("---")
            else:
                st.info(f"No posts found by {author}.")
            
            # Button to go back to all posts
            if st.button("Back to All Posts"):
                st.session_state.selected_author = None  # Clear the selected author
        else:
            # Display all posts
            posts = get_all_posts()
            if posts:
                for post in reversed(posts):  # Show latest posts first
                    st.write(f"**Post ID:** {post[0]}")
                    st.write(f"**Title:** {post[1]}")
                    author_name = post[3]
                    st.write(f"**Author:** {author_name}")

                    # Button to view posts by this author
                    if st.button(f"View posts by {author_name}", key=f"author_{post[0]}"):
                        st.session_state.selected_author = author_name
                    
                    st.write(f"**Content:** {post[2]}")
                    st.write("---")
            else:
                st.info("No posts found.")



    elif menu_choice == "Add Post" and st.session_state.logged_in:
        st.header("Add New Post")
        title = st.text_input("Enter title:")
        content = st.text_area("Enter content:")
        if st.button("Add Post"):
            if title and content:
                # Get the logged-in user's username
                author = st.session_state.get("username", "Anonymous")
                add_post(title, content, author)
                st.success("Post added successfully!")
            else:
                st.warning("Please enter both title and content.")

    elif menu_choice == "Edit Post" and st.session_state.logged_in:
        st.header("Edit Post")
        post_id = st.number_input("Enter post ID to edit:")
        if post_id:
            post = get_post_by_id(post_id)
            if post:
                st.write(f"Current Title: {post[1]}")
                new_title = st.text_input("Enter new title:", value=post[1])
                st.write(f"Current Content: {post[2]}")
                new_content = st.text_area("Enter new content:", value=post[2])
                if st.button("Update Post"):
                    edit_post(post_id, new_title, new_content)
                    st.success("Post updated successfully!")
            else:
                st.warning("Post not found.")
    elif menu_choice == "Delete Post" and st.session_state.logged_in:
        st.header("Delete Post")
        post_id = st.number_input("Enter post ID to delete:")
        if st.button("Delete Post"):
            if post_id:
                post = get_post_by_id(post_id)
                if post:
                    delete_post(post_id)
                    st.success("Post deleted successfully!")
                else:
                    st.warning("Post not found.")
            else:
                st.warning("Please enter post ID.")
    elif menu_choice == "View Posts":
        st.header("All Posts")
        posts = get_all_posts()
        if posts:
            for post in posts:
                st.write(f"**Post ID:** {post[0]}")
                st.write(f"**Title:** {post[1]}")
                st.write(f"**Author:** {post[3]}")  # Author's name
                st.write(f"**Content:** {post[2]}")
                st.write("---")
        else:
            st.info("No posts found.")

    # Add contact details to the sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Contact Me: ")
    st.sidebar.markdown("[Email](Mailto:apoorvg26@gmail.com)")
    st.sidebar.markdown("[LinkedIn](https://linkedin.com/in/aapoorvv)")



if __name__ == "__main__":
    main()