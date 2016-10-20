
"""
@Author: zixuan.zhang.victor@gmail.com
@Des: This script is developed for Microsoft Azure Networking Team.
    This script is to extract JobSet & Job & Task from email report.
    Email report is organized as HTML file.
"""


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

class SucTask():
    def __init__(self):
        self.data = {}
        for value in SuccessMap.values():
            self.data[value] = ""

    def __str__(self):
        return str(self.data)

class FaiTask():
    def __init__(self):
        self.data = {}
        for value in FailureMap.values():
            self.data[value] = ""

    def __str__(self):
        return str(self.data)

class JobSet:
    def __init__(self):
        self.start = ""
        self.end = ""
        self.tasks = []

    def __str__(self):
        content = "Total Task: %d\n" % len(self.tasks)
        content += "\n".join([str(task) for task in self.tasks])
        return content

def extractJobSetFromReport(reportPath):
    content = open(reportPath).read()
    doc = etree.HTML(content)
    bigAreas = doc.xpath("/html/body/div/table/tr")
    if len(bigAreas) != 4:
        print "ERROR: report format illegal. Big Areas not equals to 4"

    jobSet = JobSet()

    summaryArea = bigAreas[0]
    successArea = bigAreas[2]
    failureArea = bigAreas[3]

    """
    # For summaryArea
    subAreas = summaryArea.xpath("./td/table/tr")
    startTime = subAreas[1].xpath(".//span")[1].text
    endTime = subAreas[2].xpath(".//span")[1].text

    jobSet.start = startTime
    jobSet.end = endTime

    # For successArea
    successTasks = successArea.xpath("./td/table/tr")[2:]
    for task in successTasks:
        successTask = SucTask()
        properties = task.xpath("./td")
        if len(properties) != 13:
            print "ERROR: report format illegal. property count not equal to 13"
        for i in range(11):
            span = properties[i].xpath(".//span")
            successTask.data[SuccessMap[i]] = ""
            if span:
                successTask.data[SuccessMap[i]] = span[0].text
        for i in range(11, 13):
            successTask.data[SuccessMap[i]] = ""
            href = properties[i].xpath(".//span/a/@href")
            if href:
                successTask.data[SuccessMap[i]] = href[0]

        jobSet.tasks.append(successTask)
    """

    # For failureArea
    failureTasks = failureArea.xpath("./td/table/tr")[2:]
    failureTask = None
    for task in failureTasks:
        properties = task.xpath("./td")
        if len(properties) != 11 and len(properties) != 1:
            print "ERROR: report format illegal. failure property count not equal to 11 or 1"
        if len(properties) == 11:
            if failureTask:
                jobSet.tasks.append(failureTask)
            failureTask = FaiTask()
            for i in range(9):
                span = properties[i].xpath(".//span")
                failureTask.data[FailureMap[i]] = ""
                if span:
                    failureTask.data[FailureMap[i]] = span[0].text
            for i in range(9,11):
                failureTask.data[FailureMap[i]] = ""
                href = properties[i].xpath(".//span/a/@href")
                if href:
                    failureTask.data[failureMap[i]] = href[0]
        else:
            span = properties[0].xpath(".//span")
            if span:
                content = span[0].text
                if content.startswith("Error"):
                    failureTask.data["Error"] = content
                else:
                    failureTask.data["Warning"] = content
    if failureTask:
        jobSet.tasks.append(failureTask)

    return jobSet

if __name__ == "__main__":
    name = "Buildout_Report_20160731_140736.htm"
    jobSet = extractJobSetFromReport(name)
    print jobSet
