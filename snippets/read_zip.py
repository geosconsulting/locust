from zipfile import ZipFile
import os

dir_zip_files = "data/"
zipped_file = "1985_2019.zip"
unzipped_file = ZipFile(os.path.join(dir_zip_files, zipped_file))

# print(zip_file.printdir())

# list_in_zip = zip_file.infolist()
# print(type(list_in_zip))
# print(list_in_zip[0])

name_in_list = unzipped_file.namelist()
# print(name_in_list)

# for container in list_in_zip:
#     container_filename = container.filename
#     print(container_filename)

list_files_shp = []
for file_in_container in name_in_list:
    lenght_file_type = len(file_in_container.split(".")[-1])
    if lenght_file_type == 3:
        # list_files_shp.append(file_in_container.split("/"))
        list_files_shp.append(file_in_container)

