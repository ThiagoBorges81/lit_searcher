# IMPORT LIBRARIES

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import nltk

from wordcloud import WordCloud
from collections import Counter
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

st.markdown("# Individual Searcher")

# Checkbox to select data processing
data_option = st.sidebar.selectbox(
    "select data processing", ("RAW data", "FILTERED data")
)

# Check if 'data' key exists in session state
if "data" not in st.session_state:
    st.warning("No data loaded. Please go to the first page to load data.")


# RAW DATA
if data_option == "RAW data":
    st.subheader("Displaying raw data:")
    st.write(st.session_state["data"])

    df_filt1 = st.session_state["data"]
    options = range(0, df_filt1.shape[0] + 1, 1)
    selected_option = st.selectbox(
        "Select an Abstract from the RAW data for detailed view:", options
    )

    if df_filt1["Abstract"][selected_option]:
        st.write("**Study Title:**", df_filt1["Study Title"][selected_option])
        st.write("**Authors:**", df_filt1["Authors"][selected_option])
        st.write("Abstract:", df_filt1["Abstract"][selected_option])

        text = df_filt1["Abstract"][selected_option]
        wordcloud_1 = WordCloud(
            width=800, height=400, background_color="white"
        ).generate(text)
        st.write("**Wordcloud of the selected Abstract**")
        st.image(wordcloud_1.to_array())
    else:
        st.subheader(
            "Abstract not processed. Please, choose another option from the data selector."
        )

    st.write("")
    st.write("")
    st.write("")

# FILTERED DATA
elif data_option == "FILTERED data":
    st.subheader("Displaying filtered data:")
    st.write(st.session_state["filtered_data"])

    df_filt2 = st.session_state["filtered_data"]

    options = range(0, df_filt2.shape[0] + 1, 1)
    selected_option = st.selectbox(
        "Select an Abstract from the FILTERED data for detailed view:", options
    )

    if df_filt2["Abstract"][selected_option]:
        st.write("**Study Title:**", df_filt2["Study Title"][selected_option])
        st.write("**Authors:**", df_filt2["Authors"][selected_option])
        st.write("Abstract:", df_filt2["Abstract"][selected_option])

        text = df_filt2["Abstract"][selected_option]
        wordcloud = WordCloud(width=800, height=400, background_color="white").generate(
            text
        )
        st.write(
            "<strong>Wordcloud of the selected Abstract.</strong>",
            unsafe_allow_html=True,
        )
        st.image(wordcloud.to_array())

        def word_frequency(text):
            # Tokenize the text into words
            words = word_tokenize(text.lower())

            # Remove stop words
            stop_words = set(stopwords.words("english"))

            # Remove full stops and commas
            words = [
                word for word in words if word not in stop_words and word.isalnum()
            ]

            # Count the frequency of each word
            word_counts = Counter(words)

            return word_counts

        # Choosing abstract/text of interest to process
        text = df_filt2["Abstract"][selected_option]
        word_counts = word_frequency(text)

        # Convert word_counts dictionary to DataFrame
        expl = pd.DataFrame(
            word_counts.items(), columns=["word", "frequency"]
        ).sort_values("frequency", ascending=False)
        expl["relative (%)"] = np.round(
            expl["frequency"] / expl["frequency"].sum() * 100, 2
        )
        st.write(f"Total words (cleaned): {expl['frequency'].sum()}")
        st.write(expl)
    else:
        st.subheader(
            "Abstract not processed. Please, choose another option from the data selector."
        )
