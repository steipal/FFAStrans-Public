##########
#   Example FFAStrans Plugin Processor 
#       This script shows all possible interactions with FFASTrans engine
#       Depending on the node.json config, this could also be an .exe in any programming language or any other script language
#       Testing: Uncomment the writing to c:\temp\plugin_prop_input.json - execute the processor once and then on commandline, test your script this way:
#               powershell.exe -ExecutionPolicy Unrestricted -File  "C:\path-to\thisscript.ps1" "c:\temp\plugin_prop_input.json"
##########

#Write Message to Log
    Write-Output "Starting up"

#read input JSON file

    $input_json = Get-Content -Raw -Encoding UTF8 -Path $args[0] | ConvertFrom-Json
    ### $input_json| ConvertTo-Json -depth 100 | Out-File "c:\temp\plugin_prop_input.json" # writes input json to file for develpment
    $all_inputs = $input_json.proc_data.inputs
    $all_outputs = $input_json.proc_data.outputs

#get individual input values - the input "id's" are known to you because you defined them in index.html
    $testinput_val              = ($all_inputs | where { $_.id -eq "testinput" }).value
    Write-Output "Value of testinput: "$testinput_val 
    $testfolderbrowser_val      = ($all_inputs | where { $_.id -eq "testfolderbrowser" }).value
    Write-Output "Value of testfolderbrowser: "$testfolderbrowser_val
    $testfilebrowser_val        = ($all_inputs | where { $_.id -eq "testfilebrowser" }).value
    Write-Output "Value of testfilebrowser: "$testfilebrowser_val
    
    $success_msg_val    = ($all_inputs | where { $_.id -eq "successmsg" }).value
    $error_msg_val      = ($all_inputs | where { $_.id -eq "errormsg" }).value
    $end_branch_val     = ($all_inputs | where { $_.id -eq "endbranch" }).value
    $s_source_val       = ($all_inputs | where { $_.id -eq "s_source" }).value

#at this point, the processor shall do its work. We simulate some work by sleeping and report progress
        #we can set progresss by just printing a number and percent sign to STDOUT, all other text will just go to the log
        $progress = 0
        try{ #this try-finally can be used for cleanup operations when the job is cancelled by user
            while(1){
                if($progress -eq 100) {break}
                Write-Output $progress"%"
                $progress += 1
                Start-Sleep -Milliseconds 30         
            }
        }finally{
            #this is always executed, not only when the job was cancelled but also when the while loop finished. 
            # in the event of cancelling, DO NOT PRINT; otherwise the code after print will not be executed
        }
        #error handlng example (set if condition to 1 for testing:
        if (0){
            #just exit with not 0 return code
            exit 1
            #optionally set job_error_msg for display on job monitor
            $input_json.proc_data.outputs +=  @{ value = 's_job_error_msg'; data = "Some error occured in this plugin!" }
            $input_json| ConvertTo-Json -depth 100 | Out-File $input_json.processor_output_filepath      
        }
    
#add output values to input json structure
    #user variables - the "id's" of all outputs are known to you because you defined them in index.html as
    #all we need to do is to set the "data" attribute of the output 
    ($all_outputs | where { $_.id -eq "Testoutput" }).data  = "This testoutput value was calculated and set by processor"
    ($all_outputs | where { $_.id -eq "Testoutput2" }).data = "Output2 value was also set by processor"
    
    #special outputs, used to cause specific behaviour in ffastrans engine/job execution
    #Note that it is not needed to define the special variables in index.html, your processor can set them always
    $input_json.proc_data.outputs +=  @{ value = 's_job_error_msg'; data = $error_msg_val } #set job error msg - this will cause branch end with error
    $input_json.proc_data.outputs +=  @{ value = 's_success'; data = $success_msg_val } #set job success msg - this will be displayed on job monitor
    $input_json.proc_data.outputs +=  @{ value = 's_end_branch'; data = $end_branch_val }   #if set to True, current branch ends with success immediate/forcefully
    if ($s_source_val -ne ""){  #special check if s_source_val is empty, do not set the s_source variable as ffastrans would end and delete the job in this case
        $input_json.proc_data.outputs +=  @{ value = 's_source'; data = $s_source_val }         #sets source variable for rest of workflow
    }
#finally write output JSON file- its a copy of the input json but enriched with output values
    $input_json| ConvertTo-Json -depth 100 | Out-File $input_json.processor_output_filepath

#this goes to the log
    Write-Output "Done"