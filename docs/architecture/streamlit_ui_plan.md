# Streamlit UI Plan - BigQuery AI Legal Document Intelligence Platform

## 🎯 **Streamlit UI Strategy for Competition**

This document outlines the Streamlit-based user interface strategy for the BigQuery AI Legal Document Intelligence Platform, optimized for competition demonstration and judging.

---

## 🏗️ **Streamlit Architecture Overview**

### **Why Streamlit for Competition:**
- ✅ **Fast Development** - Can build complete UI in 1-2 days
- ✅ **Perfect for AI Demos** - Excellent for showcasing BigQuery AI functions
- ✅ **Interactive Widgets** - Real-time document processing and results
- ✅ **Professional Look** - Clean, modern interface for judges
- ✅ **Easy Deployment** - Simple to run and demonstrate
- ✅ **Competition Focused** - Emphasizes AI capabilities over complex UI

---

## 📱 **Streamlit Dashboard Structure**

### **Main App Layout:**
```
src/streamlit_app.py
├── 🏠 Home Page
├── 📄 Document Upload & Processing
├── 🧠 Track 1: Generative AI Demo
├── 🔍 Track 2: Vector Search Demo
├── 🔗 Hybrid Pipeline Demo
├── 📊 Results Visualization
└── 📈 Performance Metrics
```

---

## 🎨 **Streamlit UI Components**

### **1. Home Page (`st.set_page_config`)**
```python
# Page Configuration
st.set_page_config(
    page_title="BigQuery AI Legal Intelligence Platform",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Header
st.title("⚖️ BigQuery AI Legal Document Intelligence Platform")
st.subtitle("Dual-Track Approach: Generative AI + Vector Search")
st.markdown("**Competition Entry**: BigQuery AI Hackathon 2025")
```

### **2. Sidebar Navigation**
```python
# Sidebar Navigation
st.sidebar.title("🧭 Navigation")
page = st.sidebar.selectbox(
    "Choose Demo Section:",
    [
        "🏠 Home",
        "📄 Document Upload",
        "🧠 Track 1: Generative AI",
        "🔍 Track 2: Vector Search",
        "🔗 Hybrid Pipeline",
        "📊 Results Dashboard",
        "📈 Performance Metrics"
    ]
)
```

### **3. Document Upload Interface**
```python
# Document Upload Section
st.header("📄 Legal Document Upload & Processing")

# File Uploader
uploaded_file = st.file_uploader(
    "Upload Legal Document",
    type=['pdf', 'txt', 'docx'],
    help="Upload contracts, briefs, case files, or legal documents"
)

# Document Preview
if uploaded_file:
    st.success(f"✅ Uploaded: {uploaded_file.name}")

    # Document preview
    with st.expander("📖 Document Preview"):
        # Show document content
        document_text = extract_text(uploaded_file)
        st.text_area("Document Content", document_text, height=200)
```

### **4. Track 1: Generative AI Demo**
```python
# Track 1: Generative AI Functions
st.header("🧠 Track 1: Generative AI Functions")

# Function Selection
ai_function = st.selectbox(
    "Select BigQuery AI Function:",
    [
        "ML.GENERATE_TEXT - Document Summarization",
        "AI.GENERATE_TABLE - Legal Data Extraction",
        "AI.GENERATE_BOOL - Urgency Detection",
        "AI.FORECAST - Case Outcome Prediction"
    ]
)

# Execute Function
if st.button("🚀 Execute AI Function"):
    with st.spinner("Processing with BigQuery AI..."):
        result = execute_bigquery_ai_function(ai_function, document_text)
        st.success("✅ AI Processing Complete!")

        # Display Results
        st.subheader("📊 AI Results")
        st.json(result)
```

### **5. Track 2: Vector Search Demo**
```python
# Track 2: Vector Search Functions
st.header("🔍 Track 2: Vector Search Functions")

# Vector Search Options
search_type = st.selectbox(
    "Select Vector Search Function:",
    [
        "ML.GENERATE_EMBEDDING - Document Embeddings",
        "VECTOR_SEARCH - Similarity Search",
        "VECTOR_DISTANCE - Distance Calculation",
        "CREATE VECTOR INDEX - Performance Optimization"
    ]
)

# Search Parameters
if search_type == "VECTOR_SEARCH":
    similarity_threshold = st.slider("Similarity Threshold", 0.0, 1.0, 0.8)
    max_results = st.number_input("Max Results", 1, 50, 10)

# Execute Vector Search
if st.button("🔍 Execute Vector Search"):
    with st.spinner("Generating embeddings and searching..."):
        results = execute_vector_search(search_type, document_text)
        st.success("✅ Vector Search Complete!")

        # Display Similar Documents
        st.subheader("📋 Similar Legal Documents")
        for i, doc in enumerate(results):
            st.write(f"**{i+1}.** {doc['title']} (Similarity: {doc['similarity']:.3f})")
```

### **6. Hybrid Pipeline Demo**
```python
# Hybrid Pipeline: Combined Track 1 + Track 2
st.header("🔗 Hybrid Pipeline: Combined Intelligence")

# Pipeline Options
pipeline_mode = st.radio(
    "Select Pipeline Mode:",
    [
        "🔄 Full Analysis (Track 1 + Track 2)",
        "⚡ Quick Analysis (Track 1 only)",
        "🎯 Similarity Focus (Track 2 only)"
    ]
)

# Execute Hybrid Pipeline
if st.button("🚀 Run Hybrid Pipeline"):
    with st.spinner("Running dual-track analysis..."):
        results = run_hybrid_pipeline(document_text, pipeline_mode)
        st.success("✅ Hybrid Analysis Complete!")

        # Display Combined Results
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🧠 Generative AI Results")
            st.json(results['generative_ai'])

        with col2:
            st.subheader("🔍 Vector Search Results")
            st.json(results['vector_search'])
```

### **7. Results Visualization**
```python
# Results Visualization
st.header("📊 Results Visualization")

# Performance Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Processing Time", "2.3s", "0.5s faster")

with col2:
    st.metric("Accuracy", "94%", "6% improvement")

with col3:
    st.metric("Similarity Score", "0.87", "0.12 better")

with col4:
    st.metric("Cost", "$0.15", "85% savings")

# Charts and Graphs
st.subheader("📈 Performance Charts")

# Processing time chart
chart_data = pd.DataFrame({
    'Function': ['ML.GENERATE_TEXT', 'AI.GENERATE_TABLE', 'AI.GENERATE_BOOL', 'AI.FORECAST'],
    'Time (s)': [1.2, 0.8, 0.3, 2.1]
})

st.bar_chart(chart_data.set_index('Function'))
```

---

## 🎯 **Streamlit UI Features**

### **Interactive Components:**
- ✅ **File Upload** - Drag & drop legal documents
- ✅ **Real-time Processing** - Live BigQuery AI function execution
- ✅ **Progress Indicators** - Spinners and progress bars
- ✅ **Results Display** - JSON, tables, charts, metrics
- ✅ **Sidebar Navigation** - Easy section switching
- ✅ **Expandable Sections** - Detailed information on demand

### **Visualization Components:**
- ✅ **Performance Metrics** - Processing time, accuracy, cost
- ✅ **Bar Charts** - Function performance comparison
- ✅ **Similarity Scores** - Vector search results
- ✅ **Document Preview** - Uploaded document content
- ✅ **Results Tables** - Structured data display

### **User Experience:**
- ✅ **Responsive Design** - Works on different screen sizes
- ✅ **Clear Navigation** - Intuitive sidebar menu
- ✅ **Error Handling** - User-friendly error messages
- ✅ **Loading States** - Visual feedback during processing
- ✅ **Success Indicators** - Clear completion notifications

---

## 🚀 **Implementation Plan**

### **Day 1: Core Streamlit App**
- [ ] Basic app structure and navigation
- [ ] Document upload functionality
- [ ] BigQuery AI function integration
- [ ] Basic results display

### **Day 2: Enhanced Features**
- [ ] Vector search integration
- [ ] Hybrid pipeline implementation
- [ ] Visualization components
- [ ] Performance metrics

### **Day 3: Polish & Demo**
- [ ] UI/UX improvements
- [ ] Error handling
- [ ] Demo video recording
- [ ] Documentation

---

## 📋 **Streamlit Dependencies**

### **requirements.txt additions:**
```
streamlit>=1.28.0
plotly>=5.17.0
pandas>=2.0.0
numpy>=1.24.0
google-cloud-bigquery>=3.11.0
python-docx>=0.8.11
PyPDF2>=3.0.0
```

### **Streamlit Configuration:**
```toml
# .streamlit/config.toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"

[server]
headless = true
port = 8501
```

---

## 🎯 **Competition Advantages**

### **Why Streamlit UI Wins:**
1. **✅ Fast Development** - Complete UI in 1-2 days
2. **✅ AI-Focused** - Perfect for demonstrating BigQuery AI functions
3. **✅ Interactive Demo** - Judges can interact with the system
4. **✅ Professional Look** - Clean, modern interface
5. **✅ Easy Deployment** - Simple to run and demonstrate
6. **✅ Competition Aligned** - Emphasizes AI capabilities over complex UI

### **Demo Flow for Judges:**
1. **Upload Document** - Show document upload capability
2. **Track 1 Demo** - Execute all 4 BigQuery AI functions
3. **Track 2 Demo** - Demonstrate vector search capabilities
4. **Hybrid Pipeline** - Show combined dual-track approach
5. **Results Visualization** - Display performance metrics and insights

---

## 🏆 **Success Metrics**

### **UI Success Criteria:**
- ✅ **Easy Navigation** - Judges can find all features quickly
- ✅ **Clear Results** - AI function outputs are well-displayed
- ✅ **Interactive Demo** - Judges can upload and process documents
- ✅ **Professional Appearance** - Clean, modern interface
- ✅ **Fast Performance** - Quick response times
- ✅ **Error Handling** - Graceful error management

---

**🎯 This Streamlit UI plan ensures maximum competition impact by providing an interactive, professional demonstration of the dual-track BigQuery AI capabilities while maintaining focus on the core AI functions that judges will evaluate.**
