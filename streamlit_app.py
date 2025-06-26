import streamlit as st
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
import os

# Set page configuration
st.set_page_config(page_title="Enhanced Coding Interface", page_icon='💻')

# Initialize session state for file management and system instructions
if 'files' not in st.session_state:
    st.session_state.files = {
        "main.py": {"content": "print('Hello, World!')"}
    }

if 'current_file' not in st.session_state:
    st.session_state.current_file = "main.py"

if 'system_instructions' not in st.session_state:
    st.session_state.system_instructions = "Write clear and concise code. Follow best practices and ensure the code is well-commented."

# Function to apply syntax highlighting
def syntax_highlight(code, language):
    try:
        lexer = get_lexer_by_name(language)
    except:
        lexer = get_lexer_by_name("text")
    formatter = HtmlFormatter()
    return highlight(code, lexer, formatter)

# Sidebar for file management and system instructions
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

# Button to save the current file to disk
if st.sidebar.button("Save to Disk"):
    file_path = os.path.join(os.getcwd(), st.session_state.current_file)
    with open(file_path, 'w') as f:
        f.write(st.session_state.files[st.session_state.current_file]["content"])
    st.sidebar.success(f"File saved to {file_path}")

# Button to load a file from disk
uploaded_file = st.sidebar.file_uploader("Load from Disk", type=None)
if uploaded_file is not None:
    file_content = uploaded_file.read().decode("utf-8")
    st.session_state.files[uploaded_file.name] = {"content": file_content}
    st.session_state.current_file = uploaded_file.name
    st.sidebar.success(f"File loaded: {uploaded_file.name}")

# Text area for custom system instructions
st.sidebar.title("System Instructions")
system_instructions = st.sidebar.text_area(
    "Custom System Instructions",
    value=st.session_state.system_instructions,
    height=150,
    key="system_instructions"
)

# Update system instructions in session state
st.session_state.system_instructions = system_instructions

# Main coding interface
st.title(f"Editing: {st.session_state.current_file}")

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
