import streamlit as st
import pandas as pd
import altair as alt

# Add the uploaded image at the top of the page
st.image("/Users/linda/Desktop/مسار العزم/IMG_0831.jpg", use_column_width=True)

st.markdown(
    """
    <style>
    body {
        background-color: #d4e5c6; /* Light green background */
        color: #2c3e50; /* Dark navy for text */
        font-family: 'Roboto', sans-serif;
    }
    .subheader {
        color: #3cc4c3; /* Blue subheader */
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Load datasets
file_path_2024 = '/Users/linda/Desktop/مسار العزم/2024_cleanedlast.csv'
file_path_2023 = '/Users/linda/Desktop/مسار العزم/20233.csv'

# Dataset Selector
selected_year = st.radio("مجموعة البيانات عام :", ("٢٠٢٤", "٢٠٢٣"))
if selected_year == "٢٠٢٤":
    data = pd.read_csv(file_path_2024)
else:
    data = pd.read_csv(file_path_2023)

# --- Data Table and Descriptive Statistics Section ---
col1, col2 = st.columns(2)

# Data Table Section
with col1:
    if st.checkbox("Show Data Table"):
        st.markdown("### بيانات الجدول")
        st.dataframe(data)

# Descriptive Statistics Section
with col2:
    if st.checkbox("Show Descriptive Statistics"):
        st.markdown("### الإحصائيات الوصفية")
        st.write(data.describe())
        
st.title("تتبع سرعة الشاحنات")
required_columns = ['الموقع', 'التاريخ', 'الساعة', 'رقم الشاحنة', 'سرعة الشاحنة']  # أسماء الأعمدة
if all(col in data.columns for col in required_columns):
    # تصفية البيانات لتحديد السرعات التي تجاوزت 60
    over_speed_data = data[data['سرعة الشاحنة'] > 60][required_columns]
    
    if not over_speed_data.empty:
        st.warning(f"هناك {len(over_speed_data)} شاحنة تجاوزت السرعة 60!🚨")
        st.dataframe(over_speed_data)
    else:
        st.success("لا توجد شاحنات تجاوزت السرعة المحددة.")
else:
    st.error("البيانات لا تحتوي على الأعمدة المطلوبة: " + ", ".join(required_columns))

# Data Visualization Section
st.markdown(f"<h2 class='subheader'>📊 تصور البيانات - عام {selected_year}</h2>", unsafe_allow_html=True)

# Dropdown for selecting columns
selected_columns = st.multiselect("اختر عمودًا أو عمودين:", data.columns)

# Create a two-column layout for the charts
col1, col2 = st.columns(2)

# Generate the charts based on the selection
if len(selected_columns) == 1:
    with col1:
        st.markdown("### مخطط شريطي (Histogram)")
        if pd.api.types.is_numeric_dtype(data[selected_columns[0]]):
            histogram = alt.Chart(data).mark_bar().encode(
                x=alt.X(selected_columns[0], bin=alt.Bin(maxbins=30)),
                y='count()'
            )
            st.altair_chart(histogram.properties(title=f"Histogram - {selected_columns[0]}"), use_container_width=True)
        else:
            st.write(" يرجى اختيار عمود رقمي لإنشاء مخطط شريطي.")
    with col2:
        st.markdown("### مخطط دائري (Pie Chart)")
        pie_data = data[selected_columns[0]].value_counts().reset_index()
        pie_data.columns = ['Category', 'Count']
        pie_chart = alt.Chart(pie_data).mark_arc().encode(
            theta=alt.Theta(field='Count', type='quantitative'),
            color=alt.Color(field='Category', type='nominal'),
            tooltip=['Category', 'Count']
        )
        st.altair_chart(pie_chart.properties(title=f"Pie Chart - {selected_columns[0]}"), use_container_width=True)

elif len(selected_columns) == 2:
    with col1:
        st.markdown("### مخطط شريطي (Histogram)")
        if pd.api.types.is_numeric_dtype(data[selected_columns[0]]):
            histogram = alt.Chart(data).mark_bar().encode(
                x=alt.X(selected_columns[0], bin=alt.Bin(maxbins=30)),
                y='count()'
            )
            st.altair_chart(histogram.properties(title=f"Histogram - {selected_columns[0]}"), use_container_width=True)
        else:
            st.write("  يرجى اختيار عمود رقمي لإنشاء مخطط شريطي.")
    with col2:
        st.markdown("### مخطط خطي (Line Chart)")
        line_chart = alt.Chart(data).mark_line().encode(
            x=selected_columns[0],
            y=selected_columns[1]
        )
        st.altair_chart(line_chart.properties(title=f"Line Chart - {selected_columns[0]} vs {selected_columns[1]}"), use_container_width=True)
else:
    st.write(" يرجى اختيار عمود واحد أو عمودين فقط.")

# Filter Data Section
st.markdown(f"<h2 class='subheader'> تصفية البيانات - عام {selected_year}</h2>", unsafe_allow_html=True)
column_to_filter = st.selectbox("اختر العمود للتصفية:", data.columns)

if pd.api.types.is_numeric_dtype(data[column_to_filter]):
    min_value, max_value = st.slider(
        "اختر النطاق:",
        min_value=float(data[column_to_filter].min()),
        max_value=float(data[column_to_filter].max()),
        value=(float(data[column_to_filter].min()), float(data[column_to_filter].max()))
    )
    filtered_data = data[
        (data[column_to_filter] >= min_value) & (data[column_to_filter] <= max_value)
    ]
else:
    filter_value = st.text_input("أدخل القيمة للتصفية:")
    filtered_data = data[data[column_to_filter] == filter_value]

st.markdown("<h3 class='subheader'>البيانات المصفاة</h3>", unsafe_allow_html=True)
st.dataframe(filtered_data)

# Download filtered data as CSV
if not filtered_data.empty:
    csv = filtered_data.to_csv(index=False)
    st.download_button(
        label="تحميل البيانات المصفاة",
        data=csv,
        file_name=f"filtered_data_{selected_year}.csv",
        mime="text/csv"
    )
