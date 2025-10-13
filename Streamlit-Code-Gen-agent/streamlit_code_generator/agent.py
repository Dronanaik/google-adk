"""
Streamlit Code Generator Agent using Google ADK

This agent helps generate Streamlit applications based on user requirements.
It can create complete Streamlit apps with various components like charts,
forms, data tables, and interactive widgets.
"""

from google.adk.agents import Agent
from typing import Dict, List
import os


def generate_streamlit_boilerplate(app_title: str, description: str) -> Dict[str, str]:
    """
    Generates a basic Streamlit application boilerplate.
    
    Args:
        app_title (str): The title of the Streamlit application
        description (str): A brief description of what the app does
    
    Returns:
        dict: Contains status and the generated code
    """
    code = f'''"""
{app_title}

{description}
"""

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="{app_title}",
    page_icon="🚀",
    layout="wide"
)

# Main title
st.title("{app_title}")
st.markdown("---")

# Description
st.markdown("""
{description}
""")

# Main content area
def main():
    st.write("Welcome to your Streamlit app!")
    
    # Add your app logic here
    st.info("Start building your app by adding components below.")

if __name__ == "__main__":
    main()
'''
    
    return {
        "status": "success",
        "code": code,
        "message": f"Generated boilerplate for '{app_title}'"
    }


def add_data_visualization(chart_type: str, data_source: str = "sample") -> Dict[str, str]:
    """
    Generates Streamlit code for data visualization components.
    
    Args:
        chart_type (str): Type of chart (line, bar, scatter, area, map)
        data_source (str): Data source type (sample, csv, api)
    
    Returns:
        dict: Contains status and the generated code snippet
    """
    chart_code = {
        "line": '''
# Line Chart
import pandas as pd
import numpy as np

chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=['A', 'B', 'C']
)

st.line_chart(chart_data)
''',
        "bar": '''
# Bar Chart
import pandas as pd
import numpy as np

chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=['Category A', 'Category B', 'Category C']
)

st.bar_chart(chart_data)
''',
        "scatter": '''
# Scatter Plot using Plotly
import pandas as pd
import numpy as np
import plotly.express as px

df = pd.DataFrame({
    'x': np.random.randn(100),
    'y': np.random.randn(100),
    'size': np.random.randint(10, 100, 100)
})

fig = px.scatter(df, x='x', y='y', size='size')
st.plotly_chart(fig, use_container_width=True)
''',
        "area": '''
# Area Chart
import pandas as pd
import numpy as np

chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=['Series 1', 'Series 2', 'Series 3']
)

st.area_chart(chart_data)
''',
        "map": '''
# Map Visualization
import pandas as pd
import numpy as np

# Generate random coordinates (example: around San Francisco)
map_data = pd.DataFrame(
    np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
    columns=['lat', 'lon']
)

st.map(map_data)
'''
    }
    
    if chart_type.lower() not in chart_code:
        return {
            "status": "error",
            "message": f"Chart type '{chart_type}' not supported. Available: line, bar, scatter, area, map"
        }
    
    return {
        "status": "success",
        "code": chart_code[chart_type.lower()],
        "message": f"Generated {chart_type} chart code"
    }


def add_user_input_components(component_type: str) -> Dict[str, str]:
    """
    Generates Streamlit code for user input components.
    
    Args:
        component_type (str): Type of input (text, number, slider, selectbox, multiselect, 
                             checkbox, radio, date, time, file_uploader, form)
    
    Returns:
        dict: Contains status and the generated code snippet
    """
    input_components = {
        "text": '''
# Text Input
user_input = st.text_input("Enter some text:", placeholder="Type here...")
if user_input:
    st.write(f"You entered: {user_input}")
''',
        "number": '''
# Number Input
number = st.number_input("Enter a number:", min_value=0, max_value=100, value=50, step=1)
st.write(f"Selected number: {number}")
''',
        "slider": '''
# Slider
value = st.slider("Select a value:", min_value=0, max_value=100, value=50)
st.write(f"Selected value: {value}")
''',
        "selectbox": '''
# Select Box
option = st.selectbox(
    "Choose an option:",
    ["Option 1", "Option 2", "Option 3"]
)
st.write(f"You selected: {option}")
''',
        "multiselect": '''
# Multi-Select
options = st.multiselect(
    "Choose multiple options:",
    ["Option 1", "Option 2", "Option 3", "Option 4"],
    default=["Option 1"]
)
st.write(f"You selected: {', '.join(options)}")
''',
        "checkbox": '''
# Checkbox
agree = st.checkbox("I agree to the terms and conditions")
if agree:
    st.success("Thank you for agreeing!")
''',
        "radio": '''
# Radio Buttons
choice = st.radio(
    "Choose one:",
    ["Option A", "Option B", "Option C"]
)
st.write(f"You chose: {choice}")
''',
        "date": '''
# Date Input
import datetime

date = st.date_input(
    "Select a date:",
    value=datetime.date.today()
)
st.write(f"Selected date: {date}")
''',
        "time": '''
# Time Input
import datetime

time = st.time_input(
    "Select a time:",
    value=datetime.time(12, 0)
)
st.write(f"Selected time: {time}")
''',
        "file_uploader": '''
# File Uploader
uploaded_file = st.file_uploader("Choose a file", type=['csv', 'txt', 'xlsx'])
if uploaded_file is not None:
    st.success(f"File uploaded: {uploaded_file.name}")
    # Process the file here
''',
        "form": '''
# Form with Multiple Inputs
with st.form("my_form"):
    st.write("Fill out this form:")
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=0, max_value=120)
    email = st.text_input("Email")
    
    submitted = st.form_submit_button("Submit")
    if submitted:
        st.success(f"Form submitted! Name: {name}, Age: {age}, Email: {email}")
'''
    }
    
    if component_type.lower() not in input_components:
        return {
            "status": "error",
            "message": f"Component type '{component_type}' not supported. Available: {', '.join(input_components.keys())}"
        }
    
    return {
        "status": "success",
        "code": input_components[component_type.lower()],
        "message": f"Generated {component_type} input component code"
    }


def add_layout_components(layout_type: str) -> Dict[str, str]:
    """
    Generates Streamlit code for layout components.
    
    Args:
        layout_type (str): Type of layout (sidebar, columns, tabs, expander, container)
    
    Returns:
        dict: Contains status and the generated code snippet
    """
    layout_components = {
        "sidebar": '''
# Sidebar
with st.sidebar:
    st.header("Sidebar")
    st.write("This is the sidebar content")
    
    # Add sidebar widgets
    sidebar_option = st.selectbox(
        "Choose an option:",
        ["Option 1", "Option 2", "Option 3"]
    )
    
    st.info("Sidebar information")
''',
        "columns": '''
# Columns Layout
col1, col2, col3 = st.columns(3)

with col1:
    st.header("Column 1")
    st.write("Content for column 1")

with col2:
    st.header("Column 2")
    st.write("Content for column 2")

with col3:
    st.header("Column 3")
    st.write("Content for column 3")
''',
        "tabs": '''
# Tabs Layout
tab1, tab2, tab3 = st.tabs(["Tab 1", "Tab 2", "Tab 3"])

with tab1:
    st.header("Tab 1 Content")
    st.write("This is the content of tab 1")

with tab2:
    st.header("Tab 2 Content")
    st.write("This is the content of tab 2")

with tab3:
    st.header("Tab 3 Content")
    st.write("This is the content of tab 3")
''',
        "expander": '''
# Expander (Collapsible Section)
with st.expander("Click to expand"):
    st.write("This content is hidden by default")
    st.write("You can add any Streamlit components here")
    st.image("https://via.placeholder.com/300")
''',
        "container": '''
# Container
container = st.container()

with container:
    st.write("This is inside a container")
    st.button("Click me!")

st.write("This is outside the container")
'''
    }
    
    if layout_type.lower() not in layout_components:
        return {
            "status": "error",
            "message": f"Layout type '{layout_type}' not supported. Available: {', '.join(layout_components.keys())}"
        }
    
    return {
        "status": "success",
        "code": layout_components[layout_type.lower()],
        "message": f"Generated {layout_type} layout code"
    }


def add_data_display_components(display_type: str) -> Dict[str, str]:
    """
    Generates Streamlit code for data display components.
    
    Args:
        display_type (str): Type of display (dataframe, table, metric, json, code)
    
    Returns:
        dict: Contains status and the generated code snippet
    """
    display_components = {
        "dataframe": '''
# Interactive DataFrame
import pandas as pd
import numpy as np

df = pd.DataFrame(
    np.random.randn(10, 5),
    columns=['Column A', 'Column B', 'Column C', 'Column D', 'Column E']
)

st.dataframe(df, use_container_width=True)
''',
        "table": '''
# Static Table
import pandas as pd
import numpy as np

df = pd.DataFrame(
    np.random.randn(5, 3),
    columns=['Column 1', 'Column 2', 'Column 3']
)

st.table(df)
''',
        "metric": '''
# Metrics Display
col1, col2, col3 = st.columns(3)

col1.metric("Temperature", "70 °F", "1.2 °F")
col2.metric("Wind", "9 mph", "-8%")
col3.metric("Humidity", "86%", "4%")
''',
        "json": '''
# JSON Display
import json

data = {
    "name": "John Doe",
    "age": 30,
    "city": "New York",
    "hobbies": ["reading", "coding", "hiking"]
}

st.json(data)
''',
        "code": '''
# Code Display
code = """
def hello_world():
    print("Hello, World!")
    return True
"""

st.code(code, language="python")
'''
    }
    
    if display_type.lower() not in display_components:
        return {
            "status": "error",
            "message": f"Display type '{display_type}' not supported. Available: {', '.join(display_components.keys())}"
        }
    
    return {
        "status": "success",
        "code": display_components[display_type.lower()],
        "message": f"Generated {display_type} display code"
    }


def create_complete_streamlit_app(
    app_type: str,
    app_title: str = "My Streamlit App"
) -> Dict[str, str]:
    """
    Creates a complete Streamlit application based on the app type.
    
    Args:
        app_type (str): Type of app (dashboard, data_explorer, form_app, calculator, ml_demo)
        app_title (str): Title of the application
    
    Returns:
        dict: Contains status and the complete application code
    """
    
    apps = {
        "dashboard": f'''"""
{app_title} - Dashboard
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="{app_title}", page_icon="📊", layout="wide")

st.title("📊 {app_title}")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("Dashboard Controls")
    date_range = st.date_input("Select Date Range", [])
    metric_type = st.selectbox("Metric Type", ["Revenue", "Users", "Engagement"])
    st.markdown("---")
    st.info("Dashboard updated in real-time")

# Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", "$45,231", "+12%")
col2.metric("Active Users", "1,234", "+5%")
col3.metric("Conversion Rate", "3.2%", "-0.5%")
col4.metric("Avg. Session", "4m 32s", "+2%")

st.markdown("---")

# Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("Revenue Trend")
    chart_data = pd.DataFrame(
        np.random.randn(30, 1) * 100 + 1000,
        columns=['Revenue']
    )
    st.line_chart(chart_data)

with col2:
    st.subheader("User Distribution")
    pie_data = pd.DataFrame({{
        'Category': ['Mobile', 'Desktop', 'Tablet'],
        'Users': [45, 35, 20]
    }})
    fig = px.pie(pie_data, values='Users', names='Category')
    st.plotly_chart(fig, use_container_width=True)

# Data Table
st.subheader("Recent Transactions")
df = pd.DataFrame({{
    'Date': pd.date_range('2024-01-01', periods=10),
    'Transaction ID': [f'TXN{{i:04d}}' for i in range(1, 11)],
    'Amount': np.random.randint(100, 1000, 10),
    'Status': np.random.choice(['Completed', 'Pending'], 10)
}})
st.dataframe(df, use_container_width=True)
''',
        
        "data_explorer": f'''"""
{app_title} - Data Explorer
"""

import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="{app_title}", page_icon="🔍", layout="wide")

st.title("🔍 {app_title}")
st.markdown("Upload and explore your data")
st.markdown("---")

# File Upload
uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    # Data Overview
    st.subheader("Data Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("Rows", df.shape[0])
    col2.metric("Columns", df.shape[1])
    col3.metric("Memory", f"{{df.memory_usage(deep=True).sum() / 1024:.2f}} KB")
    
    # Display Data
    st.subheader("Data Preview")
    st.dataframe(df.head(10), use_container_width=True)
    
    # Statistics
    st.subheader("Statistical Summary")
    st.dataframe(df.describe(), use_container_width=True)
    
    # Column Analysis
    st.subheader("Column Analysis")
    selected_column = st.selectbox("Select column to analyze:", df.columns)
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("Value Counts")
        st.write(df[selected_column].value_counts())
    
    with col2:
        st.write("Distribution")
        st.bar_chart(df[selected_column].value_counts())
else:
    st.info("Please upload a CSV file to get started")
    
    # Sample data
    st.subheader("Or try with sample data")
    if st.button("Load Sample Data"):
        df = pd.DataFrame({{
            'Name': ['Alice', 'Bob', 'Charlie', 'David'],
            'Age': [25, 30, 35, 40],
            'City': ['New York', 'London', 'Paris', 'Tokyo']
        }})
        st.dataframe(df)
''',
        
        "form_app": f'''"""
{app_title} - Form Application
"""

import streamlit as st
import datetime

st.set_page_config(page_title="{app_title}", page_icon="📝", layout="centered")

st.title("📝 {app_title}")
st.markdown("Fill out the form below")
st.markdown("---")

with st.form("main_form"):
    st.subheader("Personal Information")
    
    col1, col2 = st.columns(2)
    with col1:
        first_name = st.text_input("First Name*")
        email = st.text_input("Email*")
        phone = st.text_input("Phone Number")
    
    with col2:
        last_name = st.text_input("Last Name*")
        date_of_birth = st.date_input("Date of Birth")
        country = st.selectbox("Country", ["USA", "UK", "Canada", "Other"])
    
    st.markdown("---")
    st.subheader("Additional Information")
    
    interests = st.multiselect(
        "Interests",
        ["Technology", "Sports", "Music", "Art", "Travel", "Reading"]
    )
    
    comments = st.text_area("Comments or Questions")
    
    agree = st.checkbox("I agree to the terms and conditions*")
    
    st.markdown("---")
    submitted = st.form_submit_button("Submit Form", type="primary")
    
    if submitted:
        if not first_name or not last_name or not email or not agree:
            st.error("Please fill in all required fields (*) and agree to terms")
        else:
            st.success("Form submitted successfully!")
            st.balloons()
            
            # Display submitted data
            with st.expander("View Submitted Data"):
                st.write(f"**Name:** {{first_name}} {{last_name}}")
                st.write(f"**Email:** {{email}}")
                st.write(f"**Phone:** {{phone}}")
                st.write(f"**Country:** {{country}}")
                st.write(f"**Interests:** {{', '.join(interests)}}")
                st.write(f"**Comments:** {{comments}}")
''',
        
        "calculator": f'''"""
{app_title} - Calculator
"""

import streamlit as st

st.set_page_config(page_title="{app_title}", page_icon="🔢", layout="centered")

st.title("🔢 {app_title}")
st.markdown("Perform basic calculations")
st.markdown("---")

# Calculator Type
calc_type = st.radio(
    "Select Calculator Type:",
    ["Basic Calculator", "BMI Calculator", "Loan Calculator"]
)

st.markdown("---")

if calc_type == "Basic Calculator":
    col1, col2 = st.columns(2)
    
    with col1:
        num1 = st.number_input("First Number", value=0.0)
    with col2:
        num2 = st.number_input("Second Number", value=0.0)
    
    operation = st.selectbox("Operation", ["Add", "Subtract", "Multiply", "Divide"])
    
    if st.button("Calculate", type="primary"):
        if operation == "Add":
            result = num1 + num2
        elif operation == "Subtract":
            result = num1 - num2
        elif operation == "Multiply":
            result = num1 * num2
        elif operation == "Divide":
            result = num1 / num2 if num2 != 0 else "Error: Division by zero"
        
        st.success(f"Result: {{result}}")

elif calc_type == "BMI Calculator":
    col1, col2 = st.columns(2)
    
    with col1:
        weight = st.number_input("Weight (kg)", min_value=0.0, value=70.0)
    with col2:
        height = st.number_input("Height (m)", min_value=0.0, value=1.75)
    
    if st.button("Calculate BMI", type="primary"):
        bmi = weight / (height ** 2)
        st.metric("Your BMI", f"{{bmi:.2f}}")
        
        if bmi < 18.5:
            st.info("Underweight")
        elif 18.5 <= bmi < 25:
            st.success("Normal weight")
        elif 25 <= bmi < 30:
            st.warning("Overweight")
        else:
            st.error("Obese")

elif calc_type == "Loan Calculator":
    loan_amount = st.number_input("Loan Amount ($)", min_value=0, value=10000)
    interest_rate = st.number_input("Annual Interest Rate (%)", min_value=0.0, value=5.0)
    loan_term = st.number_input("Loan Term (years)", min_value=1, value=5)
    
    if st.button("Calculate Payment", type="primary"):
        monthly_rate = (interest_rate / 100) / 12
        num_payments = loan_term * 12
        
        if monthly_rate > 0:
            monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
        else:
            monthly_payment = loan_amount / num_payments
        
        total_payment = monthly_payment * num_payments
        total_interest = total_payment - loan_amount
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Monthly Payment", f"${{monthly_payment:.2f}}")
        col2.metric("Total Payment", f"${{total_payment:.2f}}")
        col3.metric("Total Interest", f"${{total_interest:.2f}}")
''',
        
        "ml_demo": f'''"""
{app_title} - ML Demo
"""

import streamlit as st
import pandas as pd
import numpy as np
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

st.set_page_config(page_title="{app_title}", page_icon="🤖", layout="wide")

st.title("🤖 {app_title}")
st.markdown("Interactive Machine Learning Demo")
st.markdown("---")

# Load data
@st.cache_data
def load_data():
    iris = load_iris()
    df = pd.DataFrame(iris.data, columns=iris.feature_names)
    df['species'] = iris.target
    return df, iris

df, iris = load_data()

# Sidebar
with st.sidebar:
    st.header("Model Parameters")
    n_estimators = st.slider("Number of trees", 10, 200, 100)
    max_depth = st.slider("Max depth", 1, 20, 5)
    test_size = st.slider("Test size", 0.1, 0.5, 0.2)
    
    train_button = st.button("Train Model", type="primary")

# Main content
tab1, tab2, tab3 = st.tabs(["Data", "Model", "Predictions"])

with tab1:
    st.subheader("Dataset Overview")
    st.dataframe(df.head(10), use_container_width=True)
    
    st.subheader("Feature Distribution")
    feature = st.selectbox("Select feature:", df.columns[:-1])
    st.bar_chart(df[feature].value_counts())

with tab2:
    st.subheader("Model Training")
    
    if train_button:
        # Split data
        X = df.iloc[:, :-1]
        y = df.iloc[:, -1]
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        # Train model
        with st.spinner("Training model..."):
            model = RandomForestClassifier(
                n_estimators=n_estimators,
                max_depth=max_depth,
                random_state=42
            )
            model.fit(X_train, y_train)
            score = model.score(X_test, y_test)
        
        st.success(f"Model trained! Accuracy: {{score:.2%}}")
        
        # Feature importance
        st.subheader("Feature Importance")
        importance_df = pd.DataFrame({{
            'Feature': X.columns,
            'Importance': model.feature_importances_
        }}).sort_values('Importance', ascending=False)
        
        st.bar_chart(importance_df.set_index('Feature'))
        
        # Store model in session state
        st.session_state['model'] = model
    else:
        st.info("Click 'Train Model' in the sidebar to start")

with tab3:
    st.subheader("Make Predictions")
    
    if 'model' in st.session_state:
        col1, col2 = st.columns(2)
        
        with col1:
            sepal_length = st.number_input("Sepal Length (cm)", 4.0, 8.0, 5.0)
            sepal_width = st.number_input("Sepal Width (cm)", 2.0, 5.0, 3.0)
        
        with col2:
            petal_length = st.number_input("Petal Length (cm)", 1.0, 7.0, 4.0)
            petal_width = st.number_input("Petal Width (cm)", 0.1, 3.0, 1.0)
        
        if st.button("Predict", type="primary"):
            features = np.array([[sepal_length, sepal_width, petal_length, petal_width]])
            prediction = st.session_state['model'].predict(features)[0]
            species_name = iris.target_names[prediction]
            
            st.success(f"Predicted Species: **{{species_name}}**")
    else:
        st.warning("Please train the model first (go to Model tab)")
'''
    }
    
    if app_type.lower() not in apps:
        return {
            "status": "error",
            "message": f"App type '{app_type}' not supported. Available: {', '.join(apps.keys())}"
        }
    
    return {
        "status": "success",
        "code": apps[app_type.lower()],
        "message": f"Generated complete {app_type} application",
        "filename": f"{app_type.lower()}_app.py"
    }


def save_streamlit_code(filename: str, code: str) -> Dict[str, str]:
    """
    Saves the generated Streamlit code to a file.
    
    Args:
        filename (str): Name of the file to save (should end with .py)
        code (str): The Streamlit code to save
    
    Returns:
        dict: Contains status and message about the save operation
    """
    try:
        if not filename.endswith('.py'):
            filename += '.py'
        
        # Save to generated_apps directory
        output_dir = "generated_apps"
        os.makedirs(output_dir, exist_ok=True)
        
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(code)
        
        return {
            "status": "success",
            "message": f"Code saved to {filepath}",
            "filepath": filepath
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error saving file: {str(e)}"
        }


# Create the root agent with all tools
root_agent = Agent(
    model='gemini-2.0-flash-exp',
    name='streamlit_code_generator',
    description=(
        "An AI agent that generates Streamlit application code based on user requirements. "
        "It can create complete apps, add components, and provide code snippets for various "
        "Streamlit features including data visualization, user inputs, layouts, and more."
    ),
    instruction=(
        "You are an expert Streamlit developer assistant. Your role is to help users create "
        "Streamlit applications by generating clean, well-documented Python code. "
        "\n\n"
        "When a user asks for a Streamlit app or component:\n"
        "1. Understand their requirements clearly\n"
        "2. Use the appropriate tool to generate the code\n"
        "3. Explain what the code does and how to use it\n"
        "4. Suggest improvements or additional features they might want\n"
        "5. Offer to save the code to a file if they want\n"
        "\n"
        "Available capabilities:\n"
        "- Generate complete Streamlit applications (dashboard, data explorer, forms, calculators, ML demos)\n"
        "- Add data visualizations (line, bar, scatter, area, map charts)\n"
        "- Add user input components (text, number, slider, selectbox, forms, etc.)\n"
        "- Add layout components (sidebar, columns, tabs, expanders)\n"
        "- Add data display components (dataframes, tables, metrics, JSON, code)\n"
        "- Save generated code to files\n"
        "\n"
        "Always provide clear, runnable code with helpful comments. "
        "Be friendly and encourage users to ask questions or request modifications."
    ),
    tools=[
        generate_streamlit_boilerplate,
        add_data_visualization,
        add_user_input_components,
        add_layout_components,
        add_data_display_components,
        create_complete_streamlit_app,
        save_streamlit_code
    ],
)