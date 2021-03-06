"""
Commands for the database CLI.
"""
import click
import logging
from functools import wraps
from id3c.db.session import DatabaseSession


__all__ = [
    "etl",
    "identifier",
    "location",
    "manifest",
    "user",
    "sequence_read_set",
    "consensus_genome",
    "redcap_det",
    "receiving",
    "geocode",
    "de_identify",
    "refresh_materialized_view",
]


LOG = logging.getLogger(__name__)


def with_database_session(command):
    """
    Decorator to provide database session and error handling for a command.

    The decorated function is called with a ``db`` keyword argument to provide
    a :class:`~id3c.db.session.DatabaseSession` object.  The call happens
    within an exception handler that commits or rollsback the database
    transaction, possibly interactively.  Three new options are added to the
    command (``--dry-run``, ``--prompt``, and ``--commit``) to control this
    behaviour.
    """
    @click.option("--dry-run", "action",
        help        = "Only go through the motions of changing the database (default)",
        flag_value  = "rollback",
        default     = True)

    @click.option("--prompt", "action",
        help        = "Ask if changes to the database should be saved",
        flag_value  = "prompt")

    @click.option("--commit", "action",
        help        = "Save changes to the database",
        flag_value  = "commit")

    @wraps(command)
    def decorated(*args, action, **kwargs):
        db = DatabaseSession()

        processed_without_error = None

        try:
            command(*args, **kwargs, db = db)

        except Exception as error:
            processed_without_error = False

            LOG.error(f"Aborting with error: {error}")
            raise error from None

        else:
            processed_without_error = True

        finally:
            if action == "prompt":
                ask_to_commit = \
                    "Commit all changes?" if processed_without_error else \
                    "Commit successfully processed records up to this point?"

                commit = click.confirm(ask_to_commit)
            else:
                commit = action == "commit"

            if commit:
                LOG.info(
                    "Committing all changes" if processed_without_error else \
                    "Committing successfully processed records up to this point")
                db.commit()

            else:
                LOG.info("Rolling back all changes; the database will not be modified")
                db.rollback()

    return decorated
