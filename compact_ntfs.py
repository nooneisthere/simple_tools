import os,time,sys,getopt

#useage : python compact_ntfs.py C:\Windows

#skip_file_list no need compact type
skip_file_list = ('.zip', '.rar', '.gif', '.jpg','.jepg','.png', '.msi', '.cab', '.log',
'.mp3', '.mp4','.mov','.mkv', '.swf', '.pdf')

#不需包含以下关键字，的目录上做压缩标记，但目录下的文件依然会进行分析压缩
skip_dir_list = ('.git', 'logs', 'cache', 'boot' , 'images','recent')

#完全忽略的文件夹，不读取里面的文件
just_ignore_dir =  ('appdata','documents','manifests','h1','h2')
file_size = 5000

def list_file_org(path):
    for aflie in os.listdir(path):
        aflie =  os.path.join(path,aflie)
        if os.path.isdir(aflie):
            list_file(aflie)

def skip_dir(dname):
    for sdir in skip_dir_list:
        if( dname.lower().find(sdir) > -1):
            return (dname, sdir)

def skip_file(full_path):
    ext = os.path.splitext(full_path)[-1].lower()
    if ext in all_ext:
        all_ext[ext] += 1
    else:
        all_ext[ext] = 1

    if ext in skip_file_list:
        return ('type',ext)

    stinfo = os.stat(full_path)
    if stinfo.st_size > 1024*1024*20 :
        return ('bigsize', '{0}M' .format( stinfo.st_size // (1024*1024)))
    elif stinfo.st_size < file_size :
        return ('smallsize', '{0} byte' .format( stinfo.st_size ))
    elif(cur_time - int(stinfo.st_mtime) < 3600*24*5) :
        return ('mtime', '{0} hours ago'.format((cur_time - int(stinfo.st_mtime)) // 3600))


open_error = []
def list_file(path):
    #print(path)
    global dir_cnt,file_cnt,skip_cnt,file_processed
    try:
        flist = os.listdir(path)
    except IOError:
        print("error open:",path)
        open_error.append(path)
        return;

    for aflie in flist:

        full_path =  os.path.join(path,aflie)
        if os.path.isdir(full_path):
            dir_cnt += 1
            skip_stat = skip_dir(aflie)
        else:
            file_cnt += 1
            skip_stat = skip_file(full_path)


        if skip_stat:
            skip_cnt += 1
            if (skip_cnt < 100 or (skip_cnt % 50 == 0) ):
                print(skip_stat,full_path)

        if (skip_stat and '-u' == compact_mod ) or (not skip_stat and  '-c' == compact_mod ):
            file_processed += 1
            command = compact_cmd.format(full_path)
            #sys_result = os.popen(command).read()
            sys_result = os.system(command)
            if sys_result:
                sys_result = 'callerror:',sys_result
                print(sys_result,skip_stat,command,file=log2)
            else:
                print(sys_result,skip_stat,command,file=log1)

        if os.path.isdir(full_path) and aflie.lower() not in just_ignore_dir:
            list_file(full_path)

dir_cnt,file_cnt,skip_cnt,file_processed = 0,0,0,0
all_ext = {};
opts, pathes = getopt.gnu_getopt(sys.argv[1:], 'cus:')
print(opts, pathes)
if len(pathes) == 0:
    pathes.append(input('input path: '))

if len(pathes) == 0:
    sys.exit('no path info')

#r'compact /U /A /S:"{0}"' use to apply recrusive, decide not to do it on command ,because this script already do recrusive
compact_mod = 'test'
for opt in opts:
    print(compact_mod)
    if opt[0] == '-s' :
       file_size = int(opt[1])
    if opt[0] == '-c' :
        compact_mod = opt[0]
        compact_cmd = r'compact /C /A "{0}"'
    elif opt[0] == '-u' :
        compact_mod = opt[0]
        compact_cmd = r'compact /U /A "{0}"'
#sys.exit('test');
log1 = open('compact_info.txt', mode='w')
log2 = open('compact_error.txt', mode='a')
cur_time = int(time.time())
print(cur_time)

for path in pathes:
    list_file(path)

print('#########################################')

print('dir_cnt:',dir_cnt,'file_cnt:',file_cnt,'skip_cnt:',skip_cnt,'file_processed',file_processed)
sorted_list = sorted(all_ext, key = lambda x:all_ext[x], reverse=True)
for x in sorted_list:
    if all_ext[x] > 1 :
        print(x,all_ext[x],file=log1)

print('################error acess#########################',file=log1)
print('\n'.join(open_error))
print('\n'.join(open_error),file=log2)

log1.close()
