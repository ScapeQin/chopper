# Let me think about what I want to test with metawalker here.
# Examples:
#   concurrent writes, frequent file open, 

class Producer:
    """
    """
    def save2file(self, workload_str, tofile=""):
        if tofile != "":
            with open(tofile, 'w') as f:
                f.write(workload_str)
                f.flush()
            print "save2file. workload saved to file"
        else:
            print "save2file. no output file assigned"

    def produce_rmdir (self, np, ndir_per_pid, rootdir, pid=0, tofile=""):
        workload = ""
        for p in range(np):
            for dir in range(ndir_per_pid):
                path = self.rootdir + self.getDirpath(p, dir)
                entry = str(p)+";"+path+";"+"rm"+"\n";
                workload += entry
        
        return workload

    def produce (self, np, startOff, nwrites_per_file, nfile_per_dir, ndir_per_pid,
              wsize, wstride, rootdir, tofile="", fsync_per_write=False):
        self.np = np
        self.startOff = startOff

        # pid->dir->file->writes
        self.nwrites_per_file = nwrites_per_file
        self.nfile_per_dir = nfile_per_dir
        self.ndir_per_pid = ndir_per_pid

        self.wsize = wsize
        self.wstride = wstride
        self.fsync_per_write = fsync_per_write

        self.rootdir = rootdir

        workload = self._produce()
        
        if tofile != "":
            self.save2file(workload, tofile=tofile)
        
        return workload

    
    def getFilepath(self, dir, pid, file_id ):
        fname = ".".join( [str(pid), str(file_id), "file"] )
        dirname = self.getDirpath(pid, dir)
        return dirname + fname

    def getDirpath(self, pid, dir):
        return "pid" + str(pid) + ".dir" + str(dir) + "/" 
        

    def _produce(self):
        workload = ""
        
        # make dir
        for p in range(self.np):
            for dir in range(self.ndir_per_pid):
                path = self.rootdir + self.getDirpath(p, dir)
                entry = str(p)+";"+path+";"+"mkdir"+"\n";
                workload += entry

        # Open file
        for fid in range(self.nfile_per_dir):
            for dir in range(self.ndir_per_pid):
                for p in range(self.np):
                    path = self.rootdir + self.getFilepath(dir, p, fid)
                    entry = str(p)+";"+path+";"+"open"+"\n";
                    workload += entry

        #cur_off[pid][dir][fid]
        cur_off = [[[self.startOff for x in xrange(self.nfile_per_dir)] for x in xrange(self.ndir_per_pid)] for x in xrange(self.np)]
        for w_index in range(self.nwrites_per_file):
            for fid in range(self.nfile_per_dir):
                for dir in range(self.ndir_per_pid):
                    for p in range(self.np):
                        size = self.wsize
                        path = self.rootdir + self.getFilepath(dir, p, fid)

                        entry = str(p)+";"+path+";"+"write"+";"+str(cur_off[p][dir][fid])+";"+str(size)+"\n"
                        cur_off[p][dir][fid] += self.wstride

                        workload += entry

                        if self.fsync_per_write:
                            entry = str(p)+";"+path+";"+"fsync"+"\n";
                        workload += entry

        # fsync file
        for fid in range(self.nfile_per_dir):
            for dir in range(self.ndir_per_pid):
                for p in range(self.np):
                    path = self.rootdir + self.getFilepath(dir, p, fid)
                    entry = str(p)+";"+path+";"+"fsync"+"\n";
                    workload += entry


        # close file
        for fid in range(self.nfile_per_dir):
            for dir in range(self.ndir_per_pid):
                for p in range(self.np):
                    path = self.rootdir + self.getFilepath(dir, p, fid)
                    entry = str(p)+";"+path+";"+"close"+"\n";
                    workload += entry

        return workload


#prd = Producer()
##print prd.produce(np=1, startOff=0, 
                ##nwrites_per_file = 64, 
                ##nfile_per_dir=1, 
                ##ndir_per_pid=1,
                ##wsize=16, 
                ##wstride=16, 
                ##rootdir="/mnt/scratch/", 
                ##tofile="tmp.workload",
                ##fsync_per_write=True),

#print prd.produce(np=1, startOff=0, 
                #nwrites_per_file = 1024*1024, 
                #nfile_per_dir=1, 
                #ndir_per_pid=1,
                #wsize=1, 
                #wstride=1, 
                #rootdir="/mnt/scratch/", 
                #tofile="tmp.workload",
                #fsync_per_write=True),


