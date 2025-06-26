import streamlit as st
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
import os
from git import Repo, GitCommandError

# Set page configuration
st.set_page_config(page_title="Multi-Tab App with Git and AI Reference", page_icon='💻')

# Initialize session state for file management, chat messages, and AI references
if 'files' not in st.session_state:
    st.session_state.files = {
        "main.py": {"content": "print('Hello, World!')"}
    }
if 'current_file' not in st.session_state:
    st.session_state.current_file = "main.py"
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'repo' not in st.session_state:
    st.session_state.repo = None
if 'ai_references' not in st.session_state:
    st.session_state.ai_references = {}

# Function to apply syntax highlighting
def syntax_highlight(code, language):
    try:
        lexer = get_lexer_by_name(language)
    except:
        lexer = get_lexer_by_name("text")
    formatter = HtmlFormatter()
    return highlight(code, lexer, formatter)

# Function to simulate AI response
def get_ai_response(user_input):
    return f"Response to '{user_input}'"

# Function to scan and store file contents for AI reference
def scan_repository_for_ai(repo_path):
    ai_references = {}
    for root, _, files in os.walk(repo_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    ai_references[file_path] = f.read()
            except UnicodeDecodeError:
                # Skip binary files
                continue
    return ai_references

# Create tabs
tab1, tab2 = st.tabs(["Chat with AI", "Code Editor"])

with tab1:
    st.title("Chat with AI")

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Simulate AI response
        ai_response = get_ai_response(prompt)
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        with st.chat_message("assistant"):
            st.markdown(ai_response)

with tab2:
    st.title("Code Editor")

    # Sidebar for file and Git management
    st.sidebar.title("File Management")

    # Create a new file
    new_file_name = st.sidebar.text_input("New File Name", key="new_file_name")
    if st.sidebar.button("Create File"):
        if new_file_name:
            if new_file_name not in st.session_state.files:
                st.session_state.files[new_file_name] = {"content": ""}
                st.session_state.current_file = new_file_name
            else:
                st.sidebar.error("File already exists!")
        else:
            st.sidebar.error("Please enter a file name!")

    # File selection dropdown
    file_names = list(st.session_state.files.keys())
    selected_file = st.sidebar.selectbox("Select File", file_names, index=file_names.index(st.session_state.current_file))

    # Update current file if selection changes
    if selected_file != st.session_state.current_file:
        st.session_state.current_file = selected_file

    # Button to delete the current file
    if st.sidebar.button("Delete File"):
        if len(st.session_state.files) > 1:
            del st.session_state.files[st.session_state.current_file]
            st.session_state.current_file = file_names[0]
        else:
            st.sidebar.error("Cannot delete the only file!")

    # Git operations
    st.sidebar.title("Git Operations")
    repo_url = st.sidebar.text_input("Repository URL", key="repo_url")
    if st.sidebar.button("Clone Repository"):
        try:
            repo_dir = os.path.join(os.getcwd(), repo_url.split('/')[-1].replace('.git', ''))
            st.session_state.repo = Repo.clone_from(repo_url, repo_dir)
            st.session_state.ai_references = scan_repository_for_ai(repo_dir)
            st.sidebar.success("Repository cloned and scanned successfully!")
        except GitCommandError as e:
            st.sidebar.error(f"Error cloning repository: {e}")

    if st.session_state.repo:
        if st.sidebar.button("Add All Files"):
            st.session_state.repo.git.add(all=True)
            st.sidebar.success("All files added to staging!")

        commit_message = st.sidebar.text_input("Commit Message", key="commit_message")
        if st.sidebar.button("Commit Changes"):
            if commit_message:
                try:
                    st.session_state.repo.index.commit(commit_message)
                    st.sidebar.success("Changes committed successfully!")
                except GitCommandError as e:
                    st.sidebar.error(f"Error committing changes: {e}")
            else:
                st.sidebar.error("Please enter a commit message!")

        if st.sidebar.button("Push Changes"):
            try:
                origin = st.session_state.repo.remote(name='origin')
                origin.push()
                st.sidebar.success("Changes pushed successfully!")
            except GitCommandError as e:
                st.sidebar.error(f"Error pushing changes: {e}")

    # Text area for editing the current file
    file_content = st.text_area(
        "Code",
        value=st.session_state.files[st.session_state.current_file]["content"],
        height=400,
        key="code_editor"
    )

    # Update file content in session state
    st.session_state.files[st.session_state.current_file]["content"] = file_content

    # Display syntax highlighted code
    st.subheader("Syntax Highlighted Code")
    language = st.session_state.current_file.split('.')[-1]
    highlighted_code = syntax_highlight(file_content, language)
    st.markdown(highlighted_code, unsafe_allow_html=True)

    # Display the list of files and their content
    st.subheader("Files in Session")
    for file_name, file_data in st.session_state.files.items():
        st.write(f"**{file_name}**")
        st.code(file_data["content"])

    # Display AI references
    st.subheader("AI References")
    for file_path, content in st.session_state.ai_references.items():
        st.write(f"**{file_path}**")
        st.code(content)
