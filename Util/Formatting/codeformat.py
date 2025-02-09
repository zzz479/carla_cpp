#!/usr/bin/python

#
# Copyright (c) 2017-2020 Intel Corporation
#
# Helper script for code formatting using clang-format-3.9 and autopep

import argparse  # 用于解析命令行参数的标准库模块
import filecmp  # 用于比较文件内容的模块，可帮助进行文件差异对比等操作
import os  # 提供了与操作系统交互的函数，例如文件和目录操作相关功能
import re  # 正则表达式模块，用于处理文本匹配、查找等操作
import sets  # （注：在Python 3中，sets模块已被弃用，通常使用内置的set类型来替代它，此处可能需根据Python版本确认使用情况）用于处理集合相关操作
import subprocess  # 允许在Python程序中启动新进程，执行外部命令
import sys  # 提供了对Python解释器相关的变量和函数的访问，比如获取命令行参数等
from termcolor import cprint  # 从termcolor库中导入cprint函数，用于给终端输出添加颜色

# 定义脚本的版本号，这里版本号为 "1.3"，可以用于版本展示、兼容性判断等场景
SCRIPT_VERSION = "1.3"


# 定义CodeFormatter类，该类大概率是用于代码格式化相关功能的封装
class CodeFormatter:
    # 类的构造函数（初始化方法），用于初始化CodeFormatter类的实例对象的各个属性
    def __init__(self, command, expectedVersion, formatCommandArguments,
                 verifyCommandArguments, verifyOutputIsDiff, fileEndings,
                 fileDescription, installCommand):
        # 用于执行代码格式化操作的命令，比如可能是类似"black"（Python代码格式化工具）这样的命令字符串，
        # 具体值会在实例化类时传入，决定了实际调用哪个工具来进行格式化
        self.command = command
        # 期望的代码格式化工具的版本号，后续可能会通过某种方式（比如执行命令查看版本输出并对比）来验证实际使用的工具版本是否符合预期，
        # 以此确保格式化的效果符合要求
        self.expectedVersion = expectedVersion
        # 这是一个列表或者元组类型（通常是这样），包含了执行代码格式化命令时需要传递的额外参数，
        # 例如格式化工具可能有一些特定的配置选项（如控制缩进格式、换行规则等），通过这些参数传递给格式化命令
        self.formatCommandArguments = formatCommandArguments
        # 同样是一个列表或者元组类型，存放执行验证操作（验证代码格式化后的结果是否正确等情况）时要传递给相关验证命令的参数，
        # 不同的验证场景可能有不同的参数需求
        self.verifyCommandArguments = verifyCommandArguments
        # 一个布尔值，表示验证输出的结果是否应该呈现为差异形式（比如对比格式化前后文件内容的差异情况），
        # 如果为True，可能意味着后续会以展示差异的方式来体现验证结果
        self.verifyOutputIsDiff = verifyOutputIsDiff
        # 是一个列表，存放了需要进行代码格式化操作的文件的后缀名，例如 [".py", ".cpp"]，
        # 通过后缀名来筛选出符合要求的文件进行格式化处理
        self.fileEndings = fileEndings
        # 对要进行格式化的文件的描述信息字符串，比如 "Python source files"（表示Python源文件），
        # 可以让使用者更清晰地了解要处理文件的类型和性质
        self.fileDescription = fileDescription
        # 用于安装相应代码格式化工具的命令，在需要安装格式化工具但尚未安装的情况下，可以通过执行这个命令来安装，
        # 确保能够正常使用格式化功能
        self.installCommand = installCommand

    #试图通过verifyformatterversion函数运行来获取格式化工具的版本信息
    def verifyFormatterVersion(self):
        try:
             # 使用 subprocess.check_output 执行命令并捕获输出，去除末尾的换行符
            versionOutput = subprocess.check_output([self.command, "--version"]).rstrip('\r\n')
            if self.expectedVersion != "":
                 # 如果设置了预期版本，检查实际版本是否符合预期
                if versionOutput.startswith(self.expectedVersion):
                    print("[OK] Found formatter '" + versionOutput + "'")
                    return
                else:
                     # 版本不匹配时，打印错误信息
                    cprint("[NOT OK] Found '" + versionOutput + "'", "red")
                    cprint("[NOT OK] Version string does not start with '" + self.expectedVersion + "'", "red")
            else:
                # 如果没有设置预期版本，则直接返回
                return
        except:
             # 捕获所有异常，包括但不限于找不到命令、权限问题等，并打印错误信息
            cprint("[ERROR] Could not run " + self.command, "red")
            cprint("[INFO] Please check if correct version is installed or install with '" +
                   self.installCommand + "'", "blue")
              # 如果出现任何问题，退出程序，状态码为1表示有错误发生
        sys.exit(1)

    def printInputFiles(self):
        if len(self.inputFiles) > 0:
             # 打印找到的文件数量和类型描述
            print("Found " + self.fileDescription + " files:")
            for fileName in self.inputFiles:
                # 逐个打印文件名
                print(fileName)
            print("")
            # 打印空行以分隔输出内容

      def formatFile(self, fileName):
        """
        使用指定的命令和参数格式化文件。

        参数:
            fileName (str): 要格式化的文件名。

        返回:
            bool: 如果发生错误，则返回True；否则返回False。
        """
        # 初始化命令列表，self.command可能是一个字符串，表示主命令
        commandList = [self.command]
        # 将self.formatCommandArguments（可能是一个列表）中的参数添加到命令列表中
        commandList.extend(self.formatCommandArguments)
        # 将文件名添加到命令列表的末尾
        commandList.append(fileName)
        try:
            # 执行命令并捕获输出（如果有错误，输出将包括在stderr中并抛出异常）
            subprocess.check_output(commandList, stderr=subprocess.STDOUT)
            # 如果命令成功执行，打印成功消息
            print("[OK] " + fileName)
            # 如果没有异常，返回False表示成功
            return False
        except subprocess.CalledProcessError as e:
            # 如果命令执行失败，打印错误消息（包括命令的输出）
            cprint("[ERROR] " + fileName + " (" + e.output.rstrip('\r\n') + ")", "red")
            # 返回True表示发生错误
            return True

    def performGitDiff(self, fileName, verifyOutput):
        """
        使用git diff命令检查文件是否有更改，并与verifyOutput进行比较。

        参数:
            fileName (str): 要检查的文件名。
            verifyOutput (bytes): 用于与git diff输出进行比较的数据。

        返回:
            tuple: 一个包含两个元素的元组，(bool, str)。
                   bool表示是否发生错误，str是git diff的输出（如果没有错误则为空字符串）。
        """
        try:
            # 使用Popen启动git diff进程，并设置输入、输出和错误管道
            diffProcess = subprocess.Popen(
                ["git", "diff", "--color=always", "--exit-code", "--no-index", "--", fileName, "-"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            # 向进程发送数据（verifyOutput），并读取输出
            diffOutput, _ = diffProcess.communicate(verifyOutput)
            # 如果git diff进程返回码为0，表示没有差异，将diffOutput设置为空字符串
            if diffProcess.returncode == 0:
                diffOutput = ""
        except OSError:
            # 如果无法运行git diff，打印错误消息
            cprint("[ERROR] Failed to run git diff on " + fileName, "red")
            # 返回(True, "")表示发生错误且没有diff输出
            return (True, "")
        # 返回(False, diffOutput)表示没有错误且可能有diff输出
        return (False, diffOutput)
    def verifyFile(self, fileName, printDiff):## 创建一个命令列表，以self.command开头，添加self.verifyCommandArguments中的元素，最后添加fileName
        commandList = [self.command]
        commandList.extend(self.verifyCommandArguments)
        commandList.append(fileName)
        try:
            verifyOutput = subprocess.check_output(commandList, stderr=subprocess.STDOUT)# 使用subprocess.check_output执行命令列表中的命令，并获取输出
        except subprocess.CalledProcessError as e:
            cprint("[ERROR] " + fileName + " (" + e.output.rstrip('\r\n') + ")", "red")
            return True

        diffOutput = ""
        if self.verifyOutputIsDiff:
            diffOutput = verifyOutput
        else:
            status, diffOutput = self.performGitDiff(fileName, verifyOutput)
            if status:
                return True

        if diffOutput != "":
            cprint("[NOT OK] " + fileName, "red")
            if printDiff:
                print(diffOutput.rstrip('\r\n'))
            return True

        print("[OK] " + fileName)
        return False


class CodeFormatterClang(CodeFormatter):
    CLANG_FORMAT_FILE = ".clang-format"
    CHECKED_IN_CLANG_FORMAT_FILE = "clang-format"
    CODE_FORMAT_IGNORE_FILE = ".codeformatignore"

    def __init__(self):# 调用父类CodeFormatter的__init__方法进行初始化
        CodeFormatter.__init__(self,
                               command="clang-format-3.9",
                               expectedVersion="clang-format version 3.9",
                               formatCommandArguments=["-style=file", "-fallback-style=none", "-i"],
                               verifyCommandArguments=["-style=file", "-fallback-style=none"],
                               verifyOutputIsDiff=False,
                               fileEndings=["cpp", "hpp", "c", "h", "cc"],
                               fileDescription="source and header",
                               installCommand="sudo apt-get install clang-format-3.9")
        self.scriptPath = os.path.dirname(os.path.abspath(__file__))#
        self.checkedInClangFormatFile = os.path.join(self.scriptPath, CodeFormatterClang.CHECKED_IN_CLANG_FORMAT_FILE)

    def verifyFormatterVersion(self):
        """
        验证代码格式化器的版本是否与预期一致。

        这个方法首先调用CodeFormatter类的静态方法verifyFormatterVersion来检查格式化器的版本，
        然后调用实例方法verifyClangFormatFileExistsAndMatchesCheckedIn来验证.clang-format文件的存在和匹配性。
        """
        # 调用CodeFormatter类的静态方法来验证格式化器的版本
        CodeFormatter.verifyFormatterVersion(self)
        # 验证.clang-format文件的存在性及其与检入版本的一致性
        self.verifyClangFormatFileExistsAndMatchesCheckedIn()

    def verifyCheckedInClangFormatFileExists(self):
        """
        验证检入的.clang-format文件是否存在。

        参数:
            无

        返回:
            无
        """
        # 检查指定的.clang-format文件是否存在
        if os.path.exists(self.checkedInClangFormatFile):
            # 如果文件存在，则打印成功消息
            print("[OK] Found " + CodeFormatterClang.CHECKED_IN_CLANG_FORMAT_FILE + " file (the one that should be in a repository) " +
                  self.checkedInClangFormatFile)
        else:
            # 如果文件不存在，则打印警告消息，并询问用户是否确认继续
            cprint("[WARN] Not found " + CodeFormatterClang.CHECKED_IN_CLANG_FORMAT_FILE + " file " +
                   self.checkedInClangFormatFile, "yellow")
            self.confirmWithUserClangFormatFileCantBeVerified()

    def confirmWithUserClangFormatFileCantBeVerified(self):
        """
        当用户确认.clang-format文件无法验证时，与用户进行确认。

        如果用户没有通过命令行参数指定--yes（即self.args.yes为False），
        则询问用户是否确定他们的.clang-format文件是最新的，并且他们想要继续。
        如果用户回答不是'y'，则退出程序。

        参数:
            无

        返回:
            无（如果用户回答不是'y'，则通过sys.exit(1)退出程序）
        """
        # 检查用户是否通过命令行参数指定了--yes
        if not self.args.yes:
            # 如果没有指定--yes，则询问用户是否确定要继续
            # 注意：在Python 3中，raw_input()已被重命名为input()
            answer = input("Are you sure your .clang-format file is up-to-date and you want to continue? (y/N)")
            # 如果用户回答的不是'y'，则退出程序
            if answer != "y":
                sys.exit(1)

    def verifyClangFormatFileExistsAndMatchesCheckedIn(self):
        """
        验证.clang-format文件是否存在，并且是否与检入的版本匹配。

        这个方法首先调用verifyCheckedInClangFormatFileExists来验证检入的.clang-format文件是否存在。
        然后，它遍历输入文件列表，从每个文件的目录开始向上搜索.clang-format文件。
        如果找到的文件与检入的版本不匹配，或者根本没有找到文件，则程序将退出。

        参数:
            无

        返回:
            无（如果找到不匹配的文件或没有找到文件，则通过sys.exit(1)退出程序）
        """
        self.verifyCheckedInClangFormatFileExists()  # 验证检入的.clang-format文件是否存在
        foundClangFormatFiles = set()  # 使用set来存储找到的.clang-format文件路径，避免重复
        for fileName in self.inputFiles:  # 遍历输入文件列表
            dirName = os.path.dirname(os.path.abspath(fileName))  # 获取输入文件的绝对路径的目录部分
            # 从该目录开始向上搜索.clang-format文件
            if not self.findClangFormatFileStartingFrom(dirName, fileName, foundClangFormatFiles):
                sys.exit(1)  # 如果没有找到匹配的.clang-format文件，则退出程序

    def findClangFormatFileStartingFrom(self, dirName, fileName, foundClangFormatFiles):
        """
        从指定目录开始向上搜索.clang-format文件。

        这个方法在指定目录及其上级目录中搜索.clang-format文件。
        如果找到文件，它会检查该文件是否与检入的.clang-format文件匹配。
        如果找到匹配的文件，或者到达根目录仍未找到文件，则停止搜索。

        参数:
            dirName (str): 要开始搜索的目录路径。
            fileName (str): 与搜索相关的输入文件名（用于错误消息）。
            foundClangFormatFiles (set): 用于存储已找到的.clang-format文件路径的集合。

        返回:
            bool: 如果找到匹配的.clang-format文件，则返回True；否则返回False。
        """
        clangFormatFile = os.path.join(dirName, CodeFormatterClang.CLANG_FORMAT_FILE)  # 构建.clang-format文件的路径
        if os.path.exists(clangFormatFile):  # 如果文件存在
            if clangFormatFile not in foundClangFormatFiles:  # 避免重复处理同一个文件
                foundClangFormatFiles.add(clangFormatFile)  # 将文件路径添加到集合中
                # 检查找到的.clang-format文件是否与检入的版本匹配
                if os.path.exists(self.checkedInClangFormatFile) and \
                   not filecmp.cmp(self.checkedInClangFormatFile, clangFormatFile):
                    # 如果不匹配，则打印警告消息，并询问用户是否确定要继续
                    cprint("[WARN] " + clangFormatFile + " does not match " + self.checkedInClangFormatFile, "yellow")
                    self.confirmWithUserClangFormatFileCantBeVerified()
                    # 注意：这里原本的代码没有返回False或继续搜索的逻辑，
                    # 但根据上下文，我们可以假设如果用户确认继续，则视为“找到”了文件（尽管不匹配）。
                    # 因此，这里不返回False，而是继续执行下面的else分支（尽管逻辑上有些不严谨）。
                    # 一个更严谨的做法是，在confirmWithUser后根据用户输入决定是否继续或退出。
                else:
                    # 如果匹配或没有找到检入的.clang-format文件（后者不应该发生，因为前面已经验证过其存在性），
                    # 则打印成功消息。
                    print("[OK] Found " + CodeFormatterClang.CLANG_FORMAT_FILE +
                          " file (used by the formatter) " + clangFormatFile)
            # 无论是否匹配，都已经找到了一个.clang-format文件，因此返回True。
            # 注意：这里的逻辑可能需要根据实际需求进行调整，特别是关于不匹配文件时的处理。
            return True
        else:  # 如果当前目录中没有.clang-format文件
            dirNameOneLevelUp = os.path.dirname(dirName)  # 获取上一级目录的路径
            if dirNameOneLevelUp == dirName:  # 如果上一级目录与当前目录相同（通常是根目录的情况）
                # 打印错误消息，表示没有找到.clang-format文件
                cprint("[ERROR] Not found " + CodeFormatterClang.CLANG_FORMAT_FILE + " for " +
                       fileName + " in same directory or in any parent directory", "red")
                return False  # 返回False，表示没有找到匹配的.clang-format文件
            else:  # 如果上一级目录与当前目录不同，则继续向上搜索
                return self.findClangFormatFileStartingFrom(dirNameOneLevelUp, fileName, foundClangFormatFiles)  # 递归调用自身

    def __init__(self):
        CodeFormatter.__init__(self,
                               command="autopep8",
                               expectedVersion="",
                               formatCommandArguments=["--in-place", "--max-line-length=119"],
                               verifyCommandArguments=["--diff", "--max-line-length=119"],
                               verifyOutputIsDiff=True,
                               fileEndings=["py"],
                               fileDescription="python",
                               installCommand="sudo apt-get install python-pep8 python-autopep8")


class CodeFormat:

    def __init__(self):
        self.failure = False
        self.codeFormatterInstances = []
        return

    def parseCommandLine(self):
        parser = argparse.ArgumentParser(
            description="Helper script for code formatting.")
        parser.add_argument("input", nargs="+",
                            help="files or directories to process")
        parser.add_argument("-v", "--verify", action="store_true",
                            help="do not change file, but only verify the format is correct")
        parser.add_argument("-d", "--diff", action="store_true",
                            help="show diff, implies verify mode")
        parser.add_argument("-e", "--exclude", nargs="+", metavar="exclude",
                            help="exclude files or directories containing words from the exclude list in their names")
        parser.add_argument("-y", "--yes", action="store_true",
                            help="do not ask for confirmation before formatting more than one file")
        parser.add_argument("--version", action="version", version="%(prog)s " + SCRIPT_VERSION)
        self.args = parser.parse_args()
        if self.args.diff:
            self.args.verify = True

    def addCodeFormatter(self, codeFormatterInstance):
        self.codeFormatterInstances.append(codeFormatterInstance)

    def scanForInputFiles(self):
        for formatterInstance in self.codeFormatterInstances:
            filePattern = re.compile("^[^.].*\.(" + "|".join(formatterInstance.fileEndings) + ")$")
            formatterInstance.inputFiles = []
            for fileOrDirectory in self.args.input:
                if os.path.exists(fileOrDirectory):
                    formatterInstance.inputFiles.extend(self.scanFileOrDirectory(fileOrDirectory, filePattern))
                else:
                    cprint("[WARN] Cannot find '" + fileOrDirectory + "'", "yellow")

    def scanFileOrDirectory(self, fileOrDirectory, filePattern):
        fileList = []
        if os.path.isdir(fileOrDirectory):
            for root, directories, fileNames in os.walk(fileOrDirectory):
                directories[:] = self.filterDirectories(root, directories)
                for filename in filter(lambda name: filePattern.match(name), fileNames):
                    fullFilename = os.path.join(root, filename)
                    if self.isFileNotExcluded(fullFilename):
                        fileList.append(fullFilename)
        else:
            if self.isFileNotExcluded(fileOrDirectory) and (filePattern.match(os.path.basename(fileOrDirectory)) is not None):
                fileList.append(fileOrDirectory)
        return fileList

    def filterDirectories(self, root, directories):
        # Exclude hidden directories and all directories that have a CODE_FORMAT_IGNORE_FILE
        directories[:] = [directory for directory in directories if
                          not directory.startswith(".") and
                          not os.path.exists(os.path.join(root, directory, CodeFormatterClang.CODE_FORMAT_IGNORE_FILE))]
        return directories

    def isFileNotExcluded(self, fileName):
        if self.args.exclude is not None:
            for excluded in self.args.exclude:
                if excluded in fileName:
                    return False
        if os.path.islink(fileName):
            return False

        return True

    def confirmWithUserFileIsOutsideGit(self, fileName):
        cprint("[WARN] File is not in a Git repo: " + fileName, "yellow")
        answer = raw_input("Are you sure to code format it anyway? (y/Q)")
        if answer != "y":
            sys.exit(1)

    def confirmWithUserFileIsUntracked(self, fileName):
        cprint("[WARN] File is untracked in Git: " + fileName, "yellow")
        answer = raw_input("Are you sure to code format it anyway? (y/Q)")
        if answer != "y":
            sys.exit(1)

    def confirmWithUserGitRepoIsNotClean(self, gitRepo):
        cprint("[WARN] Git repo is not clean: " + gitRepo, "yellow")
        answer = raw_input("Are you sure to code format files in it anyway? (y/Q)")
        if answer != "y":
            sys.exit(1)

    def checkInputFilesAreInCleanGitReposAndAreTracked(self):
        if self.args.verify or self.args.yes:
            return
        gitRepos = sets.Set()
        for formatterInstance in self.codeFormatterInstances:
            for fileName in formatterInstance.inputFiles:
                gitRepo = self.getGitRepoForFile(fileName)
                if gitRepo is None:
                    self.confirmWithUserFileIsOutsideGit(fileName)
                else:
                    self.gitUpdateIndexRefresh(gitRepo)
                    if not self.isTrackedFile(fileName):
                        self.confirmWithUserFileIsUntracked(fileName)
                    elif gitRepo not in gitRepos:
                        gitRepos.add(gitRepo)
                        if not self.isCleanGitRepo(gitRepo):
                            self.confirmWithUserGitRepoIsNotClean(gitRepo)

    def getGitRepoForFile(self, fileName):
        if not self.isInsideGitRepo(fileName):
            return None
        try:
            gitProcess = subprocess.Popen(["git", "rev-parse", "--show-toplevel"],
                                          stdin=subprocess.PIPE,
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE,
                                          cwd=os.path.dirname(fileName))
            gitOutput, _ = gitProcess.communicate()
            if gitProcess.returncode == 0:
                return gitOutput.rstrip('\r\n')
        except OSError:
            cprint("[ERROR] Failed to run 'git rev-parse --show-toplevel' for " + fileName, "red")
        return None

    def isInsideGitRepo(self, fileName):
        try:
            gitProcess = subprocess.Popen(["git", "rev-parse", "--is-inside-work-tree"],
                                          stdin=subprocess.PIPE,
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE,
                                          cwd=os.path.dirname(fileName))
            gitOutput, _ = gitProcess.communicate()
            if gitProcess.returncode == 0:
                return gitOutput.rstrip('\r\n') == "true"
        except OSError:
            cprint("[ERROR] Failed to run 'git rev-parse --is-inside-work-tree' for " + fileName, "red")
        return False

    def isTrackedFile(self, fileName):
        try:
            gitProcess = subprocess.Popen(["git", "ls-files", "--error-unmatch", "--", os.path.basename(fileName)],
                                          stdin=subprocess.PIPE,
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE,
                                          cwd=os.path.dirname(fileName))
            _, _ = gitProcess.communicate()
            if gitProcess.returncode == 0:
                return True
        except OSError:
            cprint("[ERROR] Failed to run 'git ls-files --error-unmatch' for " + fileName, "red")
        return False

    def isCleanGitRepo(self, gitRepo):
        try:
            gitProcess = subprocess.Popen(["git", "diff-index", "--quiet", "HEAD", "--"],
                                          stdin=subprocess.PIPE,
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE,
                                          cwd=gitRepo)
            _, _ = gitProcess.communicate()
            if gitProcess.returncode == 0:
                return True
        except OSError:
            cprint("[ERROR] Failed to run 'git diff-index --quiet HEAD --' for " + gitRepo, "red")
        return False

    def gitUpdateIndexRefresh(self, gitRepo):
        try:
            gitProcess = subprocess.Popen(["git", "update-index", "-q", "--ignore-submodules", "--refresh"],
                                          stdin=subprocess.PIPE,
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE,
                                          cwd=gitRepo)
            _, _ = gitProcess.communicate()
            if gitProcess.returncode == 0:
                return True
        except OSError:
            cprint("[ERROR] Failed to run 'git update-index -q --ignore-submodules --refresh' for " + gitRepo, "red")
        return False

    def verifyFormatterVersion(self):
        for formatterInstance in self.codeFormatterInstances:
            if len(formatterInstance.inputFiles) > 0:
                formatterInstance.verifyFormatterVersion()

    def printMode(self):
        if self.args.verify:
            cprint("VERIFY MODE", attrs=["bold"])
        else:
            cprint("FORMAT MODE", attrs=["bold"])

    def processFiles(self):
        for formatterInstance in self.codeFormatterInstances:
            for fileName in formatterInstance.inputFiles:
                if self.args.verify:
                    self.failure |= formatterInstance.verifyFile(fileName, self.args.diff)
                else:
                    self.failure |= formatterInstance.formatFile(fileName)

    def numberOfInputFiles(self):
        count = 0
        for formatterInstance in self.codeFormatterInstances:
            count += len(formatterInstance.inputFiles)
        return count

    def confirmWithUser(self):
        if self.numberOfInputFiles() == 0:
            cprint("[WARN] No input files (or file endings unknown)", "yellow")
        elif (not self.args.verify) and (not self.args.yes) and self.numberOfInputFiles() > 1:
            for formatterInstance in self.codeFormatterInstances:
                formatterInstance.printInputFiles()
            answer = raw_input("Are you sure to code format " + str(self.numberOfInputFiles()) + " files? (y/N)")
            if answer != "y":
                sys.exit(1)


def main():
    codeFormat = CodeFormat()
    codeFormat.parseCommandLine()
    codeFormat.printMode()

    codeFormat.addCodeFormatter(CodeFormatterClang())
    codeFormat.addCodeFormatter(CodeFormatterAutopep())

    codeFormat.scanForInputFiles()
    codeFormat.verifyFormatterVersion()
    codeFormat.confirmWithUser()
    codeFormat.checkInputFilesAreInCleanGitReposAndAreTracked()
    codeFormat.processFiles()
    if codeFormat.failure:
        cprint("FAILURE", "red")
        sys.exit(1)
    else:
        cprint("SUCCESS", "green")
        sys.exit(0)

if __name__ == "__main__":
    main()
