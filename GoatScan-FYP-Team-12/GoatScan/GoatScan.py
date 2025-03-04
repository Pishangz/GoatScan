#!/usr/bin/env python3

import argparse
import os
import time
import pathlib
from termcolor import colored
import inquirer
import pyfiglet
from halo import Halo
import subprocess
import requests
import json
# New imports i added for gf/wget
from urllib.parse import urlparse
import re
import json
import shutil

# =============Install required dependencies=============


# =============Start of Program=============//


def sleep(ms=5000):
    time.sleep(ms / 1000)


def timer(seconds):
    time.sleep(seconds)


async def spinner(result):
    spinner = Halo(text='Loading...', spinner='dots')
    spinner.start()
    await time.sleep(2)  # Simulating some async operation
    spinner.succeed("Answer: " + result)


# Welcome GUI function
def welcome():
    f = pyfiglet.Figlet(font='big')
    print(f.renderText('GOATSCAN'))
    description = "=" * 100 + "\nGoatScan\nCreated by: FYP Group 12 DISM/FT/3A/04\n\nDescription: Vulnerability scanner for Wordpress Plugins; Scans for XSS, SQL, Command Injection and Broken Authentication\n" + "=" * 100
    styled_text = '\033[1;37;100m' + description + '\033[0m'
    print(styled_text)


# <<<Validate Url Function>>>
def is_valid_url(input_url):
    parsed_url = urlparse(input_url)
    return all([parsed_url.scheme, parsed_url.netloc])


# Retrieve Admin Cookie
def user_configurations(url, uname, pwd):
    # configurations = {
    #     "ipaddr": "157.245.144.50",
    #     "username": "root",
    #     "password": "1qwer%$#@!"
    # }
    configurations = {
        "ipaddr": f"{url}",
        "username": f"{uname}",
        "password": f"{pwd}"
    }
    json_data = json.dumps(configurations)
    return json_data


# Login and retrieve cookie function
def wp_login(userInputs):

    try:
        loaded_userInputs = json.loads(userInputs)
        ip_addr = loaded_userInputs["ipaddr"]
        username = loaded_userInputs["username"]
        password = loaded_userInputs["password"]
        login_url = "http://" + ip_addr + "/wp-login.php?loggedout=true&wp_lang=en_US"

        # Log in and retrieve the authentication cookie
        session = requests.Session()
        login_payload = {
            "log": username,
            "pwd": password,
            "wp-submit": "Log In"
        }

        response = session.post(login_url, data=login_payload)
        
        # Check if the login was successful (HTTP status 200)
        if response.status_code == 200:
            # Retrieve the cookie data
            cookies = session.cookies

            # Convert the cookie data to a dictionary
            cookie_dict = {cookie.name: cookie.value for cookie in cookies}

            cookie_string = '; '.join(
                [f"{key}={value}" for key, value in cookie_dict.items()])

            # Close the session
            session.close()
            
            # Return the cookie data dictionary
            return cookie_string
        else:
            # Close the session and return an error message
            session.close()
            return "Login failed: HTTP status " + str(response.status_code)
    
    except Exception as e:
        return "Error: " + str(e)


# Extract specific lines & cols from php/jsonn file
def extractLines(filePath, start, end, startCol, endCol):

    with open(filePath, 'r') as file:
        lines = file.readlines()

    # Extract the relevant lines
    start_line = max(start - 1, 0)  # Since lines are 0-indexed
    end_line = min(end, len(lines))

  # Extract the code between the specified columns
    code_lines = lines[start_line:end_line]

    # Adjust the start and end columns for the first and last line respectively
    code_lines[0] = code_lines[0][startCol - 1:]
    code_lines[-1] = code_lines[-1][:endCol]

    # Join the lines to get the PHP code
    php_code = ''.join(code_lines)
    return php_code


# Generate Static Output File
def generateFinalOutput(semgrepOutputFiles,dynamicOutputFiles, output_dir):

  # Iterating through the dictionary and printing key-value pairs

    finalResultText = ''

    # for vulnType, file in semgrepOutputFiles.items():

    #     finalResultText += f'-------------------------------------------------------------------------------\n'
    #     finalResultText += f'Name: \t\t\t{vulnType}\n'
    #     finalResultText += f'-------------------------------------------------------------------------------\n\n'

    #     with open(file, 'r') as f:
    #         json_data = json.load(f)
    #         semgrep_results = json_data.get('results')

    #     resultNo = 0

    #     for result in semgrep_results:

    #         resultNo += 1
    #         extra = result.get('extra')

    #         # Check Rule is not Taint Rule
    #         if 'dataflow_trace' not in extra:
    #             # if not extra'dataflow_trace']['taint_source']:
    #             path = result.get('path')
    #             start = result.get('start')
    #             startLine = start['line']
    #             startColumn = start['col']
    #             end = result.get('end')
    #             endLine = end['line']
    #             endColumn = end['col']
    #             sourceSinkFunction = extractLines(
    #                 path, startLine, endLine, startColumn, endColumn)

    #             finalResultText += f'Result #{resultNo}:\n\n'
    #             finalResultText += f'Source:\n\tline {startLine}: {sourceSinkFunction}\n\n'

    #         # Taint Rule
    #         else:
    #             message = extra['message']
    #             metadata = extra['metadata']
    #             severity = extra['severity']

    #             # Storing Other Results
    #             finalResultText += f'Result #{resultNo}:\n\n'
    #             finalResultText += f'Message: {message}\n'

    #             # Getting Source Results
    #             source = extra['dataflow_trace']['taint_source'][1][0]
    #             sourceStartLine = source['start']['line']
    #             sourceEndLine = source['end']['line']

    #             sourceStartColumn = source['start']['col']
    #             sourceEndColumn = source['end']['col']
    #             sourcePath = source['path']
    #             sourceFunction = extractLines(
    #                 sourcePath, sourceStartLine, sourceEndLine, sourceStartColumn, sourceEndColumn)

    #             # Storing Source Results
    #             finalResultText += f'FilePath: {sourcePath}\n'
    #             if sourceStartLine == sourceEndLine:
    #                 finalResultText += f'Source:\n\tline {sourceStartLine}: {sourceFunction}\n\n'
    #             else:
    #                 finalResultText += f'Source:\n\tline {sourceStartLine} - {sourceEndLine}: {sourceFunction}\n\n'

    #             # Getting Intermediate Var Results

    #             if 'intermediate_vars' in extra['dataflow_trace']:
    #                 intermediateVars = extra['dataflow_trace']['intermediate_vars']
    #                 for intermediateVar in intermediateVars:
    #                     intermediateVarPath = intermediateVar['location']['path']
    #                     intermediateVarStartLine = intermediateVar['location']['start']['line']
    #                     intermediateVarEndLine = intermediateVar['location']['end']['line']
    #                     intermediateVarStartColumn = intermediateVar['location']['start']['col']
    #                     intermediateVarEndColumn = intermediateVar['location']['end']['col']
    #                     if not (intermediateVarStartLine == sourceStartLine and intermediateVarEndLine == sourceEndLine):
    #                         intermediateVarFunction = extractLines(
    #                             intermediateVarPath, intermediateVarStartLine, intermediateVarEndLine, intermediateVarStartColumn, intermediateVarEndColumn)
    #                         # Storing Intermediate Variables Results
    #                         if intermediateVarStartLine == intermediateVarEndLine:
    #                             finalResultText += f'Intermediate Var:\n\tline {intermediateVarStartLine}: {intermediateVarFunction}\n'
    #                         else:
    #                             finalResultText += f'Intermediate Var:\n\tline {intermediateVarStartLine} - {intermediateVarEndLine}: {intermediateVarFunction}\n'

    #             # Getting Sink Results
    #             sink = extra['dataflow_trace']['taint_sink'][1][0]
    #             sinkStartLine = sink['start']['line']
    #             sinkEndLine = sink['end']['line']
    #             sinkStartColumn = sink['start']['col']
    #             sinkEndColumn = sink['end']['col']
    #             sinkPath = sink['path']
    #             sinkFunction = extractLines(
    #                 sinkPath, sinkStartLine, sinkEndLine, sinkStartColumn, sinkEndColumn)

    #             # Storing Sink Results
    #             if sinkStartLine == sinkEndLine:
    #                 finalResultText += f'\nSink:\n\tline {sinkStartLine}: {sinkFunction}\n'
    #             else:
    #                 finalResultText += f'\nSink:\n\tline {sinkStartLine} - {sinkEndLine}: {sinkFunction}\n'

    #         finalResultText += f'--------------------------------------------------------------------------------\n'


    if dynamicOutputFiles:   
        for dynamicTool, file in dynamicOutputFiles.items():
            finalResultText += f'-------------------------------------------------------------------------------\n'
            finalResultText += f'Name: \t\t\t{dynamicTool}\n'
            finalResultText += f'-------------------------------------------------------------------------------\n\n'
            
            if dynamicTool == 'DALFOX (DYNAMIC XSS)':
                
                resultNo = 0
                with open(file, 'r') as f:
                    dalfox_results = json.load(f)
                    
                for result in dalfox_results:
                    resultNo+=1
                    if result:
                        message =result.get('message_str')
                        severity = result.get('severity')
                        cwe = result.get('cwe')
                        vulnerable_url = result.get('data')
                        payload = result.get("payload")
                        parameter_name = result.get('param')
                        finalResultText += f'Result #{resultNo}:\n\n'
                        finalResultText += f'Severity: {severity}\n'
                        finalResultText += f'CWE: {cwe}\n'
                        finalResultText += f'Vulnerable Url: {vulnerable_url}\n\n'
                        finalResultText += f'Payload: {payload}\n'
                        finalResultText += f'Parameter: {parameter_name}\n\n'
                        finalResultText += f'--------------------------------------------------------------------------------\n'
     
            else:
                #SQLMAP folder
                if os.path.exists(file):
                    for root, dirs, files in os.walk(file):
                        resultNo = 0
                        for dir_name in dirs:
                            log_file_path = os.path.join(root, dir_name, 'log')
                            target_file_path = os.path.join(root, dir_name, 'target.txt')           
                            if os.path.exists(log_file_path) and os.path.exists(target_file_path):
                                with open(log_file_path, 'r') as log_file:
                                    log_contents = log_file.read()
                                with open(target_file_path, 'r') as target_file:
                                    target_contents = target_file.read()

                                # Split the target contents into individual URLs
                                urls = target_contents.split('\n')

                                # Split the log contents into individual sections based on '---'
                                log_sections = log_contents.split('---\n')
                                # Iterate through each URL and corresponding log section
                                for url, log_section in zip(urls, log_sections):

                                    finalResultText += f'Result #{resultNo}:\n\n'
                                    finalResultText += f'\nTarget URL: {url}\n'

                                    # Extract parameter, type, title, and payload from the log section
                                    injection_points=[]

                                    for line in log_section.split('\n'):
                                        if 'Parameter:' in line:
                                            finalResultText += f'\nParameter: {parameter_name}\n'
                                            parameter_name = line.split('Parameter:')[1].strip()
                                        elif 'Type:' in line:
                                            injection_point = {'type': line.split('Type:')[1].strip()}
                                        elif 'Payload:' in line:
                                            injection_point['payload'] = line.split('Payload:')[1].strip()
                                            injection_points.append(injection_point.copy())  # Use copy to avoid overwriting

                                 
                                    for inj_point in injection_points:
                                        finalResultText += '\n\tType: '+ inj_point['type']+'\n'
                                        finalResultText +='\n\tPayload: '+ inj_point['payload']+'\n\n'
                                    
                                    finalResultText += f'--------------------------------------------------------------------------------\n'
                                        

                
        


    # Write all the results to the file
    finalResult = os.path.join(output_dir, f'FinalResults.txt')
    with open(finalResult, 'w') as file:
        file.writelines(finalResultText)

    print(f"File is written out to: {finalResult}")


# <<<Tools>>>

# <<<Semgrep Function>>>

def run_SemGrep(scan_target, type, rule_directory, temp_dir):

    # rule_directory = XssSemgrepRules / SQLiSemgrepRules

    semgrep_output = f"{temp_dir}/{type}_output.json"

    if os.path.exists(semgrep_output):
        os.remove(semgrep_output)
        print(f"File '{semgrep_output}' deleted successfully.")

    # Semgrep custom rule scan (Depends on xss's new rule format)
    semgrep_command = ["semgrep", "--config", rule_directory,
                       scan_target, "--json", "-o", f"{semgrep_output}"]

    # process = subprocess.Popen(semgrep_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # stdout, stderr = process.communicate()

    try:
        subprocess.run(semgrep_command, check=True)
    except subprocess.CalledProcessError as e:
        print("An error occurred while running Semgrep:", e)

    return semgrep_output


# <<<SnykFunction>>>

def run_Snyk(scan_target, type):
    snyk_command = ["snyk", "code", "test", scan_target]
    process = subprocess.Popen(
        snyk_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    temp_dir = os.path.join(os.getcwd(), 'temp')
    os.makedirs(temp_dir, exist_ok=True)

    # Write the stdout (snyk's output) to a file in the temp_dir
    result_file = os.path.join(temp_dir, f'{type}_snyk.txt')
    with open(result_file, 'wb') as f:
        f.write(stdout)

    print(f"{type} Snyk results are stored in {result_file}")
    return result_file


# <<<Wget Function>>>

# If error occurs, error will be stored in the text file instead of being outputed

# Command Equalvilant: wget --spider --header "Cookie: wordpress_81650aaabe3befdc917288ce56482dd7=root%7C1689239527%7CfpSWHdgOvw21tzHILaUi20F4e0vPAHfjC7MXaK4Zqml%7C1720138b4b32f865eeeb1d1389a57b73d779e3858bce545d6a1f4ab3ce80e422; wp-settings-1=libraryContent%3Dbrowse%26posts_list_mode%3Dlist%26editor%3Dtinymce%26mfold%3Do; wp-settings-time-1=1688981179; PHPSESSID=4m612sbeqf2vohkcqi5atc70v2; wordpress_test_cookie=WP%20Cookie%20check; wordpress_logged_in_81650aaabe3befdc917288ce56482dd7=root%7C1689239527%7CfpSWHdgOvw21tzHILaUi20F4e0vPAHfjC7MXaK4Zqml%7C83f70fa1981c3277007503c62b08c135257b08e36a5aa527fbb681a010c880b2"
# -r http://157.245.144.50/wp-admin 2>&1 | grep -E -o "(http|https)://[a-zA-Z0-9./?=_-]*"| sort | uniq > temp/urls3.txt

def run_wget(url, cookie, temp_dir):

    #Ensure url ends with '/'
    if not url.endswith('/'):
        url += '/'

    #Wget output
    urls_file = 'temp/wget.txt'
    print(urls_file)


    if not cookie:
        print('no wget cookie')
        wget_command = [
        'wget', 
        '--spider', 
        '-r', 
        url
        ]

    else:
        # Have not check this command
        
        wget_command = [
        'wget', 
        '--spider',
        f'Cookie: {cookie}', 
        '-r', 
        url
        ]

    full_command = (
        ' '.join(wget_command) +
        ' 2>&1 | grep -E -o "(http|https)://[a-zA-Z0-9./?=_-]*" | sort | uniq > ' +
        urls_file
    )

    try:
        subprocess.run(full_command, shell=True, check=True, executable="/bin/bash")

    except subprocess.CalledProcessError as e:
        print("An error occurred while running Wget:", e)




    print(f"Wget URLs are stored in {urls_file}")
    return (urls_file)


# <<<Gf Function>>>
# Command Equalvilant: cat urls.txt | gf xss | eval sed 's/temp\\///' | eval sort -u > gf-output.txt

def run_gf(urls_file, type, temp_dir, url):
    # Run gf for {vulnerability_type} patterns

    params_urls_file = 'temp/gf.txt'
    print (params_urls_file)

    try:
        subprocess.run(
            f"cat {urls_file} | gf {type} > {params_urls_file}", shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print("An error occurred while running gf:", e)

    print(f"Gf {type} Urls with parameters are stored in {params_urls_file}")
    return (params_urls_file)


# <<<Dalfox Function>>>
def run_DalFox(param_urls, cookie, temp_dir):

    dalfox_output = f'temp/dalfox.json'
    print (cookie)
    print(type(cookie))

    if os.path.exists(dalfox_output):
        os.remove(dalfox_output)
        print(f"File '{dalfox_output}' deleted successfully.")

    if cookie: 
        # dalfox_command = ['dalfox', 'file', param_urls, '--cookie', 'security=low; PHPSESSID=3959afr5laqcoe5u10ee4j6qna', '--skip-bav', '--format', 'json', '-o', dalfox_output]   
        dalfox_command = ['dalfox', 'file', param_urls, '--cookie', cookie, '--skip-bav', '--format', 'json', '-o', dalfox_output]   
    else: 
        dalfox_command = ['dalfox', 'file', param_urls, '--skip-bav', '--format', 'json', '-o', dalfox_output]        

    try:
        result = subprocess.run(dalfox_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print("An error occurred while running Dalfox:", e)

    print(f"Dalfox resutls is being stored in {dalfox_output}")
    return (dalfox_output)


def run_sqlmap(param_urls, cookie, temp_dir):
     
    # sqlmap_dir = temp_dir + "/sqlmap"
    sqlmap_dir= 'temp/sqlmap'

    if os.path.exists(sqlmap_dir):
        shutil.rmtree(sqlmap_dir)
        print(f"Folder '{sqlmap_dir}' deleted successfully.")
        print(cookie)

    if cookie: 
        # sqlmap_command = ["sqlmap", "-m", param_urls, "--cookie",'security=low; PHPSESSID=3959afr5laqcoe5u10ee4j6qna',"--batch","--risk","2","--level", "1", "--threads", "10", "--output-dir", sqlmap_dir]
        sqlmap_command=["sqlmap", "-m", param_urls, "--cookie", cookie ,"--batch","--risk","2","--level", "1", "--threads", "10", "--output-dir", sqlmap_dir]
    else:
        sqlmap_command = ["sqlmap", "-m", param_urls, "--batch","--risk","2","--level","1","--threads", "10", "--output-dir", sqlmap_dir]
        
    try:
        subprocess.run(sqlmap_command, check=True)
    except subprocess.CalledProcessError as e:
        print("An error occurred while running SQLMap:", e)

    return (sqlmap_dir)

# End of Tools........

# <<<Static Scan Functions>>>
def scanning_command(args):
    welcome()
    plugin_folder = args.scan
    wordpress_url = args.url
    user_name = args.uname
    password = args.pwd
    output = args.output
    cookie = args.cookie
    dynamicOutputFiles = False

    # Create "vulnerability-scanner/temp" directory
    current_dir = os.getcwd()
    temp_dir = os.path.join(current_dir, 'temp')


    output_dir = os.path.join(current_dir, 'output')
    # Create the temp directory if it doesn't exist
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
     # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)     

    # # XSS Static Analysis
    # xssOutput = run_SemGrep(plugin_folder, 'XSS',
    #                         'SemgrepRules/XSS', temp_dir)
    # timer(20)

    # # SQL Static Analysis
    # sqliOutput = run_SemGrep(plugin_folder, 'SQLi',
    #                          'SemgrepRules/SQLI', temp_dir)
    # timer(20)

    # # Command Injection Static Analysis
    # cmdiOutput = run_SemGrep(plugin_folder, 'Cmdi',
    #                          f'SemgrepRules/CmdI', temp_dir)

    # timer(20)
    # # Broken Authentication Static Analysis
    
    # #ifAuthFailCheck
    # AuthFailOutput = run_SemGrep(plugin_folder, 'AuthFail',
    #                              'SemgrepRules/AuthFail', temp_dir)

    # semgrepOutputFiles = {'XSS': xssOutput,
    #                       'SQLI': sqliOutput,
    #                       'CmdI': cmdiOutput,
    #                       'AuthFail': AuthFailOutput
    #                       }

    semgrepOutputFiles = False

    if wordpress_url:
        dynamicOutputFiles = dynamic_scan(wordpress_url, user_name, password, cookie, temp_dir)
        generateFinalOutput(semgrepOutputFiles,dynamicOutputFiles,output_dir)
    else:
        generateFinalOutput(semgrepOutputFiles,dynamicOutputFiles,output_dir)    

    
# <<<Dynamic Scan Functions>>>
def dynamic_scan(wordpress_url, user_name, password, cookie, temp_dir):

    print('indynamic')

    if (user_name and password and not cookie):
        # Get Cookie with User Config
        user_configurations = (wordpress_url, user_name, password)

        cookie = wp_login(user_configurations) 
        print('Scanning for Authenticated Pages')

    elif cookie:
        #validate cookie
        print('valid cookie')
    else:
        cookie=False

    # Check if input is an url
    if is_valid_url(wordpress_url):
        print("validurl")

        if not cookie.startswith("'") and not cookie.endswith("'"):
            enclosed_cookie = f"'{cookie}'"

        else:
            enclosed_cookie =cookie

        # Website Crawling
        # urls_file = run_wget(wordpress_url, enclosed_cookie, temp_dir)

        # XSS Dynamic Analysis

        # xss_urls_file = run_gf(urls_file, 'xss', temp_dir, wordpress_url)
        xss_urls_file = 'temp/gf.txt'
        dalfox_output = run_DalFox(xss_urls_file, enclosed_cookie, temp_dir)
    

        timer(20)
        # SQL Dynamic Analysis

        # sqli_urls_file = run_gf(urls_file, 'sql',temp_dir, wordpress_url)
        sqli_urls_file = 'temp/gfsql.txt'
        sqlmap_output = run_sqlmap(sqli_urls_file, enclosed_cookie, temp_dir)

        dynamicOutputFiles = {'DALFOX (DYNAMIC XSS)':dalfox_output,
                              'SQLMAP (DYNAMIC SQLI)':sqlmap_output}
        
        return dynamicOutputFiles

    else:
        print("Invalid URL, please enter a valid input.")


# <<< Argparser module >>>
# var parser defines the program's cmd-line interface
parser = argparse.ArgumentParser(
    description='[BROADCAST] FYP Group 12 of class DISM/FT/3A/04 introduces you to GoatScan! [BROADCAST]')
subparsers = parser.add_subparsers(title="Commands", dest="command")


# Sub-parser for the 'Scanning' command
scanning_parser = subparsers.add_parser('Scanning', help='Scan the plugin')
scanning_parser.add_argument(
    '-f', '--file', dest='scan', required=True, help='Scan plugin file/folder')
scanning_parser.add_argument(
    '-o', '--output', dest='output', required=True, help='Output.txt file destination')
scanning_parser.add_argument(
    '-u', '--url', dest='url', help='Scan wordpress website url')
scanning_parser.add_argument(
    '-n', '--uname', dest='uname', help='Your username for your wordpress website')
scanning_parser.add_argument(
    '-p', '--pwd', dest='pwd', help='Your password for your wordpress website')
scanning_parser.add_argument(
    '-c', '--cookie', dest='cookie', help='Cookie for your website')
# function to call when "Scanning" is used
scanning_parser.set_defaults(func=scanning_command)


args = parser.parse_args()

# <<< End of Argparser module >>>

if hasattr(args, "func"):
    args.func(args)
else:
    parser.print_help()
