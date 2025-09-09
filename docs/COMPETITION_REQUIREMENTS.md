# BigQuery AI Hackathon - Competition Requirements Analysis

## Competition Overview

**Competition Name:** BigQuery AI - Building the Future of Data
**Host:** Google Cloud
**Prize Pool:** $100,000 total
**Competition Type:** Featured Hackathon
**Status:** 14 days remaining (Deadline: September 22, 2025)
**Participation:** 4,741 Entrants, 58 Submissions

### Key Challenge
We challenge you to go beyond traditional analytics and build groundbreaking solutions using BigQuery's cutting-edge AI capabilities. This is your opportunity to solve real-world business problems using BigQuery's Generative AI, Vector Search, and Multimodal capabilities.

## Problem Statement

Companies are sitting on piles of data, including chat logs, PDFs, screenshots, and recordings, but they can't do much with it. Existing tools are typically built for just one data format, or they require too much manual work. This makes it hard to find patterns, generate content, or even answer basic questions.

**Your Task:** Build a working prototype that uses BigQuery's AI capabilities to process unstructured or mixed-format data. That might mean pulling up similar documents from a giant text archive, creating summaries on the fly, or stitching together insights from messy, mixed data. Whatever you build, the idea is to solve a real problem using tools that feel like an extension of SQL, not a separate system.

## Three Competition Tracks

### Track 1: The AI Architect 🧠 (Generative AI)

**Mission:** Use BigQuery's built-in generative AI to architect intelligent business applications and workflows. Build solutions that can generate creative content, summarize complex information, or even forecast future trends directly within your data warehouse.

**Required Tools (Must use at least one):**

#### Generative AI in SQL:
- **`ML.GENERATE_TEXT`**: The classic function for large-scale text generation
- **`AI.GENERATE`**: Generate free-form text or structured data based on a schema from a prompt
- **`AI.GENERATE_BOOL`**: Get a simple True/False answer about your data
- **`AI.GENERATE_DOUBLE`**: Extract a specific decimal number from text
- **`AI.GENERATE_INT`**: Extract a specific whole number from text
- **`AI.GENERATE_TABLE`**: Create a structured table of data from a single prompt
- **`AI.FORECAST`**: Predict future values for time-series data with a single function

#### Generative AI in BigFrames (Python):
- **`bigframes.ml.llm.GeminiTextGenerator`**: Leverage the power of Gemini models in your Python workflows
- **`bigframes.DataFrame.ai.forecast()`**: Run powerful forecasting models directly on your DataFrames

**Inspiration Projects:**
- **Hyper-Personalized Marketing Engine**: Generate unique marketing emails for every customer based on their individual purchase history and preferences
- **Executive "Insight" Dashboard**: Develop a dashboard that automatically ingests raw support call logs and transforms them into summarized, categorized, and actionable business insights

### Track 2: The Semantic Detective 🕵️‍♀️ (Vector Search)

**Mission:** Go beyond keyword matching and uncover deep, semantic relationships in your data using BigQuery's native vector search. Build systems that understand meaning and context to find similar items, concepts, or issues with incredible accuracy.

**Required Tools (Must use at least one):**

#### Vector Search in SQL:
- **`ML.GENERATE_EMBEDDING`**: Transform your data (text, images) into meaningful vector representations
- **`VECTOR_SEARCH`**: The core function to find items based on meaning, not just keywords. Can be used with or without a vector index
- **`CREATE VECTOR INDEX`**: Build an index for speeding up similarity search on larger tables (1 million rows or above)

#### Vector Search in BigFrames (Python):
- **`bigframes.ml.llm.TextEmbeddingGenerator()`**: Create embeddings seamlessly in your Python environment
- **`bigframes.bigquery.create_vector_index()`**: Build a vector index programmatically using Python
- **`bigframes.bigquery.vector_search()`**: Query your vector index using the BigFrames API

**Inspiration Projects:**
- **Intelligent Triage Bot**: Instantly find historical support tickets that are semantically similar to a new, incoming ticket to speed up resolution time. The bot may also recommend a solution based on past ticket resolutions
- **Smart Substitute Recommender**: Suggest ideal product substitutes based on a deep understanding of product attributes, not just shared tags or categories

### Track 3: The Multimodal Pioneer 🖼️ (Multimodal)

**Mission:** Break the barriers between structured and unstructured data using BigQuery's multimodal capabilities. Combine numerical and categorical data with images, documents, and other rich media to unlock insights that are impossible to find in siloed datasets.

**Required Tools (Must use at least one):**

#### Multimodal Features in SQL:
- **`Object Tables`**: Create a structured SQL interface over your unstructured files in Cloud Storage
- **`ObjectRef`**: A data type that lets you reference and pass unstructured data to AI models

#### Multimodal Features in BigFrames (Python):
- **`BigFrames Multimodal Dataframe`**: Natively load, transform, and analyze mixed data types (text, images, tables) together

**Inspiration Projects:**
- **Revolutionize Real Estate Valuation**: Improve property price predictions by fusing structured data (e.g., sqft, # of bedrooms) with unstructured data from street-level and satellite imagery
- **Automated Quality Control Agent**: Detect discrepancies between a product's listed specifications, its marketing description, and its actual product image

## Submission Requirements

### Core Submission Components

1. **Kaggle Writeup** (Required)
   - Must be attached to the competition page
   - Must address specific sections (see below)

2. **Public Notebook** (Required)
   - Code must be well-documented and clearly show BigQuery AI implementation
   - Must be viewable without login
   - Can be GitHub repository link, Kaggle notebook link, or included in writeup

3. **Public Video/Blog** (Optional but Recommended)
   - Showcase your work and tell the story of how you used BigQuery AI
   - Can be posted to Medium, YouTube, X (Twitter), TikTok, or any public platform
   - Must be viewable without login

4. **User Survey** (Optional - Bonus Points)
   - Attach as text file in data section
   - Points awarded for completeness, not content
   - 3 questions about team experience and feedback

### Kaggle Writeup Required Sections

1. **Project Title**: A creative and descriptive name for the project
2. **Problem Statement**: A brief, one-paragraph summary of the hackathon problem you are solving
3. **Impact Statement**: A brief summary on what material impact the solution achieves

### Submission Rules

- You must use at least one approach (can use two or all three)
- Submissions are only eligible for one prize
- Each team is limited to one Writeup
- Writeup can be un-submitted, edited, and re-submitted multiple times
- Final submission must be made prior to deadline
- Any un-submitted or draft Writeups by deadline will not be considered
- Private Kaggle Resources attached to public Writeups will be made public after deadline

## Evaluation Criteria

### Technical Implementation (35%)
- **Code Quality (20%)**:
  - 0% - The code didn't work
  - 10% - The code ran but took inordinate time or was difficult to follow
  - 20% - The code ran easily and was clean to read
- **BigQuery AI Usage (15%)**:
  - 0% - BigQuery AI usage was irrelevant to the solution
  - 5% - BigQuery AI were used but not a core function of the solution
  - 15% - BigQuery AI was used well throughout the solution

### Innovation and Creativity (25%)
- **Novelty (10%)**:
  - 0% - You can easily find the approach online right now
  - 10% - This was an innovative approach to the solution
- **Impact (15%)**:
  - 0% - There is no consideration on any metric
  - 5% - The solution moves a metric slightly
  - 15% - The solution makes a large improvement in its space

### Demo and Presentation (20%)
- **Problem/Solution Clarity (10%)**:
  - 0% - The problem and solution relationship was difficult to follow
  - 5% - The problem and solution relationship was clear but documentation was non-existent
  - 10% - There is a clear relationship and documentation was clear
- **Technical Explanation (10%)**:
  - 0% - There was no explanation
  - 5% - There was an explanation or architectural diagram but not both
  - 10% - There was a clear explanation and architectural diagram

### Assets (20%)
- **Public Blog/Video (10%)**:
  - 0% - There was no blog or video
  - 5% - There was a blog or video but it wasn't clear what the solution intended to demonstrate
  - 10% - There was a blog or video clearly demonstrating the solution
- **Public Code Repository (10%)**:
  - 0% - The code is not publicly available
  - 10% - The code was made publicly available in GitHub

### Bonus (Optional, 10%)
- **Feedback on BigQuery AI (5%)**:
  - 0% - No feedback or friction points provided
  - 5% - Feedback or friction points provided
- **Survey Completion (5%)**:
  - 0% - No, the survey was not completed
  - 5% - Yes, the survey was attached and completed

## Prize Structure

### Overall Track - $100,000 Total

#### Generative AI Track
- **1st Place**: $15,000
- **2nd Place**: $9,000
- **3rd Place**: $6,000

#### Vector Search Track
- **1st Place**: $15,000
- **2nd Place**: $9,000
- **3rd Place**: $6,000

#### Multimodal Track
- **1st Place**: $15,000
- **2nd Place**: $9,000
- **3rd Place**: $6,000

#### Honorable Mentions
- **2 Awards**: $5,000 each

## Timeline

- **Start Date**: August 12, 2025
- **Final Submission Deadline**: September 22, 2025 (11:59 PM UTC)
- **Judging Period**: September 22, 2025 - October 6, 2025
- **Results Announcement**: October 13, 2025

*Note: Judging period subject to change based on number of submissions received*

## Data Sources

**No specific data provided** - You are encouraged to use any publicly available dataset for your submission.

### Recommended Data Sources:

1. **BigQuery Public Datasets**
   - Overview: https://cloud.google.com/bigquery/public-data
   - Marketplace: https://console.cloud.google.com/marketplace/browse?filter=solution-type:dataset

2. **Cloud Storage Public Datasets**
   - Images: https://cloud.google.com/storage/docs/public-datasets

3. **Sample Multimodal Data**
   - Images: `gs://cloud-samples-data/bigquery/tutorials/cymbal-pets/images/`
   - Documents: `gs://cloud-samples-data/bigquery/tutorials/cymbal-pets/documents/`

## Getting Started Resources

### Approach 1: Generative AI 🧠
- **SQL Sample**: [BigQuery AI Functions Sample](https://github.com/GoogleCloudPlatform/generative-ai/blob/main/gemini/use-cases/applying-llms-to-data/bigquery_generative_ai_intro.ipynb)
- **Python Sample**: [BigFrames AI Forecast Sample](https://github.com/googleapis/python-bigquery-dataframes/blob/main/notebooks/kaggle/bq_dataframes_ai_forecast.ipynb)
- **Documentation**: [AI.GENERATE](https://cloud.google.com/bigquery/docs/reference/standard-sql/bigqueryml-syntax-ai-generate), [AI.FORECAST](https://cloud.google.com/bigquery/docs/reference/standard-sql/bigqueryml-syntax-ai-forecast)
- **Blog**: [What's new with BigQuery AI and ML?](https://cloud.google.com/blog/products/data-analytics/bigquery-adds-new-ai-capabilities)

### Approach 2: Vector Search 🕵️‍♀️
- **SQL Sample**: [BigQuery Vector Search Sample](https://github.com/GoogleCloudPlatform/generative-ai/blob/main/gemini/use-cases/applying-llms-to-data/bigquery_embeddings_vector_search.ipynb)
- **Python Sample**: [BigFrames Vector Search Sample](https://github.com/googleapis/python-bigquery-dataframes/blob/main/notebooks/kaggle/vector-search-with-bigframes-over-national-jukebox.ipynb)
- **Documentation**: [Vector Search Introduction](https://cloud.google.com/bigquery/docs/vector-search-intro), [Generate Embeddings](https://cloud.google.com/bigquery/docs/reference/standard-sql/bigqueryml-syntax-generate-embedding)
- **Blog**: [BigQuery vector search, setting the stage for a new class of AI-powered analytics](https://cloud.google.com/blog/products/data-analytics/bigquery-vector-search-is-now-ga)

### Approach 3: Multimodal 🖼️
- **SQL Sample**: [BigQuery Multimodal Sample](https://github.com/GoogleCloudPlatform/generative-ai/blob/main/gemini/use-cases/applying-llms-to-data/multimodal-analysis-bigquery/analyze_multimodal_data_bigquery.ipynb)
- **Python Sample**: [BigFrames Multimodal Sample](https://github.com/googleapis/python-bigquery-dataframes/blob/main/notebooks/kaggle/describe-product-images-with-bigframes-multimodal.ipynb)
- **Documentation**: [Analyze multimodal data in BigQuery](https://cloud.google.com/bigquery/docs/analyze-multimodal-data)
- **Blog**: [A Practical Guide to Multimodal Data Analytics](https://medium.com/google-cloud/a-practical-guide-to-multimodal-data-analytics-ae706a3f14e0)

### End-to-End Codelab
- [Petverse Multimodal Codelab](https://codelabs.developers.google.com/devsite/codelabs/petverse_multimodal) - Blends all three approaches

## Competition Judges

- **Jing Jing** - Google
- **Gautam Gupta** - Engineering Leader, Google
- **Rachael DS** - Google
- **Gabe Weiss** - Google
- **Wei Hsia** - Google
- **Yves-Laurent Kom Samo** - Software Engineer, Google
- **Omid Fatemieh** - AI/ML/Search Eng Leader, Google BigQuery
- **Jiaxun Wu** - Google
- **Jeff Nelson** - Developer Advocacy, Google
- **Ivan SMF** - Google

## Key Success Factors

1. **Technical Excellence**: Clean, efficient code that effectively uses BigQuery AI
2. **Innovation**: Novel approach that addresses significant real-world problems
3. **Impact**: Clear demonstration of business value and measurable improvements
4. **Presentation**: Well-documented solution with clear problem-solution relationship
5. **Public Assets**: High-quality blog/video and publicly available code repository

## Identity Verification

**Important**: This competition requires identity verification to submit. You'll need to verify your identity before the submission deadline.

---

*This analysis is based on the official competition page as of September 9, 2025. Please refer to the official competition page for the most up-to-date information.*
