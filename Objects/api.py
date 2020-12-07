import inspect
import logging
import re
from datetime import datetime, timedelta
from typing import Union

from pythoncom import com_error  # NOTE: ignore IDE errors as this exception class is dynamically created by Win32 COM

import Objects.abat_collections as ab_col
import Objects.enumerations as enum


class Decorators:
    """
    These decorators provide powerful dynamic handling of function calls for logging and method resolution
    purposes
    """

    @staticmethod
    def runnable(ab_classes: list):
        """
        This decorator is used to determine which classes can run a particular method. Decorate all methods in
        AllMethods with @Decorators.runnable, all attributes in AllAttributes with @property and @Decorators.runnable,
        and specify inside a list of the names of the classes that can access the method or the name of a single class
        that can run it

        If 'All' (case-sensitive) is added to @Decorators.runnable, then it takes precedence over everything else and
        will attempt to run that method. If it is unsupported, an exception will be thrown by the COM

        Returns '-1' if the method is unsupported by the class calling it

        Raises a COM Exception if a method is called but COM cannot invoke that particular method. The reason for this
        is that ActiveBatch's documentation has discrepancies and errata that are not properly documented. Some methods
        that are listed as supported are in fact unsupported, so calling the method results in an exception

        This is sort of a lazy way to do it tbh. I just needed a quick way to prototype some tools that I had in mind
        without having to be so strict about the classes and their methods. It would have been ideal if I could parse
        the CHM documentation so I wouldn't have to type so much because I can autogenerate the code (to an extent)
        using the documentation. This way I can at least start using a particular class's methods easily, quickly, and
        in a way that's reusable and (relatively) easy to manage

        As a bonus, this whole wrapper can also serve as the logging facility for all the method calls and can be used
        to wrap around and handle exceptions raised by the COM
        """

        def decorator(wrapped):
            def wrapper(self, *args, **kwargs):
                __instance = self.cls
                __funcname = wrapped.__name__
                __clsname = type(__instance).__name__
                if 'All' in ab_classes or __clsname in ab_classes:
                    _sig = inspect.signature(wrapped)
                    _binding = _sig.bind(self, *args, **kwargs)
                    _arguments = _binding.arguments
                    _argdict = dict(_arguments)
                    try:
                        _result = wrapped(self, *args, **kwargs)
                        return _result
                    except AttributeError as e:
                        logging.warning(f"AttributeError was raised when calling {__funcname} using the args "
                                        f"{_argdict}")
                        logging.exception(e, exc_info=True)
                        raise
                    except com_error as e:
                        _msg = f"A COM error was encountered when attempting to run the <{__funcname}> method of the " \
                               f"<{__clsname}> class with the arguments {_argdict}. The error message is " \
                               f"'{e.args[2][2]}'"
                        logging.error(_msg)
                        logging.exception(e, exc_info=True)
                        raise
                    except Exception as e:
                        logging.exception(e, exc_info=True)
                        raise
                else:
                    msg = f"Unsupported method <{__funcname}> for class <{__clsname}>. <{__funcname}> can " \
                          f"only be invoked by the following classes: {', '.join(ab_classes)}"
                    try:
                        raise AttributeError(msg)
                    except AttributeError:
                        logging.warning(msg)
                        raise

            return wrapper

        return decorator


class AllAttributes(object):
    def __init__(self, cls, obj):
        self.cls = cls
        self.obj = obj

    @staticmethod
    def normalize_date(date):
        date = date.__str__()  # convert into a parsable string representation
        date = date[:19]  # trim the timezone portion of the datetime string
        date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')  # convert to python native datetime object
        return date

    @property
    @Decorators.runnable('All')
    def ObjectType(self):
        # TODO return an Auditing collection object
        return type(self.cls).__name__

    @property
    @Decorators.runnable('All')
    def Auditing(self):
        # TODO return an Auditing collection object
        return self.obj.Auditing

    @property
    @Decorators.runnable('All')
    def Defaults(self):
        # TODO return a Defaults collection object
        return self.obj.Defaults

    @property
    @Decorators.runnable('All')
    def Path(self):
        return self.obj.Path

    @property
    @Decorators.runnable('All')
    def FullPath(self):
        return self.obj.FullPath

    @property
    @Decorators.runnable('All')
    def GlobalDisable(self):
        return self.obj.GlobalDisable

    @property
    @Decorators.runnable('All')
    def ID(self):
        return self.obj.ID

    @property
    @Decorators.runnable(
        ['ObjectLite', 'CalendarLite', 'QueueLite', 'UserAccountLite', 'FolderLite', 'AbatReferenceLite',
         'IAbatObjectLite', 'JobLite', 'PlanLite', 'ResourceLite', 'ObjectListLite', 'ServiceLibraryLite',
         'ScheduleLite']
    )
    def IsDeleted(self):
        # this seems to be unsupported; entries for IsDeleted have a red symbol on the documentation and invoking it
        # causes a COM exception even for classes where it is specified as a public member
        return self.obj.IsDeleted

    @property
    @Decorators.runnable(['Job'])
    def QueueObjectID(self):
        return self.obj.QueueObjectID

    @property
    @Decorators.runnable('All')
    def Label(self):
        return self.obj.Label

    @property
    @Decorators.runnable('All')
    def Name(self):
        return self.obj.Name

    @property
    @Decorators.runnable('CalendarLite')
    def NextDate(self):
        return self.obj.NextDate

    @property
    @Decorators.runnable('All')
    def Owner(self):
        return self.obj.Owner

    @property
    @Decorators.runnable('All')
    def ParentID(self):
        return self.obj.ParentID

    @property
    @Decorators.runnable('All')
    def RevisionID(self):
        return self.obj.RevisionID

    @property
    @Decorators.runnable('All')
    def Tags(self):
        return self.obj.Tags

    @property
    @Decorators.runnable(['Schedule'])
    def CalendarType(self):
        cal_type = enum.CalendarTypes(self.obj.CalendarType)
        return cal_type.name

    @property
    @Decorators.runnable('All')
    def CreationDateTime(self):
        _creation = self.normalize_date(self.obj.CreationDateTime)  # convert into a parsable string representation
        return _creation

    @property
    @Decorators.runnable(['Job', 'JobLite', 'Plan', 'Reference'])
    def EnableActiveBatchEventTriggers(self) -> bool:
        return self.obj.EnableActiveBatchEventTriggers

    @property
    @Decorators.runnable('All')
    def Enabled(self) -> bool:
        return self.obj.Enabled

    @property
    @Decorators.runnable(['Job', 'JobLite', 'Plan', 'Reference'])
    def EnableEventTriggers(self) -> bool:
        return self.obj.EnableEventTriggers

    @property
    @Decorators.runnable(['Job', 'JobLite'])
    def EnableRunImmediately(self) -> bool:
        return self.obj.EnableRunImmediately

    @property
    @Decorators.runnable(['Job', 'JobLite', 'Plan', 'Reference'])
    def EnableTimerTriggers(self) -> bool:
        return self.obj.EnableTimerTriggers

    @property
    @Decorators.runnable(['JobLite', 'JobHistoryInstance'])
    def ExecutionDateTime(self):
        return self.obj.ExecutionDateTime

    @property
    @Decorators.runnable(['Plan', 'PlanLite', 'Job', 'JobLite', 'ReferenceLite'])
    def LastInstanceExecutionDateTime(self):
        _last = self.normalize_date(self.obj.LastInstanceExecutionDateTime)
        return _last

    @property
    @Decorators.runnable(['PlanLite', 'Job', 'JobLite', 'ReferenceLite'])
    def NextScheduledExecutionDateTime(self):
        _next = self.normalize_date(self.obj.NextScheduledExecutionDateTime)
        return _next

    @property
    @Decorators.runnable(['Job'])
    def EnableLogging(self):
        return self.obj.EnableLogging

    @property
    @Decorators.runnable(['Job'])
    def RetainLogFileDuration(self):
        return self.obj.RetainLogFileDuration

    @property
    @Decorators.runnable(['Job'])
    def LoggingMethod(self):
        return self.obj.LoggingMethod

    @property
    @Decorators.runnable(['Job'])
    def SaveJobHistoryDuration(self):
        return self.obj.SaveJobHistoryDuration


class AllMethods:
    """
    AllMethods contains all the methods for every class in ActiveBatch. Whether they can be used or not is dictated by
    the @Decorators.runnable decorator attached to each method. If the class inheriting AllMethods is included in
    @Decorators.runnable, then that class can access the method, otherwise a warning is displayed and -1 is returned

    For example:
    abat_obj = <class 'Objects.api.Schedule'>

    abat_obj.Disconnect() - will return a message indicating that the particular method is not runnable by the Schedule
    class

    """

    def __init__(self, cls, obj):
        self.cls = cls
        self.obj = obj

    @staticmethod
    def now(days=0.0, seconds=0.0, microseconds=0.0, milliseconds=0.0, minutes=0.0, hours=0.0, weeks=0.0):
        """This is analogous to a GETDATE(). Passing an integer to the parameters causes the function to perform a
        timedelta using the given parameter. For example, calling self.now(days=1) calculates now minus 1 day"""
        _now = datetime.now()
        _fmt = '%Y/%m/%d %H:%M:%S'
        _delta = timedelta(days,
                           seconds,
                           microseconds,
                           milliseconds,
                           minutes,
                           hours,
                           weeks
                           )
        _now -= _delta
        return _now.strftime(_fmt)

    @Decorators.runnable('JobScheduler')
    def Connect(self, Job_Scheduler: str, Username: str = '', Password: str = '', SavePassword: str = False):
        """This is the first step of every connection"""
        self.obj.Connect(JobScheduler=Job_Scheduler, Username=Username, Password=Password, SavePassword=SavePassword)

    @Decorators.runnable('JobScheduler')
    def Disconnect(self):
        self.obj.Disconnect()

    @Decorators.runnable('All')
    def Delete(self, ForceDelete: bool = False):
        self.obj.Delete(ForceDelete=ForceDelete)

    @Decorators.runnable('All')
    def DeleteEx(self, ForceDelete: bool = False, PermenentlyDelete: bool = False):
        self.obj.DeleteEx(ForceDelete=ForceDelete, PermenentlyDelete=PermenentlyDelete)

    @Decorators.runnable('All')
    def Disable(self):
        logging.info(f'disabling [{self.obj.Name} : {self.obj.ID}]')
        self.obj.Disable()

    @Decorators.runnable('All')
    def Enable(self):
        logging.info(f'enabling [{self.obj.Name} : {self.obj.ID}]')
        self.obj.Enable()

    @Decorators.runnable('All')
    def RefreshData(self):
        self.obj.RefreshData()

    @Decorators.runnable('All')
    def GetAssociations(self, ObjectLiteFilter: int = 65535):
        """Defaults to 65535 which is all objects. Refer to AbatObjectsLite in enumerations"""
        return self.obj.GetAssociations(ObjectLiteFilter=ObjectLiteFilter)

    @Decorators.runnable('All')
    def GetAuditsEx(self, StartDateTime='', EndDateTime='', Count=''):
        return self.obj.GetAuditsEx(StartDateTime=StartDateTime, EndDateTime=EndDateTime, Count=Count)

    @Decorators.runnable('All')
    def PurgeObject(self, option):
        """Stumped on this, documentation gives no clue as to what 'option' even is"""
        self.obj.PurgeObject(option=option)

    @Decorators.runnable('All')
    def RestoreObject(self, RevisionID: int):
        self.obj.RestoreObject(RevisionID=RevisionID)

    @Decorators.runnable(['Plan', 'PlanLite', 'Folder', 'FolderLite', 'JobScheduler'])
    def AddObject(self, *args, **kwargs):
        # TODO found a potential bug with the interaction of AddObject and non-collection objects
        # found that the system doesn't stop you from placing a plan or folder inside of a job object
        # this causes the job object to be invisible on the frontend
        return self.obj.AddObject(*args, **kwargs)

    @Decorators.runnable(['Plan', 'PlanLite', 'Folder', 'FolderLite', 'JobScheduler'])
    def CreateObject(self, ObjectName: str):
        self.obj.CreateObject(ObjectName=ObjectName)

    @Decorators.runnable(['Plan', 'PlanLite', 'Queue', 'QueueLite', 'Reference', 'ReferenceLite', 'Job', 'JobLite'])
    def FlushInstances(self):
        return self.obj.FlushInstances()

    @Decorators.runnable(['JobScheduler'])
    def GetObjectType(self, ObjectKey):
        __version = self.cls.version
        __server = self.cls.server
        __otype = self.obj.GetObjectType(ObjectKey)

        # this entire block is a quick fix for the errant behavior in the GetObjectType method of the JobScheduler class
        if __version <= 9:
            if __otype == 3:  # only Folders and Plans return this type (in versions > 10)
                __obj = self.cls.GetAbatObject(ObjectKey)
                __dict = {'FullPath': __obj.FullPath, 'ID': __obj.ID}
                logging.warning(f"\n\n\tERRATA WARNING: The ActiveBatch documentation classifies Plans as an "
                                f"ObjectType '3' and Folders as an ObjectType '14', but the actual observed behavior "
                                f"is that these two objects return the same type '3'."
                                f"\n\tPer the official ActiveBatch "
                                f"knowledgebase, this is a known issue and has been fixed in V10 and above, but since "
                                f"you are connecting to an ActiveBatch version {__version} on the server "
                                f"'{__server}', please be mindful of this discrepancy."
                                f"\n\tI have done my best to try to infer the correct type of the object by "
                                f"attempting to query its attributes through the COM."
                                f"\n\tThis patch works quite well and will only be performed if the version of "
                                f"Activebatch you're connecting to is 9 or lower."
                                f"\n\n\tThis warning was raised by the GetObjectType method when calling it on the "
                                f"object {__dict}\n"
                                )
                # trying my best to infer the proper type by looking at which attribute calls throw an exception
                try:
                    _ = __obj.DisableTemplateOnError  # only Plans and Jobs have this attribute
                    return 3
                except AttributeError:
                    try:
                        # only Plans and Folders have this attribute, but if the check preceding this fails and this
                        # current check passes, then it has to be a Folder, else it's an unknown object so re-raise
                        _ = __obj.ReplacePermissionsOnChildObjects
                        return 14
                    except AttributeError as e:
                        logging.error('FATAL ERROR occured inside the version checking section of the runnable '
                                      'decorator')
                        logging.exception(e, exc_info=True)
                        raise
            else:
                return self.obj.GetObjectType(ObjectKey)

        # if version >= 10, then perform normal operation
        return self.obj.GetObjectType(ObjectKey)

    @Decorators.runnable(
        ['AlertObjectLite', 'Calendar', 'Folder', 'JobScheduler', 'Plan', 'PlanLite', 'QueueLite', 'ReferenceLite',
         'ResourceLite', 'ScheduleLite', 'UserAccountLite', 'FolderLite', 'JobLite', 'ObjectListLite',
         'ServiceLibraryLite'
         ]
    )
    def GetAbatObject(self, *args, **kwargs):
        return self.obj.GetAbatObject(*args, **kwargs)

    @Decorators.runnable('JobScheduler')
    def GetAbatObjectLite(self, *args, **kwargs):
        return self.obj.GetAbatObjectLite(*args, **kwargs)

    @Decorators.runnable(['JobScheduler', 'Job', 'Plan', 'Queue', 'Reference'])
    def GetAlertsEx(self):
        return ab_col.JobAlerts(self.obj.GetAlertsEx())

    @Decorators.runnable(['Job', 'Plan', 'Queue', 'Reference'])
    def GetAssociatedAlertObjects(self):
        return ab_col.AlertObjects(self.obj.GetAssociatedAlertObjects())

    @Decorators.runnable(['Job', 'Plan', 'Reference', 'Schedule'])
    def GetAssociatedCalendarsObjectId(self):
        return ab_col.AbatObjectIDs(self.obj.GetAssociatedCalendarsObjectId())

    @Decorators.runnable(['Job', 'Plan', 'Reference'])
    def GetAssociatedSchedules(self):
        """It is documented to return an AbatSchedules collection object, however no documentation exists of that
        particular object, returning a list just for ease"""
        # TODO revisit before finalizing to determine what to do with this undocumented collections object
        # created my own SchedulesCollection class to deal with this
        try:
            _schedules = ab_col.ScheduleCollection(self.obj.GetAssociatedSchedules())
        except AttributeError:
            _schedules = []
        return _schedules

    @Decorators.runnable(['Job', 'Plan', 'Reference'])
    def GetAssociatedSchedulesObjectId(self):
        return ab_col.AbatObjectIDs(self.obj.GetAssociatedSchedulesObjectId())

    @Decorators.runnable(['Job', 'Plan', 'Reference'])
    def GetBatchStarts(self):
        return self.obj.GetBatchStarts()

    @Decorators.runnable('Plan')
    def GetCompletionRules(self):
        # TODO returns a PlanCompletionRules collection object
        return self.obj.GetCompletionRules()

    @Decorators.runnable(
        ['Plan', 'PlanLite', 'JobScheduler', 'Queue', 'QueueLite', 'Reference', 'ReferenceLite', 'Job', 'JobLite',
         'RecycleBin']
    )
    def GetCounters(self):
        # TODO returns a Counters collection object
        return self.obj.GetCounters()

    @Decorators.runnable(['Job', 'Plan', 'Reference', 'JobScheduler'])
    def GetDependencies(self):
        return self.obj.GetDependencies()

    @Decorators.runnable(['Job', 'Plan', 'Reference'])
    def GetEventTriggers(self):
        return self.obj.GetEventTriggers()

    @Decorators.runnable(['Job', 'Plan', 'Reference'])
    def GetExclusionList(self):
        return self.obj.GetExclusionList()

    @Decorators.runnable('Plan')
    def GetJobPolicy(self):
        return self.obj.GetJobPolicy()

    @Decorators.runnable(['Plan', 'JobScheduler', 'Folder', 'FolderLite', 'RecycleBin'])
    def GetObjectsLite(self, Filter: int = 65535):
        """Refer to ObjectLiteFilter on the ActiveBatch documentation"""
        _obj_collection = ab_col.ObjectsLite(self.obj.GetObjectsLite(Filter))
        return _obj_collection

    @Decorators.runnable(
        ['Plan', 'Folder', 'JobScheduler', 'AlertObject', 'Calendar', 'IAbatObject', 'Job', 'ObjectList', 'Queue',
         'Reference', 'ResourceObject', 'Schedule', 'ServiceLibrary', 'tag', 'UserAccount']
    )
    def GetSecurityAccounts(self):
        # TODO returns a collection of SecurityAccounts, create a SecurityAccounts class and have this method return a
        # TODO list of those objects instead
        return self.obj.GetSecurityAccounts()

    @Decorators.runnable(['Plan', 'Folder', 'JobScheduler', 'Job', 'JobHistory', 'Queue', 'Reference', 'UserAccount'])
    def GetVariables(self):
        # TODO returns a collection of Variables, create a Variables class and have this method return a
        # TODO list of those objects instead
        return self.obj.GetVariables()

    @Decorators.runnable(
        ['Plan', 'Folder', 'AlertObject', 'Calendar', 'IAbatObject', 'Job', 'ObjectList', 'Queue', 'Reference',
         'ResourceObject', 'Schedule', 'ServiceLibrary', 'UserAccount']
    )
    def HasPermission(self, PermissionMask: int) -> bool:
        return self.obj.HasPermission(PermissionMask)

    @Decorators.runnable(
        ['Plan', 'Folder', 'JobScheduler', 'AlertObject', 'Calendar', 'IAbatObject', 'Job', 'ObjectList', 'Queue',
         'Reference', 'ResourceObject', 'Schedule', 'ServiceLibrary', 'UserAccount']
    )
    def IsDirty(self) -> bool:
        return self.obj.IsDirty()

    @Decorators.runnable(['Plan', 'PlanLite', 'Folder', 'FolderLite'])
    def IsPublished(self) -> bool:
        return self.obj.IsPublished()

    @Decorators.runnable(['Plan', 'PlanLite', 'Folder', 'FolderLite'])
    def Publish(self,
                Name: str,
                Description: str
                ):
        self.obj.Publish(Name, Description)

    @Decorators.runnable(['Plan', 'PlanLite', 'Reference', 'ReferenceLite', 'Job', 'JobLite', 'MonitoringProps'])
    def ResetAverage(self):
        self.obj.ResetAverage()

    @Decorators.runnable(['Queue', 'QueueLite', 'Plan', 'PlanLite', 'Reference', 'ReferenceLite', 'Job', 'JobLite'])
    def ResetCounters(self):
        self.obj.ResetCounters()

    @Decorators.runnable(['Folder', 'FolderLite', 'Plan', 'PlanLite'])
    def TakeOwnership(self):
        self.obj.TakeOwnership()

    @Decorators.runnable(
        ['Folder', 'JobScheduler', 'Policy', 'AlertObject', 'Calendar', 'IAbatObject', 'Job', 'JobHistoryInstance',
         'ObjectList', 'Plan', 'Queue', 'Reference', 'ResourceObject', 'Schedule', 'ServiceLibrary', 'UserAccount']
    )
    def Unpublish(self):
        self.obj.Unpublish()

    @Decorators.runnable(
        ['Folder', 'JobScheduler', 'Policy', 'AlertObject', 'Calendar', 'IAbatObject', 'Job', 'JobHistoryInstance',
         'ObjectList', 'Plan', 'Queue', 'Reference', 'ResourceObject', 'Schedule', 'ServiceLibrary', 'UserAccount']
    )
    def Update(self):
        self.obj.Update()

    @Decorators.runnable(
        ['JobScheduler', 'Plan', 'PlanLite', 'Queue', 'QueueLite', 'Reference', 'ReferenceLite', 'Job', 'JobLite']
    )
    def UpdateCounters(self):
        self.obj.UpdateCounters()

    @Decorators.runnable(['AlertObject', 'Calendar', 'ObjectList', 'Schedule', 'UserAccount'])
    def GetAssociatedJobs(self):
        return ab_col.AbatVariantItems(self.obj.GetAssociatedJobs())

    @Decorators.runnable('Schedule')
    def GetExactDates(self):
        _collection = self.obj.GetExactDates()
        return ab_col.AbatVariantItems(_collection)

    @Decorators.runnable('Schedule')
    def GetScheduledDates(self, StartDate, EndDate):
        _collection = self.obj.GetScheduledDates(StartDate=StartDate, EndDate=EndDate)
        return ab_col.AbatVariantItems(_collection)

    @Decorators.runnable('Schedule')
    def TimeSpec_GetExactTimes(self):
        _collection = self.obj.TimeSpec_GetExactTimes()
        return ab_col.AbatVariantItems(_collection)

    @Decorators.runnable(['Plan', 'PlanLite', 'Job', 'JobLite', 'Reference', 'ReferenceLite'])
    def Trigger3(self,
                 QueueName: str = '',
                 JobParameters: str = '',
                 Flags: int = 0,
                 Username: str = '',
                 Password: str = '',
                 Variables: object = '',
                 Reserved: str = ''
                 ):
        """
        Major disclaimer. ActiveBatch apparently CANNOT agree on parameter defaults. Be mindful of how you are passing
        params. Refer to this implementation in the future if you have trouble with other class methods especially if
        they take any parameters

        Syntax is very finnicky. Flags have to be int, Variables have to be object, else string. Cannot default to just
        NoneType objects

        :param QueueName:
        :param JobParameters:
        :param Flags:
        :param Username:
        :param Password:
        :param Variables:
        :param Reserved:
        :return:
        """
        # TODO add all parameters from doc
        # TODO variables have to be passed as a variable collection, need to implement an easy variable collection that
        # TODO adheres to ActiveBatch's requirements
        # TODO as of right now, this has no way of actually accepting proper variables
        # TODO grab variable collection creator in previous iteration of the AB API code for guidance
        self.obj.Trigger3(QueueName=QueueName,
                          JobParameters=JobParameters,
                          Flags=Flags,
                          Username=Username,
                          Password=Password,
                          Variables=Variables,
                          Reserved=Reserved
                          )

    @Decorators.runnable(['Folder', 'FolderLite'])
    def GetChildInstances(self, Count: int = '', InstanceStateFilter: int = '', ShowOldestFirst: bool = False,
                          StartDateTime: str = '', EndDateTime: str = ''):
        return self.obj.GetChildInstances(Count=Count,
                                          InstanceStateFilter=InstanceStateFilter,
                                          ShowOldestFirst=ShowOldestFirst,
                                          StartDateTime=StartDateTime,
                                          EndDateTime=EndDateTime
                                          )

    @Decorators.runnable(['Folder', 'IAbatObject', 'Job', 'ServiceLibrary'])
    def IsPropertyLocked(self, PropertyName: str):
        return self.obj.IsPropertyLocked(PropertyName)

    @Decorators.runnable(['JobScheduler', 'PlanLite', 'QueueLite', 'ReferenceLite', 'JobLite', 'Job'])
    def GetInstances(self, Count: int = 100, InstanceStateFilter: int = 65535, ShowOldestFirst=True,
                     StartDateTime: str = None, EndDateTime: str = None):

        if EndDateTime is None:
            _endDateTime = self.now()
        else:
            _endDateTime = EndDateTime

        if StartDateTime is None:
            _startDateTime = self.now(-365)
        else:
            _startDateTime = StartDateTime

        _instances = self.obj.GetInstances(Count, InstanceStateFilter, ShowOldestFirst, _startDateTime, _endDateTime)
        _objects = ab_col.ObjectsLite(_instances)
        # _results = [self.cls.get_object(_object.ID) for _object in _objects]
        return _objects

    @Decorators.runnable(['Folder', 'IAbatObject', 'Job', 'ServiceLibrary'])
    def IsPropertyLocked(self, PropertyName: str):
        return self.obj.IsPropertyLocked(PropertyName)

    def _create_intermediate_folders(self, DestinationKey):
        def which_exists():
            assert isinstance(DestinationKey, str)
            try:
                d_key = int(DestinationKey)
                logging.warning(f"The provided DestinationKey {DestinationKey} is not compatible with "
                                f"create_if_not_exists option.")
                return {d_key: (self.ObjectExists(d_key), None)}
            except ValueError:
                d_key = DestinationKey

            paths = []
            path_components = d_key.split('/')
            for idx in range(len(path_components)):
                if idx == 0:
                    continue
                if idx == 1:
                    _currpath = '/'
                else:
                    _currpath = '/'.join(path_components[:idx + 1])

                _label = path_components[idx]
                _parent = '/'.join(path_components[:idx])
                _exists = self.ObjectExists(_currpath)
                _dict = {'key': _currpath, 'parent': _parent, 'exists': _exists,
                         'label': _label}
                paths.append(_dict)

            return paths

        for item in which_exists():
            __key, __exists, __label, __parent = item['key'], item['exists'], item['label'], item['parent']
            if not __exists:
                logging.info(f'Creating {__key}')
                folder_obj = self.CreateObject(ObjectName='Folder')
                folder_obj.Label = __label
                folder_obj.Name = __label
                logging.debug(f"Adding '{__key}' to path '{__parent}'")
                self.AddObject(__parent, folder_obj)

    @Decorators.runnable(['JobScheduler'])
    def MoveObject(self, SourceKey: Union[int, str], DestinationKey: Union[int, str]):
        self.obj.MoveObject(SourceKey=SourceKey, DestinationKey=DestinationKey)

    @Decorators.runnable(['JobScheduler'])
    def MoveObjectTo(self, SourceKey: Union[int, str], DestinationKey: Union[int, str], create_if_not_exists=False):
        """

        Args:
            SourceKey - path of object (string), id of object (int) or id of object (string)
            DestinationKey - path of object (string), id of object (int) or id of object (string)
            create_if_not_exists - if True, then new folders are created to create the directory structure required
                                 - this only works with string paths and not with any ID (i.e. paths that have not been
                                 created yet, so they don't have IDs yet)
                                 - if create_if_not_exists is True, then all items in the given path must either not
                                 exist or must exist as folders, otherwise it will raise an exception indicating that
                                 an object in the path already exists as a non-folder object

        I've modified this object to only allow moving objects to a Folder and nothing else
        """

        if create_if_not_exists:
            self._create_intermediate_folders(DestinationKey=DestinationKey)

        logging.debug(f"Moving '{SourceKey}' to '{DestinationKey}'")
        destination_type = self.obj.GetObjectType(DestinationKey)
        destination_type = enum.ObjectType(destination_type).name
        # TODO errata - (fixed in V10) plans and folders return the same type as per official ActiveBatch KB
        _isfolder = destination_type in ['abatOT_Folder', 'abatOT_Plan']
        if _isfolder is True:
            self.obj.MoveObject(SourceKey=SourceKey, DestinationKey=DestinationKey)
        else:
            raise ValueError(f"The destination key '{DestinationKey}' is not a folder'")

    @Decorators.runnable(['AlertObject', 'Job', 'ObjectList', 'Schedule'])
    def CopyObject(self):
        # TODO different classes return different objects, need to map to appropriate class when the object is copied
        return self.obj.CopyObject()

    @Decorators.runnable(['JobScheduler'])
    def CopyObjectTo(self, SourceKey: Union[int, str], DestinationKey: Union[int, str], create_if_not_exists=False):
        """
        ActiveBatch has a method called CopyObject that is available for Job, ObjectList and Schedule objects but not
        for Plans, Folders, etc. The most reliable way to perform a full copy is to extract the XML of the source and
        rebuild it in the desired location
        """
        if create_if_not_exists:
            self._create_intermediate_folders(DestinationKey=DestinationKey)

        logging.debug(f"Copying '{SourceKey}' to '{DestinationKey}'")
        destination_type = self.obj.GetObjectType(DestinationKey)
        destination_type = enum.ObjectType(destination_type).name
        # TODO errata - (fixed in V10) plans and folders return the same type as per official ActiveBatch KB
        _isfolder = destination_type in ['abatOT_Folder', 'abatOT_Plan']
        if _isfolder is True:
            # we will need the two objects below to facilitate the importing and exporting of objects in memory
            # the two objects will contain methods that we need to do this properly
            __export = self.obj.CreateObject("Export")  # creating an object of class Export
            __import = self.obj.CreateObject("Import")  # creating an object of class Import
            # now we get the original object
            __obj = self.obj.GetAbatObject(SourceKey)
            # we use the Export method of the Export class to get the XML of the original object
            __export_obj = __export.Export(__obj.ID)
            # we re-import the XML to a different location
            __import.Import(DestinationKey, __export_obj)
        else:
            raise ValueError(f"The destination key '{DestinationKey}' is not a folder'")

    @Decorators.runnable(['JobScheduler'])
    def ObjectExists(self, ObjectKey: Union[int, str]) -> bool:
        return bool(self.obj.ObjectExists(ObjectKey=ObjectKey))

    @Decorators.runnable(['JobScheduler'])
    def CreateObject(self, ObjectName):
        try:
            return self.obj.CreateObject(ObjectName=ObjectName)
        except Exception as e:
            logging.warning(f"{ObjectName} is not a valid ObjectName for this method. Please consult the documentation")
            logging.exception(e, exc_info=True)
            return None

    @Decorators.runnable(['JobScheduler'])
    def Search(self, SearchRootKey: Union[str, int], SearchString: str = '*', ObjectFilter: int = 65535,
               FieldNames: str = 'AllFields', Recursive: bool = True):

        """
        Member Value Description
        abatOLF_Job 1 Include Jobs.
        abatOLF_Plan 2 Include Plan.
        abatOLF_JobAndPlan 3 Include Plan and Job objects.
        abatOLF_ExecutionQueue 4 Include Execution Queues.
        abatOLF_GenericQueue 8 Include Generic Queues.
        abatOLF_Queue 12 Include all Queues.
        abatOLF_Schedule 16 Include Schedules.
        abatOLF_Calendar 32 Include Calendars.
        abatOLF_UserAccount 64 Include User Accounts.
        abatOLF_AlertObject 128 Include Alert Objects.
        abatOLF_ResourceObject 256 Include Resource Objects.
        abatOLF_Reference 512 Include Reference Objects.
        abatOLF_ServiceLibrary 1024
        abatOLF_Folder 2048
        abatOLF_ObjectList 4096
        abatOLF_All 65535 Include all objects.

        :param SearchRootKey:
        :param SearchString:
        :param ObjectFilter:
        :param FieldNames:
        :param Recursive:
        :return:
        """
        _search_results = self.obj.Search(SearchRootKey=SearchRootKey,
                                          SearchString=SearchString,
                                          ObjectFilter=ObjectFilter,
                                          FieldNames=FieldNames,
                                          Recursive=Recursive
                                          )
        _search_results = ab_col.ObjectsLite(_search_results)

        return _search_results


class JobScheduler(AllMethods, AllAttributes):
    """JobScheduler is special since it is technically the 'connection'"""

    def __init__(self, obj, server, version):
        super().__init__(cls=self, obj=obj)
        self.obj = obj
        self.server = server
        self.version = version

    def __repr__(self):
        return f"{self.obj.Name}`{self.ObjectType}"

    def __str__(self):
        return f"{self.obj.Name}"

    def _get_object(self, key, lite=True):
        """
        This is used to easily map an object to its corresponding class in the api module
        Once mapped, the object's methods are exposed for ease of use

        Please consult the documentation for more guidance into the usage of these objects

        :param key:
        :param lite:
        :return:
        """

        if not isinstance(lite, bool):
            raise ValueError

        method_map = {}
        # map the strings to the classes
        if lite is False:
            method_map = {'ServiceLibrary': ServiceLibrary,
                          'abatOT_Job': Job,
                          'abatOT_Plan': Plan,
                          'abatOT_Queue': Placeholder,
                          'abatOT_Schedule': Schedule,
                          'abatOT_Calendar': Calendar,
                          'abatOT_UserAccount': UserAccount,
                          'abatOT_ResourceObject': Placeholder,
                          'abatOT_AlertObject': Alerts,
                          'abatOT_Reference': Placeholder,
                          'abatOT_Instance': Placeholder,
                          'abatOT_JobScheduler': JobScheduler,
                          'abatOT_ServiceLibrary': Placeholder,
                          'abatOT_Folder': Folder,
                          'abatOT_GenericQueue': Placeholder,
                          'abatOT_ObjectList': Placeholder
                          }
        if lite is True:
            method_map = {'ServiceLibrary': ServiceLibrary,
                          'abatOT_Job': JobLite,
                          'abatOT_Plan': PlanLite,
                          'abatOT_Queue': Placeholder,
                          'abatOT_Schedule': ScheduleLite,
                          'abatOT_Calendar': CalendarLite,
                          'abatOT_UserAccount': UserAccount,
                          'abatOT_ResourceObject': Placeholder,
                          'abatOT_AlertObject': AlertsLite,
                          'abatOT_Reference': Placeholder,
                          'abatOT_Instance': Placeholder,
                          'abatOT_JobScheduler': JobScheduler,
                          'abatOT_ServiceLibrary': Placeholder,
                          'abatOT_Folder': FolderLite,
                          'abatOT_GenericQueue': Placeholder,
                          'abatOT_ObjectList': Placeholder
                          }

        objtype = int(self.GetObjectType(key))  # returns an integer
        objname = enum.ObjectType(objtype).name  # maps the integer to a string
        if lite is True:
            obj = self.GetAbatObjectLite(key)
        else:
            obj = self.GetAbatObject(key)

        return method_map[objname](self, obj)

    def Search(self, SearchRootKey: Union[str, int], SearchString: str = '*', ObjectFilter: int = 65535,
               FieldNames: str = 'AllFields', Recursive: bool = True, GetFullObjects: bool = False):
        _search_results = super().Search(SearchRootKey=SearchRootKey, SearchString=SearchString,
                                         ObjectFilter=ObjectFilter, FieldNames=FieldNames, Recursive=Recursive
                                         )
        _items = []
        for item in _search_results:
            if GetFullObjects:
                _item = self.get_object(item.ID, lite=False)
            else:
                _item = self.get_object(item.ID, lite=True)
            _items.append(_item)

        return _items

    def get_object(self, key, lite=True):
        _keys = list()
        logging.debug(f'get_object({key})')
        if isinstance(key, list):
            for item in key:
                if hasattr(item, '_username_'):
                    logging.debug(f'Searching for object ID {item.ID}')
                    _keys.append(self._get_object(item.ID, lite))
                else:
                    _keys.append(self._get_object(item, lite))
        else:
            return self._get_object(key, lite)
        return _keys

    def UndoPendingChanges(self, obj_id):
        self.obj.UndoPendingChanges(obj_id)


class ServiceLibrary(AllMethods, AllAttributes):
    """
    This object type seems to be a hidden system object of sorts. It is undocumented and entirely unaccounted for
    in all of the available documentation. Only found it by chance when doing a brute recursive search on the root
    directory.

    Example ID 795056
    Path /$System/Asci.ActiveBatch.AmazonEc2
    """

    def __init__(self, scheduler, obj):
        super().__init__(cls=self, obj=obj)
        self.scheduler = scheduler
        self.obj = obj
        self.__liteobj = None

    @property
    def LiteObject(self):
        if self.__liteobj is None:
            self.__liteobj = self.scheduler.get_object(self.ID, lite=True)
        return self.__liteobj

    def __repr__(self):
        return f"{self.obj.Name}`{self.ObjectType}"

    def __str__(self):
        return f"{self.obj.Name}"


class Job(AllMethods, AllAttributes):
    def __init__(self, scheduler, obj):
        super().__init__(cls=self, obj=obj)
        self.scheduler = scheduler
        self.obj = obj
        self.__liteobj = None

    @property
    def LiteObject(self):
        if self.__liteobj is None:
            self.__liteobj = self.scheduler.get_object(self.ID, lite=True)
        return self.__liteobj

    def __repr__(self):
        return f"{self.obj.Name}`{self.ObjectType}"

    def __str__(self):
        return f"{self.obj.Name}"


class JobLite(AllMethods, AllAttributes):
    def __init__(self, scheduler, obj):
        super().__init__(cls=self, obj=obj)
        self.scheduler = scheduler
        self.obj = obj
        self.__fullobj = None

    @property
    def FullObject(self):
        if self.__fullobj is None:
            self.__fullobj = self.scheduler.get_object(self.ID, lite=False)
        return self.__fullobj

    def __repr__(self):
        return f"{self.obj.Name}`{self.ObjectType}"

    def __str__(self):
        return f"{self.obj.Name}"


class Alerts(AllMethods, AllAttributes):
    def __init__(self, scheduler, obj):
        super().__init__(cls=self, obj=obj)
        self.scheduler = scheduler
        self.obj = obj
        self.__liteobj = None

    @property
    def LiteObject(self):
        if self.__liteobj is None:
            self.__liteobj = self.scheduler.get_object(self.ID, lite=True)
        return self.__liteobj

    def __repr__(self):
        return f"{self.obj.Name}`{self.ObjectType}"

    def __str__(self):
        return f"{self.obj.Name}"


class AlertsLite(AllMethods, AllAttributes):
    def __init__(self, scheduler, obj):
        super().__init__(cls=self, obj=obj)
        self.scheduler = scheduler
        self.obj = obj
        self.__fullobj = None

    @property
    def FullObject(self):
        if self.__fullobj is None:
            self.__fullobj = self.scheduler.get_object(self.ID, lite=False)
        return self.__fullobj

    def __repr__(self):
        return f"{self.obj.Name}`{self.ObjectType}"

    def __str__(self):
        return f"{self.obj.Name}"


class UserAccount(AllMethods, AllAttributes):
    def __init__(self, scheduler, obj):
        super().__init__(cls=self, obj=obj)
        self.scheduler = scheduler
        self.obj = obj
        self.__liteobj = None

    @property
    def LiteObject(self):
        if self.__liteobj is None:
            self.__liteobj = self.scheduler.get_object(self.ID, lite=True)
        return self.__liteobj

    def __repr__(self):
        return f"{self.obj.Name}`{self.ObjectType}"

    def __str__(self):
        return f"{self.obj.Name}"


class Placeholder(AllMethods, AllAttributes):
    def __init__(self, scheduler, obj):
        super().__init__(cls=self, obj=obj)
        self.scheduler = scheduler
        self.obj = obj
        logging.warning(f"This object type is currently unsupported")

    def __repr__(self):
        return f"{self.obj.Name}`{self.ObjectType}"

    def __str__(self):
        return f"{self.obj.Name}"


class Calendar(AllMethods, AllAttributes):
    def __init__(self, scheduler, obj):
        super().__init__(cls=self, obj=obj)
        self.scheduler = scheduler
        self.obj = obj
        self.__liteobj = None

    @property
    def LiteObject(self):
        if self.__liteobj is None:
            self.__liteobj = self.scheduler.get_object(self.ID, lite=True)
        return self.__liteobj

    def __repr__(self):
        return f"{self.obj.Name}`{self.ObjectType}"

    def __str__(self):
        return f"{self.obj.Name}"


class CalendarLite(AllMethods, AllAttributes):
    def __init__(self, scheduler, obj):
        super().__init__(cls=self, obj=obj)
        self.scheduler = scheduler
        self.obj = obj
        self.__fullobj = None

    @property
    def FullObject(self):
        if self.__fullobj is None:
            self.__fullobj = self.scheduler.get_object(self.ID, lite=False)
        return self.__fullobj

    def __repr__(self):
        return f"{self.obj.Name}`{self.ObjectType}"

    def __str__(self):
        return f"{self.obj.Name}"


class Schedule(AllMethods, AllAttributes):
    def __init__(self, scheduler, obj):
        super().__init__(cls=self, obj=obj)
        self.scheduler = scheduler
        self.obj = obj
        self.__liteobj = None

    @property
    def LiteObject(self):
        if self.__liteobj is None:
            self.__liteobj = self.scheduler.get_object(self.ID, lite=True)
        return self.__liteobj

    def __repr__(self):
        return f"{self.obj.Name}`{self.ObjectType}"

    def __str__(self):
        return f"{self.obj.Name}"

    def _typemapper(self):
        # TODO
        _timetype = enum.ScheduleTimeSpecType(self.obj.TimeSpec_Type).name
        _daytype = enum.ScheduleDaySpecType(self.obj.DaySpec_Type).name

        _daystr = ''
        if _daytype == 'abatSDST_Daily':
            _daystr = self._d_daily()
        elif _daytype == 'abatSDST_Weekly':
            _daystr = self._d_weekly()
        elif _daytype == 'abatSDST_Monthly':
            _daystr = self._d_monthly()
        elif _daytype == 'abatSDST_Yearly':
            _daystr = ''
        elif _daytype == 'abatSDST_Quarterly':
            _daystr = ''

        _timestr = ''
        if _timetype == 'abatSTST_HoursMinutes':
            _timestr = self._t_hoursminutes()
        elif _timetype == 'abatSTST_ExactTimes':
            _timestr = self._t_exacttimes()
        elif _timetype == 'abatSTST_Every':
            _timestr = self._t_every()

        return f"{_daystr}_{_timestr}"

    def _d_daily(self):
        """determine the dayspec portion of the name using a daily configuration"""
        _str = ''
        _interval = self.obj.DaySpec_DailyInterval
        _plural = 'Day' if _interval == 1 else 'Days'  # EveryDay instead of Every1Day - idk just felt like it
        _interval = _interval if _interval != 1 else ''
        return f"Every{_interval}{_plural}"

    def _d_weekly(self):
        """determine the dayspec portion of the name using a weekly configuration"""
        _str = ''
        _dayseries = enum.ScheduleDays(self.obj.DaySpec_WeeklyDaysOfWeek).str_days
        _dayseries_daynames = [re.search('^.*_(\w+)$', x).group(1)[:3] for x in _dayseries]
        _daystrings = ''.join(_dayseries_daynames)
        _interval = self.obj.DaySpec_WeeklyInterval
        _plural = 'Week' if _interval == 1 else 'Weeks'
        _interval = _interval if _interval != 1 else ''  # EveryWeek instead of Every1Week - idk just felt like it
        _str = f'Every{_interval}{_plural}.{_daystrings}'

        return _str

    def _d_monthly(self):
        """determine the dayspec portion of the name using a monthly configuration"""
        _montype = enum.ScheduleMonthlyType(self.obj.DaySpec_MonthlyType).name
        _interval = self.obj.DaySpec_MonthlyInterval
        _plural = 'Month' if _interval == 1 else 'Months'
        _interval = _interval if _interval != 1 else ''  # EveryMonth instead of Every1Month - idk just felt like it
        _str = ''

        def _type_day(_day_of_month_):
            _return = ''
            _day = _day_of_month_
            _daystr = str(_day)[-1]  # get the last digit to figure out its ordinal name
            if _daystr == '1':
                _return = f'Every{_interval}{_plural}.{_day}st'
            elif _daystr == '2':
                _return = f'Every{_interval}{_plural}.{_day}nd'
            elif _daystr == '3':
                _return = f'Every{_interval}{_plural}.{_day}rd'
            else:
                _return = f'Every{_interval}{_plural}.{_day}th'
            return _return

        def _type_nth(_monthly_instance_, _monthly_dayofweek_):
            _instance_type = enum.ScheduleInstanceType(_monthly_instance_).value
            _instance_day = enum.ScheduleInstanceDay(_monthly_dayofweek_).value
            _return = f'Every{_interval}{_plural}.{_instance_type}{_instance_day}'
            return _return

        def _type_series(_day_series_):
            _day_series_ = _day_series_.replace(',', ' ')
            _return = f'Every{_interval}{_plural}.{_day_series_}'
            return _return

        if _montype == 'abatSMT_Day':
            _str = _type_day(self.obj.DaySpec_MonthlyDayOfMonth)
        elif _montype == 'abatSMT_Nth':
            _str = _type_nth(self.obj.DaySpec_MonthlyInstance, self.obj.DaySpec_MonthlyDayOfWeek)
        elif _montype == 'abatSMT_Series':
            _str = _type_series(self.obj.DaySpec_MonthlyDaySeries)
        return _str

    def _t_hoursminutes(self):
        """returns the string value name of the schedule using an 'HoursMinutes' configuration"""
        # pad h/m for 24hr clock (09:01 AM becomes 0901 instead of 91, 10:01 to 1001 instead of 101)
        _h, _m = self.obj.TimeSpec_Hours, self.obj.TimeSpec_Minutes
        return f'{_h:0>2}{_m:0>2}'

    def _t_exacttimes(self):
        """returns the string value name of the schedule using an 'ExactTimes' configuration"""
        _times = self.TimeSpec_GetExactTimes().to_list()
        _strings = []
        for _time in _times:
            _h, _m = _time.DateTime.hour, _time.DateTime.minute
            # pad h/m for 24hr clock (09:01 AM becomes 0901 instead of 91, 10:01 to 1001 instead of 101)
            _strings.append(f"{_h:0>2}{_m:0>2}")
        _str = '_'.join(_strings)
        return _str

    def _t_every(self):
        """returns the string value name of the schedule using an 'Every' configuration"""
        _str = f"Every_{self.obj.TimeSpec_Interval}m"
        return _str

    @property
    def production_name(self):
        """
        returns the production name of the schedule
        """
        # TODO needs to check if a schedule already exists
        # max 128 bytes
        return self._typemapper()

    def productionalize_schedulename(self):
        """This will change the name of the object to its corresponding production name"""
        logging.debug(self.production_name)
        self.obj.Name = self.production_name
        self.obj.Label = self.production_name
        self.obj.Update()


class ScheduleLite(AllMethods, AllAttributes):
    def __init__(self, scheduler, obj):
        super().__init__(cls=self, obj=obj)
        self.scheduler = scheduler
        self.obj = obj
        self.__fullobj = None

    @property
    def FullObject(self):
        if self.__fullobj is None:
            self.__fullobj = self.scheduler.get_object(self.ID, lite=False)
        return self.__fullobj

    def __repr__(self):
        return f"{self.obj.Name}`{self.ObjectType}"

    def __str__(self):
        return f"{self.obj.Name}"


class Plan(AllMethods, AllAttributes):
    def __init__(self, scheduler, obj):
        super().__init__(cls=self, obj=obj)
        self.scheduler = scheduler
        self.obj = obj
        # self._associated_schedules_ = self.GetAssociatedSchedules().to_list()
        self._associated_schedules_ = []
        self.__liteobj = None

    @property
    def LiteObject(self):
        if self.__liteobj is None:
            self.__liteobj = self.scheduler.get_object(self.ID, lite=True)
        return self.__liteobj

    def __getattr__(self, item):
        # the 'lite' `Plan` object contains an attribute that is not available for the 'full' `Plan` object
        # the 'lite' and 'full' `Job` objects on the other hand both share this attribute
        # I have no fucking clue why the brilliant folks over at ASCI decided this was a good design choice
        # In any case, I'm providing a way to override that functionality by making a separate call to get the lite
        # object before querying this attribute
        if item == 'NextScheduledExecutionDateTime':
            return self.LiteObject.NextScheduledExecutionDateTime
        else:
            return self.item

    def __repr__(self):
        return f"{self.obj.Name}`{self.ObjectType}"

    def __str__(self):
        return f'{self.obj.Name}'

    def productionalize_schedulenames(self):
        for _sched in self._associated_schedules_:
            _sched.productionalize_schedulename()

    def production_names(self):
        """
        Returns a dictionary containing the object and its ideal production name. Uses the object's ID as the key

        {id: (obj, prod_name)}
        id - the activebatch object's ID
        obj - the Schedule object
        prod_name - the ideal production name of the object
        """
        _prodnames = {}
        for _sched in self._associated_schedules_:
            _prodnames[_sched.ID] = (_sched, _sched.production_name)
        return _prodnames


class PlanLite(AllMethods, AllAttributes):
    def __init__(self, scheduler, obj):
        super().__init__(cls=self, obj=obj)
        self.scheduler = scheduler
        self.obj = obj
        self.__fullobj = None

    @property
    def FullObject(self):
        if self.__fullobj is None:
            self.__fullobj = self.scheduler.get_object(self.ID, lite=False)
        return self.__fullobj

    def __repr__(self):
        return f"{self.obj.Name}`{self.ObjectType}"

    def __str__(self):
        return f'{self.obj.Name}'


class JobAlert(AllMethods, AllAttributes):
    """IMPORTANT, this class is mentioned in the documentation but not actually documented. I have no idea what this
    class is, putting here just so I can continue writing the code"""

    def __init__(self, scheduler, obj):
        super().__init__(cls=self, obj=obj)
        self.scheduler = scheduler
        self.obj = obj

    def __repr__(self):
        return f"{self.obj.Name}`{self.ObjectType}"

    def __str__(self):
        return f"{self.obj.Name}"


class Folder(AllMethods, AllAttributes):
    def __init__(self, scheduler, obj):
        super().__init__(cls=self, obj=obj)
        self.scheduler = scheduler
        self.obj = obj
        self.__liteobj = None

    @property
    def LiteObject(self):
        if self.__liteobj is None:
            self.__liteobj = self.scheduler.get_object(self.ID, lite=True)
        return self.__liteobj

    def __repr__(self):
        return f"{self.obj.Name}`{self.ObjectType}"

    def __str__(self):
        return f"{self.obj.Name}"


class FolderLite(AllMethods, AllAttributes):
    def __init__(self, scheduler, obj):
        super().__init__(cls=self, obj=obj)
        self.scheduler = scheduler
        self.obj = obj
        self.__fullobj = None

    @property
    def FullObject(self):
        if self.__fullobj is None:
            self.__fullobj = self.scheduler.get_object(self.ID, lite=False)
        return self.__fullobj

    def __repr__(self):
        return f"{self.obj.Name}`{self.ObjectType}"

    def __str__(self):
        return f"{self.obj.Name}"
