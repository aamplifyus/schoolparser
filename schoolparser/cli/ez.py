import click
from click_help_colors import HelpColorsGroup, version_option

from .about import about
from .channel_annotations import view_bad_chs, annotate_bad_chs, delete_bad_chs
from .metadata import metadata
from .pat_summary import pat_summary
from .plot import plot
from .run import run

"""
.. click:: ez:entry
    :prog: entry
    :show-nested:
    
    .. code-block:: python
       :linenos
       ez metadata [options]
       ez pat-summary [options]
       ez run [options]
       ez plot [options]
       ez analysis [options]
"""


@click.group(
    cls=HelpColorsGroup, help_headers_color="yellow", help_options_color="green",
)
@version_option(version="1.0", prog_name="EZTrack", message_color="yellow")
@click.pass_context
def entry(ctx):
    """
    Entry point for EZTrack. 
    
    The workflow of the CLI assumes that you have
    securely uploaded your EEG data to EZTrack and properly annotated. For additional information
    on how datasets are identified, please refer to the EZTrack User Manual.

    To run EZTrack on a specified subject dataset, the minimal command is:

        ez run --subject_id <sub_id> --session_id <session_id> --run_id <run_id>

    See below for more options. To see the full instructions on a specific command, view its help message. For
    instance, for run, that would be

        ez run --help

    """


entry.add_command(metadata)
entry.add_command(pat_summary)
entry.add_command(run)
entry.add_command(plot)
entry.add_command(annotate_bad_chs)
entry.add_command(delete_bad_chs)
entry.add_command(view_bad_chs)
entry.add_command(about)
