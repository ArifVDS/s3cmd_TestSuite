# s3cmd_TestSuite
Generic s3cmd put/get request testing utility to validate the Object Store API calls

This test suite could be used to simulate put/get/delete object from and to your Object Store system by simply specifying 
action input to the 'input.xml' file.

Execution pattern : 
# python s3cmdtestrunner.py
---------------------------------------------------------------------------------------------
Usage:
Pattern: s3cmdtestrunner.py [--testcase=<testcase_name>/--xml=<case_xml_file> --iteration=<iter_cound>]
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


Options:
  -h, --help            show this help message and exit
  -t TESTNAME, --testcase=TESTNAME
                        Defined test case name
  -i ITERATIONS, --iteration=ITERATIONS
                        Iteration count of execution
  --xml=INPUT_XML       xml file defining each of the testcases
---------------------------------------------------------------------------------------------
