import logging
import requests
from tempfile import NamedTemporaryFile


def get_data(tar_url: str, target: str, processor):
    result = None
    logging.info('Starting the download of %s', tar_url)
    req = requests.get(tar_url, stream=True, allow_redirects=True)
    buf = NamedTemporaryFile()
    for block in req.iter_content(chunk_size=4096):
        buf.write(block)
    buf.flush()
    logging.debug('Download finished, starting extraction')
    result = processor(buf, target)
    buf.close()

    logging.info(f'File extracted to %s', result.as_posix())
    return result.as_posix()
