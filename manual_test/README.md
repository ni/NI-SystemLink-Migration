# Setup
Ideal setup would include:
1. A 'dev' machine where you will run the populate/validate scripts. That machine needs the setup described in [CONTRIBUTING.md](../CONTRIBUTING.md). Each step that is run on the dev machine stores data locally that will be used by subsequent steps.
1. A SystemLink server to use as the original machine, with nislmigrate installed as described in the top-level [README.md](../README.md)
1. A SystemLink server to use as the destination machine, also with nislmigrate installed. If you don't have 2 machines, you can use a vm, and restore to a 'clean' snapshot before restoring.

# Basic Steps for all of the manual tests
1. On dev machine, populate a server with sample data for one or more services:

   ```
   poetry run py .\manual_test\test_<service1>.py -s https://<original-systemlink-server> -u <username> -p <password> populate
   poetry run py .\manual_test\test_<service2>.py -s https://<original-systemlink-server> -u <username> -p <password> populate
   ...
   ```

1. On the 'original' SystemLink server, capture the data for the services you are testing. Use the --dir option to save data to a location that will be accessiable to the destination machine (and won't be lost if you are using a VM snapshot):

   `nislmigrate capture --<service1> --<service2> ... --dir \\nirvana\temp\<username>\migration`
1. Prepare the 'destination' machine if necessary.  If you're reverting to a clean VM snapshot do that now.

1. On the 'dev' machine record any prepopulated data for the services you are testing:

   ```
   poetry run py .\manual_test\test_<service1>.py -s https://<destination-systemlink-server> -u <username> -p <password> record
   poetry run py .\manual_test\test_<service2>.py -s https://<destination-systemlink-server> -u <username> -p <password> record
   ...
   ```

1. On the 'destination' SystemLink server, restore the data for the services you are testing. Note that this will overwrite the existing data on the server:

   `nislmigrate restore --<service1> --<service2> ... --dir \\nirvana\temp\<username>\migration --force`

1. On the 'dev' machine, validate that the data was restored properly for each service that you are testing. The command will report an error if the data on the destination server doesn't match the initial data from the original server.

   ```
   poetry run py .\manual_test\test_<service1>.py -s https://<destination-systemlink-server> -u <username> -p <password> validate
   poetry run py .\manual_test\test_<service2>.py -s https://<destination-systemlink-server> -u <username> -p <password> validate
   ...
   ```
   
# Considerations for specific services

## File
### Relationship to other service tests
By default, the file test validates that only the files that were present at the time `populate` was run. If `populate` for other tests also add files, that will cause file `validate` to fail. Ideally file `populate` should be run as late as possible, after other test that create files. If that is not possible, you can alternatively pass a parameter to file `validate` which will cause it to ignore extra files:

`poetry run py .\manual_test\test_file.py -s https://<destination-systemlink-server> -u <username> -p <password> --relax-validation validate`

### Test cases
Test file with 3 storage locations (configurable in NI SystemLink Server Configuration, on the FileIngestion page):
1. File System, Default file location
2. File System, Non-default file location
3. Amazon Simple Storage Service (S3)

 Note that the storage location configuration on the server being restored must be identical to the storage location configuration on the server when data was captured.