from google.cloud import storage


import glob
import os
import xarray as xr
import pandas as pd
import gcsfs

import tkinter as tk
from tkinter import filedialog

import google.oauth2.credentials

credentials = google.oauth2.credentials.Credentials('ya29.a0AfH6SMBejrpIQeOYb0o7W2-USVlarw77krwU9l8N8eu_3eD5HTKRq9dLE28RRKwJt9sG-Gkg72DnH4CJedM7Cs45Xn_TpD-RSEh5glcLZusSW30L8LJOo1_NhyoMorGA7mn20dU88EDWzQRQRB9wpV5xZXdmTkgxw0phbg')
print(credentials.client_id)
print(credentials.client_secret)
print(credentials.to_json())

root = tk.Tk()
root.withdraw()

url_fao = 'https://console.cloud.google.com/storage/browser/fao-ecmwf-data'
bucket_name = 'fao-ecmwf-data'
storage_client = storage.Client("fao-maps")

fs = gcsfs.GCSFileSystem()
grib_list = fs.ls('fao-ecmwf-data')
last_grib = grib_list[-1].split('/')[1]


def get_bucket():

    bucket = storage_client.get_bucket(bucket_name)
    print('LOCATION %s' % bucket.location)

    return bucket


def download_grib(source_grib_file, destination_grib_dir):

    """Downloads a blob from the bucket."""
    # bucket_name = "your-bucket-name"
    # source_blob_name = "storage-object-name"
    # destination_file_name = "local/path/to/file"

    bucket = get_bucket()

    destination_grib_file = destination_grib_dir + source_grib_file + ".grib"

    # Construct a client side representation of a blob.
    # Note `Bucket.blob` differs from `Bucket.get_blob` as it doesn't retrieve
    # any content from Google Cloud Storage. As we don't need additional data,
    # using `Bucket.blob` is preferred here.
    blob = bucket.blob(source_grib_file)
    blob.download_to_filename(destination_grib_file)

    print("Blob {} downloaded to {}".format(source_grib_file, destination_grib_file))


# download_grib(last_grib, '../data/ecmwf/')


def list_gribs():
    """Lists all the blobs in the bucket."""

    # Note: Client.list_blobs requires at least package version 1.17.0.
    blobs = storage_client.list_blobs(bucket_name)

    # for blob in blobs:
    #     print(blob.name)

    for page in blobs.pages:
        print('=' * 50)
        print('    Page number: {:d}'.format(blobs.page_number))
        print('  Items in page: {:d}'.format(page.num_items))
        print('     First item: {!r}'.format(next(page)))
        print('Items remaining: {:d}'.format(page.remaining))
        print('Next page token: {}'.format(blobs.next_page_token))

    return blobs

# list_gribs()

def list_gribs_prefix(prefix=None,delimiter=None):
    """Lists all the blobs in the bucket."""

    # Note: Client.list_blobs requires at least package version 1.17.0.
    blobs = storage_client.list_blobs(bucket_name,prefix=prefix,delimiter=delimiter)

    print("Blobs:")
    for blob in blobs:
        print(blob.name)

    if delimiter:
        print("Prefixes:")
        for prefix in blobs.prefixes:
            print(prefix)

    return blobs

midnight_batch=list_gribs_prefix('A1D051900')
midday_batch=list_gribs_prefix('A1D051912')


def grib_metadata(blob_name):
    """Prints out a blob's metadata."""

    bucket = get_bucket()

    # Retrieve a blob, and its metadata, from Google Cloud Storage.
    # Note that `get_blob` differs from `Bucket.blob`, which does not
    # make an HTTP request.
    blob = bucket.get_blob(blob_name)

    print("Blob: {}".format(blob.name))
    print("Bucket: {}".format(blob.bucket.name))
    print("Storage class: {}".format(blob.storage_class))
    print("ID: {}".format(blob.id))
    print("Size: {} bytes".format(blob.size))
    print("Updated: {}".format(blob.updated))
    print("Generation: {}".format(blob.generation))
    print("Metageneration: {}".format(blob.metageneration))
    print("Etag: {}".format(blob.etag))
    print("Owner: {}".format(blob.owner))
    print("Component count: {}".format(blob.component_count))
    print("Crc32c: {}".format(blob.crc32c))
    print("md5_hash: {}".format(blob.md5_hash))
    print("Cache-control: {}".format(blob.cache_control))
    print("Content-type: {}".format(blob.content_type))
    print("Content-disposition: {}".format(blob.content_disposition))
    print("Content-encoding: {}".format(blob.content_encoding))
    print("Content-language: {}".format(blob.content_language))
    print("Metadata: {}".format(blob.metadata))
    # print("Custom Time: {}".format(blob.custom_time))
    print("Temporary hold: ", "enabled" if blob.temporary_hold else "disabled")
    print("Event based hold: ", "enabled" if blob.event_based_hold else "disabled",)
    if blob.retention_expiration_time:
        print(
            "retentionExpirationTime: {}".format(
                blob.retention_expiration_time
            )
        )

# grib_metadata(last_grib)

def get_gribs_from_local_dir(file_dir_path):

    # file_dir_path = filedialog.askdirectory()

    file_dir_path_search = file_dir_path + '/*'

    # Using '*' pattern
    files = []
    for complete_path in glob.glob(file_dir_path_search):
        filename = os.path.basename(complete_path)
        has_ext = filename.split(".")
        if len(has_ext) == 1:
            files.append(file_dir_path + "/" + filename)
        else:
            pass

    return files

# get_gribs_from_local_dir()


# REMOTE DATA NOT AVAILABLE AS WRITING ON BUCKET IS NOT ALLOWED AND IDX cannot be generated
def metadata_remote_grib():

    grib_list = fs.ls('fao-ecmwf-data')

    print(grib_list[-1])

    ds = xr.open_dataset("gcs://fao-ecmwf-data/A1D01200000012103001" ,
                         engine='cfgrib' ,
                         backend_kwargs={'filter_by_keys': {'edition': 1}})

    print(ds.time.values , ds.valid_time.values , pd.to_timedelta(ds.step.values))

# metadata_remote_grib()

def metadata_gribs(files_found):

    for file in enumerate(files_found):
        if "A1T" not in file[1].split("/")[-1]:
            ds = xr.open_dataset(file[1], engine='cfgrib', backend_kwargs={'filter_by_keys':{'edition': 1}})
            print(file[1], ds.time.values, ds.valid_time.values, pd.to_timedelta(ds.step.values))


# files = get_gribs_from_local_dir()
# metadata_gribs(files)
