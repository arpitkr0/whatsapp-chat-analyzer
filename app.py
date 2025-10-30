import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import platform
import seaborn as sns

# =============================
# 🔹 Font compatibility for emojis
# =============================
if platform.system() == "Windows":
    plt.rcParams['font.family'] = 'Segoe UI Emoji'
elif platform.system() == "Darwin":  # macOS
    plt.rcParams['font.family'] = 'Apple Color Emoji'
else:  # Linux
    plt.rcParams['font.family'] = 'Noto Color Emoji'

# =============================
# 🔹 Sidebar Title
# =============================
st.sidebar.title("📊 WhatsApp Chat Analyzer")

# =============================
# 🔹 Load demo file function
# =============================
DEMO_CHAT_PATH = "demo.txt"  

def load_demo_file():
    with open(DEMO_CHAT_PATH, "r", encoding="utf-8") as f:
        return f.read()

# =============================
# 🔹 File uploader
# =============================
uploaded_file = st.sidebar.file_uploader("Choose a WhatsApp chat file (.txt)", type=["txt"])

# =============================
# 🔹 Use uploaded or demo data
# =============================
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    st.sidebar.success("✅ Custom chat file uploaded successfully!")
else:
    st.sidebar.info("ℹ️ No file uploaded — showing demo chat by default.")
    data = load_demo_file()

# =============================
# 🔹 Preprocess Data
# =============================
df = preprocessor.preprocess(data)

# fetch unique users
user_list = df['user'].unique().tolist()
if 'group_notification' in user_list:
    user_list.remove('group_notification')
user_list.sort()
user_list.insert(0, "Overall")

selected_user = st.sidebar.selectbox("Show analysis for", user_list, index=0)

# =============================
# 🔹 Automatically show analysis
# =============================

# Stats Area
num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
st.title("📈 Top Statistics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.header("Total Messages")
    st.title(num_messages)
with col2:
    st.header("Total Words")
    st.title(words)
with col3:
    st.header("Media Shared")
    st.title(num_media_messages)
with col4:
    st.header("Links Shared")
    st.title(num_links)

# Monthly timeline
st.title("🗓️ Monthly Timeline")
timeline = helper.monthly_timeline(selected_user, df)
fig, ax = plt.subplots()
ax.plot(timeline['time'], timeline['message'], color='green')
plt.xticks(rotation='vertical')
st.pyplot(fig)

# Daily timeline
st.title("📅 Daily Timeline")
daily_timeline = helper.daily_timeline(selected_user, df)
fig, ax = plt.subplots()
ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
plt.xticks(rotation='vertical')
st.pyplot(fig)

# Activity Map
st.title('🕒 Activity Map')
col1, col2 = st.columns(2)

with col1:
    st.header("Most Busy Day")
    busy_day = helper.week_activity_map(selected_user, df)
    fig, ax = plt.subplots()
    ax.bar(busy_day.index, busy_day.values, color='purple')
    plt.xticks(rotation='vertical')
    st.pyplot(fig)

with col2:
    st.header("Most Busy Month")
    busy_month = helper.month_activity_map(selected_user, df)
    fig, ax = plt.subplots()
    ax.bar(busy_month.index, busy_month.values, color='orange')
    plt.xticks(rotation='vertical')
    st.pyplot(fig)

st.title("📆 Weekly Activity Heatmap")
user_heatmap = helper.activity_heatmap(selected_user, df)
fig, ax = plt.subplots()
ax = sns.heatmap(user_heatmap)
st.pyplot(fig)

# Busiest Users (Group Level)
if selected_user == 'Overall':
    st.title('🏆 Most Busy Users')
    x, new_df = helper.most_busy_users(df)
    fig, ax = plt.subplots()

    col1, col2 = st.columns(2)
    with col1:
        ax.bar(x.index, x.values, color='red')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)
    with col2:
        st.dataframe(new_df)

# WordCloud
st.title("☁️ Word Cloud")
df_wc = helper.create_wordcloud(selected_user, df)
fig, ax = plt.subplots()
ax.imshow(df_wc)
st.pyplot(fig)

# Most Common Words
st.title('🗣️ Most Common Words')
most_common_df = helper.most_common_words(selected_user, df)
fig, ax = plt.subplots()
ax.barh(most_common_df[0], most_common_df[1])
plt.xticks(rotation='vertical')
st.pyplot(fig)

# Emoji Analysis
st.title("😀 Emoji Analysis")
emoji_df = helper.emoji_helper(selected_user, df)

col1, col2 = st.columns(2)
with col1:
    st.dataframe(emoji_df)
with col2:
    fig, ax = plt.subplots()
    ax.pie(emoji_df[1].head(), labels=emoji_df[0].head(), autopct="%0.2f%%")
    st.pyplot(fig)
