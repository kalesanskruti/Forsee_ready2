import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os
import subprocess

class ForseeBackendService(win32serviceutil.ServiceFramework):
    _svc_name_ = "ForseeBackend"
    _svc_display_name_ = "FORSEE Intelligence Backend"
    _svc_description_ = "Industrial reliability and PHM engine for FORSEE Intelligence."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.process = None

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        if self.process:
            self.process.terminate()

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def main(self):
        # Path to the uvicorn executable and app
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.chdir(backend_dir)
        
        # Start uvicorn in a subprocess
        cmd = [
            "python", "-m", "uvicorn", "app.main:app",
            "--host", "0.0.0.0", "--port", "8000"
        ]
        
        self.process = subprocess.Popen(cmd, env=os.environ.copy())
        
        # Wait for the stop event
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(ForseeBackendService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(ForseeBackendService)
