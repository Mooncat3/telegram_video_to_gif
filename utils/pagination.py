from math import ceil


def split_pages(total: int, per_page: int):
    return ceil(max(total, 1) / per_page)
