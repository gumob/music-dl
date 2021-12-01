#!/usr/bin/env python
# coding: utf-8


def padded_num(num=-1, max_num=1):
    """
    The function that convert int to zero padded string

    :param int num: Number to be converted to string
    :param int max_num: Numbers to determine digits
    :return:
    """

    digit = len(str(max_num))
    if num >= 0:
        return str(num).zfill(digit)
    else:
        return '?' * digit


def contains_at_least(l1, l2):
    """
    Checking if two lists share at least one element
    https://stackoverflow.com/questions/24270711/checking-if-two-lists-share-at-least-one-element

    :param list l1: Array to compare
    :param list l2: Array to compare
    :return: bool result: If two lists share at least one element, return true
    """

    return any(x in l1 for x in l2)
