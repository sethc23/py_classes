
from aprinto_settings                           import *
from os                                         import system           as os_cmd
from os                                         import environ          as os_environ
from time                                       import sleep            as delay
from re                                         import findall          as re_findall
from subprocess                                 import Popen            as sub_popen
from subprocess                                 import PIPE             as sub_PIPE
from sys                                        import path             as py_path
py_path.append(                                 os_environ['HOME'] + '/.scripts')
from System_Control                             import System_Config

from psycopg2                                   import connect          as psycopg2_connect
aprinto_conn                                =   psycopg2_connect("dbname='%s' user='postgres' host='%s' password='' port=%s"
                                                         %(DB_NAME,DB_HOST,DB_PORT));
aprinto_cur                                 =   aprinto_conn.cursor()
from pandas                                 import read_sql         as pd_read_sql
from sqlalchemy                             import create_engine
aprinto_engine                              =   create_engine(r'postgresql://postgres:postgres@%s:%s/%s'
                                                                %(DB_HOST,DB_PORT,DB_NAME),
                                                                encoding='utf-8',
                                                                echo=False)
# pd_read_sql('',aprinto_engine)
# from ipdb import set_trace as i_trace; i_trace()
import                                  sys
reload(                                 sys)
sys.setdefaultencoding(                 'UTF8')

def remove_from_ip_addresses(context,cred=''):
    aprinto_conn.set_isolation_level(0)
    if cred=='':             mach_id     =   context.machine_id
    else:                    mach_id     =   cred
    cmd =   """ DELETE FROM aprinto_access
                WHERE ip_addr = '%s'
            """%THIS_IP
    if mach_id=='None':      cmd         +=  "AND machine_id is null"
    else:                    cmd         +=  "AND machine_id = '%s'"%mach_id
    aprinto_cur.execute(cmd)

def before_step(context, step):

    if step.name.find("a successful 'handshake' with Aporo servers from a(n)")>=0:
        cred,machine_id         =   re_findall(r'\"(.+?)\"',str(step.name))
        if cred=='manager':
            t=pd_read_sql("""   INSERT INTO aprinto_access (date_created,machine_id,ip_addr,vend_name,known_user,type_admin)
                                VALUES ('now'::timestamp with time zone,'%s','%s','tmp','true','true')
                                RETURNING uid
                                """ % (machine_id,THIS_IP),aprinto_engine)['uid'][0]
            context.row_created     =   t

        elif cred=='vendor' and context.feature.name.find('Client Computer Authentication via a Contract')==-1:
            t=pd_read_sql("""   INSERT INTO aprinto_access (date_created,machine_id,ip_addr,vend_name,known_user,type_vendor)
                                VALUES ('now'::timestamp with time zone,'%s','%s','tmp','true','true')
                                RETURNING uid
                                """ % (machine_id,THIS_IP),aprinto_engine)['uid'][0]
            context.row_created     =   t

def after_step(context, step):

    ft_name         =   context.feature.name
    scenario_name   =   context.scenario.name
    step_name       =   step.name

    if step.status == "failed" and [it for it in context.tags].count('debug')>0:
        import ipdb
        ipdb.post_mortem(step.exc_traceback)

    elif step.status == "failed" and [BEHAVE_TXT_ON_ERROR].count(True)>0:
        msg             =   ['Failure: %s --'%ft_name,
                            'Feature: %s'%ft_name,
                            'Scenario: %s'%scenario_name,
                            'STEPS:']

        all_steps       =   context.scenario.steps
        for it in all_steps:
            s           =   it.name
            if s==step_name:
                msg.append('\tFAILED -->> '+s)
                break
            else:
                msg.append('\t'+s)

        msg.append('VARS:')

        std_vars        =   ['scenario', 'tags', 'text', 'stdout_capture', 'feature', 'log_capture', 'table', 'stderr_capture']
        current_vars    =   context._record.keys()
        for it in current_vars:
            if std_vars.count(it)==0:
                try:
                    msg.append('\t'+it+': '+str(context.__getattr__(it)))
                except:
                    pass

        msg.append('-- END --')
        pb_msg          =   '\n'.join(msg)
        pb_url          =   make_pastebin(pb_msg,msg[0],'2W',1)
        mail_msg        =   '\n'.join([msg[0],pb_url])

        cmd             =   'logger -t "Aprinto_Unit_Test" "%s"' % mail_msg.replace('\n',' ').replace('-','')
        proc            =   sub_popen([''.join(cmd)], stdout=sub_PIPE, shell=True)
        (t, err)        =   proc.communicate()

        if BEHAVE_TXT_ON_ERROR==True:

            cmd         =   'echo "%s" | mail -t 6174295700@vtext.com'%mail_msg
            proc        =   sub_popen([''.join(cmd)], stdout=sub_PIPE, shell=True)
            (t, err)    =   proc.communicate()

def before_scenario(context, scenario):

    celery_tails = ['A manager prints a Client Contract',
                    'After a manager prints a Client Contract, the Client prints the same Contract',
                    'Check In Requests & Document Post Attempts Made to Aporo']

    if scenario.name.find('Check In Requests')>=0:
        t                           =   str(scenario.steps[1])
        t                           =   t[t.find('"')+1:t.rfind('"')]
        cred,machine_id             =   re_findall(r'\"(.+?)\"',t)

        if cred=='manager':
            t=pd_read_sql("""   INSERT INTO aprinto_access (date_created,machine_id,ip_addr,vend_name,known_user,type_admin)
                                VALUES ('now'::timestamp with time zone,'%s','%s','tmp','true','true')
                                RETURNING uid
                                """ % (machine_id,THIS_IP),aprinto_engine)['uid'][0]
            context.row_created     =   t

        elif cred=='vendor':
            t=pd_read_sql("""   INSERT INTO aprinto_access (date_created,machine_id,ip_addr,vend_name,known_user,type_vendor)
                                VALUES ('now'::timestamp with time zone,'%s','%s','tmp','true','true')
                                RETURNING uid
                                """ % (machine_id,THIS_IP),aprinto_engine)['uid'][0]
            context.row_created     =   t

    if celery_tails.count(scenario.name)>0:
        context.celery_tail         =   '/tmp/aprinto_celery_tail'
        cmd                         =   PY_PATH + '/tests/files/tail_celery.bash'
        proc                        =   sub_popen([''.join(cmd)], stdout=sub_PIPE, shell=True)
        (t, err)                    =   proc.communicate()

        if hasattr(context,'processes'):
            context.processes.append(str(t))
        else:
            context.processes       =   [str(t)]
        # from ipdb import set_trace as i_trace; i_trace()
        delay(2)

def after_scenario(context, scenario):

    if [it for it in context.tags].count('no_clean')==0:

        if hasattr(context,'processes'):
            for it in context.processes:
                os_cmd('kill %s' % it)

        if hasattr(context,'celery_tail'):
            os_cmd('rm %s' % context.celery_tail)

        if hasattr(context,'files_created'):
            for it in context.files_created:
                os_cmd('rm -f %s'%it)


    if scenario.status!='failed' and [it for it in context.tags].count('no_clean')==0:

        if scenario.name.find('Check In Requests')>=0:

            if context.credentials=='manager' or context.credentials=='vendor':
                aprinto_conn.set_isolation_level(0)
                aprinto_cur.execute("delete from aprinto_access where uid='%s'"%context.row_created)
                if context.result=='OK':
                    f_path = PY_PATH.rstrip('/') + '/media/processed/' + context.order_tag + '_' + context.pdf_id_grp[0] + '.pdf'
                    os_cmd('rm -f %s' % f_path)

            elif context.credentials=='unknown':
                aprinto_conn.set_isolation_level(0)
                aprinto_cur.execute("delete from aprinto_access where machine_id='unknown' and ip_addr='%s'" % THIS_IP)
                if context.result=='OK':
                    f_path = PY_PATH.rstrip('/') + '/media/unknown/' + context.order_tag + '_' + context.pdf_id_grp[0] + '.pdf'
                    os_cmd('rm -f %s' % f_path)

            for it in context.pdf_id_grp:
                aprinto_conn.set_isolation_level(0)
                aprinto_cur.execute(""" DELETE FROM aprinto_pdfs
                                        WHERE pdf_id = '%s'
                                    """%(it))

        elif scenario.name=='Blacklisting an IP Address':

            remove_from_ip_addresses(context)

            for it in context.pdf_id_grp:
                aprinto_conn.set_isolation_level(0)
                aprinto_cur.execute(""" DELETE FROM aprinto_pdfs
                                        WHERE pdf_id = '%s'
                                    """%(it))

        elif scenario.name=='A manager prints a Client Contract':

            aprinto_conn.set_isolation_level(0)
            aprinto_cur.execute("delete from aprinto_pdfs where user_id = '%s'"%context.vendor_id)
            aprinto_conn.set_isolation_level(0)
            aprinto_cur.execute("delete from aprinto_access where uid = '%s'"%context.vendor_id)

            if context.credentials=='manager':
                aprinto_conn.set_isolation_level(0)
                aprinto_cur.execute("delete from aprinto_access where uid='%s'"%context.row_created)

        elif scenario.name=='After a manager prints a Client Contract, the Client prints the same Contract':
            for cred in context.user_cred_grp:
                t = pd_read_sql(""" DELETE FROM aprinto_pdfs
                                    WHERE machine_id = '%s'
                                    RETURNING local_document doc,user_id
                                """%cred,aprinto_engine)
                os_cmd('rm -f %s'%t['doc'][0])

                remove_from_ip_addresses(context,cred)

                if t['user_id'][0]!=None:
                    aprinto_conn.set_isolation_level(0)
                    aprinto_cur.execute(""" DELETE FROM aprinto_access
                                            WHERE uid = '%s'
                                        """%(t['user_id'][0]))

        elif scenario.name=='Confirm Printer Driver Available for Fast Download':
            os_cmd('rm -f %s'%context.dl_file)

def before_feature(context, feature):
    context.USER                    =   os_environ['USER']

    CFG                             =   System_Config()
    cfgs                            =   []
    # cfgs.extend(                        CFG.adjust_settings( *['aprinto','behave_txt_false'] ) )
    cfgs.extend(                        CFG.adjust_settings( *['aprinto','celery_txt_false'] ) )
    cfgs.extend(                        CFG.adjust_settings( *['nginx','access_log_disable'] ) )
    context.CFG,context.cfgs        =   CFG,cfgs

    redis_features                  =   ['Client Computer Authentication via a Contract',
                                         'Limited Server Access']
    if redis_features.count(feature.name)>0:
        import redis
        context.redis               =   redis.StrictRedis(host='localhost',
                                                          port=6379,
                                                          db=0)
    non_local_host_features         =   ['Verify Online Presence']
    if non_local_host_features.count(feature.name)>0:
        cfgs.extend(                    CFG.adjust_settings( *['hosts','192.168.3.51_disable'] ) )
    else:
        cfgs.extend(                    CFG.adjust_settings( *['hosts','192.168.3.51_enable'] ) )


def after_feature(context,feature):
    context.CFG.restore_settings(       context.cfgs)
    context.cfgs                    =   []