"""
De-identify personally identifiable information (PII) by generating a hash.
"""
import click
import logging
import hashlib
import pandas as pd
from os import environ
from sys import stdout
from typing import Tuple
from id3c.cli import cli
from id3c.cli.io.pandas import (
    load_input_from_file_or_stdin,
)


LOG = logging.getLogger(__name__)

@cli.command("de-identify")
@click.argument("columns",
    metavar = "<columns>",
    nargs = -1)

@click.argument("filename",
    metavar = "<filename.{csv,tsv,xls,xlsx}>",
    type = click.File("r"))

@click.option("--drop-input-columns",
    is_flag = True,
    help = "Optional flag to drop <columns> from output")

def de_identify(columns, filename, drop_input_columns):
    """
    De-identify data by generating a hash.

    Given a <filename.{csv,tsv,xls,xlsx}> that contains personally identifiable
    information (PII), generate a hash using specified <columns> and an environment
    variable, "ID3C_DEIDENTIFY_SECRET".

    <columns> are column names of fields to include in the hash. All values are
    joined in the order of of the column names, so keep the order of column
    names consistent!

    <columns> values are expected to be canonicalized before running this
    command!

    <filename.{csv,tsv,xls,xlsx}> accepts `-` as a special file that refers
    to stdin, assuming data is formatted as comma-separated values.
    This is expected when piping output from `id3c geocode` directly into
    this command.

    Generated hashes are output to stdout along with input data as
    comma-separated values. Provided <columns> can be dropped with the
    --drop-input-columns flag.
    """
    input_df = load_input_from_file_or_stdin(filename)
    fields_to_include = extract_fields_from_input(input_df, columns)
    joined_fields = fields_to_include.apply(lambda x: ' '.join(x), axis=1)

    hashes = joined_fields.map(lambda x: generate_hash(x) if x else None)

    output_df = input_df.copy()
    output_df['hash'] = hashes

    if drop_input_columns:
        try:
            output_df.drop(columns = list(columns), inplace = True)
        except KeyError as error:
            LOG.error(f"{error}. Columns are: {list(output_df.columns)}")
            raise error from None

    output_df.to_csv(stdout, index = False)


def extract_fields_from_input(input_df: pd.DataFrame,
                              columns: Tuple[str, ...]) -> pd.DataFrame:
    """
    Extract specified *columns* from the *input* and return values as a
    pandas DataFrame
    """
    try:
        fields = input_df[list(columns)]

    except KeyError as error:
        LOG.error(f"{error}. Input columns: {list(input_df.columns)}")
        raise error from None

    return fields


def generate_hash(identifier: str, secret: str = None) -> str:
    """
    Hash *secret* with *identifier* that is linked to identifiable records.

    >>> generate_hash("foo", "abadsecret")
    '72a79a0f21b20b9c7d0a117addc0d917bcda3065c9c8329aea77b11cb39096c8'

    >>> generate_hash("foo", "")
    Traceback (most recent call last):
        ...
    AssertionError: Empty *secret* provided!
    ...

    >>> generate_hash("", "abadsecret")
    Traceback (most recent call last):
        ...
    AssertionError: Empty *identifier* provided!
    ...

    >>> generate_hash("foo")
    Traceback (most recent call last):
        ...
    Exception: The environment variable ID3C_DEIDENTIFY_SECRET is required.

    >>> import os
    >>> os.environ["ID3C_DEIDENTIFY_SECRET"] = ""
    >>> generate_hash("foo")
    Traceback (most recent call last):
        ...
    AssertionError: Empty *secret* provided!
    ...

    >>> os.environ["ID3C_DEIDENTIFY_SECRET"] = "abadsecret"
    >>> generate_hash("foo")
    '72a79a0f21b20b9c7d0a117addc0d917bcda3065c9c8329aea77b11cb39096c8'
    """
    if secret is None:
        try:
            secret = environ["ID3C_DEIDENTIFY_SECRET"]
        except KeyError:
            raise Exception("The environment variable ID3C_DEIDENTIFY_SECRET is required.")

    assert len(identifier) > 0, "Empty *identifier* provided!"
    assert len(secret) > 0, "Empty *secret* provided!"

    new_hash = hashlib.sha256()
    new_hash.update(identifier.encode("utf-8"))
    new_hash.update(secret.encode("utf-8"))
    return new_hash.hexdigest()
