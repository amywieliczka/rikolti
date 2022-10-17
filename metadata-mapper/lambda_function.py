import json
import os
import sys

from nuxeo_mapper import NuxeoVernacular
from mapper import UCLDCWriter
from oac_mapper import OAC_Vernacular
from islandora_oai_dc_mapper import IslandoraVernacular

DEBUG = os.environ.get('DEBUG', False)


def get_source_vernacular(source_type):
    if source_type == 'NuxeoMapper':
        return NuxeoVernacular
    if source_type == 'oac_dc':
        return OAC_Vernacular
    if source_type == 'islandora_oai_dc_mapper':
        return IslandoraVernacular


# {"collection_id": 26098, "source_type": "nuxeo", "page_filename": "r-0"}
# {"collection_id": 26098, "source_type": "nuxeo", "page_filename": 2}
def lambda_handler(payload, context):
    if DEBUG:
        payload = json.loads(payload)

    vernacular_cls = get_source_vernacular(payload.get('mapper_type'))
    vernacular = vernacular_cls(payload)
    if DEBUG:
        api_resp = vernacular.get_local_api_response()
    else:
        api_resp = vernacular.get_s3_api_response()

    source_metadata_records = vernacular.parse(api_resp)
    mapped_records = [record.to_UCLDC() for record in source_metadata_records]

    writer = UCLDCWriter(payload)
    if DEBUG:
        writer.write_local_mapped_metadata([
            record.to_dict() for record in mapped_records])
    else:
        writer.write_s3_mapped_metadata([
            record.to_dict() for record in mapped_records])

    return {
        'statusCode': 200,
        'body': json.dumps(payload)
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Map metadata from the institution's vernacular")
    parser.add_argument('payload', help='json payload')
    args = parser.parse_args(sys.argv[1:])
    lambda_handler(args.payload, {})
