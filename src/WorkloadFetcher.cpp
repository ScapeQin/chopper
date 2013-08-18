#include <string>
#include <stdlib.h>
#include <iostream>
#include <fstream>
#include <sstream>
#include <queue>
#include <assert.h>
#include <iterator>
#include <string>

#include "Util.h"
#include "WorkloadFetcher.h"

using namespace std;

///////////////////////////////////////////
///////////////////////////////////////////
// WorkloadEntry
//

WorkloadEntry::WorkloadEntry(const std::string &line)
{
    setEntry(line);
}

void
WorkloadEntry::setEntry(const std::string &line)
{
    _entry_str = line;
    vector<string> a = Util::split(_entry_str, ';', _tokens);

    setItemCache();
}

bool WorkloadEntry::setItemCache()
{
    if ( !isHEAD() ) {
        istringstream( _tokens[0] ) >> _pid;
        _path = _tokens[1];
        _operation = _tokens[2];
        return true;
    } else {
        return false;
    }
}


bool
WorkloadEntry::isHEAD() const
{
    if ( _tokens.size() > 0 && _tokens[0] == "HEAD" )
        return true;
    else 
        return false;
}

///////////////////////////////////////////
///////////////////////////////////////////
// WorkloadFetcher
WorkloadFetcher::WorkloadFetcher(int bsize, const char *workloadpath)
    :_bufSize(bsize)
{ 
    assert(_bufSize > 0);
    _workloadStream.open(workloadpath);
    if (! _workloadStream.is_open()) {
        cerr << "ERROR, workload file (" << workloadpath << ") cannot be open." << endl;
        exit(1);
    }
}

WorkloadFetcher::~WorkloadFetcher()
{
    _workloadStream.close();
}

// Return 1: got the entry
// Return EOF: reach the eof of file, entry may have
//             random data
int 
WorkloadFetcher::readEntryFromStream(WorkloadEntry &entry)
{
    string line;
    if (getline(_workloadStream, line)) {
        istringstream iss(line);
        
        entry.setEntry(line);
        return 1;
    }
    return EOF;
}


// fetch one entry from buffer, if buffer is
// empty, read it from workload file.
// Note that when buffer size should be at least 1
//
// Return number of entries fetched, or EOF (indicating
// nothing more can be fetched (EOF and empty buffer))
int 
WorkloadFetcher::fetchEntry(WorkloadEntry &entry)
{
    // Fill buffer if it is empty
    if ( _entryBuf.empty() ) {
        if ( fillBuffer() == 0 ) {
            // buffer is empty due to empty source
            return EOF;
        }
    }

    assert(!_entryBuf.empty());
    entry = _entryBuf.front(); // the oldest entry
    _entryBuf.pop();
    return 1;
}

// It tries to fill up the buffer, but it can fail
// when the source (plfs workload file) is empty.
// Let me assume that's the only reason. When it returns
// < buffer size, you know the source is empty.
int
WorkloadFetcher::fillBuffer()
{
    int nleft = _bufSize - _entryBuf.size();
    while ( nleft > 0 ) {
        WorkloadEntry lp_entry;
        int ret;
        ret = readEntryFromStream(lp_entry);
        if ( ret == 1 ) {
            _entryBuf.push(lp_entry);
            nleft--;
        } else {
            // ret == EOF
            break;
        }
    }   
    // when you can get nothing in fillBuffer,
    // you know you have nothing in source file
    return (_bufSize - nleft); 
}








