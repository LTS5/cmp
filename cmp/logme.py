# Copyright (C) 2009-2011, Ecole Polytechnique Federale de Lausanne (EPFL) and
# Hospital Center and University of Lausanne (UNIL-CHUV), Switzerland
# All rights reserved.
#
#  This software is distributed under the open-source license Modified BSD.

# Code from
# from http://devlishgenius.blogspot.com/2008/10/logging-in-real-time-in-python.html

import sys, os, os.path as op
import logging, subprocess

def getLog(fpath):
    logFormat = "%(levelname)-8s : %(asctime)s : %(name)-10s : %(message)s"
    logFormatter = logging.Formatter( logFormat )
    
    consolehandler = logging.StreamHandler()
    consolehandler.setLevel( logging.DEBUG )
    consolehandler.setFormatter( logFormatter )
    
    if not op.exists(fpath):
        try:
            os.makedirs(op.dirname(fpath))
        except:
            pass

    errfpath = fpath + '.error'
    if not op.exists(errfpath):
        try:
            os.makedirs(op.dirname(errfpath))
        except:
            pass

    logFile = fpath
    logFileErr = errfpath
    
    filehandler = logging.FileHandler( logFile )
    filehandler.setLevel( logging.DEBUG )
    filehandler.setFormatter( logFormatter )

    filehandler2 = logging.FileHandler( logFileErr )
    filehandler2.setLevel( logging.ERROR )
    filehandler2.setFormatter( logFormatter )

    logging.getLogger( '' ).addHandler( consolehandler )
    logging.getLogger( '' ).addHandler( filehandler )
    logging.getLogger( '' ).addHandler( filehandler2 )
    
    mainlog = logging.getLogger( "main" )
    mainlog.setLevel( logging.DEBUG )
    
    return mainlog

def mkLocalLog( f ):
    # Could set _localLog as an attribute on the function:
    #   f._localLog = ..., but user would have to access it
    #  as an attribute: &lt;func&gt;._localLog( "&lt;msg&gt;" ).
    # Instead we add it to the function's globals dict.
    # If someone knows how to add it to the function's locals
    #  that would be great!
    
    ll = logging.getLogger( f.__name__ )
    ll.setLevel( logging.DEBUG )
    
    f.__globals__[ "_localLog" ] = ll
    return f


@mkLocalLog
def runCmd( cmd, log, sleep_interval=0.5 ):

    # timestamp for name
    import random
    t = random.randint(1, 10000000)
    # create in temporary file
    import tempfile
    fname = op.join(tempfile.gettempdir(), "out_fifo_%s" % str(t))
    # import time module
    import time

    try:
        os.unlink( fname )
    except: pass
    
    os.mkfifo( fname )

    try:
      
        fifo = os.fdopen( os.open( fname,
                                   os.O_RDONLY | os.O_NONBLOCK ) )
    
        newcmd = "( %s ) 1>%s 2>&1"%( cmd, fname )
    
        process = subprocess.Popen( newcmd, shell = True,
                                    stdout = subprocess.PIPE,
                                    stderr = subprocess.STDOUT )
        
        _localLog.debug( "Running: %s"%( cmd, ) )
    
        while process.returncode == None:
            # None means process is still running

            # pause for a while
            time.sleep(sleep_interval)

            # need to poll the process once so the returncode
            # gets set (see docs)
            process.poll()
    
            try:
                line = fifo.readline().strip()
            except:
                continue
    
            if line:
                log.info( line )
    
        remaining = fifo.read()
    
        if remaining:
            for line in [ line
                          for line in remaining.split( "\n" )
                          if line.strip() ]:
                log.info( line.strip() )
    
        if process.returncode:
            _localLog.critical( "Return Value: %s"%( process.returncode, ) )
        else:
            _localLog.debug( "Return Value: %s"%( process.returncode, ) )
    
    finally:
        try:
            os.unlink( fname )
        except:
            _localLog.warning( "Failed to unlink '%s'." % fname)

def GetInHMS(seconds):
    hours = seconds / 3600
    seconds -= 3600*hours
    minutes = seconds / 60
    seconds -= 60*minutes
    return "%02d:%02d:%02d" % (hours, minutes, seconds)

def send_email_notification(message, gconf, log, host = 'localhost'):
    
    import smtplib
    from email.mime.text import MIMEText
    
    # add subject information
    text = "Module:%s\nTime: %s\nProject Directory: %s\nSubject: %s\nTimepoint: %s\nWorkingdir: %s" % (message[0], \
            GetInHMS(message[1]), gconf.project_dir, gconf.subject_name, gconf.subject_timepoint, gconf.subject_workingdir)
    fromaddr = 'Connectome Mapper <info@connectomics.org>'
    
    msg = MIMEText(text)
    msg['Subject'] = "CMP - %s - Finished" % message[0]
    msg['From'] = fromaddr 
    msg['To'] = ", ".join(gconf.emailnotify)

    try:
        smtpObj = smtplib.SMTP(host)
        smtpObj.sendmail(fromaddr, gconf.emailnotify, msg.as_string())         
        log.info("Successfully sent email")    
    except smtplib.SMTPException:
        log.info("Error: Unable to send email")
    finally:
        smtpObj.quit()

