from typing import Any
import click
import streamlit.cli
from streamlit.cli import configurator_options
import os


@click.command(context_settings=dict(ignore_unknown_options=True,
                                     allow_extra_args=True))
@configurator_options
@click.argument("args", nargs=-1)
@click.pass_context
def manage(ctx: click.Context, args: Any, **kwargs: Any):
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'ui/management_dash.py')
    ctx.forward(streamlit.cli.main_run, target=filename, args=args, *kwargs)


@click.command(context_settings=dict(ignore_unknown_options=True,
                                     allow_extra_args=True))
@configurator_options
@click.argument("args", nargs=-1)
@click.pass_context
def ui(ctx: click.Context, args: Any, **kwargs: Any):
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'ui/inference_dash.py')
    ctx.forward(streamlit.cli.main_run, target=filename, args=args, *kwargs)
