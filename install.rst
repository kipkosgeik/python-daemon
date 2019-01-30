'''
# List here what you need to be installed before your daemon runs like external libraries to be managed by PIP

# You can also run linux commands for setup like create directories
'''


pip install selenium
yum install vim
pip install pyvirtualdisplay


pip install python-keyczar
mkdir -p /opt/kz 
keyczart create --location=/tmp/kz --purpose=crypt 
keyczart addkey --location=/tmp/kz --status=primary 

