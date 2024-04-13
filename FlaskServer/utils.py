def merge_and_sort(part_set, whole_set):
    # Get the elements in set2 that are not in set1
    unique_set2 = sorted(list(whole_set - part_set))

    # Sort set1
    sorted_set1 = sorted(list(part_set))

    # Merge set1, unique_set2, and any remaining elements of set2
    return sorted_set1 + unique_set2

def format_timestamp(date):
    # Format the datetime object into the desired string format
    formatted_timestamp = date.strftime('%d-%m-%Y %H:%M')

    return formatted_timestamp