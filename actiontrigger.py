#!/usr/bin/python

import os
import hashlib
import logging
import logging.handlers
import subprocess
import tempfile
import sys
import time
from uuid import uuid4

logger_name = 's3cmdtest'
s3_cmd_config_path = <configfilepath>
pass_tests = []
fail_tests = []
time_out_counter = []

class MasterClass():

    def initialize(self):

        self.logger.info('Perform the setup operation for the test runner.')
        created_buckets = self.execute_s3cmd('ls')
        if created_buckets:
            self.s3_bucket = created_buckets.split('s3://')[1].split('\n')[0]
        else:
            self.s3_bucket = 'test-bucket-%s' % uuid4()
            self.execute_s3cmd('mb s3://%s' % self.s3_bucket)
        return self.s3_bucket
        self.logger.info('Used s3cmd version: %s' % self.execute_s3cmd('--version'))

    def execute_s3cmd(self, subcommand):

        command = '%s/s3cmd-1.6.0/s3cmd -c %s %s' % (os.getcwd().strip(),s3_cmd_config_path, subcommand)
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        s3cmd_output, s3cmd_stderr  = proc.communicate()
        self.logger.info('S3cmd Output: %s' % s3cmd_output)
        self.logger.info('S3cmd Error: %s' % s3cmd_stderr)
        return s3cmd_output

    def log_process(self):
        self.configure_logger()
        self.initialize_logger()

    def make_tmp_file(self, file_path=None, remove=False, file_size='20M'):
        if not file_path:
            _, file_path = tempfile.mkstemp()
            self.logger.info('File [%s] created successfully.' % file_path)
            if remove is False:
                self.logger.info('Write [%s] of data to the file [%s]' % (file_size, file_path))
                self.execute_command('dd if=/dev/urandom of=%s bs=%s count=1' % (file_path, file_size))
        elif not os.path.isfile(file_path):
            open(file_path, 'w').close()
        if remove:
            self.logger.info('Removing the temp file [%s] from the system' % file_path)
            os.remove(file_path)
        return file_path


    def calc_file_checksum(self, file_path):
        with open(file_path) as file_handle:
            return hashlib.md5(file_handle.read()).hexdigest()

    def execute_command(self, command):
        proc = subprocess.Popen(command,stdout=subprocess.PIPE, shell=True)
        return proc.communicate()[0]

    def initialize_logger(self):

        self.logger = logging.getLogger(logger_name)
        for handler in self.logger.handlers:
            self.logger.removeHandler(handler)
        self.logger.propagate = False
        # create console handler and set level to info
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        # logger output to log file
        self.logger.setLevel(logging.INFO)
        extended_log_format = logging.Formatter('%(asctime)-15s %(levelname)-8s %(message)s')
        rotating_file_handler = logging.handlers.RotatingFileHandler('%s.log' % logger_name,
                                                                     maxBytes=5 * 1024 * 1024,
                                                                     backupCount=5)
        rotating_file_handler.setFormatter(extended_log_format)
        self.logger.addHandler(rotating_file_handler)
        return logger_name

    @classmethod
    def configure_logger(self):
        self.logger = logging.getLogger(logger_name)

    def check_data_integrity(self, bucket, object_file, original_checksum):
        """
        *Function to check the data integrity after the s3cmd object*
        """
        self.logger.info('Performing data integrity check operation...')
        object_file_get = '/tmp/get_%s' % object_file
        self.logger.info('Getting the bucket to the location [%s]' % object_file_get)
        get_output_integrity = self.execute_s3cmd('get s3://%s/%s %s' % (bucket, object_file, object_file_get))
        if 'Problem: timeout:' in get_output_integrity :
            self.logger.info('[Problem: timeout:] has caused this test to fail during get operation')
            time_out_counter.append('Timeout during GET')
        if os.path.isfile(object_file_get):
            self.logger.info('Object found at location [%s], Get object : Succeeded' % (object_file_get))
            new_checksum = self.calc_file_checksum(object_file_get)
            time.sleep(5)
        self.logger.info('original_checksum=[%s]' % original_checksum)
        self.logger.info('new_checksum=[%s]' % new_checksum)
        if original_checksum == new_checksum:
            os.remove(object_file_get)
            return True
        else:
            return False

    def cleanup_action(self):

        self.logger.info('Performing the Clean-Up operation after the test execution.')
        all_buckets_objects = self.execute_s3cmd('la')
        for each_obj in all_buckets_objects.split('\n'):
            if each_obj:
                self.logger.info('Performing the delete action on the object[%s].' %(each_obj.split('s3://')[1]))
                delete_status = self.execute_s3cmd('del --recursive s3://%s' % (each_obj.split('s3://')[1]))
        '''
        bucket_list = self.execute_s3cmd('ls')
        for each_bucket in bucket_list.split('\n'):
            if each_bucket:
                self.logger.info('Deleting the created bucket [%s] with force action' % (each_bucket.split('s3://')[1]))
                self.execute_s3cmd('rb --force s3://%s' % (each_bucket.split('s3://')[1]))
        '''
        bucket_object = self.execute_s3cmd('ls')
        if not bucket_object:
            self.logger.info('System is clean, no object/bucket found on the system.')
        else:
            self.logger.info('Following are the object/bucket remaining on the system [bucket_object]')
        self.logger.info('Clean-up [/tmp] directory')
        self.execute_command('rm -rf /tmp/tmp*')

    def result_verification(self, test_name, status):

        if status is True:
            pass_tests.append(test_name)
            self.logger.info('Test run status * * * * *  [PASS]')
            self.cleanup_action()
        else:
            fail_tests.append(test_name)
            self.logger.info('Test run status * * * * *  [FAILED]')
        self.logger.info('Test execution [%s] - - - - - Completed\n' % test_name)

    def result_summary(self):

        pass_count = len(pass_tests)
        fail_count = len(fail_tests)
        summary_file = '%s/Result_Summary.txt' % (os.getcwd().strip())
        if os.path.exists(summary_file):
            os.remove(summary_file)
        with open(summary_file, "w") as f:
            f.write('_ _ _ _ [s3cmdTestsuite] execution summary on client [%s]'
                    ' _ _ _ _' %(self.execute_command('hostname').strip()))
            f.write('\nNumber of Testcase passed = [%s]' % pass_count)
            f.write('\nFollowing are the Testcase that passed = %s' % pass_tests)
            f.write('\n\nNumber of Testcase failed = [%s]' % fail_count)
            f.write('\nFollowing are the Testcase that failed = %s' % fail_tests)
            f.write('\nNumber of Time_out occurance during get operation = %s' % (len(time_out_counter)))
        f.close()


