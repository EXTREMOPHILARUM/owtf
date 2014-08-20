import os
import json
from framework.lib.exceptions import InvalidParameterType
from framework.db import models


class POutputDB(object):
    def __init__(self, Core):
        self.Core = Core

    def DeriveHTMLOutput(self, plugin_output):
        self.Core.Reporter.Loader.reset()
        Content = ''
        for item in plugin_output:
            Content += getattr(self.Core.Reporter, item["type"])(**item["output"])
        return(Content)

    def DeriveOutputDict(self, obj, target_id=None):
        if target_id:
            self.Core.DB.Target.SetTarget(target_id)
        if obj:
            pdict = dict(obj.__dict__)
            pdict.pop("_sa_instance_state", None)
            # If output is present, json decode it
            if pdict.get("output", None):
                pdict["output"] = self.DeriveHTMLOutput(
                    json.loads(pdict["output"]))
            if pdict.get("date_time", None):
                pdict["date_time"] = pdict["date_time"].strftime(
                    self.Core.DB.Config.Get("DATE_TIME_FORMAT"))
            return pdict

    def DeriveOutputDicts(self, obj_list, target_id=None):
        if target_id:
            self.Core.DB.Target.SetTarget(target_id)
        dict_list = []
        for obj in obj_list:
            dict_list.append(self.DeriveOutputDict(obj, target_id))
        return(dict_list)

    def GenerateQueryUsingSession(self, session, filter_data):
        query = session.query(models.PluginOutput)
        if filter_data.get("plugin_type", None):
            if isinstance(filter_data.get("plugin_type"), (str, unicode)):
                query = query.filter_by(plugin_type=filter_data["plugin_type"])
            if isinstance(filter_data.get("plugin_type"), list):
                query = query.filter(models.PluginOutput.plugin_type.in_(
                    filter_data["plugin_type"]))
        if filter_data.get("plugin_group", None):
            if isinstance(filter_data.get("plugin_group"), (str, unicode)):
                query = query.filter_by(
                    plugin_group=filter_data["plugin_group"])
            if isinstance(filter_data.get("plugin_group"), list):
                query = query.filter(models.PluginOutput.plugin_group.in_(
                    filter_data["plugin_group"]))
        if filter_data.get("plugin_code", None):
            if isinstance(filter_data.get("plugin_code"), (str, unicode)):
                query = query.filter_by(plugin_code=filter_data["plugin_code"])
            if isinstance(filter_data.get("plugin_code"), list):
                query = query.filter(models.PluginOutput.plugin_code.in_(
                    filter_data["plugin_code"]))
        if filter_data.get("status", None):
            if isinstance(filter_data.get("status"), (str, unicode)):
                query = query.filter_by(status=filter_data["status"])
            if isinstance(filter_data.get("status"), list):
                query = query.filter(models.PluginOutput.status.in_(
                    filter_data["status"]))
        try:
            if filter_data.get("user_rank", None):
                if isinstance(filter_data.get("user_rank"), (str, unicode)):
                    query = query.filter_by(
                        user_rank=int(filter_data["user_rank"]))
                if isinstance(filter_data.get("user_rank"), list):
                    numbers_list = [int(x) for x in filter_data["user_rank"]]
                    query = query.filter(models.PluginOutput.user_rank.in_(
                        numbers_list))
            if filter_data.get("owtf_rank", None):
                if isinstance(filter_data.get("owtf_rank"), (str, unicode)):
                    query = query.filter_by(
                        owtf_rank=int(filter_data["owtf_rank"]))
                if isinstance(filter_data.get("owtf_rank"), list):
                    numbers_list = [int(x) for x in filter_data["owtf_rank"]]
                    query = query.filter(models.PluginOutput.owtf_rank.in_(
                        numbers_list))
            """ Not sure if these are needed
            if filter_data.get("owtf_rank[lt]", None):
                if isinstance(filter_data.get("owtf_rank[lt]"), list):
                    filter_data["owtf_rank[lt]"] = filter_data["owtf_rank[lt]"][0]
                query = query.filter(models.PluginOutput.owtf_rank < int(filter_data["owtf_rank[lt]"]))
            if filter_data.get("owtf_rank[gt]", None):
                if isinstance(filter_data.get("owtf_rank[gt]"), list):
                    filter_data["owtf_rank[gt]"] = filter_data["owtf_rank[gt]"][0]
                query = query.filter(models.PluginOutput.owtf_rank > int(filter_data["owtf_rank[gt]"]))
            if filter_data.get("user_rank[lt]", None):
                if isinstance(filter_data.get("user_rank[lt]"), list):
                    filter_data["user_rank[lt]"] = filter_data["user_rank[lt]"][0]
                query = query.filter(models.PluginOutput.user_rank < int(filter_data["user_rank[lt]"]))
            if filter_data.get("user_rank[gt]", None):
                if isinstance(filter_data.get("user_rank[gt]"), list):
                    filter_data["user_rank[gt]"] = filter_data["user_rank[gt]"][0]
                query = query.filter(models.PluginOutput.user_rank > int(filter_data["user_rank[gt]"]))
            """
        except ValueError:
            raise InvalidParameterType(
                "Integer has to be provided for integer fields")
        return query

    def GetAll(self, filter_data=None, target_id=None):
        if not filter_data:
            filter_data = {}
        self.Core.DB.Target.SetTarget(target_id)
        Session = self.Core.DB.Target.GetOutputDBSession()
        session = Session()
        query = self.GenerateQueryUsingSession(session, filter_data)
        results = query.all()
        session.close()
        return(self.DeriveOutputDicts(results, target_id))

    def GetUnique(self, target_id=None):
        """
        Returns a dict of some column names and their unique database
        Useful for advanced filter
        """
        self.Core.DB.Target.SetTarget(target_id)
        Session = self.Core.DB.Target.GetOutputDBSession(target_id)
        session = Session()
        unique_data = {
            "plugin_type": [i[0] for i in session.query(models.PluginOutput.plugin_type).distinct().all()],
            "plugin_group": [i[0] for i in session.query(models.PluginOutput.plugin_group).distinct().all()],
            "status": [i[0] for i in session.query(models.PluginOutput.status).distinct().all()],
            "user_rank": [i[0] for i in session.query(models.PluginOutput.user_rank).distinct().all()],
            "owtf_rank": [i[0] for i in session.query(models.PluginOutput.owtf_rank).distinct().all()],
        }
        session.close()
        return(unique_data)

    def DeleteAll(self, filter_data, target_id=None):
        """
        Here keeping filter_data optional is very risky
        """
        Session = self.Core.DB.Target.GetOutputDBSession(target_id)
        session = Session()
        query = self.GenerateQueryUsingSession(
            session,
            filter_data)  # Empty dict will match all results
        # Delete the folders created for these plugins
        for plugin in query.all():
            # First check if path exists in db
            if plugin.output_path:
                output_path = os.path.join(
                    self.Core.Config.GetOutputDirForTargets(),
                    plugin.output_path)
                if os.path.exists(output_path):
                    self.Core.rmtree(output_path)
        # When folders are removed delete the results from db
        results = query.delete()
        session.commit()
        session.close()

    def Update(self, plugin_group, plugin_type, plugin_code, patch_data, target_id=None):
        Session = self.Core.DB.Target.GetOutputDBSession(target_id)
        session = Session()
        query = self.GenerateQueryUsingSession(
            session,
            {
                "plugin_group": plugin_group,
                "plugin_type": plugin_type,
                "plugin_code": plugin_code
            })
        obj = query.first()
        if obj:
            try:
                if patch_data.get("user_rank", None):
                    if isinstance(patch_data["user_rank"], list):
                        patch_data["user_rank"] = patch_data["user_rank"][0]
                    obj.user_rank = int(patch_data["user_rank"])
                if patch_data.get("user_notes", None):
                    if isinstance(patch_data["user_notes"], list):
                        patch_data["user_notes"] = patch_data["user_notes"][0]
                    obj.user_notes = patch_data["user_notes"]
                session.merge(obj)
                session.commit()
            except ValueError:
                raise InvalidParameterType(
                    "Integer has to be provided for integer fields")
        session.close()

    def PluginAlreadyRun(self, PluginInfo, Target=None):
        Session = self.Core.DB.Target.GetOutputDBSession(Target)
        session = Session()
        plugin_output = session.query(models.PluginOutput).get(
            PluginInfo["key"])
        if plugin_output:
            return(self.DeriveOutputDict(plugin_output, Target))
        return(plugin_output)  # This is nothin but a "None" returned

    def SavePluginOutput(self,
                         plugin,
                         output,
                         duration,
                         target=None,
                         owtf_rank=None):
        """Save into the database the command output of the plugin `plugin."""
        session = self.Core.DB.Target.GetOutputDBSession(target)
        session = session()
        session.merge(models.PluginOutput(
            key=plugin["key"],
            plugin_code=plugin["code"],
            plugin_group=plugin["group"],
            plugin_type=plugin["type"],
            output=json.dumps(output),
            start_time=plugin["start"],
            end_time=plugin["end"],
            execution_time=duration,
            status=plugin["status"],
            # Save path only if path exists i.e if some files were to be stored
            # it will be there
            output_path=(plugin["output_path"] if os.path.exists(
                self.Core.PluginHandler.GetPluginOutputDir(plugin)) else None),
            owtf_rank=owtf_rank)
            )
        session.commit()
        session.close()

    def SavePartialPluginOutput(self, Plugin, Output, Message, Duration, target_id=None):
        Session = self.Core.DB.Target.GetOutputDBSession(target_id)
        session = Session()
        session.merge(models.PluginOutput(
            key=Plugin["key"],
            plugin_code=Plugin["code"],
            plugin_group=Plugin["group"],
            plugin_type=Plugin["type"],
            output=json.dumps(Output),
            error=Message,
            start_time=Plugin["start"],
            end_time=Plugin["end"],
            execution_time=Duration,
            status=Plugin["status"],
            # Save path only if path exists i.e if some files were to be stored
            # it will be there
            output_path=(Plugin["output_path"] if os.path.exists(
                self.Core.PluginHandler.GetPluginOutputDir(Plugin)) else None)
            ))
        session.commit()
        session.close()
