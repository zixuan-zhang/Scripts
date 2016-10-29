
"""
@Author: zixuan.zhang.victor@gmail.com
@Des: This script is developed for Microsoft Azure Networking Team.
    This script is to extract JobSet & Job & Task from email report.
    Email report is organized as HTML file.
"""

import os
import uuid
from lxml import etree

FilePath = "Buildout_Report_20160731_140736.htm"

SuccessMap = {
        0 : "ClusterName",
        1 : "Status",
        2 : "Generation",
        3 : "ClusterType",
        4 : "DcFolder",
        5 : "AZSet",
        6 : "COLO",
        7 : "ROW",
        8 : "SeedUpdateTime",
        9 : "IPS",
        10 : "CodeReview",
        11 : "Dpk",
        12 : "Ngg"
        }

FailureMap = {
        0 : "ClusterName",
        1 : "Status",
        2 : "Generation",
        3 : "ClusterType",
        4 : "DcFolder",
        5 : "AZSet",
        6 : "COLO",
        7 : "ROW",
        8 : "SeedUpdateTime",
        9 : "DPK",
        10: "NGG",
        11: "Error",
        12: "Warning"
        }

TotalMap = {
        0 : "ClusterName",
        1 : "Status",
        2 : "Generation",
        3 : "ClusterType",
        4 : "DcFolder",
        5 : "AZSet",
        6 : "COLO",
        7 : "ROW",
        8 : "SeedUpdateTime",
        9 : "IPS",
        10: "CodeReview",
        11: "Dpk",
        12: "Ngg",
        13: "Error",
        14: "Warning"
        }

class SucTask():
    def __init__(self):
        self.jobSetId = None
        self.startTime = None
        self.endTime = None
        self.data = {}
        for value in SuccessMap.values():
            self.data[value] = ""

    def __str__(self):
        content = "\n".join(["   %s : %s" % (item[0], item[1]) for item in self.data.items()])
        content += "\nEndTime: %s\n" % self.endTime
        return content

class FaiTask():
    def __init__(self):
        self.jobSetId = None
        self.startTime = None
        self.endTime = None
        self.data = {}
        for value in FailureMap.values():
            self.data[value] = ""

    def __str__(self):
        content = "\n".join(["   %s : %s" % (item[0], item[1]) for item in self.data.items()])
        content += "\nEndTime: %s\n" % self.endTime
        return content

class Task():
    def __init__(self, task):
        self.totalPropertyCount = 15
        self.data = {}
        for i in range(self.totalPropertyCount):
            if TotalMap[i] in task.data:
                self.data[TotalMap[i]] = task.data[TotalMap[i]]
            else:
                self.data[TotalMap[i]] = None
        self.startTime = task.startTime
        self.endTime = task.endTime
        self.jobSetId = task.jobSetId
        self.jobId = str(uuid.uuid1())

    def __str__(self):
        contents = []
        contents.append(self.jobSetId)
        contents.append(self.jobId);
        contents.append(self.startTime)
        contents.append(self.endTime)
        for i in range(self.totalPropertyCount):
            value = self.data[TotalMap[i]] if self.data[TotalMap[i]] else " "
            contents.append(value.replace("\r\n", ""))
        return "|".join(contents)

class JobSet:
    def __init__(self):
        self.jobSetId = ""
        self.start = ""
        self.end = ""
        self.successTasks = []
        self.failureTasks = []

    def __str__(self):
        content = "Total Task: %d\n" % (len(self.successTasks) + len(self.failureTasks))
        content += "StartTime: %s\nEndTime: %s\n" % (self.start, self.end)
        content += "\n".join([str(task) for task in self.successTasks])
        content += "\n".join([str(task) for task in self.failureTasks])
        return content

    def adjustTaskTime(self):
        for task in self.successTasks:
            task.endTime = self.end
        for task in self.failureTasks:
            task.endTime = self.end

def extractJobSetFromReport(reportPath):
    content = open(reportPath).read()
    doc = etree.HTML(content)
    bigAreas = doc.xpath("/html/body/div/table/tr")
    if len(bigAreas) <= 2:
        print "ERROR: report format illegal. Big Areas not less or equal than 2"

    jobSet = JobSet()

    summaryArea = bigAreas[0]
    successArea = None
    failureArea = None

    if len(bigAreas) == 4:
        successArea = bigAreas[2]
        failureArea = bigAreas[3]
    else:
        thatArea = bigAreas[2]
        span = thatArea.xpath("./td/table/tr/td//span/text()")
        if span:
            text = span[0]
            if text.find("None") != -1:
                failureArea = thatArea
            else:
                successArea = thatArea

    # For summaryArea
    subAreas = summaryArea.xpath("./td/table/tr")
    startTime = subAreas[1].xpath(".//span")[1].text
    endTime = subAreas[2].xpath(".//span")[1].text

    jobSet.start = startTime
    jobSet.end = endTime
    jobSet.jobSetId = str(uuid.uuid1())

    # For successArea
    if successArea is not None:
        successTasks = successArea.xpath("./td/table/tr")[2:]
        for task in successTasks:
            successTask = SucTask()
            properties = task.xpath("./td")
            if len(properties) != 13:
                print "ERROR: report format illegal. property count not equal to 13"
                exit(0)
            for i in range(11):
                span = properties[i].xpath(".//span//text()")
                successTask.data[SuccessMap[i]] = ""
                if span:
                    successTask.data[SuccessMap[i]] = "".join(s for s in span)
            for i in range(11, 13):
                successTask.data[SuccessMap[i]] = ""
                href = properties[i].xpath(".//span/a/@href")
                if href:
                    successTask.data[SuccessMap[i]] = href[0]

            successTask.endTime = endTime
            successTask.startTime = startTime
            successTask.jobSetId = jobSet.jobSetId
            jobSet.successTasks.append(successTask)

    # For failureArea
    if failureArea is not None:
        failureTasks = failureArea.xpath("./td/table/tr")[2:]
        failureTask = None
        for task in failureTasks:
            properties = task.xpath("./td")
            if len(properties) != 11 and len(properties) != 1:
                print "ERROR: report format illegal. failure property count not equal to 11 or 1"
                exit(0)
            if len(properties) == 11:
                if failureTask:
                    failureTask.endTime = endTime
                    failureTask.startTime = startTime
                    failureTask.jobSetId = jobSet.jobSetId
                    jobSet.failureTasks.append(failureTask)
                failureTask = FaiTask()
                for i in range(9):
                    span = properties[i].xpath(".//span//text()")
                    failureTask.data[FailureMap[i]] = ""
                    if span:
                        failureTask.data[FailureMap[i]] = "".join(s for s in span)
                for i in range(9,11):
                    failureTask.data[FailureMap[i]] = ""
                    href = properties[i].xpath(".//span/a/@href")
                    if href:
                        failureTask.data[FailureMap[i]] = href[0]
            else:
                span = properties[0].xpath(".//span//text()")
                if span:
                    content = "".join([s for s in span])
                    if content.startswith("Error"):
                        failureTask.data["Error"] = content
                    else:
                        failureTask.data["Warning"] = content
        if failureTask:
            failureTask.endTime = endTime
            failureTask.startTime = startTime
            failureTask.jobSetId = jobSet.jobSetId
            jobSet.failureTasks.append(failureTask)

    return jobSet

def getAllJobSets():
    reportDir = "/home/ubuntu/workspace/project/migration/reports"
    files = [os.path.join(reportDir, f) for f in os.listdir(reportDir)]
    files = sorted(files)
    jobSets = []
    for name in files:
        # print "Processing %s" % name
        jobSet = extractJobSetFromReport(name)
        jobSets.append(jobSet)
    return jobSets

def get_cluster_names(clusterFile):
    clusters = None
    fp = open(clusterFile)
    lines = fp.readlines()
    clusters = [line.strip() for line in lines]
    return clusters

def get_last_task_for_clusters(clusterFile):
    # clusterNames = get_cluster_names(clusterFile);
    clusterNames = ["MWH01PrdApp10-01", "CZ4PrdApp01-01", "BYAPrdApp22"]
    jobSets = getAllJobSets()
    clusterTasks = {}
    for jobSet in jobSets:
        for task in jobSet.successTasks:
            clusterName = task.data["ClusterName"]
            if clusterName in clusterNames:
                clusterTasks[clusterName] = task
        for task in jobSet.failureTasks:
            clusterName = task.data["ClusterName"]
            if clusterName in clusterNames:
                clusterTasks[clusterName] = task
    for clusterName in clusterNames:
        if clusterName not in clusterTasks:
            continue
        # print "%s : \t%s : \t%s" % (clusterName, clusterTasks[clusterName].endTime, clusterTasks[clusterName].data["Status"])
        task = Task(clusterTasks[clusterName])
        print str(task)

if __name__ == "__main__":
    clusterFile78 = "/home/ubuntu/workspace/project/migration/clusters.txt"
    clusterFile09 = "/home/ubuntu/workspace/project/migration/clusters09.txt"
    clusterFile10 = "/home/ubuntu/workspace/project/migration/clusters10.txt"
    clusterFileToBeInserted = "/home/ubuntu/workspace/project/migration/ClustersNeedToBeInserted.txt"
    get_last_task_for_clusters(clusterFileToBeInserted)
