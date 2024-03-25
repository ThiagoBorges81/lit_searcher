# IMPORT LIBRARIES

import streamlit            as st
import pandas               as pd
import numpy                as np
import requests
import json
import time
from wordcloud      import WordCloud
from nltk.tokenize  import word_tokenize
from nltk.corpus    import stopwords
from collections    import Counter

from pymed          import PubMed


# APP TITLE
st.title("Literature Searcher")

# FETCH DATA
# Search keywords
search_terms = st.text_input("Insert the keywords of interest(separated by single space)", value="").lower()
st.write("The current search term is", search_terms)

if search_terms:

    @st.cache_data
    def retrieve_pubmed_data(query):
        # Initialize PubMed object
        pubmed = PubMed()

        results = pubmed.query(query)

        data_list = []

        for article in results:
            json_string = article.toJSON()

            article_dict = json.loads(json_string)
            data_list.append(article_dict)

        df = pd.DataFrame(data_list)

        df = df[
            [
                "title",
                "authors",
                "abstract",
                "keywords",
                "journal",
                "publication_date",
                "doi",
            ]
        ]

        # Fix the authors names
        author_lists = df["authors"]
        full_name = []
        for i, author_list in enumerate(author_lists):
            publication_authors = []
            for author_info in author_list:

                # Check if 'lastname' and 'firstname' keys are present and not None
                if (
                    "lastname" in author_info
                    and author_info["lastname"] is not None
                    and "firstname" in author_info
                    and author_info["firstname"] is not None
                ):

                    last_name = author_info["lastname"]
                    first_name = author_info["firstname"]
                    author_name = last_name + "," + first_name
                    publication_authors.append(author_name)
            full_name.append(publication_authors)

        df["author_fn"] = full_name
        df = df.drop("authors", axis=1)
        df = df[
            [
                "title",
                "author_fn",
                "abstract",
                "keywords",
                "journal",
                "publication_date",
                "doi",
            ]
        ]
        df.rename(
            columns={
                "title": "Study Title",
                "author_fn": "Authors",
                "abstract": "Abstract",
                "keywords": "Keywords",
                "journal": "Journal",
                "publication_date": "Publication date",
                "doi": "DOI",
            },
            inplace=True,
        )
        return df


    data_load_state = st.text("Processing information...")

    data = retrieve_pubmed_data(search_terms)
    st.text(f"Search found {data.shape[0]} references")

    data_load_state.text("Done! Proceed to the next step!")

    if st.checkbox("Show raw data"):
        st.subheader("Raw data")
        st.write(data)


    if st.checkbox("Would you like to filter your data?"):
        st.subheader("Insert the filtering terms:")

        # Checkbox for selecting fields to filter
        st.write("Below, please select fields to filter BEFORE you enter your keywords:")
        st.write("Ignore the warning message below, if it appears")
        filter_study_title = st.checkbox("Study Title")
        filter_abstract = st.checkbox("Abstract")
        filter_keywords = st.checkbox("Keywords")

        # Search keywords
        keywords_filter = st.text_input("Insert the keywords for filtering", value="")
        st.write("The keywords you're looking for are:", keywords_filter)

        if keywords_filter:

            # Splitting search terms into individual keywords
            keywords_filter = keywords_filter.split()

            # Filter the DataFrame based on selected fields and keywords
            filtered_data = data
            if filter_study_title:
                filtered_data = data[
                    data.apply(
                        lambda row: any(
                            keyword.lower() in str(row["Study Title"]).lower()
                            for keyword in keywords_filter
                        ),
                        axis=1,
                    )
                ]
            if filter_abstract:
                filtered_data = data[
                    data.apply(
                        lambda row: any(
                            keyword.lower() in str(row["Abstract"]).lower()
                            for keyword in keywords_filter
                        ),
                        axis=1,
                    )
                ]
            if filter_keywords:
                filtered_data = data[
                    data.apply(
                        lambda row: any(
                            keyword.lower() in str(row["Keywords"]).lower()
                            for keyword in keywords_filter
                        ),
                        axis=1,
                    )
                ]

            # Combine multiple filters if more than one checkbox is selected
            if filter_study_title and filter_abstract:
                filtered_data = data[
                    (
                        data.apply(
                            lambda row: any(
                                keyword.lower() in str(row["Study Title"]).lower()
                                for keyword in keywords_filter
                            ),
                            axis=1,
                        )
                    )
                    | (
                        data.apply(
                            lambda row: any(
                                keyword.lower() in str(row["Abstract"]).lower()
                                for keyword in keywords_filter
                            ),
                            axis=1,
                        )
                    )
                ]
            if filter_study_title and filter_keywords:
                filtered_data = data[
                    (
                        data.apply(
                            lambda row: any(
                                keyword.lower() in str(row["Study Title"]).lower()
                                for keyword in keywords_filter
                            ),
                            axis=1,
                        )
                    )
                    | (
                        data.apply(
                            lambda row: any(
                                keyword.lower() in str(row["Keywords"]).lower()
                                for keyword in keywords_filter
                            ),
                            axis=1,
                        )
                    )
                ]
            if filter_abstract and filter_keywords:
                filtered_data = data[
                    (
                        data.apply(
                            lambda row: any(
                                keyword.lower() in str(row["Abstract"]).lower()
                                for keyword in keywords_filter
                            ),
                            axis=1,
                        )
                    )
                    | (
                        data.apply(
                            lambda row: any(
                                keyword.lower() in str(row["Keywords"]).lower()
                                for keyword in keywords_filter
                            ),
                            axis=1,
                        )
                    )
                ]
            if filter_study_title and filter_abstract and filter_keywords:
                filtered_data = data[
                    (
                        data.apply(
                            lambda row: any(
                                keyword.lower() in str(row["Study Title"]).lower()
                                for keyword in keywords_filter
                            ),
                            axis=1,
                        )
                    )
                    | (
                        data.apply(
                            lambda row: any(
                                keyword.lower() in str(row["Abstract"]).lower()
                                for keyword in keywords_filter
                            ),
                            axis=1,
                        )
                    )
                    | (
                        data.apply(
                            lambda row: any(
                                keyword.lower() in str(row["Keywords"]).lower()
                                for keyword in keywords_filter
                            ),
                            axis=1,
                        )
                    )
                ]

        st.write(filtered_data)
        st.subheader(f"Filtering has narrowed the RAW data to {filtered_data.shape[0]} references")
        st.write('')
        st.subheader('Finished searching for references? Please, go to the individual search page for further processing.')

    #####################
    #INDIVIDUAL SEARCHER#
    #####################
    # FILTERED DATA
    # elif data_option == "FILTERED data":
    if st.checkbox("Display filtered data"):
        st.subheader("Displaying filtered data:")
        st.write(filtered_data)
        
        options = range(0, filtered_data.shape[0] + 1, 1)
        selected_option = st.selectbox(
            "Select an Abstract from the FILTERED data for detailed view:", options
        )

        if filtered_data["Abstract"][selected_option]:
            st.write("**Study Title:**", filtered_data["Study Title"][selected_option])
            st.write("**Authors:**", filtered_data["Authors"][selected_option])
            st.write("Abstract:", filtered_data["Abstract"][selected_option])

            text = filtered_data["Abstract"][selected_option]
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
            text = filtered_data["Abstract"][selected_option]
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