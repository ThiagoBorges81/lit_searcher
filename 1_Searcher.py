# IMPORT LIBRARIES

import streamlit            as st
import pandas               as pd
import numpy                as np
import requests
import json
import time
import matplotlib.pyplot    as plt
from pymed          import PubMed
from wordcloud      import WordCloud


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
        if 'data' not in st.session_state:
            st.session_state['data'] = None
        st.session_state['data'] = data

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
        st.subheader(f"Filtered data set has now {filtered_data.shape[0]} references")
        st.write('')
        st.subheader('Finished searching for references? Please, go to the individual search page for further processing.')

        if 'filtered_data' not in st.session_state:
            st.session_state['filtered_data'] = None
            st.session_state['filtered_data'] = filtered_data.reset_index()
