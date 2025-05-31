#!/usr/bin/env python
import string
# import random # No longer used after deterministic changes
import sys
import hashlib

length_of_page = 3239
# loc_mult and title_mult should be based on the actual charset size (len(urdu_chars))
# This will be initialized properly after urdu_chars is defined.
loc_mult = None
title_mult = None


help_text = '''
--checkout <addr> - Checks out a page of a book. Also displays the page's title.

--fcheckout <file>   Does exactly the search does, but with address in the file.

--search <'text'> - Does 3 searches for the text you input:
>Page contains: Finds a page which contains the text.
>Page only contains: Finds a page which only contains that text and nothing else.
>Title match: Finds a title which is exactly this string. For a title match, it will only match the first 25 characters. Addresses returned for title matches will need to have a page number added to the tail end, since they lack this.
Mind the quotemarks.

--fsearch <file> - Does exactly the search does, but with text in the file.

--file <file> - Dump result into the file

--help (or help, or nothing, or word salad) - Prints this message'''

urdu_chars = sorted(set("۰ ۱ ۲ ۳ ۴ ۵ ۶ ۷ ۸ ۹"
                "آ أ ا ب پ ت ٹ ث ج چ ح خ د ڈ ذ ر ڑ ز ژ س ش ص ض ط ظ ع غ ف ق ک گ ل "
                " م ن ں و ؤ ہ ۂ ۃ ھ ء ی ئ ے ۓ \n"
                "؛ ، ٫  ؟ ۔ ٪"
                "\u064e \u064B \u0670 \u0650 \u064F \u064d"
                " ؀ ؁ ؂ ؃ ؍ ؎ ؏ ؐ ؑ ؒ ؓ ؔ ؕ ٌ ّ ْ ٓ ٔ ٖ ٗ ٘ ٬"))

# Initialize multipliers after urdu_chars is defined and its length is known
BASE_CHAR_COUNT = len(urdu_chars)
if BASE_CHAR_COUNT == 0:
    raise ValueError("Urdu character set is empty, cannot proceed.")

loc_mult = pow(BASE_CHAR_COUNT, length_of_page)
title_mult = pow(BASE_CHAR_COUNT, 25)


def get_deterministic_padding(seed_string, target_length, charset):
    """Generates a fixed string of a given length using characters from charset based on the seed_string."""
    if not charset:
        return ""  # Or raise an error if charset cannot be empty

    padding = []
    current_hash = hashlib.sha256(seed_string.encode('utf-8')).hexdigest()
    hash_index = 0
    charset_len = len(charset)

    while len(padding) < target_length:
        if hash_index + 2 > len(current_hash):
            # Rehash the current hash if we've run out of bytes
            current_hash = hashlib.sha256(current_hash.encode('utf-8')).hexdigest()
            hash_index = 0

        hex_byte_str = current_hash[hash_index:hash_index+2]
        char_code = int(hex_byte_str, 16)
        padding.append(charset[char_code % charset_len])
        hash_index += 2

    return "".join(padding)

def text_prep(text):
    # digs = set('abcdefghijklmnopqrstuvwxyz, .')
    prepared = ''
    for letter in text:
        if letter in urdu_chars:
            prepared += letter
        # elif letter.lower() in digs:
        #     prepared += letter.lower()
        # elif letter == '\n':
        #     prepared += ' '
    return prepared



def arg_check(input_array):
    coms = {'--checkout': [0, None],
            '--search': [0, None],
             '--test': [0, None],
             '--fsearch': [0, None],
             '--fcheckout': [0, None],
             '--file': [0, None]}
    try:
        for argv in input_array[1:]:
            if argv == '--checkout':
                coms['--checkout'][0] = 1
                coms['--checkout'][1] = input_array[input_array.index(argv) + 1]
            if argv == '--search':
                coms['--search'][0] = 1
                coms['--search'][1] = input_array[input_array.index(argv) + 1]
            if argv == '--test':
                coms['--test'][0] = 1
            if argv == '--fsearch':
                coms['--fsearch'][0] = 1
                coms['--fsearch'][1] = input_array[input_array.index(argv) + 1]
            if argv == '--fcheckout':
                coms['--fcheckout'][0] = 1
                coms['--fcheckout'][1] = input_array[input_array.index(argv) + 1]
            if argv == '--file':
                coms['--file'][0] = 1
                coms['--file'][1] = input_array[input_array.index(argv) + 1]
        if input_array[1:] is not False or len(input_array) == 1:
            in_coms = False
            for inp in input_array[1:]:
                if inp in coms:
                    in_coms = True
            if not in_coms:
                print(help_text)
    except Exception as e:
        print('Due to \'' + str(e) + ' error\' read this:')
        print(help_text)
        sys.exit()
    return coms


def filed(input_dict, text):
    if input_dict['--file'][0]:
        with open(input_dict['--file'][1], 'w') as file:
            file.writelines(text)
        print('\nFile '+ input_dict['--file'][1] + ' was writen')



# def test():
#     assert stringToNumber('a') == 0, stringToNumber('a')
#     assert stringToNumber('ba') == 89, stringToNumber('ba')
#     assert len(getPage('asaskjkfsdf:2:2:2:33')) == length_of_page, len(getPage('asasrkrtjfsdf:2:2:2:33'))
#     assert 'hello kitty' == toText(int(int2base(stringToNumber('hello kitty'), 36), 36))
#     assert int2base(4, 36) == '4', int2base(4, 36)
#     assert int2base(10, 36) == 'A', int2base(10, 36)
#     test_string = '.................................................'
#     assert test_string in getPage(search(test_string))
#     print ('Tests completed')


def main(input_dict):
    if input_dict['--checkout'][0]:
        key_str = input_dict['--checkout'][1]
        text  ='\nTitle: '+getTitle(key_str) + '\n'+getPage(key_str)+'\n'
        print(text)
        filed(input_dict, text)
    elif input_dict['--search'][0]:
        search_str = text_prep(input_dict['--search'][1])
        key_str = search(text_prep(search_str))
        text1 = '\nPage which includes this text:\n' + getPage(key_str)+'\n\n@ address '+key_str+'\n'
        only_key_str = search(search_str.ljust(length_of_page))
        text2 = '\nPage which contains only this text:\n'+ getPage(only_key_str)+'\n\n@ address '+only_key_str+'\n'
        text3 = '\nTitle which contains this text:\n@ address '+ searchTitle(search_str)
        text = text1 + text2 + text3
        print(text)
        filed(input_dict, text)
    elif input_dict['--test'][0]:
        test()
    elif input_dict['--fsearch'][0]:
        file = input_dict['--fsearch'][1]
        with open(file, 'r') as f:
            lines = ''.join([line for line in f.readlines() if line != '\n'])
        search_str = text_prep(lines)
        key_str = search(search_str)
        text1 = '\nPage which includes this text:\n'+ getPage(key_str) +'\n\n@ address '+ key_str +'\n'
        only_key_str = search(search_str.ljust(length_of_page))
        text2 = '\nPage which contains only this text:\n' + getPage(only_key_str) + '\n\n@ address '+ only_key_str +'\n'
        text3 = '\nTitle which contains this text:\n@ address ' + searchTitle(search_str) +'\n'
        text = text1 + text2 + text3
        print(text)
        filed(input_dict, text)
    elif input_dict['--fcheckout'][0]:
        file = input_dict['--fcheckout'][1]
        with open(file, 'r') as f:
            key_str = ''.join([line for line in f.readlines() if line != '\n'])[:-1]
        text  ='\nTitle: '+getTitle(key_str) + '\n'+getPage(key_str)+'\n'
        print(text)
        filed(input_dict, text)

def search(search_str_input):
    # Use a hash of the input search string to derive values
    # Using a different seed for each value group by slicing or rehashing if necessary
    base_hash = hashlib.sha256(search_str_input.encode('utf-8')).hexdigest()

    # Derive wall, shelf, volume, page from the hash
    # Ensure values are within their original ranges
    # Use different parts of the hash for different values to ensure some independence
    hash_int = int(base_hash[:16], 16) # Use first 16 hex chars for these

    wall = str((hash_int >> 0) % 4)
    shelf = str((hash_int >> 2) % 5) # Use next bits for shelf
    volume_val = (hash_int >> 4) % 32 # Use next bits for volume
    volume = str(volume_val).zfill(2)
    page_val = (hash_int >> 9) % 410 # Use next bits for page
    page = str(page_val).zfill(3)

    loc_str = page + volume + shelf + wall
    loc_int = int(loc_str)

    # Derive depth for front_padding
    # Use another part of the hash for depth
    depth_hash_int = int(base_hash[16:32], 16) # Use next 16 hex chars

    # If search_str_input is too long, truncate it and set depth to 0.
    current_search_str = search_str_input
    if len(current_search_str) >= length_of_page:
        current_search_str = current_search_str[:length_of_page]
        depth = 0
    else:
        max_depth = length_of_page - len(current_search_str)
        # max_depth will always be > 0 here.
        depth = depth_hash_int % max_depth

    front_padding_seed = current_search_str + "_front"
    front_padding = get_deterministic_padding(front_padding_seed, depth, urdu_chars)

    # The length of the main content (front_padding + current_search_str)
    content_so_far_len = depth + len(current_search_str)
    back_padding_len = length_of_page - content_so_far_len

    # Ensure back_padding_len is not negative (it shouldn't be if logic above is correct)
    if back_padding_len < 0:
        back_padding_len = 0

    back_padding_seed = current_search_str + "_back"
    back_padding = get_deterministic_padding(back_padding_seed, back_padding_len, urdu_chars)

    page_content_to_find = front_padding + current_search_str + back_padding

    # At this point, page_content_to_find should be exactly length_of_page.
    # If it's not, there's a flaw in the padding length calculations.
    # Let's assert this for development, then remove if confident or handle.
    if len(page_content_to_find) != length_of_page:
        # This case should ideally not be reached. If it is, it means the logic for calculating
        # depth, front_padding_len, or back_padding_len is incorrect.
        # For robustness, one might truncate or pad, but it masks the underlying error.
        # For now, let's ensure it by simple truncation/padding as a last resort,
        # but flag that this is non-ideal.
        # print(f"Warning: page_content_to_find length is {len(page_content_to_find)}, expected {length_of_page}. Adjusting.")
        if len(page_content_to_find) > length_of_page:
            page_content_to_find = page_content_to_find[:length_of_page]
        else:
            # This specific padding here is a sign of an error in length calculation above.
            # It should be filled by get_deterministic_padding to be consistent, but which seed?
            # The original ljust was a bug.
            # Forcing it to length_of_page by appending a default char if calculations were wrong.
            if urdu_chars:
                 page_content_to_find = (page_content_to_find + urdu_chars[0] * length_of_page)[:length_of_page]
            else: # Should not happen
                 page_content_to_find = (page_content_to_find + ' ' * length_of_page)[:length_of_page]

    hex_addr = int2base(stringToNumber(page_content_to_find) + (loc_int * loc_mult), 36)
    key_str = hex_addr + ':' + wall + ':' + shelf + ':' + volume + ':' + page

    # Test the generated key
    page_text_from_key = getPage(key_str)

    # The assertion should compare the page content derived by getPage(key_str)
    # with the page_content_to_find that was used to generate the key_str's hex_addr.
    assert page_text_from_key == page_content_to_find, \
        f"\nAssertionError in search:\nGenerated page text does not match expected page content.\n" + \
        f"Expected ({len(page_content_to_find)} chars):\n'{page_content_to_find}'\n" + \
        f"Got ({len(page_text_from_key)} chars):\n'{page_text_from_key}'\n" + \
        f"Search input: '{search_str_input}'\nKey: '{key_str}'"

    return key_str

def getTitle(address):
    addressArray = address.split(':')
    hex_addr = addressArray[0]
    wall = addressArray[1]
    shelf = addressArray[2]
    volume = addressArray[3].zfill(2)
    loc_int = int(volume+shelf+wall)
    key = int(hex_addr, 36)
    key -= loc_int*title_mult
    # key is the numerical representation of the title content.
    # No need to convert to base 36 string and back.
    result = toText(key, target_length=25) # Pass key directly

    # The following deterministic padding should not be needed if toText guarantees length
    # and the title was generated from a 25-char string.
    # However, if a title can be conceptually shorter and then padded:
    padding_needed = 25 - len(result)
    if padding_needed > 0:
        # This implies the original number for title was "smaller" than a full 25-char string of urdu_chars[0]
        # Or title_content_to_find in searchTitle was shorter than 25 before stringToNumber
        # getTitle is now responsible for ensuring final length is 25.
        # The toText will provide a base string of 25 chars (potentially left-padded with urdu_chars[0]).
        # If the *semantic* content is shorter, and then deterministically padded, that's different.
        # The current design of searchTitle creates a 25-char title_content_to_find.
        # So, toText(key, target_length=25) should be sufficient.
        # Let's rely on toText to handle the length.
        pass # result should already be 25 characters.

    # Ensure it's exactly 25, as a final check (toText should handle this)
    if len(result) != 25:
        # This would indicate an issue with toText's target_length logic
        result = (result + urdu_chars[0] * 25)[:25] if urdu_chars else (result + ' ' * 25)[:25]
    return result

def searchTitle(search_str_input):
    # Use a hash of the input search string to derive values
    base_hash = hashlib.sha256(search_str_input.encode('utf-8')).hexdigest()

    # Derive wall, shelf, volume from the hash
    # Using first 8 hex characters for this, can be adjusted.
    hash_int = int(base_hash[:8], 16)

    wall = str(hash_int % 4)
    shelf = str((hash_int >> 2) % 5) # Use next bits
    volume_val = (hash_int >> 4) % 32 # Use next bits
    volume = str(volume_val).zfill(2)

    loc_str = volume + shelf + wall
    loc_int = int(loc_str)

    # Prepare the search string for title: max 25 chars, padded to 25
    # The original searchTitle uses the *input* search_str for ljust after truncating.
    # The padding character for ljust in the original is space ' '.
    # Our get_deterministic_padding uses urdu_chars.
    # For consistency with original title search logic, we must replicate its padding.
    # However, getTitle itself now uses deterministic urdu_char padding.
    # The search_str for title should be what getTitle is expected to produce *before* its own padding.

    processed_search_str = search_str_input[:25]
    # If shorter than 25, getTitle will pad it.
    # If exactly 25, getTitle will use it as is.
    # If longer than 25, getTitle truncates.
    # The stringToNumber should be based on this (potentially shorter) string.
    # The key generated must allow getTitle to reconstruct this.

    # The original searchTitle does: search_str = search_str[:25].ljust(25)
    # This means it pads with spaces. If getTitle is to match this,
    # it must be able to produce this exact space-padded string if the original string < 25.
    # But getTitle is now modified to use urdu_chars for padding.
    # This creates a mismatch.
    # For the assertion `assert search_str == getTitle(key_str)` to hold,
    # `search_str` here must be what `getTitle` would output for `key_str`'s text component.

    # Let's define `title_content_to_find` as what `getTitle` should produce from `key_str`'s text part.
    # This is the original `search_str_input` truncated to 25 chars,
    # and if shorter than 25, it will be padded by `getTitle` using `get_deterministic_padding`.

    title_content_to_find = search_str_input[:25]
    if len(title_content_to_find) < 25:
        # This is how getTitle will pad it.
        padding = get_deterministic_padding(title_content_to_find, 25 - len(title_content_to_find), urdu_chars)
        title_content_to_find += padding
    # If search_str_input was longer than 25, title_content_to_find is now exactly 25 chars.

    hex_addr = int2base(stringToNumber(title_content_to_find) + (loc_int * title_mult), 36)
    key_str = hex_addr + ':' + wall + ':' + shelf + ':' + volume

    # Test the generated key
    title_from_key = getTitle(key_str)

    assert title_from_key == title_content_to_find, \
        f"\nAssertionError in searchTitle:\nGenerated title does not match expected title content.\n" + \
        f"Expected ({len(title_content_to_find)} chars):\n'{title_content_to_find}'\n" + \
        f"Got ({len(title_from_key)} chars):\n'{title_from_key}'\n" + \
        f"Search input: '{search_str_input}'\nKey: '{key_str}'"

    return key_str

def getPage(address):
    hex_addr, wall, shelf, volume, page = address.split(':')
    volume = volume.zfill(2)
    page = page.zfill(3)
    loc_int = int(page+volume+shelf+wall)
    key = int(hex_addr, 36)
    key -= loc_int*loc_mult
    # key is the numerical representation of the page content.
    result = toText(key, target_length=length_of_page)

    # The get_deterministic_padding call is for cases where the page's inherent content
    # (represented by `key`) is conceptually shorter than length_of_page, and this
    # additional padding makes it unique.
    # However, if `key` was generated by `search`, `result` from `toText` should already be
    # `length_of_page` long (due to `target_length` in `toText`).
    # Thus, `padding_needed` should be 0 for such keys.
    padding_needed = length_of_page - len(result)
    if padding_needed > 0:
        # This block should ideally not be hit if key comes from search() of a full page string.
        # If it is hit, it means `toText` with `target_length` didn't produce the full length,
        # or the original number `key` was truly "small".
        additional_padding = get_deterministic_padding(result, padding_needed, urdu_chars)
        result += additional_padding

    # Final check for length, toText should manage this.
    if len(result) != length_of_page:
        # This indicates an issue with toText or the padding logic above.
        result = (result + urdu_chars[0] * length_of_page)[:length_of_page] if urdu_chars else (result + ' ' * length_of_page)[:length_of_page]

    return result

def toText(x, target_length=None):
    digs_list = list(urdu_chars) # Use the list directly
    if not digs_list:
        return ""

    if x == 0:
        if target_length is not None:
            return digs_list[0] * target_length
        return digs_list[0]

    sign = 1
    if x < 0:
        sign = -1
        x *= -1

    output_digits = []
    while x:
        output_digits.append(digs_list[x % BASE_CHAR_COUNT])
        x //= BASE_CHAR_COUNT

    if target_length is not None:
        while len(output_digits) < target_length:
            output_digits.append(digs_list[0])
        if len(output_digits) > target_length:
            # Keep the least significant target_length digits
            output_digits = output_digits[:target_length]

    if sign < 0:
        output_digits.append('-')

    output_digits.reverse()
    return "".join(output_digits)

def stringToNumber(iString):
    digs_list = list(urdu_chars) # Use the list directly
    result = 0
    for x_idx in range(len(iString)):
        char = iString[len(iString) - 1 - x_idx]
        try:
            result += digs_list.index(char) * pow(BASE_CHAR_COUNT, x_idx)
        except ValueError:
            # Handle character not in urdu_chars, though text_prep should prevent this for user input.
            # For content generated by get_deterministic_padding, it should always be valid.
            # Consider raising an error or specific handling if a char is not found.
            # For now, mimics original implicit behavior (would fail if char not in ''.join(list(urdu_chars)))
            raise ValueError(f"Character '{char}' not found in urdu_chars during stringToNumber.")
    return result

def int2base(x, base):
    digs = string.digits + 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    if x < 0: sign = -1
    elif x == 0: return digs[0]
    else: sign = 1
    x *= sign
    digits = []
    while x:
        digits.append(digs[x % base])
        x //= base
    if sign < 0:
        digits.append('-')
    digits.reverse()
    return ''.join(digits)

def test_search_and_getPage_consistency():
    print("Running internal test: test_search_and_getPage_consistency...")

    test_query = "اردو میری پسندیدہ زبان ہے"
    prepared_query = text_prep(test_query)

    # --- Test 1: Standard search (text embedded in a page) ---
    print("Test 1: Standard search (prepared_query embedded in a page)")
    search_key_full_page = search(prepared_query) # This call already has an internal assertion

    # Manually reconstruct expected content for external verification
    base_hash_for_depth = hashlib.sha256(prepared_query.encode('utf-8')).hexdigest()
    depth_hash_int = int(base_hash_for_depth[16:32], 16)

    current_search_str_for_depth_calc = prepared_query
    if len(current_search_str_for_depth_calc) >= length_of_page:
        # This path won't be taken by our short prepared_query
        depth_for_expected = 0
        current_search_str_for_depth_calc = current_search_str_for_depth_calc[:length_of_page]
    else:
        max_depth_for_expected = length_of_page - len(current_search_str_for_depth_calc)
        depth_for_expected = depth_hash_int % max_depth_for_expected

    front_padding_seed = current_search_str_for_depth_calc + "_front"
    expected_front_padding = get_deterministic_padding(front_padding_seed, depth_for_expected, urdu_chars)

    content_so_far_len = depth_for_expected + len(current_search_str_for_depth_calc)
    expected_back_padding_len = length_of_page - content_so_far_len
    if expected_back_padding_len < 0: expected_back_padding_len = 0 # Should not happen

    back_padding_seed = current_search_str_for_depth_calc + "_back"
    expected_back_padding = get_deterministic_padding(back_padding_seed, expected_back_padding_len, urdu_chars)

    expected_content_full_page_search = expected_front_padding + current_search_str_for_depth_calc + expected_back_padding

    # Ensure expected_content is exactly length_of_page (it should be by construction)
    if len(expected_content_full_page_search) != length_of_page:
        print(f"Warning (Test 1): expected_content_full_page_search length is {len(expected_content_full_page_search)}, adjusting.")
        if len(expected_content_full_page_search) > length_of_page:
            expected_content_full_page_search = expected_content_full_page_search[:length_of_page]
        else:
            expected_content_full_page_search = (expected_content_full_page_search + urdu_chars[0] * length_of_page)[:length_of_page]


    retrieved_content_full_page = getPage(search_key_full_page)
    assert retrieved_content_full_page == expected_content_full_page_search, \
        f"Test 1 Failed: Retrieved content does not match expected reconstructed content.\n" + \
        f"Expected ({len(expected_content_full_page_search)}):\n'{expected_content_full_page_search}'\n" + \
        f"Got ({len(retrieved_content_full_page)}):\n'{retrieved_content_full_page}'"
    print("Test 1: External assertion passed.")

    # --- Test 2: Exact page match (prepared_query is the basis for the entire page) ---
    print("\nTest 2: Exact page match (prepared_query forms the basis of the entire page)")
    exact_page_content_query = prepared_query
    if len(prepared_query) < length_of_page:
        # This logic is similar to app.py's construction for "exact page match"
        padding_for_exact = get_deterministic_padding(prepared_query, length_of_page - len(prepared_query), urdu_chars)
        exact_page_content_query = prepared_query + padding_for_exact
    elif len(prepared_query) > length_of_page:
        exact_page_content_query = prepared_query[:length_of_page]
    # If len(prepared_query) == length_of_page, it's used as is.

    search_key_exact_match = search(exact_page_content_query) # Internal assertion runs

    retrieved_content_exact_match = getPage(search_key_exact_match)
    assert retrieved_content_exact_match == exact_page_content_query, \
        f"Test 2 Failed: Retrieved content does not match the exact query content.\n" + \
        f"Expected ({len(exact_page_content_query)}):\n'{exact_page_content_query}'\n" + \
        f"Got ({len(retrieved_content_exact_match)}):\n'{retrieved_content_exact_match}'"
    print("Test 2: External assertion passed.")

    print("\nInternal test_search_and_getPage_consistency successfully passed.")


if __name__ == "__main__":
    # Original main execution:
    input_dict= arg_check(sys.argv)
    main(input_dict)
