#!/usr/bin/python
import uuid
import sys
import os
from actiontrigger import MasterClass
from optparse import OptionParser
from random import randint
from xml.dom.minidom import parse
import xml.dom.minidom
import traceback
import subprocess

class TesttRunner(MasterClass):
    
    def test_create_bucket(self, testname, iterations):

        self.logger.info('Test [%s] - - - - - Started' % testname)
        self.logger.info('Iteration = [%s]' % iterations)
        self.logger.info('s3cmd utility syntax  = [s3cmd mb s3://<bucketname>]')
        try:
            bucket_instance = self.initialize()
            buckets = self.execute_s3cmd('mb s3://%s' % ('firstbucket'))
            self.logger.info('verify [s3cmd mb] command execution status')
            if 's3://' in buckets:
                self.logger.info('Bucket created on the system is [%s]' % buckets)
                self.s3_bucket = buckets.split('s3://')[1].split('\n')[0]
                self.logger.info('Bucket [%s] created on the system' % self.s3_bucket)
                return True
        except:
            execption_error = traceback.format_exc()
            self.logger.info('Exception error : %s' % execption_error)
            self.logger.info('Error : List bucket s3 command failed with error')
            return False

    def test_list_buckets(self, testname, iterations):

        self.logger.info('Test [%s] - - - - - Started' % testname)
        self.logger.info('Iteration = [%s]' % iterations)
        self.logger.info('s3cmd utility syntax  = [s3cmd ls]')
        try:
            bucket_instance = self.initialize()
            buckets = self.execute_s3cmd('ls')
            self.logger.info('verify [s3cmd ls] command execution status')
            if 's3://' in buckets:
                self.logger.info('Buckets [%s] found on the system' % buckets)
                self.s3_bucket = buckets.split('s3://')[1].split('\n')[0]
                self.logger.info('Bucket [%s] found on the system' % self.s3_bucket)
                return True
        except: 
            execption_error = traceback.format_exc()
            self.logger.info('Exception error : %s' % execption_error)
            self.logger.info('Error : List bucket s3 command failed with error')
            return False

    def test_list_bucket_contents(self, testname, iterations):

        self.logger.info('Test [%s] - - - - - Started' % testname)
        self.logger.info('Iteration = [%s]' % iterations)
        self.logger.info('s3cmd utility syntax  = [s3cmd put <file> <bucket>]')
        try:
            bucket_instance = self.initialize()
            self.logger.info('Perform operation PUT object')
            file_to_put = self.make_tmp_file()
            self.logger.info('Put temp file [%s] on bucket [%s] initiated' % (file_to_put, bucket_instance))
            with open(file_to_put, 'w') as file_handle:
                file_handle.write('dummy-file-content')
            self.logger.info('verify [s3cmd put] command execution status')
            self.execute_s3cmd('put %s s3://%s' % (file_to_put, bucket_instance))
            self.logger.info('LIST bucket contents after the put operation')
            files = self.execute_s3cmd('ls s3://%s' % bucket_instance)
            file_name = file_to_put.split(os.sep)[2]
            if file_name in files:
                self.logger.info('Object [%s] instance found in the bucket [%s]' % (file_name, bucket_instance))
                return True
        except: 
            execption_error = traceback.format_exc()
            self.logger.info('Exception error : %s' % execption_error)
            self.logger.info('Error : List bucket object instance s3 command failed with error')
            return False

    def test_put_get_delete(self, testname, iterations):

        self.logger.info('Test [%s] - - - - - Started' % testname)
        self.logger.info('Iteration = [%s]' % iterations)
        self.logger.info('s3cmd utility syntax  = [s3cmd put <file> <bucket>]')
        try:
            bucket_instance = self.initialize()
            self.logger.info('--Perform operation PUT object')
            file_to_put = self.make_tmp_file()
            file_to_put_basename = os.path.basename(file_to_put)
            self.logger.info('Put temp file [%s] on bucket [%s] initiated' % (file_to_put, bucket_instance))
            with open(file_to_put, 'w') as file_handle:
                file_handle.write('dummy-file-content')
            self.logger.info('verify [s3cmd put] command execution status')
            self.execute_s3cmd('put %s s3://%s' % (file_to_put, bucket_instance))
            self.logger.info('LIST bucket contents after the put operation')
            files = self.execute_s3cmd('ls s3://%s' % bucket_instance)
            file_name = file_to_put.split(os.sep)[2]
            if file_name in files:
                self.logger.info('Object [%s] instance found in the bucket [%s]' % (file_name, bucket_instance))
            self.logger.info('--Perform GET operation of the uploaded object, verify that the correct value')
            self.logger.info('s3cmd utility syntax  = [s3cmd get <bucket>/<contents> <dest_location>]')
            file_to_get = self.make_tmp_file(remove=True)
            self.logger.info('Get the contents[%s] from the bucket [%s] to the destination '
                             'location [%s]' %(file_to_put_basename, bucket_instance, file_to_get))
            self.execute_s3cmd('get s3://%s/%s %s' % (bucket_instance, file_to_put_basename,
                                                   file_to_get))
            if os.path.isfile(file_to_get):
                self.logger.info('Object found at location [%s], get content succeeded' % (file_name))
                self.logger.info('--Data integrity check on bucket object')
                original_checksum = self.calc_file_checksum(file_to_put)
                new_checksum = self.calc_file_checksum(file_to_get)
                if original_checksum != new_checksum:
                    self.logger.info('Object data integrity check failed')
                    return False
            else:
                return False
            self.logger.info('--Perform delete the uploaded object.')
            self.execute_s3cmd('del s3://%s/%s' % (bucket_instance, file_to_put_basename))
            self.logger.info('Verify delete operation execution status.')
            files = self.execute_s3cmd('ls s3://%s' % bucket_instance)
            file_name = file_to_put.split(os.sep)[2]
            if not file_name in files:    
                self.logger.info('Object [%s] instance deleted from the bucket [%s]' % (file_name, bucket_instance))
                return True
        except: 
            execption_error = traceback.format_exc()
            self.logger.info('Exception error : %s' % execption_error)
            self.logger.info('Error : Put_Get_Delete s3 object command failed with error')
            return False        



    def test_multipart_IO(self, testname, iterations):

        self.logger.info('Test [%s] - - - - - Started' % testname)
        self.logger.info('Iteration = [%s]' % iterations)
        self.logger.info('s3cmd utility syntax  = [s3cmd --multipart-chunk-size-mb=5 put <file> <bucket>]')
        try:
            bucket_instance = self.initialize()
            self.logger.info('Create a tmp file and Write 150M of data to it')
            file_to_put = self.make_tmp_file(remove=False, file_size='150M')
            file_to_put_basename = os.path.basename(file_to_put)
            original_checksum = self.calc_file_checksum(file_to_put)
            self.logger.info('Perform s3cmd put with a three part, making part size set to 50M each')
            self.execute_s3cmd('--multipart-chunk-size-mb=50 put %s s3://%s' % (file_to_put, bucket_instance))
            self.logger.info('verify [s3cmd put] command execution status')
            self.logger.info('LIST bucket contents after the put operation')
            object = self.execute_s3cmd('ls s3://%s/%s' % (bucket_instance, file_to_put_basename))
            if object:
                self.logger.info('Object [%s] instance found in the bucket [%s]' % (object, bucket_instance))
            else:
                self.logger.info('Error : Object instance not found in the bucket [%s]' % ( bucket_instance)) 
                return False
            if self.check_data_integrity(bucket_instance, file_to_put_basename, original_checksum) is True:
                self.logger.info('Data integrity check passed')
                return True
            else:
                self.logger.info('Error : Data integrity check failed')
                return False
        except: 
            execption_error = traceback.format_exc()
            self.logger.info('Exception error : %s' % execption_error)
            self.logger.info('Error : Put multipart s3 object command failed with error')
            return False        



    def test_put_overwrite_get_delete(self, testname, iterations):

        self.logger.info('Test [%s] - - - - - Started' % testname)
        self.logger.info('Iteration = [%s]' % iterations)
        self.logger.info('s3cmd utility syntax  = [s3cmd put --force <file> <bucket>]')
        try:
            bucket_instance = self.initialize()
            self.logger.info('Perform a object PUT object operation')
            self.logger.info('Create a tmp file and Write 20M of data to it')
            file_to_put = self.make_tmp_file(remove=False, file_size='20M')
            initial_size = os.stat(file_to_put).st_size
            self.logger.info('Initial object size before overwirte = [%s]' % initial_size)
            file_to_put_basename = os.path.basename(file_to_put)
            self.execute_s3cmd('put %s s3://%s' % (file_to_put, bucket_instance))
            self.logger.info('verify [s3cmd put] command execution status')
            self.logger.info('LIST bucket contents after the put operation')
            files = self.execute_s3cmd('ls s3://%s' % bucket_instance)
            file_name = file_to_put.split(os.sep)[2]
            if file_name in files:
                self.logger.info('Object [%s] instance found in the bucket [%s]' % (file_name, bucket_instance))
            else:
                self.logger.info('Erro : Object [%s] instance not found in the bucket [%s]' % (file_name, bucket_instance)) 
                return False
            self.logger.info('Overwrite the uploaded object instance with a new larger oject with option force')
            overwrite_file = self.make_tmp_file(remove=False, file_size='40M')
            overwrite_checksum = self.calc_file_checksum(overwrite_file)
            self.execute_s3cmd('put --force %s s3://%s/%s' % (overwrite_file, bucket_instance,
                                                           file_to_put_basename))
            self.logger.info('List the overwritten object, verify that the file overwrite operation succeeds')
            files = self.execute_s3cmd('ls s3://%s/%s' % (bucket_instance, file_to_put_basename))
            overwrite_obj_size = files.split('  ')[1]
            self.logger.info('Object size after overwirte operation : [%s]' % overwrite_obj_size)
            if int(overwrite_obj_size) > int(initial_size):
                self.logger.info('Object overwrite operation successful')
            else:
                self.logger.info('Error : Object overwrite operation failed') 
                return False
            if self.check_data_integrity(bucket_instance, file_to_put_basename, overwrite_checksum) is True:
                self.logger.info('Data integrity check passed')
                return True
            else:
                self.logger.info('Error : Data integrity check failed')
                return False
        except: 
            execption_error = traceback.format_exc()
            self.logger.info('Exception error : %s' % execption_error)
            self.logger.info('Error : Overwrite s3 object command failed with error')
            return False    


    def test_put_copy_get_delete(self, testname, iterations):

        self.logger.info('Test [%s] - - - - - Started' % testname)
        self.logger.info('Iteration = [%s]' % iterations)
        self.logger.info('s3cmd utility syntax  = [s3cmd cp <bucket/file_new> <bucket/file_old>]')
        try:
            bucket_instance = self.initialize()
            self.logger.info('Perform a object PUT object operation')
            file_to_put = self.make_tmp_file()
            original_checksum = self.calc_file_checksum(file_to_put)
            file_to_put_basename = os.path.basename(file_to_put)
            self.execute_s3cmd('put %s s3://%s' % (file_to_put, bucket_instance))
            self.logger.info('verify [s3cmd put] command execution status')
            self.logger.info('LIST bucket contents after the put operation')
            files = self.execute_s3cmd('ls s3://%s' % bucket_instance)
            file_name = file_to_put.split(os.sep)[2]
            if file_name in files:
                self.logger.info('Object [%s] instance found in the bucket [%s]' % (file_name, bucket_instance))
            else:
                self.logger.info('Error : Object [%s] instance not found in the bucket [%s]' % (file_name, bucket_instance)) 
                return False
            self.logger.info('Perform object [COPY ]operation from one bucket to another')
            self.logger.info('Create a new bucket [copytestbucket]')
            random_number = randint(10, 20)
            copy_bucket = self.execute_s3cmd('mb s3://copytestbucket%s' % random_number).split('s3://')[1].split("/' ")[0]
            self.logger.info('Bucket [%s] created successfully' % copy_bucket)
            self.execute_s3cmd('cp s3://%s/%s s3://%s' % (bucket_instance, file_to_put_basename,
                                                       copy_bucket))
            self.logger.info('List the copied object, verify that the file copy operation succeeds')
            file_in_list = self.execute_s3cmd('ls %s%s' % (copy_bucket, file_to_put_basename))
            if file_in_list:
                self.logger.info('Object [%s] instance found in the bucket [%s]' % (file_name, bucket_instance))
            else:
                self.logger.info('Erro : Object [%s] instance not found in the bucket [%s]' % (file_name, bucket_instance))
                return False
            self.logger.info('Perform data integrity check on bucket object [%s/%s]' % (copy_bucket, file_to_put_basename))
            if self.check_data_integrity(copy_bucket, file_to_put_basename, original_checksum) is True:
                self.logger.info('Data integrity check passed')
                return True
            else:
                self.logger.info('Error : Data integrity check failed')
                return False
        except: 
            execption_error = traceback.format_exc()
            self.logger.info('Exception error : %s' % execption_error)
            self.logger.info('Error : Copy s3 object command failed with error')
            return False


    def test_put_move_get_delete(self, testname, iterations):

        self.logger.info('Test [%s] - - - - - Started' % testname)
        self.logger.info('Iteration = [%s]' % iterations)
        self.logger.info('s3cmd utility syntax  = [s3cmd mv <bucket/file_new> <bucket>]')
        try:
            bucket_instance = self.initialize()
            self.logger.info('Perform a object PUT object operation')
            file_to_put = self.make_tmp_file()
            original_checksum = self.calc_file_checksum(file_to_put)
            file_to_put_basename = os.path.basename(file_to_put)
            self.execute_s3cmd('put %s s3://%s' % (file_to_put, bucket_instance))
            self.logger.info('verify [s3cmd put] command execution status')
            self.logger.info('LIST bucket contents after the put operation')
            files = self.execute_s3cmd('ls s3://%s' % bucket_instance)
            file_name = file_to_put.split(os.sep)[2]
            if file_name in files:
                self.logger.info('Object [%s] instance found in the bucket [%s]' % (file_name, bucket_instance))
            else:
                self.logger.info('Erro : Object [%s] instance not found in the bucket [%s]' % (file_name, bucket_instance))
                return False
            self.logger.info('Perform object MOVE operation from one bucket to another')
            self.logger.info('Create a new bucket [movetestbucket]')
            random_number = randint(10, 20)
            move_bucket = self.execute_s3cmd('mb s3://movetestbucket%s' % random_number).split("s3://")[1].split("/' ")[0]
            self.logger.info('Bucket [%s] created successfully' % move_bucket)
            self.logger.info('Perform the MOVE operation on uploaded object to the new bucket [%s]' % move_bucket)
            self.execute_s3cmd('mv s3://%s/%s s3://%s' % (bucket_instance, file_to_put_basename, move_bucket))
            self.logger.info('List the moved object, verify that the file move operation succeeds')
            files = self.execute_s3cmd('ls %s/%s' % (move_bucket, file_to_put))
            file_name = file_to_put.split(os.sep)[2]
            if file_name in file_to_put_basename:
                self.logger.info('Object [%s] instance found in the bucket [%s]' % (file_name, bucket_instance))
            else:
                self.logger.info('Error : Object [%s] instance not found in the bucket [%s]' % (file_name, bucket_instance)) 
                return False
            self.logger.info('Perform data integrity check on bucket object [%s/%s]' % (move_bucket, file_to_put_basename))
            if self.check_data_integrity(move_bucket, file_to_put_basename, original_checksum) is True:
                self.logger.info('Data integrity check passed')
                return True
            else:
                self.logger.info('Error : Data integrity check failed')
                return False
        except: 
            execption_error = traceback.format_exc()
            self.logger.info('Exception error : %s' % execption_error)
            self.logger.info('Error : Move s3 object command failed with error')
            return False

    def test_list_all_objects(self, testname, iterations):

        self.logger.info('Test [%s] - - - - - Started' % testname)
        self.logger.info('Iteration = [%s]' % iterations)
        self.logger.info('s3cmd utility syntax  = [s3cmd la]')
        try:
            bucket_instance = self.initialize()
            self.logger.info('Perform a 10 object PUT operation')
            file_count =  0
            store_file = []
            while file_count < 10:
                file_to_put = self.make_tmp_file()
                store_file.append(file_to_put)
                self.execute_s3cmd('put %s s3://%s' % (file_to_put, bucket_instance))
                file_count += 1
            store_file_length = len(store_file)
            self.logger.info('List  all objects and buckets with [s3cmd la]')
            all_buckets_objects = []
            listall_output = self.execute_s3cmd('la').strip()
            self.logger.info('The output of [s3cmd la] is [%s]' % listall_output)
            for each_obj in listall_output.split('\n'):
                if each_obj:
                    all_buckets_objects.append(each_obj)
            self.logger.info('Verify that store_file length is equal to the length of list all bucket output')
            if store_file_length == len(all_buckets_objects):
                self.logger.info('Number of object same as created. Test successed. ')
                return True
            else:
                self.logger.info('Error : Number of objected are not same as created.')
                return False
        except:
            execption_error = traceback.format_exc()
            self.logger.info('Exception error : %s' % execption_error)
            self.logger.info('Error : List_All s3 object command failed with error')
            return False

    def test_multipart_random_IO(self, testname, iterations):

        self.logger.info('Test [%s] - - - - - Started' % testname)
        self.logger.info('Iteration = [%s]' % iterations)
        self.logger.info('s3cmd utility syntax  = [s3cmd --multipart-chunk-size-mb=5 put <file> <bucket>]')
        try:
            bucket_instance = self.initialize()
            file_size_list = ['100M', '250M', '500M', '1000M']
            file_name_list = []
            file_basename_list = []
            original_checksum_list = []
            self.logger.info('Create multiple files with variable size for random IO operation')
            self.logger.info('Test has a longer running time. Please wait!!!')
            for file_size in file_size_list:
                self.logger.info('Create a tmp file and Write [%s] of data to it' % file_size)
                file_to_put = self.make_tmp_file(remove=False, file_size=file_size)
                file_name_list.append(file_to_put)
            for file_name in file_name_list:
                fsize_MB = os.stat(file_name).st_size>>20
                file_basename_list.append(os.path.basename(file_name))
                original_checksum_list.append(self.calc_file_checksum(file_name))
                self.logger.info('File name [%s] is with size [%sMB]' %(file_name, fsize_MB))
                self.logger.info('Choosing five random chunk-size in MB within range (5-100) for '
                                  'multipart put operation.')
                count = 0
                while count < 5:
                    random_fsize = randint(5, 100)
                    self.logger.info('------------------------------------------------------------------')
                    self.logger.info('Performing s3cmd put with chunk-size=[%sMB] on a [%sMB] file' % (random_fsize, fsize_MB))
                    output = self.execute_s3cmd('--multipart-chunk-size-mb=%s put %s s3://%s' % (random_fsize, file_name, bucket_instance))
                    self.logger.info('%s' % output)
                    count = count + 1
            self.logger.info('verify [s3cmd put] command execution status')
            self.logger.info('LIST bucket contents after the put operation')
            for file_basename in file_basename_list:
                self.logger.info('Verify the presence of file [%s] on the bucket [%s]' % (file_basename, bucket_instance))
                object = self.execute_s3cmd('ls s3://%s/%s' % (bucket_instance, file_basename))
                if object:
                    self.logger.info('Object [%s] instance found in the bucket [%s]' % (object, bucket_instance))
                else:
                    self.logger.info('Erro : Object instance not found in the bucket [%s]' % ( bucket_instance))
                    return False
            for original_checksum in  original_checksum_list:
                for file_basename in file_basename_list:
                    if self.check_data_integrity(bucket_instance, file_basename, original_checksum) is True:
                        self.logger.info('Data integrity check passed')
                        return True
                    else:
                        self.logger.info('Error : Data integrity check failed')
                        return False
        except:
            execption_error = traceback.format_exc()
            self.logger.info('Exception error : %s' % execption_error)
            self.logger.info('Error : Put multipart s3 object command failed with error')
            return False
  

    def test_multipart_random_IO_input_parts(self, testname, iterations):

        self.logger.info('Test [%s] - - - - - Started' % testname)
        self.logger.info('Iteration = [%s]' % iterations)
        self.logger.info('s3cmd utility syntax  = [s3cmd --multipart-chunk-size-mb=5 put <file> <bucket>]')
        try:
            bucket_instance = self.initialize()
            self.logger.info('Create Master file for IO operation')
            self.logger.info('Test has a longer running time. Please wait!!!')
            self.logger.info('Create a tmp file and Write 5GB of data to it')
            command = 'dd if=/dev/urandom of=/tmp/test5gb.txt bs=1000M count=5'
            proc = subprocess.Popen(command,stdout=subprocess.PIPE, shell=True)
            Output =  proc.communicate()[0]
            print Output
            file_basename_list = []
            original_checksum_list = []
            for  count in range(0,1000):
                self.logger.info('------------------------- Counter=[%s] -------------------------' % count)
                command = 'dd if=/tmp/test5gb.txt of=/tmp/data%s.txt bs=5M count=%s' % (count, count)
                proc = subprocess.Popen(command,stdout=subprocess.PIPE, shell=True)
                Output =  proc.communicate()[0]
                print Output
                self.logger.info('Performing s3cmd put with chunk-size=[%sMB] on a [%sMB] file' % (5, count*5))
                output = self.execute_s3cmd('--multipart-chunk-size-mb=5 put /tmp/data%s.txt s3://%s' % (count, bucket_instance))
                #self.logger.info('%s' % output)
                file_path_full = '/tmp/data%s.txt' %count
                file_basename = os.path.basename(file_path_full)
                original_checksum = self.calc_file_checksum(file_path_full)
                self.logger.info('Verify the presence of file [%s] on the bucket [%s]' % (file_basename, bucket_instance))
                object = self.execute_s3cmd('ls s3://%s/%s' % (bucket_instance, file_basename))
                if object:
                    self.logger.info('Object [%s] instance found in the bucket [%s]' % (object, bucket_instance))
                else:
                    self.logger.info('Error : Object instance not found in the bucket [%s]' % ( bucket_instance))
                    return False
                if self.check_data_integrity(bucket_instance, file_basename, original_checksum) is True:
                    self.logger.info('Data integrity check passed')
                    os.remove(file_path_full)
                else:
                    self.logger.info('Error : Data integrity check failed')
                    #return False
            return True
        except:
            execption_error = traceback.format_exc()
            self.logger.info('Exception error : %s' % execption_error)
            self.logger.info('Error : Put multipart s3 object command failed with error')
            return False


usage = """
Pattern: %prog [--testcase=<testcase_name>/--xml=<case_xml_file> --iteration=<iter_cound>]
Cases are : 	"create_bucket"
		"list_bucket" 
		"list_bucket_contents"
		"put_get_delete"
		"multipart_IO"
		"overwrite_object"
		"copy_object_instance"
		"move_object_instance"
		"list_all_objects_buckets" 
                "multipart_random_IO"
		"multipart_random_IO_input_parts"
XML	  :	"testinput.xml" , please sepcify the above cases as the case title onto the xml
iteration :	<Count of Iteration to be executed>
"""
	
def main():
    parser = OptionParser(usage=usage)
    parser.add_option('-t', '--testcase', dest='testname', help='Defined test case name')
    parser.add_option('-i', '--iteration', type="int", dest='iterations', default=1, help='Iteration count of execution')
    parser.add_option('--xml', dest='input_xml', help='xml file defining each of the testcases')
    (options, args) = parser.parse_args()
    base_obj = MasterClass()
    base_obj.log_process()
    class_obj = TesttRunner()
    test_name_list = []
    base_obj.logger.info('*******************************************************************')
    base_obj.logger.info('Test execution initialized on client [%s]' % (base_obj.execute_command('hostname')))
    base_obj.logger.info('*******************************************************************')
    if options.testname:
        base_obj.logger.info('\nProcessing the test execution from console input.')
        test_name_list.append(options.testname)
    elif options.input_xml:
        base_obj.logger.info('\nProcessing the test execution from XML file input.')
        for cases in xml_extractor(options.input_xml):
            test_name_list.append(cases.getAttribute("title"))
    else:
        base_obj.logger.info('Input Error : Test case input not provided : [%s]' % usage)
        sys.exit(0)
    for testname in test_name_list:
        base_obj.logger.info('\n\n***TestCase that is under execution is [[%s]]***' % testname)
        iteration = 0
        if (testname == 'create_bucket'):
            while iteration < options.iterations:
                test_status = class_obj.test_create_bucket(testname, iteration)
                base_obj.result_verification(testname, test_status)
                iteration += 1
        elif (testname == 'list_bucket'):
            while iteration < options.iterations:
                test_status = class_obj.test_list_buckets(testname, iteration)
                base_obj.result_verification(testname, test_status)
                iteration += 1
        elif (testname == 'list_bucket_contents'):
            while iteration < options.iterations:
                test_status = class_obj.test_list_bucket_contents(testname, iteration)
                base_obj.result_verification(testname, test_status)
                iteration += 1
        elif (testname == 'put_get_delete'):
            while iteration < options.iterations:
                test_status = class_obj.test_put_get_delete(testname, iteration)
                base_obj.result_verification(testname, test_status)
                iteration += 1
        elif (testname == 'multipart_IO'):
            while iteration < options.iterations:
                test_status = class_obj.test_multipart_IO(testname, iteration)
                base_obj.result_verification(testname, test_status)
                iteration += 1
        elif (testname == 'overwrite_object'):
            while iteration < options.iterations:
                test_status = class_obj.test_put_overwrite_get_delete(testname, iteration)
                base_obj.result_verification(testname, test_status)
                iteration += 1
        elif (testname == 'copy_object_instance'):
            while iteration < options.iterations:
                test_status = class_obj.test_put_copy_get_delete(testname, iteration)
                base_obj.result_verification(testname, test_status)
                iteration += 1
        elif (testname == 'move_object_instance'):
            while iteration < options.iterations:
                test_status = class_obj.test_put_move_get_delete(testname, iteration)
                base_obj.result_verification(testname, test_status)
                iteration += 1
        elif (testname == 'list_all_objects_buckets'):
            while iteration < options.iterations:
                test_status = class_obj.test_list_all_objects(testname, iteration)
                base_obj.result_verification(testname, test_status)
                iteration += 1
        elif (testname == 'multipart_random_IO'):
            while iteration < options.iterations:
                test_status = class_obj.test_multipart_random_IO(testname, iteration)
                base_obj.result_verification(testname, test_status)
                iteration += 1
        elif (testname == 'multipart_random_IO_input_parts'):
            while iteration < options.iterations:
                test_status = class_obj.test_multipart_random_IO_input_parts(testname, iteration)
                base_obj.result_verification(testname, test_status)
                iteration += 1
    base_obj.result_summary()

def xml_extractor(input_xml):
    """
    Open XML document using minidom parser to extract the input xml file
    """
    pwd = os.getcwd()
    filepath = '%s/%s' % (pwd, input_xml)
    DOMTree = xml.dom.minidom.parse(filepath)
    collection = DOMTree.documentElement
    testcases = collection.getElementsByTagName("case")
    return testcases

def error_capture(status):
    """
    Capture the error state of the command execution.
    """
    result_list = []
    if status is False:
        result_list.append(status)

if __name__ == '__main__':
    main()
