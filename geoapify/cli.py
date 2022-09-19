import logging
import click

from geoapify import Client


logging.basicConfig(level=logging.DEBUG)

CONTEXT_SETTINGS = {
    'help_option_names': ['-h', '--help']
}


@click.group(context_settings=CONTEXT_SETTINGS)
def main():
    """
    CLI for the Geoapify REST API.

    \b
    geoapify <something>  -> Do something.
    """
    pass


@main.command()
@click.argument('path_input_file', type=click.Path(exists=True))
@click.option('-k', '--key', default=None)
def post_batch_jobs(path_input_file, key):
    if key is None:
        pass  # TODO read from env variables if not provided
    client = Client(api_key=key)

    # TODO: read inputs and parameters from file
    result_urls = client.batch.post_batch_jobs_and_get_job_urls(api='', inputs=[])
    # TODO: write result_urls to disk


if __name__ == '__main__':
    main()
