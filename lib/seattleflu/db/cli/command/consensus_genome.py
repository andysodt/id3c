"""
Backfill previously generated consensus genomes that were not uploaded to ID3C.
"""
import click
import logging
import json
from seattleflu.db.cli import cli
from seattleflu.db.session import DatabaseSession


LOG = logging.getLogger(__name__)

@cli.group("consensus-genome", help=__doc__)
def consensus_genome():
    pass

@consensus_genome.command("upload")
@click.argument("consensus_genome-file",
    metavar = "<consensus_genome.ndjson>",
    type = click.File("r"))

def upload(consensus_genome_file):
    """
    Upload consensus genomes and summary statistics to the warehouse receiving area.

    Consensus genomes and summary statistics should be in newline-delimited JSON
    format that matches those generated by the assembly pipeline.
    """
    db = DatabaseSession()

    try:
        LOG.info(f"Copying consensus genome records from {consensus_genome_file.name}")

        row_count = db.copy_from_ndjson(("receiving", "consensus_genome", "document"), consensus_genome_file)

        LOG.info(f"Received {row_count:,} consensus genome records")
        LOG.info("Committing all changes")
        db.commit()

    except:
        LOG.info("Rolling back all changes; the database will not be modified")
        db.rollback()
        raise
