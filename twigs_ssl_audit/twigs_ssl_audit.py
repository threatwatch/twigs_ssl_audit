import sys
import re
import os
import shutil
import stat
import subprocess
import logging
import json
import tempfile
import traceback

def get_rating(sev):
    if sev == 'INFO' or sev == 'OK':
        return '1'
    if sev == 'LOW':
        return '2'
    if sev == 'MEDIUM':
        return '3'
    if sev == 'HIGH':
        return '4'
    if sev == 'CRITICAL':
        return '5'
    return '1'

def get_inventory(args):
    asset_id = args.assetid
    if asset_id == None or asset_id.strip() == "":
        asset_id = args.url
    asset_name = None
    if args.assetname == None or args.assetname.strip() == "":
        asset_name = asset_id 
    else:
        asset_name = args.assetname

    asset_data = {}
    asset_data['id'] = asset_id
    asset_data['name'] = asset_name
    asset_data['type'] = "Web Application" 
    asset_data['owner'] = args.handle
    asset_data['products'] = [] 
    asset_data['tags'] = [args.url] 

    logging.info("Running ssl audit for "+args.url)
    logging.info("This may take some time")

    findings = run_ssl_audit(args)
    if findings == None:
        return None
    asset_data['config_issues'] = findings

    # disable scan
    args.no_scan = True
    return [ asset_data ]

def run_ssl_audit(args):
    findings = []
    SSL_AUDIT_PATH = os.path.dirname(os.path.realpath(__file__)) + '/ssl_audit/testssl.sh'
    temp_name = next(tempfile._get_candidate_names())
    defult_tmp_dir = tempfile._get_default_tempdir()
    audit_out = defult_tmp_dir + '/' + temp_name + '.json'
    try:
        cmd = SSL_AUDIT_PATH + ' -oJ ' + audit_out + ' ' +args.url
        cmdarr = [cmd]
        dev_null_device = open(os.devnull, "w")
        subprocess.check_output(cmdarr, stderr=dev_null_device, shell=True)
        dev_null_device.close()
    except subprocess.CalledProcessError as e:
        logging.error("Error running ssl audit: %s" % str(e))
        logging.error(traceback.format_exc())
        return None 

    jf = open(audit_out, 'r')
    out = jf.read()
    jf.close()
    os.remove(audit_out)
    odict = json.loads(out)
    if 'scanResult' in odict:
        if 'pretest' in odict['scanResult'][0]:
            for p in odict['scanResult'][0]['pretest']:
                issue = {}
                issue['twc_id'] = 'ssl-audit-'+p['id']
                issue['twc_title'] = p['id']
                issue['details'] = p['finding']
                issue['rating'] = get_rating(p['severity']) 
                issue['type'] = 'SSL'
                if not args.info and issue['rating'] == '2':
                    continue
                issue['object_id'] = args.url 
                issue['asset_id'] = args.assetid
                issue['object_meta'] = '' 
                findings.append(issue)
        if 'protocols' in odict['scanResult'][0]:
            for p in odict['scanResult'][0]['protocols']:
                issue = {}
                issue['twc_id'] = 'ssl-audit-'+p['id']
                issue['twc_title'] = 'protocol: '+p['id']
                issue['details'] = p['finding']
                issue['rating'] = get_rating(p['severity']) 
                issue['type'] = 'SSL'
                if not args.info and issue['rating'] == '1':
                    continue
                issue['object_id'] = args.url 
                issue['asset_id'] = args.assetid
                issue['object_meta'] = '' 
                findings.append(issue)
        if 'grease' in odict['scanResult'][0]:
            for p in odict['scanResult'][0]['grease']:
                issue = {}
                issue['twc_id'] = 'ssl-audit-'+p['id']
                issue['twc_title'] = p['id']
                issue['details'] = p['finding']
                issue['rating'] = get_rating(p['severity']) 
                issue['type'] = 'SSL'
                if not args.info and issue['rating'] == '1':
                    continue
                issue['object_id'] = args.url 
                issue['asset_id'] = args.assetid
                issue['object_meta'] = '' 
                findings.append(issue)
        if 'grease' in odict['scanResult'][0]:
            for p in odict['scanResult'][0]['grease']:
                issue = {}
                issue['twc_id'] = 'ssl-audit-'+p['id']
                issue['twc_title'] = p['id']
                issue['details'] = p['finding']
                issue['rating'] = get_rating(p['severity']) 
                issue['type'] = 'SSL'
                if not args.info and issue['rating'] == '1':
                    continue
                issue['object_id'] = args.url 
                issue['asset_id'] = args.assetid
                issue['object_meta'] = '' 
                findings.append(issue)
        if 'ciphers' in odict['scanResult'][0]:
            for p in odict['scanResult'][0]['ciphers']:
                issue = {}
                issue['twc_id'] = 'ssl-audit-'+p['id']
                issue['twc_title'] = 'cipher: '+p['id']
                finding = p['finding']
                if 'cwe' in p:
                    finding = finding + ' ' + p['cwe']
                issue['details'] = finding
                issue['rating'] = get_rating(p['severity']) 
                issue['type'] = 'SSL'
                if not args.info and issue['rating'] == '1':
                    continue
                issue['object_id'] = args.url 
                issue['asset_id'] = args.assetid
                issue['object_meta'] = ''
                findings.append(issue)
        if 'fs' in odict['scanResult'][0]:
            for p in odict['scanResult'][0]['fs']:
                issue = {}
                issue['twc_id'] = 'ssl-audit-'+p['id']
                issue['twc_title'] = 'forward secrecy: '+p['id']
                issue['details'] = p['finding']
                issue['rating'] = get_rating(p['severity']) 
                issue['type'] = 'SSL'
                if not args.info and issue['rating'] == '1':
                    continue
                issue['object_id'] = args.url 
                issue['asset_id'] = args.assetid
                issue['object_meta'] = ''
                findings.append(issue)
        if 'serverPreferences' in odict['scanResult'][0]:
            for p in odict['scanResult'][0]['serverPreferences']:
                issue = {}
                issue['twc_id'] = 'ssl-audit-'+p['id']
                issue['twc_title'] = 'server preference: '+p['id']
                issue['details'] = p['finding']
                issue['rating'] = get_rating(p['severity']) 
                issue['type'] = 'SSL'
                if not args.info and issue['rating'] == '1':
                    continue
                issue['object_id'] = args.url 
                issue['asset_id'] = args.assetid
                issue['object_meta'] = ''
                findings.append(issue)
        if 'serverDefaults' in odict['scanResult'][0]:
            for p in odict['scanResult'][0]['serverDefaults']:
                issue = {}
                issue['twc_id'] = 'ssl-audit-'+p['id']
                issue['twc_title'] = 'server default: '+p['id']
                issue['details'] = p['finding']
                issue['rating'] = get_rating(p['severity']) 
                issue['type'] = 'SSL'
                if not args.info and issue['rating'] == '1':
                    continue
                issue['object_id'] = args.url 
                issue['asset_id'] = args.assetid
                issue['object_meta'] = ''
                findings.append(issue)
        if 'headerResponse' in odict['scanResult'][0]:
            for p in odict['scanResult'][0]['headerResponse']:
                issue = {}
                issue['twc_id'] = 'ssl-audit-'+p['id']
                issue['twc_title'] = 'header response: '+p['id']
                issue['details'] = p['finding']
                issue['rating'] = get_rating(p['severity']) 
                issue['type'] = 'SSL'
                if not args.info and issue['rating'] == '1':
                    continue
                issue['object_id'] = args.url 
                issue['asset_id'] = args.assetid
                issue['object_meta'] = ''
                findings.append(issue)
        if 'vulnerabilities' in odict['scanResult'][0]:
            for p in odict['scanResult'][0]['vulnerabilities']:
                issue = {}
                issue['twc_id'] = 'ssl-audit-'+p['id']
                issue['twc_title'] = 'vulnerability: '+p['id']
                finding = p['finding']
                if 'cve' in p:
                    finding = finding + ' ' + p['cve']
                if 'cwe' in p:
                    finding = finding + ' ' + p['cwe']
                issue['details'] = finding
                issue['rating'] = get_rating(p['severity']) 
                issue['type'] = 'SSL'
                if not args.info and issue['rating'] == '1':
                    continue
                issue['object_id'] = args.url 
                issue['asset_id'] = args.assetid
                issue['object_meta'] = ''
                findings.append(issue)
        if 'cipherTests' in odict['scanResult'][0]:
            for p in odict['scanResult'][0]['cipherTests']:
                issue = {}
                issue['twc_id'] = 'ssl-audit-'+p['id']
                issue['twc_title'] = 'cipher test: '+p['id']
                issue['details'] = p['finding']
                issue['rating'] = get_rating(p['severity']) 
                issue['type'] = 'SSL'
                if not args.info and issue['rating'] == '1':
                    continue
                issue['object_id'] = args.url 
                issue['asset_id'] = args.assetid
                issue['object_meta'] = ''
                findings.append(issue)
        if 'browserSimulations' in odict['scanResult'][0]:
            for p in odict['scanResult'][0]['browserSimulations']:
                issue = {}
                issue['twc_id'] = 'ssl-audit-'+p['id']
                issue['twc_title'] = 'browser simulation: '+p['id']
                issue['details'] = p['finding']
                issue['rating'] = get_rating(p['severity']) 
                issue['type'] = 'SSL'
                if not args.info and issue['rating'] == '1':
                    continue
                issue['object_id'] = args.url 
                issue['asset_id'] = args.assetid
                issue['object_meta'] = ''
                findings.append(issue)
        if 'rating' in odict['scanResult'][0]:
            for p in odict['scanResult'][0]['rating']:
                issue = {}
                issue['twc_id'] = 'ssl-audit-'+p['id']
                issue['twc_title'] = p['id']
                issue['details'] = p['finding']
                issue['rating'] = get_rating(p['severity']) 
                issue['type'] = 'SSL'
                if not args.info and issue['rating'] == '1':
                    continue
                issue['object_id'] = args.url 
                issue['asset_id'] = args.assetid
                issue['object_meta'] = ''
                findings.append(issue)
    return findings
