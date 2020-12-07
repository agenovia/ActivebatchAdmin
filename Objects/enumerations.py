import re


class BaseEnumeration(object):
    """
    Any method call made to an ActiveBatch object to retrieve an enumeration returns an integer. This class helps
    to easily retrieve either the string representation of an object or its 'name' or the integer representation or its
    'code'

    Inherit this class on all enumeration objects and pass it an int_mapping of the structure {'str_name': 'int_value'}
    along with the returned enumeration value
    """

    def __init__(self, value, int_mapping):
        self.str_mapping = {val: key for key, val in int_mapping.items()}
        try:
            value = int(value)
        except ValueError:
            value = value

        if isinstance(value, int):
            self.name = self.str_mapping[value]
            self.code = value
        elif isinstance(value, str):
            self.name = value
            self.code = int_mapping[value]


class AccessType(BaseEnumeration):
    """
    The values below indicate the scope and accessability for the specific variable.
    """

    def __init__(self, value):
        int_mapping = {"abatAT_Public": 1,
                       "abatAT_Private": 2
                       }
        super().__init__(value, int_mapping)


class ObjectType(BaseEnumeration):
    """
    Member                  Value   Description
    abatOT_Job              2       Represents a Job object.
    abatOT_Plan             3       Represents a Plan object.
    abatOT_Queue            4       Represents a Queue object. This includes both execution and generic queue.
    abatOT_Schedule         5       Represents a Schedule object.
    abatOT_Calendar         6       Represents a Calendar object.
    abatOT_UserAccount      7       Represents a User Account object.
    abatOT_ResourceObject   8       Represents a Resource Object.
    abatOT_AlertObject      9       Represents a Alert Object.
    abatOT_Reference        10      Represents a Reference object.
    abatOT_Instance         11      Represents an Instance object.
    abatOT_JobScheduler     12      Represents the Job Scheduler object.
    abatOT_ServiceLibrary   13
    abatOT_Folder           14
    abatOT_GenericQueue     15
    abatOT_ObjectList       16
    """

    def __init__(self, value):
        """
        `value` is an int that corresponds to the member

        Inverted the key-value pair that was specified in the documentation to make the object_mapper easier to
        implement and read. If you are doing any cleanup here, please make sure the object_mapper is taken into
        consideration.

        :param value:
        """

        int_mapping = {'Unknown': 0,
                       'ServiceLibrary': 1,  # ServiceLibrary objects return this value even though it is documented as
                       # an entirely different value; since they are the same, I'm mapping it just as if it were, but
                       # I'm not giving it the same value of 'abatOT_ServiceLibrary' as it is listed in the
                       # documentation--this is to help me figure out what exactly is going on if I choose to test this
                       # in the future See Documentation Errata
                       'abatOT_Job': 2,
                       'abatOT_Plan': 3,  # WARNING both plans and objects return an objecttype of 3 -- errata in the
                       # documentation. per official ActiveBatch knowledgebase, this behavior was fixed starting V10
                       'abatOT_Queue': 4,
                       'abatOT_Schedule': 5,
                       'abatOT_Calendar': 6,
                       'abatOT_UserAccount': 7,
                       'abatOT_ResourceObject': 8,
                       'abatOT_AlertObject': 9,
                       'abatOT_Reference': 10,
                       'abatOT_Instance': 11,
                       'abatOT_JobScheduler': 12,
                       'abatOT_ServiceLibrary': 13,
                       'abatOT_Folder': 14,
                       'abatOT_GenericQueue': 15,
                       'abatOT_ObjectList': 16
                       }
        super().__init__(value, int_mapping)


class AbatObjectsLite(BaseEnumeration):
    def __init__(self, value):
        """
        Member                  Value   Description
        abatISF_NotRun          1       Instance is not running. This is typically an initial state.
        abatISF_Waiting         2       Instance is waiting. See InstanceStateDetail for more information.
        abatISF_Preprocessing   4       Instance is in pre-processing.
        abatISF_Ready           8       Instance is ready to execute.
        abatISF_Executing       16      Instance is executing.
        abatISF_Orphaned        32      Instance is orphaned. This means that the Execution Agent may be disconnected
                                            from the Job Scheduler and a timely status isn't possible at this time.
        abatISF_Active          62      Instance is active.
        abatISF_Aborted         64      Instance has been aborted.
        abatISF_Failed          128     Instance has failed.
        abatISF_Succeeded       256     Instance has succeeded.
        abatISF_Completed       448     Instance has completed.
        abatISF_All             65535   All possible instance states.
        """
        str_mapping = {'abatISF_NotRun': 1,
                       'abatISF_Waiting': 2,
                       'abatISF_Preprocessing': 4,
                       'abatISF_Ready': 8,
                       'abatISF_Executing': 16,
                       'abatISF_Orphaned': 32,
                       'abatISF_Active': 62,
                       'abatISF_Aborted': 64,
                       'abatISF_Failed': 128,
                       'abatISF_Succeeded': 256,
                       'abatISF_Completed': 448,
                       'abatISF_All': 65535
                       }
        super().__init__(value, str_mapping)


class JobSecurityAccess(BaseEnumeration):
    """
    Member                  Value       Description
    abatJSA_ReadVariables   4           May read job variables.
    abatJSA_ReadProperties  2           May read properties of the job.
    abatJSA_Read            6           Read: May read job properties.
    abatJSA_Write           8           Write: May write job properties.
    abatJSA_Modify          14          Modify: May read/write job properties.
    abatJSA_Delete          16          Delete: May delete the job definition.
    abatJSA_Submit          64          Submit: May submit this job to a queue.
    abatJSA_Use             64          Use: May use this object as part or in reference to another.
    abatJSA_Manage          61440       Manage: May issue job operations to this object.
    abatJSA_Executive       3840        Executive: May Take Ownership of this object.
    abatJSA_Trigger         65536       Trigger: May issue a TRIGGER operation on this job.
    abatJSA_TriggerQueue    196608      Trigger Queue: May issue a TRIGGER operation on this job and also direct the job
                                            to a different queue.
    abatJSA_TriggerParams   327680      Trigger Parameters: May issue a TRIGGER operation on this job and change the
                                            job's parameters as part of that trigger.
    abatJSA_TriggerCreds    589824      Trigger Credentials: May issue a TRIGGER operation on this job and change it's
                                            security credentials.
    abatJSA_InstanceCtrl    32505856    Instance Control: User may issue operations which control the instance.
    abatJSA_ChangePerms     256         Change Permissions. User may change the security permissions of this object.
    abatJSA_TakeOwnership   512         Can take ownership of the job.
    abatJSA_FullControl     -1          Full Control. User may issue all possible operations to the object.
    """

    def __init__(self, value):
        int_mapping = {'abatJSA_ReadVariables': 4,
                       'abatJSA_ReadProperties': 2,
                       'abatJSA_Read': 6,
                       'abatJSA_Write': 8,
                       'abatJSA_Modify': 14,
                       'abatJSA_Delete': 16,
                       # yet another questionable design choice by ActiveBatch, Submit and Use are functionally the same
                       # and share the same key for whatever reason, Use will always take precedence; might be that one
                       # code is already being used by some other function call and they decided to just not change
                       # anything and make 2 codes that are functionally the same--I think it's stupid and lazy
                       'abatJSA_Submit': 64,
                       'abatJSA_Use': 64,
                       'abatJSA_Manage': 61440,
                       'abatJSA_Executive': 3840,
                       'abatJSA_Trigger': 65536,
                       'abatJSA_TriggerQueue': 196608,
                       'abatJSA_TriggerParams': 327680,
                       'abatJSA_TriggerCreds': 589824,
                       'abatJSA_InstanceCtrl': 32505856,
                       'abatJSA_ChangePerms': 256,
                       'abatJSA_TakeOwnership': 512,
                       'abatJSA_FullControl': -1
                       }
        super().__init__(value, int_mapping)


class ScheduleDaySpecType(BaseEnumeration):
    """
    This corresponds to what type of runtime the job has

    Member              Value       Description
    abatSDST_None       0           Reserved.
    abatSDST_Daily      1           Daily. Computation is in days.
    abatSDST_Weekly     2           Weekly. Computation is by day of week and number of weeks.
    abatSDST_Monthly    3           Monthly.
    abatSDST_Yearly     4           Yearly.
    abatSDST_Quarterly  5           Quarterly.
    abatSDST_Custom     6           Custom supports Date Arithmetic tags for date computation.

    """

    def __init__(self, value):
        int_mapping = {'abatSDST_None': 0,
                       'abatSDST_Daily': 1,
                       'abatSDST_Weekly': 2,
                       'abatSDST_Monthly': 3,
                       'abatSDST_Yearly': 4,
                       'abatSDST_Quarterly': 5,
                       'abatSDST_Custom': 6
                       }
        super().__init__(value, int_mapping)


class ScheduleTimeSpecType(BaseEnumeration):
    """
    Member                  Value   Description
    abatSTST_HoursMinutes   1       Hours and Minutes. Values are used as a union to produce times.
    abatSTST_ExactTimes     2       Exact Times. A list of specific times.
    abatSTST_Every          3       Every. Every "n" minutes, where the "n" is also an integral value of a 0 to 59
                                    minute hour. For example, every 10 minutes means 0,10,20,30,40,50 regardless of
                                    when the schedule was created.

    """

    def __init__(self, value):
        int_mapping = {'abatSTST_HoursMinutes': 1,
                       'abatSTST_ExactTimes': 2,
                       'abatSTST_Every': 3
                       }
        super().__init__(value, int_mapping)


class ScheduleMonthlyType(BaseEnumeration):
    """"""

    def __init__(self, value):
        int_mapping = {'abatSMT_Day': 1,
                       'abatSMT_Nth': 2,
                       'abatSMT_Series': 3
                       }
        super().__init__(value, int_mapping)


class ScheduleInstanceDay(BaseEnumeration):
    """"""

    def __init__(self, value):
        int_mapping = {'abatSID_WeekendDay': 0,
                       'abatSID_Sunday': 1,
                       'abatSID_Monday': 2,
                       'abatSID_Tuesday': 3,
                       'abatSID_Wednesday': 4,
                       'abatSID_Thursday': 5,
                       'abatSID_Friday': 6,
                       'abatSID_Saturday': 7,
                       'abatSID_Day': 8,
                       'abatSID_WeekDay': 9
                       }
        super().__init__(value, int_mapping)

        # TODO do not handle this on the enumeration module, build a utilities module instead
        self.value = re.search(r'.*_(\w+)', self.name).group(1)


class ScheduleInstanceType(BaseEnumeration):
    """"""

    def __init__(self, value):
        int_mapping = {'abatSIT_First': 1,
                       'abatSIT_Second': 2,
                       'abatSIT_Third': 3,
                       'abatSIT_Fourth': 4,
                       'abatSIT_Last': 5,
                       }
        super().__init__(value, int_mapping)

        # TODO do not handle this on the enumeration module, build a utilities module instead
        self.value = re.search(r'.*_(\w+)', self.name).group(1)


class ScheduleDays(BaseEnumeration):
    """The values below represent a bitmask of dates which are considered business days.
    This is a bitmask, so to make it easier on myself I've added methods for returning a list of days that correspond to
    the value passed to this class
    """

    def __init__(self, value):
        int_mapping = {'abatSD_Sunday': 1,
                       'abatSD_Monday': 2,
                       'abatSD_Tuesday': 4,
                       'abatSD_Wednesday': 8,
                       'abatSD_Thursday': 16,
                       'abatSD_Friday': 32,
                       'abatSD_Saturday': 64,

                       }
        super().__init__(value, int_mapping)

        # TODO do not handle this on the enumeration module, build a utilities module instead
        def __str_days():
            _bin = bin(value)  # this is a str (e.g. 38 = '0b100110')
            _binary_list = [int(i) for i in _bin[2:]]
            _binary_list.reverse()  # reverse to get big endian
            _decimals = []
            for idx, val in enumerate(_binary_list, 0):
                if val:
                    _decimals.append(int(2 ** idx))

            _return = []
            for _dec in _decimals:
                _return.append(super().str_mapping[_dec])
            return _return

        def __int_days(list_of_days):
            _return = []
            for day in list_of_days:
                _return.append(int_mapping[day])
            return _return

        self.str_days = __str_days()
        self.int_days = __int_days(self.str_days)


class CalendarTypes(BaseEnumeration):
    def __init__(self, value):
        int_mapping = {'abatCAT_Calendar': 1,
                       'abatCAT_FiscalCalendar': 2,
                       'abatCAT_BusinessCalendar': 3
                       }
        super().__init__(value, int_mapping)
