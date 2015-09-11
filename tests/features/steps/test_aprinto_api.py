from behave             import *
from hamcrest           import assert_that, equal_to, is_not

from aprinto_settings   import *
from os                 import system           as os_cmd
from os.path            import isfile           as os_isfile
from re                 import sub              as re_sub
from datetime           import datetime         as DT
from time               import sleep            as delay
from uuid               import uuid4            as get_guid
from json               import dumps            as j_dumps
from subprocess         import check_output     as sub_check_output
from pandas             import read_sql         as pd_read_sql
from pandas             import DataFrame        as pd_DataFrame
from sqlalchemy         import create_engine
from psycopg2           import connect          as psycopg2_connect
import                  requests
from selenium           import webdriver
aprinto_engine                  =   create_engine(r'postgresql://postgres:postgres@%s:%s/%s'%(DB_HOST,DB_PORT,DB_NAME),
                                    encoding='utf-8',
                                    echo=False)
aprinto_conn                    =   psycopg2_connect("""dbname='%s' user='postgres' host='%s' password='' port=%s
                                                     """%(DB_NAME,DB_HOST,DB_PORT));
aprinto_cur                     =   aprinto_conn.cursor()
F_DIR                           =   PY_PATH + '/tests/files/'

def download_file(context):
    context.dl_file             =   F_DIR + context.url[context.url.rfind('/')+1:]
    context.dl_start            =   DT.utcnow()
    with open(context.dl_file, 'wb') as handle:
        req = requests.get(context.url, stream=True)

        if not req.ok:
            context.req         =   req
            context.resp_code   =   context.req.status_code
            context.resp_msg    =   context.req.reason
            return context


        for block in req.iter_content(1024):
            if not block:
                break
            handle.write(block)
            handle.flush()

    context.req                 =   req
    context.resp_code           =   context.req.status_code
    context.resp_msg            =   context.req.reason
    return context
def get_task_results(context):
    with open('/tmp/aprinto_celery_tail','r') as f:
        x                       =   f.readlines()
    cols                        =   ['task_status','task_name','task_id']
    df                          =   pd_DataFrame(columns=cols)
    for it in x:
        if it.split()[3]=='task':
            t=re_sub('(.*)(\\btask\\b\s)([^:]+)(: document_processing\.\\b)([^\(]+)\(([^\)]+)\)(.*)','\g<3>,\g<5>,\g<6>',it).replace('\n','')
            D                   =   dict(zip(cols,t.split(',')))
            df                  =   df.append(D,ignore_index=True)
    context.celery_results      =   df
    return context

@given('We want to verify the online presence of the domain "{domain}"')
def step_impl(context,domain):
    context.domain          =   domain
@given('"{page_title}" is live and we access "{webpage}"')
def step_impl(context,page_title,webpage):
    context.page_title      =   page_title
    context.url             =   webpage
@given('a new IP address')
def step_impl(context):
    aprinto_conn.set_isolation_level(0)
    aprinto_cur.execute("delete from aprinto_access where ip_addr = '%s'"%THIS_IP)
    context.this_ip         =   THIS_IP
@given('data for posting to "{order_post_url}"')
def step_impl(context,order_post_url):
    context.post_url        =   order_post_url
    pdf_id                  =   str(get_guid())
    if hasattr(context,'pdf_id_grp'):
        context.pdf_id_grp.append(pdf_id)
    else:
        context.pdf_id_grp  =   [pdf_id]
    headers                 =   {'Content-type' :   'application/json'}
    context.data            =   {'json'         :[{
                                        'pdf_id'            :   pdf_id,
                                        'printer_id'        :   'printer_id1',
                                        'application_name'  :   'application_name1',
                                        'doc_name'          :   'test_unit_1'
                                    }],
                                'headers'       :   headers}
@given('a successful \'handshake\' with Aporo servers from a(n) "{credentials}" with the credentials: "{machine_id}"')
def step_impl(context,credentials,machine_id):
    context.credentials     =   credentials
    context.machine_id      =   machine_id
    context.execute_steps(
        unicode(""" given data for posting to "http://printer.aporodelivery.com/api/check/"
                    when the post request is from a(n) "%s" with the credentials: "%s"
                    and the data is posted
                    then Aporo will return: "CREATED"
                    """%(credentials,machine_id)))
@given('a "{doc_type}" for uploading to "{upload_url}" with "{paired}" PDF_ID')
def step_impl(context,doc_type,upload_url,paired):
    context.post_url            =   upload_url

    if doc_type=='Client Contract':
        f_name                  =   'test_contract.pdf'
    elif doc_type=='pdf':
        f_name                  =   'test_page.pdf'
    elif doc_type=='txt':
        f_name                  =   'test_doc.txt'
    f_path                      =   F_DIR + f_name

    if paired=='the same':
        if hasattr(context,'order_tag'):
            new_name            =   context.order_tag + '_' + context.pdf_id_grp[-1] + f_path[f_path.rfind('.'):]
        else: new_name          =   context.pdf_id_grp[-1] + f_path[f_path.rfind('.'):]
    elif paired=='a different':
        new_uuid                =   str(get_guid())
        if hasattr(context,'order_tag'):
            new_name            =   context.order_tag + '_' + new_uuid + f_path[f_path.rfind('.'):]
        else: new_name          =   new_uuid + f_path[f_path.rfind('.'):]

    context.upload_file         =   new_name
    new_path                    =   '/tmp/' + new_name
    context.upload_fpath        =   new_path
    if hasattr(context,'files_created'):
        context.files_created.append(new_path)
    else:
        context.files_created   =   [new_path]

    os_cmd('cp %s %s'%(f_path,new_path))
    h                           =   'form-data; '
    h                          +=   'name="local_document"; '
    h                          +=   'filename="%s"'%new_path
    headers                     =   {'Content-Disposition' :   h}
    context.data                =   {'headers'      :   headers,
                                    'files': {'local_document': open(new_path,'rb')},
                                    }
@given('a "{user_type}" with credentials "{user_creds}" prints the "{client_name}" Contract')
def step_impl(context,user_type,user_creds,client_name):
    if hasattr(context,'user_type_grp'):
        context.user_type_grp.append(user_type)
        context.user_cred_grp.append(user_creds)
    else:
        context.user_type_grp  =   [user_type]
        context.user_cred_grp  =   [user_creds]
    context.client_name         =   client_name
    context.execute_steps(
        unicode(""" given a successful 'handshake' with Aporo servers from a(n) "%s" with the credentials: "%s"
                    and a "Client Contract" for uploading to "http://printer.aporodelivery.com/" with "the same" PDF_ID
                    when the data is posted
                    """%(user_type,user_creds)))
@given('"{client_name}" in the Contract becomes registered within "{process_seconds}" seconds')
def step_impl(context,client_name,process_seconds):
    context.client_name     =   client_name
    context.process_seconds =   process_seconds
    context.execute_steps(
        unicode(""" then within "%s" seconds
                    and "%s" in the Contract becomes registered
                    """%(process_seconds,client_name)))




@when('the post request is from a(n) "{credentials}" with the credentials: "{machine_id}"')
def step_impl(context,credentials,machine_id):
    context.credentials     =   credentials
    context.machine_id      =   machine_id
    if machine_id == "None":
        assert_that(context.data['json'][0].has_key('machine_id'), equal_to(False))
    else:
        context.data['json'][0].update({'machine_id':machine_id})
        assert_that(context.data['json'][0].has_key('machine_id'), equal_to(True))
@when('the request format is "{request_format}"')
def step_impl(context,request_format):
    context.request_format  =   request_format
    if   request_format == 'valid':   validity_check = True
    elif request_format == 'invalid':
        a=context.data['json'][0].keys()
        del context.data['json'][0][a[0]]
        validity_check = False
    fields                  =   sorted(['pdf_id','printer_id','machine_id',
                                 'application_name','doc_name'])
    t                       =   context.data['json'][0]
    t_keys                  =   sorted(t.keys())
    assert_that(t_keys==fields,equal_to(validity_check),str(t_keys)+'\n\n'+str(fields))
    if validity_check==True:
        assert_that(len(t['pdf_id'])<=38,equal_to(True))
@when('the data is posted')
def step_impl(context):
    try:
        context.req         =   requests.post(context.post_url,**context.data)
        if context.post_url.find('/api/check')>0:
            try:
                t           =   eval(context.req.content)
                context.order_tag = t['order_tag']
            except:
                pass

    except requests.exceptions.ConnectionError as x:
        context.resp_code   =   x.args[0].args[1].args[0]
        context.resp_msg    =   x.args[0].args[1].args[1]
        assert_that(            context.resp_msg,   equal_to('OK'))
    except requests.Timeout:
        timeout             =   True
        assert_that(            timeout,   equal_to(False) )
@when('the date is posted "{post_count}" more times (with a different UUID)')
def step_impl(context,post_count):
    cnt = int(post_count)
    for it in range(cnt):
        pdf_id              =   str(get_guid())
        context.pdf_id_grp.append(pdf_id)
        context.data['json'][0]['pdf_id']=pdf_id
        context.execute_steps(unicode("when the data is posted"))
@when('"{company}" logs in with user: "{username}" and pw: "{pw}"')
def step_impl(context,company,username,pw):
    D = webdriver.PhantomJS(    executable_path='/usr/local/bin/phantomjs')
    D.set_window_position(      0, 0)
    D.set_window_size(          300, 300)
    D.desired_capabilities[     'applicationCacheEnabled'] = True
    D.desired_capabilities[     'locationContextEnabled'] = True
    D.desired_capabilities[     'databaseEnabled'] = True
    D.desired_capabilities[     'webStorageEnabled'] = True
    D.desired_capabilities[     'JavascriptEnabled'] = True
    D.desired_capabilities[     'acceptSslCerts'] = True
    D.desired_capabilities[     'browserConnectionEnabled'] = True
    D.desired_capabilities[     'rotatable'] = True
    login                   =   'http://admin.gnamgnamapp.com/login'
    D.get(                      login)
    D.find_element_by_id(       "email").send_keys(username)
    D.find_element_by_id(       "password").send_keys(pw)
    D.find_element_by_id(       "login-btn").click()
    D.implicitly_wait(          20)
    context.webpage_source  =   D.page_source.lower()


@then('the page will contain "{this}"')
def step_impl(context,this):
    assert_that(                context.webpage_source.find(this.lower())>-1,
                                equal_to(True),)


@then('"{host_file}" should not internally direct requests')
def step_impl(context,host_file):
    T                       =   {'host_file':host_file,
                                 'domain'   :context.domain}
    cmd                     =   'cat %(host_file)s'%T
    proc                    =   sub_check_output(cmd, shell=True)
    if proc.find('%(domain)s'%T) == -1:
        assert True is True
    else:
        cmd                 =   'cat %(host_file)s | grep %(domain)s'%T
        proc                =   sub_check_output(cmd, shell=True)
        assert_that(proc[0],        equal_to('#'),      str(proc))
@then('the page should start loading within "{response_time}" seconds')
def step_impl(context,response_time):
    headers                     =   {'Content-type': 'text/html; charset=UTF-8'}
    data                        =   {'headers'  :   headers,
                                    'timeout'  :   float(response_time)}
    if str(context.scenario.name).lower().find('download')>0:
        context                 =   download_file(context)
    else:
        try:
            context.req         =   requests.get(context.url,**data)
            context.timeout     =   False
            context.resp_code   =   context.req.status_code
            context.resp_msg    =   context.req.reason
        except requests.exceptions.ConnectionError as x:
            context.timeout     =   False
            context.resp_code   =   x.args#[0].args[1].args[0]
            context.resp_msg    =   x.args#[0].args[1].args[1]
            assert_that(context.resp_msg,           equal_to('OK'))
        except requests.Timeout:
            context.timeout     =   True
            assert_that( context.timeout,   equal_to(False) )
@then('the download should finish within "{download_time}" seconds')
def step_impl(context,download_time):
    context.dl_end          =   DT.strptime(context.req.headers['date'].replace(' GMT',''),
                                            '%a, %d %b %Y %H:%M:%S')
    context.dl_duration     =   (context.dl_end-context.dl_start).resolution.total_seconds()
    assert_that( context.dl_duration<=eval(download_time),   equal_to(True) )
@then('the webpage should be unchanged')
def step_impl(context):
    f_path                  =   F_DIR + str(context.page_title).lower().replace(' ','_')+'_orig.html'
    with open(f_path,'r') as f:
        orig                =   f.read()
    assert_that(context.req.content,equal_to(orig))
@then('the response message should be "{msg}" with response code "{code}"')
def step_impl(context,msg,code):
    assert_that( context.resp_code, equal_to(int(code)), str(context.resp_code) )
    assert_that( context.resp_msg,  equal_to(msg),       str(context.resp_msg)  )
@then('"{client_name}" becomes associated with "{user_creds}"')
def step_impl(context,client_name,user_creds):
    context.client      =   client_name
    context.user_creds  =   user_creds
    cmd = """
        select * from aprinto_access
        where vend_name ~* '%s'
        and machine_id = '%s'"""%(context.client,user_creds)
    print cmd
    context.vendor = pd_read_sql(cmd,aprinto_engine)
    assert_that(len(context.vendor),        equal_to(1),      str(context.vendor))
@then('the source IP address "{known_user}" as a Known User')
def step_impl(context,known_user):
    cmd = """
        select count(*) cnt from aprinto_access
        where ip_addr = '%s'
        and machine_id = '%s'"""%(THIS_IP,context.user_creds)
    match_num = pd_read_sql(cmd,aprinto_engine)['cnt'][0]
    assert_that(match_num,                  equal_to(1),      str(match_num))
@then('upon a second post to "{url}" with a "{doc_type}" and with "{paired_pdf_id}" PDF_ID')
def step_impl(context,url,doc_type,paired_pdf_id):
    context.execute_steps(
        unicode(""" given a "%s" for uploading to "%s" with "%s" PDF_ID
                    when the data is posted
                    """%(doc_type,url,paired_pdf_id)))
@then('Aporo will return: "{result}"')
def step_impl(context,result):
    context.result          =   result
    assert_that(context.req.reason.upper(),         equal_to(result))
@then('(if not FORBIDDEN) Aporo creates a DB entry and returns an Order Tag, a Post Url, and QR code information')
def step_impl(context):
    if context.result == 'CREATED':
        T                   =   eval(context.req.content)
        context.order_tag   =   T['order_tag']

        # DB Entry:
        T.update({'pdf_id':context.pdf_id_grp[-1]})
        context.db_entry = pd_read_sql("""
            select * from aprinto_pdfs
            where pdf_id = '%(pdf_id)s'
            and order_tag = '%(order_tag)s'
            """%T,aprinto_engine)
        assert_that(len(context.db_entry),        equal_to(1))

        # Aporo Response
        assert_that( type(T),equal_to(dict),T)
        assert_that( (T.has_key('order_tag')==True and T['order_tag']!=''), equal_to(True))
        assert_that( (T.has_key('doc_post_url')==True and T['doc_post_url']!=''), equal_to(True))
        assert_that( (T.has_key('order_tag')==True and T['order_tag']!=''), equal_to(True))
        assert_that( (T.has_key('qr_code_x')==True
                      and T.has_key('qr_code_y')==True
                      and T.has_key('qr_code_scale')==True), equal_to(True))
@then('the source IP is blacklisted')
def step_impl(context):
    context.blacklisted = pd_read_sql("""
        select blacklist bl from aprinto_access
        where ip_addr = '%s'"""%context.this_ip,aprinto_engine).bl[0]
    assert_that(context.blacklisted,        equal_to('true'),      str(context.blacklisted))
@then('within "{process_seconds}" seconds')
def step_impl(context,process_seconds):
    delay(int(eval(process_seconds)))
@then('Celery processes the document and concludes with "{celery_end}"')
def step_impl(context,celery_end):
    delay(2)
    context.celery_end          =   celery_end
    if context.celery_end!='None':
        context                 =   get_task_results(context)
        tasks                   =   context.celery_results.task_name.unique().tolist()
        all_task_events         =   context.celery_results.task_name.tolist()
        assert_that(all_task_events.count(celery_end)>0,equal_to(True))
@then('Redis stores Celery results')
def step_impl(context):
    if context.celery_end!='None':
        task_id                 =   context.celery_results[context.celery_results.task_name==context.celery_end].task_id.tolist()[0]
        r                       =   context.redis.keys("*%s" % task_id)
        assert_that(len(r)>0,equal_to(True))
@then('"{the_client}" in the Contract becomes registered')
def step_impl(context,the_client):
    context.client = the_client
    cmd = """
        select * from aprinto_access
        where vend_name ~* '%s' """%context.client
    context.vendor = pd_read_sql(cmd,aprinto_engine)
    assert_that(len(context.vendor),        equal_to(1),      str(context.vendor))
    context.vendor_id = str(context.vendor.uid[0])
    cmd = """
        select status from aprinto_pdfs
        where user_id = %s
        and pdf_id='%s' """%(context.vendor_id,context.pdf_id_grp[-1])
    pdf_status = pd_read_sql(cmd,aprinto_engine)
    assert_that(pdf_status['status'][0],    equal_to('NV'),      str(pdf_status))
    # 'task succeeded: document_processing.add_new_vendor_info'
    # redis result for same
@then('the "{doc}" is saved to the "{save_dir}" directory')
def step_impl(context,doc,save_dir):
    context.k_path = PY_PATH.rstrip('/') + '/' + save_dir + context.upload_file

    if hasattr(context,'files_created'):
        context.files_created.append(context.k_path)
    else:
        context.files_created  =   [context.k_path]

    assert_that(os_isfile(context.k_path),  equal_to(True))