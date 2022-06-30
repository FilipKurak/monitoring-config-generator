from argparse import ArgumentParser
import re

PASSWORDSTATE_URL = 'https://passwords/pid='
CONFIG_FILE_NAME = 'A3.SDC.monitoring.config'


def header(configuration_string):
    configuration_string += '####### ' + customer + ' #######\n'
    return configuration_string


def check_processing(configuration_string):
    configuration_string += '[' + customer + '_Check_Processing]\n'
    configuration_string += 'className=jdbc.DatabaseExecutor\n'
    configuration_string += "query=select case when one=two and two=three then 1 else 0 end from (" \
                            "select count(*) as one from SCHSCHDTASKEXEC_QH where qhoutcome ='STARTED' " \
                            "and (QHSCHTASKNAME like '%rocessing%' or qhtaskname like '%rocessing%')) a, (" \
                            "select count(*) as two from d_data_owner_processing where status='RUNNING') b, (" \
                            "select count(*) as three from monsyststatus_mu where mustatus='BEING_PROCESSED') c\n"
    configuration_string += 'message=Processing information in MIM, scheduler and database doesn''t match, ' \
                            'monitor the system and act if the situation persists for more than 2 hours. \n'
    configuration_string += 'refval=1\n'
    configuration_string += 'compare=equal\n'
    configuration_string = add_db_part(configuration_string)
    return configuration_string


def check_processing_price(configuration_string):
    configuration_string += '[' + customer + '_Check_Processing]\n'
    configuration_string += 'className=EmptyCheck\n'
    configuration_string += 'message=Not applicable\n'
    configuration_string += 'system_name=' + customer + '\n'
    configuration_string += 'result=true\n'
    configuration_string += '\n'
    return configuration_string


def check_activity_log(configuration_string):
    configuration_string += '[' + customer + '_Activity_Log]\n'
    configuration_string += 'className=jdbc.ActivityLog\n'
    configuration_string = add_db_part(configuration_string)
    return configuration_string


def check_mw_code(configuration_string):
    configuration_string += '[' + customer + '_Get_MWCode]\n'
    configuration_string += 'className=MWCode\n'
    configuration_string += 'mwcode=' + mwcode + '\n'
    configuration_string += 'system_name=' + customer + '\n'
    configuration_string += 'result=true\n'
    configuration_string += '\n'
    return configuration_string


def check_batch_log(configuration_string):
    configuration_string += '[' + customer + '_Batch_Log]\n'
    configuration_string += 'className=jdbc.BatchLog\n'
    configuration_string = add_db_part(configuration_string)
    return configuration_string


def check_scheduled_tasks(configuration_string):
    configuration_string += '[' + customer + '_Failed_Scheduled_Tasks]\n'
    configuration_string += 'className=jdbc.ScheduledTaskFailures\n'
    configuration_string = add_db_part(configuration_string)
    return configuration_string


def check_interface_delay(configuration_string):
    configuration_string += '[' + customer + '_Interface_Delay_Check]\n'
    configuration_string += 'className=jdbc.DatabaseExecutor\n'
    configuration_string += 'refval=0\n'
    configuration_string += 'compare=equal\n'
    configuration_string += "query=SELECT count(*) FROM INTERFINST_II II JOIN INTERFACE_IR IR ON IR.IRID=II.IRID " \
                            "WHERE IR.IRINTTYP = 'BATCH_S3' and iidelay < 60000\n"
    configuration_string = add_db_part(configuration_string)
    return configuration_string


def check_document_log(configuration_string):
    configuration_string += '[' + customer + '_Document_Log]\n'
    configuration_string += 'className=jdbc.DocumentLog\n'
    configuration_string = add_db_part(configuration_string)
    return configuration_string


def check_listeners(configuration_string):
    configuration_string += '[' + customer + '_Listener_Watcher]\n'
    configuration_string += 'className=http.SpringBeanIgnite\n'
    configuration_string += 'spring-bean=ListenerManager.getNumberOfListeners()-' \
                            'ListenerManager.getNumberOfRunningListeners()\n'
    configuration_string += 'expected_result=0\n'
    configuration_string = add_gui_part(configuration_string)
    return configuration_string


def check_login(configuration_string):
    configuration_string += '[' + customer + '_Login]\n'
    configuration_string += 'className=http.GIMLogin\n'
    configuration_string = add_gui_part(configuration_string)
    return configuration_string


def check_uptime(configuration_string):
    configuration_string += '[' + customer + '_Uptime]\n'
    configuration_string += 'className=http.UptimeIgnite\n'
    configuration_string += 'uptime=2h\n'
    configuration_string += 'compare_uptime=longer\n'
    configuration_string = add_gui_part(configuration_string)
    return configuration_string


def check_scheduler_status(configuration_string):
    configuration_string += '[' + customer + '_SchedulerStatus]\n'
    configuration_string += 'className=http.SchedulerStatus\n'
    configuration_string += 'paused=false\n'
    configuration_string = add_gui_part(configuration_string)
    return configuration_string


def mw_listeners(configuration_string):
    configuration_string += '[' + customer + '_DisableListeners]\n'
    configuration_string += 'className=complex.StopListenersIgnite\n'
    configuration_string += 'method=SpringBean\n'
    configuration_string = add_gui_part(configuration_string)
    return configuration_string


def mw_scheduler(configuration_string):
    configuration_string += '[' + customer + '_Scheduler]\n'
    configuration_string += 'className=http.Scheduler\n'
    configuration_string += 'paused=true\n'
    configuration_string += 'user=admin\n'
    configuration_string = add_gui_part(configuration_string)
    return configuration_string


def add_gui_part(configuration_string):
    configuration_string += 'system_name=' + customer + '\n'
    configuration_string += 'pw_link=' + PASSWORDSTATE_URL + gui_password_id + '\n'
    configuration_string += '\n'
    return configuration_string


def add_db_part(configuration_string):
    configuration_string += 'system_name=' + customer + '\n'
    configuration_string += 'databaseType=POSTGRES\n'
    configuration_string += 'pw_link=' + PASSWORDSTATE_URL + db_password_id + '\n'
    configuration_string += '\n'
    return configuration_string


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("--customer", dest="customer")
    parser.add_argument("--product", dest="product")
    parser.add_argument("--gui_password_id", dest="gui_password_id")
    parser.add_argument("--db_password_id", dest="db_password_id")
    parser.add_argument("--mwcode", dest="mwcode")
    args = parser.parse_args()

    if args.customer is None:
        customer = input('Customer: ')
    else:
        customer = args.customer

    if args.product is None:
        product = input('Inventory/Price?')
    else:
        product = args.product

    if args.gui_password_id is None:
        gui_password_id = input('Gui password id: ')
    else:
        gui_password_id = args.gui_password_id

    if args.db_password_id is None:
        db_password_id = input('DB password id: ')
    else:
        db_password_id = args.db_password_id

    if args.mwcode is None:
        mwcode = input('MW Code: ')
    else:
        mwcode = args.mwcode

    arguments = args.__dict__

    result = ''''''
    result = header(result)
    result = check_mw_code(result)
    if product == 'Inventory':
        result = check_processing(result)
    else:
        result = check_processing_price(result)
    result = check_activity_log(result)
    result = check_batch_log(result)
    result = check_scheduled_tasks(result)
    if customer not in ['John Bean Technologies - JBT_Price', 'Krones AG_Price']:
        result = check_interface_delay(result)
    result = check_document_log(result)
    result = check_listeners(result)
    result = check_login(result)
    result = check_uptime(result)
    result = check_scheduler_status(result)

    print("*** Print new config ***")
    print(result)

    #
    with open(CONFIG_FILE_NAME, 'r') as file:
        data = file.read()

    customer_regex = re.compile('#+ ' + customer + ' #+(?:\n.*)*?\n#', re.MULTILINE)
    customer_fragment = str(customer_regex.findall(data))[2:-3]
    if customer_fragment == '':
        something_new = data[:-1] + result + '#'
        print('No previous config found')
    else:
        # if not only_listeners:
        something_new = re.sub(customer_regex, result + '#', data)
        print('Modifying existing config')

    print("*** Print result that will be commited ***")
    print(something_new)

    f = open(CONFIG_FILE_NAME, 'w')
    f.write("%s" % something_new)
    f.close()

    result = ''''''
    result = header(result)
    result = mw_listeners(result)
    result = mw_scheduler(result)

    if mwcode == 'AP02':
        mw_config_file_name = 'Docker_PreMaintenanceWindow_JP.config'
    else:
        mw_config_file_name = 'Docker_PreMaintenanceWindow.config'

    f = open(mw_config_file_name, 'w')
    f.write("%s" % result)
    f.close()
