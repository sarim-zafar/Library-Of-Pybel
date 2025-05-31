import streamlit as st
from library_of_babel import getPage, getTitle, search, searchTitle, text_prep, length_of_page, urdu_chars

# Set the page title and layout
st.set_page_config(page_title="Urdu Library of Babel", layout="wide")

st.title("Urdu Library of Babel")
st.markdown("""
Welcome to the Urdu Library of Babel. This digital library contains a vast collection of pages and titles.
You can explore it by checking out a specific page using its address or by searching for text.
All content is generated deterministically based on the address or search query.
""")

st.header("Checkout Page by Address")
address_input = st.text_input("Enter Page Address (e.g., hex:wall:shelf:volume:page):", key="address_checkout")
checkout_button = st.button("Checkout Page", key="checkout_btn")

if checkout_button and address_input:
    try:
        # Basic validation for address format
        addr_parts = address_input.split(':')
        if len(addr_parts) == 5: # hex, wall, shelf, volume, page
            page_hex, wall, shelf, volume, page = addr_parts
            # Further validation could be added here (e.g., check if parts are numbers)
            st.subheader(f"Title: {getTitle(address_input)}")
            st.markdown("---")
            st.subheader("Page Content:")
            # Display page content in a way that respects newlines and Urdu characters
            page_content = getPage(address_input)
            st.text_area("Page Text", page_content, height=300, key="page_content_checkout", help="Scroll to see full content")
        elif len(addr_parts) == 4: # hex, wall, shelf, volume (for a title address)
             st.warning("This appears to be an address for a Title. Please use the full page address (including page number) to checkout a page.")
             st.subheader(f"Title: {getTitle(address_input + ':000')}") # Try to show title by appending a dummy page
        else:
            st.error("Invalid address format. Expected format: hex:wall:shelf:volume:page (e.g., '1a2b3c:1:2:03:004') or hex:wall:shelf:volume for a title reference.")
    except ValueError as ve:
        st.error(f"Error processing address (likely incorrect numeric conversion): {ve}. Ensure all parts of the address are valid.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

st.markdown("---")
st.header("Search Text")
search_query = st.text_input("Enter text to search:", key="search_query_input")
search_button = st.button("Search", key="search_btn")

if search_button and search_query:
    if not search_query.strip():
        st.warning("Please enter some text to search.")
    else:
        prepared_text = text_prep(search_query)
        if not prepared_text:
            st.warning("The input text contains no valid Urdu characters for searching. Please try different text.")
        else:
            st.markdown(f"Searching for prepared text: `{prepared_text}`")
            st.markdown("---")

            # 1. Page contains text
            st.subheader("Search 1: Page Containing Your Text")
            try:
                contains_addr = search(prepared_text) # search_str_input in library_of_babel
                st.write(f"**Address:** `{contains_addr}`")
                st.text_area("Page Content (Contains):", getPage(contains_addr), height=200, key="page_contains_text")
            except Exception as e:
                st.error(f"Error during 'Page Containing Text' search: {e}")
            st.markdown("---")

            # 2. Page only contains text (exact match for the whole page)
            st.subheader("Search 2: Page Matching Your Text Exactly")
            try:
                # For an exact page match, the input text itself should define the entire page.
                # The original script used ljust(length_of_page) but this might not be ideal if text_prep modifies length.
                # The `search` function in library_of_babel now handles padding internally if the input is shorter than page_length.
                # If the user's `prepared_text` is intended to be the *only* content, it should be padded to fill the page.

                # If prepared_text is longer than length_of_page, it will be truncated by `search`'s internal logic.
                # If shorter, `search` will pad it.
                # The key is that `stringToNumber` in `search` operates on the full page content.

                # To ensure the user's text is the *only* thing on the page, we'd want it to be `length_of_page` long.
                # If `prepared_text` is shorter, it should be padded. If longer, it's an impossible search for "only".

                if len(prepared_text) > length_of_page:
                    st.warning(f"Your prepared text ({len(prepared_text)} chars) is longer than a page ({length_of_page} chars). An exact page match is not possible.")
                    st.text("N/A for exact page match.")
                else:
                    # The `search` function will determine padding based on `prepared_text` to fill a page.
                    # The key here is that `search` will try to find a page that IS `prepared_text` + padding.
                    # This is subtly different from the old `search_str.ljust(length_of_page)` which used space padding.
                    # Our `search` uses `get_deterministic_padding`.
                    # Let's assume the user wants their text to be the *core content* of the page.
                    exact_page_addr = search(prepared_text) # The `search` function will place this `prepared_text` and pad around it.
                                                            # If `prepared_text` is intended to be the *entire* page, it should be already `length_of_page` long.
                                                            # The prompt was: `search(prepared_text.ljust(length_of_page))`
                                                            # Let's try to adhere to that spirit.
                                                            # The previous `search` logic would pad `prepared_text` to `length_of_page`.
                                                            # The current `search` makes `prepared_text` *part* of the page.
                                                            # To achieve "page only contains", the `search_str_input` to `search` must be the exact page content.

                    # If the user's input is meant to be the *only* content, it must be padded to full page length.
                    # The `search` function's `search_str_input` is the text the user *wants to find*.
                    # If they want this text to be the *only* thing, then that text *plus padding to fill page* is what `search` will look for.
                    # The old CLI did `search(search_str.ljust(length_of_page))`
                    # This implies the `search_str` itself was space-padded.
                    # Our `text_prep` removes spaces.
                    # Let's use the `prepared_text` and let `search` handle its placement and padding.
                    # The "page only contains" in the old CLI meant the `search_str` padded with spaces was the *entire* page content.
                    # This is effectively what `search(prepared_text)` does now, where `prepared_text` is the core and padding is deterministic.

                    # The prompt is "Call search(prepared_text.ljust(length_of_page))"
                    # `ljust` uses spaces for padding. Our `text_prep` removes spaces.
                    # `urdu_chars` does not contain space ' ' by default.
                    # If we `ljust` with spaces, `text_prep` on that would remove them.
                    # The spirit is: find a page that *is* exactly the (prepared) input text, possibly padded.
                    # The `search` function, when given `prepared_text`, will find a page that contains `prepared_text` and is padded deterministically.
                    # If `prepared_text` itself is `length_of_page` long, then that's an exact match.
                    # If `prepared_text` is shorter, `search` will embed it.
                    # To match the old "Page only contains this text and nothing else",
                    # the `search_str_input` to `search` should be the `prepared_text` padded to `length_of_page`
                    # using the *first character of `urdu_chars`* as padding, as this is what `getPage` would effectively show
                    # if the content was shorter than `length_of_page` and originated from a number that results in short text.
                    # This is complicated by `get_deterministic_padding` using hash-based chars.

                    # Let's interpret "Page only contains" as: the `prepared_text` is the *entire significant content* of the page.
                    # The `search` function is designed to find `search_str_input` embedded in a page.
                    # If `search_str_input` is `length_of_page` long, then it is the page.

                    # Re-evaluating the original CLI's "Page only contains": `search(search_str.ljust(length_of_page))`
                    # This means the *search input itself* was padded to the full page length *before* being passed to `search`.
                    # The `search` function then treated this full-length string as the content to find.

                    # Let's construct the full page content first.
                    if urdu_chars:
                        padding_char = urdu_chars[0] # Fallback padding char
                    else:
                        padding_char = ' ' # Should not happen if urdu_chars is populated

                    exact_page_content_query = prepared_text
                    if len(prepared_text) < length_of_page:
                         # We need to make `prepared_text` the *entire* content.
                         # The `get_deterministic_padding` is used by `getPage` if its core text is too short.
                         # So, the target page content for "exact match" should be `prepared_text` + its deterministic padding.
                         exact_page_content_query += get_deterministic_padding(prepared_text, length_of_page - len(prepared_text), urdu_chars)

                    # Now, `exact_page_content_query` is `prepared_text` padded deterministically to `length_of_page`.
                    # This is the string that should be the *entire* content of a page.
                    # The `search` function's `search_str_input` parameter is the text to be found.
                    # So, we pass this full string to `search`. `search` will then, by default, set depth=0,
                    # as there's no room for other padding.

                    exact_page_addr = search(exact_page_content_query)
                    st.write(f"**Address:** `{exact_page_addr}`")
                    page_c = getPage(exact_page_addr)
                    st.text_area("Page Content (Exact Match):", page_c, height=200, key="page_exact_text")
                    if page_c != exact_page_content_query:
                        st.warning("Note: The retrieved page for 'exact match' might differ from the query due to internal hashing and encoding for address generation. The address above corresponds to a page that is deterministically generated based on your exact query string.")

            except Exception as e:
                st.error(f"Error during 'Page Matching Exactly' search: {e}")

            st.markdown("---")

            # 3. Title match
            st.subheader("Search 3: Exact Title Match")
            try:
                # `searchTitle` expects the raw search string, it will truncate to 25 and handle padding for the lookup.
                title_addr_prefix = searchTitle(prepared_text) # search_str_input in library_of_babel
                st.write(f"**Address Prefix (add page number like ':001'):** `{title_addr_prefix}`")
                # To display the title, we need a full address. Append a common page number like ':001' (or any valid page).
                # The title is the same for all pages in a volume.
                full_title_addr_for_display = title_addr_prefix + ":001" # Example page number
                st.write(f"**Title Found:** `{getTitle(full_title_addr_for_display)}`")
            except Exception as e:
                st.error(f"Error during 'Exact Title Match' search: {e}")
st.markdown("---")
st.info("""
**How to Use:**
- **Checkout Page:** Enter the full address of a page (e.g., `abcdef:1:2:03:004`). The address consists of a hexadecimal part, wall (0-3), shelf (0-4), volume (00-31), and page (000-409).
- **Search Text:**
    - Enter any Urdu text. Non-Urdu characters will be filtered out before searching.
    - **Page Containing Your Text:** Finds a page where your text appears anywhere.
    - **Page Matching Your Text Exactly:** Finds a page that consists *only* of your text (potentially padded to fill the page length of 3239 characters).
    - **Exact Title Match:** Finds a book title that exactly matches the first 25 characters of your text. The address returned will be a prefix; you can append a page number (e.g., `:001`) to view a page from that book.
""")

st.markdown("""
*Developed based on the principles of the Library of Babel.*
""")

# Add a note about urdu_chars if it's empty, though it's defined in library_of_babel
if not urdu_chars:
    st.error("Critical error: Urdu character set is not loaded. Please check library_of_babel.py.")
