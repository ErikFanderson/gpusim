

#"Start","Duration","Grid X","Grid Y","Grid Z","Block X","Block Y","Block Z","Registers Per Thread","Static SMem","Dynamic SMem","Size","Throughput","SrcMemType","DstMemType","Device","Context","Stream","Src Dev","Src Ctx","Dst Dev","Dst Ctx","Name"

def parseLog(headerNum,filename):
    '''
    Parses log file and generates compatible trace file
    Src
    "Size"
    "Src Dev"
    "Dst Dev"
    "Name"
    '''
    columnList = []
    #dictList
    #Open files, skip header, and generate list of all columns/categories in csv file
    f_read = open("nvproflogs/" + filename,'r')
    f_write = open("traceFiles/" + filename.strip(".log"),'w')
    for i in range(headerNum):
        f_read.readline()
    columnList = f_read.readline().strip().replace('"','').split(',')
    units = f_read.readline().strip().split(',')
    sizeInd = columnList.index("Size")
    srcInd = columnList.index("Src Dev")
    dstInd = columnList.index("Dst Dev")
    nameInd = columnList.index("Name")
    #Read lines with PtoP access and generate trace file
    for line in f_read:
        if "PtoP" in line:
            line = line.replace('"','').strip().split(',')
            line[srcInd] = line[srcInd].replace('(',')').split(')')[1]
            line[dstInd] = line[dstInd].replace('(',')').split(')')[1]
            if units[sizeInd] == "KB":
                line[sizeInd] = str(int(float(line[sizeInd])*1e3))
            elif units[sizeInd] == "MB":
                line[sizeInd] = str(int(float(line[sizeInd])*1e6))
            elif units[sizeInd] == "GB":
                line[sizeInd] = str(int(float(line[sizeInd])*1e9))
            else:
                line[sizeInd] = "UnknownUnits"
            f_write.write(line[nameInd].replace(" ","-") + ' ' + 'delay ' + line[srcInd]  + ' ' + line[dstInd] + ' ' + line[sizeInd] + '\n')
    #Close files
    f_read.close()
    f_write.close()


if __name__ == "__main__":
    parseLog(3,"cifar10_resnet20_v2_parameterserver_8347.log")
